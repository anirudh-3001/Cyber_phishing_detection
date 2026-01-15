import whois
import ssl
import socket
import requests
from datetime import datetime
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

# Suspicious keywords in content/forms that indicate phishing
PHISHING_KEYWORDS = {
    "verify": 3, "confirm": 3, "validate": 3,
    "update": 2, "upgrade": 2,
    "login": 1, "signin": 1, "account": 1,
    "password": 2, "credential": 2,
    "urgent": 3, "action": 2, "required": 2,
    "expire": 2, "expire soon": 3,
    "click here": 2, "click now": 2,
    "unclassified": 2
}

LEGITIMATE_KEYWORDS = {
    "privacy": -2, "terms": -2, "about": -2,
    "contact": -1, "help": -1, "faq": -1,
    "blog": -1, "news": -1, "documentation": -2,
    "security": -1
}


def get_whois_score(domain: str) -> Tuple[float, Dict]:
    """
    Analyze WHOIS data for domain registration age.
    
    Score: 0.0-1.0 (0.0 = legitimate, 1.0 = phishing)
    Returns: (score, details_dict)
    """
    try:
        whois_data = whois.whois(domain)
        
        # Extract creation date
        creation_date = whois_data.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        if not creation_date:
            # No creation date found - suspicious
            return 0.6, {"status": "no_creation_date"}
        
        # Calculate domain age
        days_old = (datetime.now() - creation_date).days
        
        # Scoring logic
        if days_old < 30:
            score = 0.9  # Very new domain - suspicious
        elif days_old < 90:
            score = 0.7  # New domain - somewhat suspicious
        elif days_old < 365:
            score = 0.4  # Less than a year - neutral
        else:
            score = 0.1  # Old domain - legitimate indicator
        
        return score, {
            "status": "found",
            "creation_date": creation_date.isoformat(),
            "days_old": days_old,
            "score": score
        }
    
    except Exception as e:
        logger.warning(f"WHOIS lookup failed for {domain}: {e}")
        # If WHOIS fails, neutral score
        return 0.5, {"status": "lookup_failed", "error": str(e)}


def get_ssl_score(domain: str) -> Tuple[float, Dict]:
    """
    Analyze SSL certificate for validity and domain matching.
    
    Score: 0.0-1.0 (0.0 = legitimate, 1.0 = phishing)
    Returns: (score, details_dict)
    """
    try:
        # Get SSL certificate
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        
        # Check certificate validity
        if not cert:
            return 0.8, {"status": "no_cert"}
        
        # Extract subject alternative names
        san_list = []
        for item in cert.get('subjectAltName', []):
            if item[0] == 'DNS':
                san_list.append(item[1])
        
        # Check if domain matches certificate
        common_name = cert.get('subject', ((),))[0][0][1]
        all_names = san_list + [common_name]
        
        # Domain matching
        domain_match = False
        for name in all_names:
            if domain.lower() == name.lower() or domain.lower().endswith('.' + name.lower()):
                domain_match = True
                break
        
        if not domain_match:
            # Domain doesn't match cert - phishing indicator
            return 0.85, {
                "status": "domain_mismatch",
                "cert_domains": all_names,
                "requested_domain": domain
            }
        
        # Check cert expiry
        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        days_until_expiry = (not_after - datetime.now()).days
        
        if days_until_expiry < 0:
            # Expired certificate - phishing indicator
            return 0.9, {"status": "expired", "expired_date": cert['notAfter']}
        elif days_until_expiry < 30:
            # Expiring soon - legitimate but suspicious
            return 0.4, {"status": "expiring_soon", "days_until_expiry": days_until_expiry}
        else:
            # Valid certificate - legitimate
            return 0.1, {
                "status": "valid",
                "expires": cert['notAfter'],
                "days_until_expiry": days_until_expiry
            }
    
    except socket.timeout:
        logger.warning(f"SSL check timeout for {domain}")
        return 0.5, {"status": "timeout"}
    except ConnectionRefusedError:
        # Port 443 not open - likely HTTP only
        return 0.7, {"status": "no_https"}
    except Exception as e:
        logger.warning(f"SSL analysis failed for {domain}: {e}")
        return 0.5, {"status": "analysis_failed", "error": str(e)}


