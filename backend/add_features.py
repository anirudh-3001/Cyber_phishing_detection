import pandas as pd
import math
from urllib.parse import urlparse
import re


# ----------------- HELPERS -----------------

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    probs = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in probs)


def estimate_domain_age(domain: str) -> int:
    """
    Offline domain age estimation (paper-safe).
    Uses TLD + lexical heuristics.
    """
    suspicious_tlds = [
        ".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top",
        ".click", ".work", ".zip", ".link"
    ]

    # Very new / abused TLDs
    if any(domain.endswith(tld) for tld in suspicious_tlds):
        return 5

    # Random-looking domains → newer
    if "-" in domain or re.search(r"\d", domain):
        return 30

    # Long-established looking domain
    return 180


# ----------------- FEATURE EXTRACTION -----------------

def extract_features(url: str):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower().replace("www.", "")

    # ---------- SSL ----------
    tls_valid = 1 if parsed.scheme == "https" else 0

    # ---------- DOMAIN AGE (OFFLINE SAFE) ----------
    domain_age_days = estimate_domain_age(domain)

    # ---------- URL LEXICAL FEATURES ----------
    url_length = len(url)
    dot_count = url.count(".")
    hyphen_count = url.count("-")
    digit_ratio = sum(c.isdigit() for c in url) / len(url)
    has_at = int("@" in url)
    entropy = shannon_entropy(url)

    # ---------- KEYWORDS ----------
    suspicious_js = int(any(k in url.lower() for k in [
        "login", "verify", "secure", "account",
        "bank", "update", "signin", "confirm"
    ]))

    # ---------- REDIRECT HEURISTIC ----------
    redirect_count = url.count("http")

    return [
        domain_age_days,
        tls_valid,
        redirect_count,
        suspicious_js,
        url_length,
        dot_count,
        hyphen_count,
        digit_ratio,
        has_at,
        entropy
    ]


# ----------------- DATASET BUILD -----------------

def generate_ml_dataset():
    df = pd.read_csv("dataset_phase1.csv")

    rows = []
    for _, row in df.iterrows():
        try:
            url = row["url"]
            label = row["label"]

            features = extract_features(url)
            rows.append(features + [label])

        except Exception:
            continue

    columns = [
        "domain_age_days",
        "tls_valid",
        "redirect_count",
        "suspicious_js",
        "url_length",
        "dot_count",
        "hyphen_count",
        "digit_ratio",
        "has_at",
        "entropy",
        "label"
    ]

    out = pd.DataFrame(rows, columns=columns)
    out.to_csv("dataset_ml.csv", index=False)

    print("✅ dataset_ml.csv regenerated (OFFLINE, WHOIS-safe)")
    print("\nClass distribution:")
    print(out["label"].value_counts())


# ----------------- MAIN -----------------

if __name__ == "__main__":
    generate_ml_dataset()