def get_content_score(url: str) -> Tuple[float, Dict]:
    """
    Analyze page HTML/CSS for phishing indicators.
    
    Score: 0.0-1.0 (0.0 = legitimate, 1.0 = phishing)
    Returns: (score, details_dict)
    """
    try:
        # Fetch page content with timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=5, headers=headers, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        text = soup.get_text().lower()
        html = response.text.lower()
        
        # Score calculation
        score = 0.0
        indicators = {}
        
        # 1. Check for login forms
        forms = soup.find_all('form')
        password_fields = soup.find_all('input', {'type': 'password'})
        indicators['forms_count'] = len(forms)
        indicators['password_fields'] = len(password_fields)
        
        if len(password_fields) > 0:
            score += 0.15  # Forms with passwords = phishing indicator
        
        # 2. Check for suspicious keywords
        suspicious_score = 0
        legitimate_score = 0
        
        for keyword, weight in PHISHING_KEYWORDS.items():
            if keyword in text:
                suspicious_score += weight
        
        for keyword, weight in LEGITIMATE_KEYWORDS.items():
            if keyword in text:
                legitimate_score += abs(weight)
        
        indicators['suspicious_keywords'] = suspicious_score
        indicators['legitimate_keywords'] = legitimate_score
        
        # Normalize keyword scores (0-0.3 range)
        if suspicious_score > 0:
            keyword_indicator_score = min(0.3, suspicious_score / 10)
            score += keyword_indicator_score
        
        if legitimate_score > 0:
            score = max(0.0, score - (legitimate_score / 20))
        
        # 3. Check for external scripts/iframes (potential drive-by downloads)
        external_scripts = soup.find_all('script', {'src': True})
        external_iframes = soup.find_all('iframe')
        indicators['external_scripts'] = len(external_scripts)
        indicators['iframes'] = len(external_iframes)
        
        if len(external_iframes) > 3:
            score += 0.1
        
        # 4. Check for suspicious meta tags
        meta_refreshes = soup.find_all('meta', {'http-equiv': 'refresh'})
        if len(meta_refreshes) > 0:
            score += 0.15  # Meta refresh = often phishing
            indicators['meta_refresh'] = True
        
        # 5. Check page title similarity to major brands
        title = soup.find('title')
        brand_keywords = ['login', 'signin', 'verify', 'confirm', 'update account', 'urgent action']
        if title and any(keyword in title.text.lower() for keyword in brand_keywords):
            score += 0.05
        
        # Normalize score to 0-1 range
        score = min(1.0, score)
        
        return score, {
            "status": "analyzed",
            "score": score,
            "indicators": indicators
        }
    
    except requests.Timeout:
        logger.warning(f"Content fetch timeout for {url}")
        return 0.4, {"status": "timeout"}
    except requests.RequestException as e:
        logger.warning(f"Content fetch failed for {url}: {e}")
        return 0.3, {"status": "fetch_failed", "error": str(e)}
    except Exception as e:
        logger.warning(f"Content analysis failed for {url}: {e}")
        return 0.3, {"status": "analysis_failed", "error": str(e)}


def get_advanced_analysis_score(url: str) -> Dict:
    """
    Perform advanced analysis and return all scores.
    
    Returns comprehensive analysis dict.
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        
        # Get individual scores
        whois_score, whois_details = get_whois_score(domain)
        ssl_score, ssl_details = get_ssl_score(domain)
        content_score, content_details = get_content_score(url)
        
        # Calculate weighted average
        advanced_score = (
            0.3 * whois_score +
            0.4 * ssl_score +
            0.3 * content_score
        )
        
        return {
            "whois": {
                "score": whois_score,
                "details": whois_details
            },
            "ssl": {
                "score": ssl_score,
                "details": ssl_details
            },
            "content": {
                "score": content_score,
                "details": content_details
            },
            "advanced_score": advanced_score,
            "url": url,
            "domain": domain
        }
    
    except Exception as e:
        logger.error(f"Advanced analysis failed for {url}: {e}")
        return {
            "error": str(e),
            "advanced_score": 0.5,  # Neutral on error
            "url": url
        }
