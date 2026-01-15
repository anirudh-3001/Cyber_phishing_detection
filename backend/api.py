from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import joblib, logging, math, re
from urllib.parse import urlparse
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import pipeline
from reputation import load_phishing_prefixes, is_known_phishing
from canonicalize import canonicalize_url
from fingerprint import generate_fingerprint, get_prefix

# ---------------- APP ----------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- GLOBALS ----------------
model = joblib.load("rf_model.pkl")
load_phishing_prefixes()

FEATURE_NAMES = [
    "domain_age_days", "tls_valid", "redirect_count", "suspicious_js",
    "url_length", "dot_count", "hyphen_count",
    "digit_ratio", "has_at", "entropy"
]

# ---------------- UTILS ----------------
def shannon_entropy(s: str) -> float:
    probs = [s.count(c) / len(s) for c in set(s)]
    return -sum(p * math.log2(p) for p in probs) if s else 0.0


def explain_ml_decision(model, feature_names, values):
    scores = dict.fromkeys(feature_names, 0)
    for tree in model.estimators_:
        node = 0
        while tree.tree_.children_left[node] != -1:
            f = tree.tree_.feature[node]
            t = tree.tree_.threshold[node]
            node = tree.tree_.children_left[node] if values[f] <= t else tree.tree_.children_right[node]
            scores[feature_names[f]] += 1
    total = sum(abs(v) for v in scores.values()) or 1
    return {k: round(abs(v)/total, 3) for k,v in scores.items()}


# ---------------- ERROR HANDLER ----------------
@app.exception_handler(Exception)
async def error_handler(_, exc):
    return JSONResponse(status_code=500, content={"error": str(exc)})


# ---------------- FINGERPRINT ----------------
@app.post("/fingerprint")
def fingerprint_url(payload: dict):
    url = payload["url"]
    canonical = canonicalize_url(url)
    fp = generate_fingerprint(canonical)
    prefix = get_prefix(fp)

    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "").lower()

    suspicious = sum([
        "-" in domain,
        bool(re.search(r"\d", domain)),
        len(domain) < 8
    ])

    domain_age_days = 5 if any(domain.endswith(t) for t in [".tk",".ml",".ga",".cf",".click",".zip"]) \
        else 30 if suspicious >= 2 else 180

    return {
        "fingerprint": fp,
        "prefix": prefix,
        "domain_age_days": domain_age_days,
        "tls_valid": int(parsed.scheme == "https"),
        "redirect_count": url.count("http"),
        "suspicious_js": int(any(k in url.lower() for k in ["login","verify","update","confirm","secure"])),
        "url_length": len(url),
        "dot_count": url.count("."),
        "hyphen_count": url.count("-"),
        "digit_ratio": sum(c.isdigit() for c in url) / max(len(url),1),
        "has_at": int("@" in url),
        "entropy": shannon_entropy(url)
    }


# ---------------- DETECT ----------------
@app.post("/detect")
def detect(payload: dict):
    prefix = payload.get("prefix")

    # ---------- REPUTATION ----------
    if is_known_phishing(prefix):
        return {
            "result": "phishing",
            "method": "reputation",
            "confidence": 1.0,
            "reasons": ["Matched known phishing fingerprint"]
        }

    values = [payload.get(f, 0) for f in FEATURE_NAMES]

    pred = model.predict([values])[0]
    probs = model.predict_proba([values])[0]

    explanation = explain_ml_decision(model, FEATURE_NAMES, values)

    reasons = []
    if payload.get("tls_valid") == 0:
        reasons.append("Website does not use HTTPS")
    if payload.get("domain_age_days", 0) < 30:
        reasons.append("Domain appears newly registered")
    if payload.get("suspicious_js") == 1:
        reasons.append("Suspicious keywords found in URL")
    if payload.get("hyphen_count", 0) > 2:
        reasons.append("Excessive hyphens in domain")

    return {
        "result": "phishing" if pred == 0 else "legitimate",
        "method": "machine_learning",
        "confidence": round(max(probs), 3),
        "ml_probabilities": {
            "phishing": round(probs[0], 3),
            "legitimate": round(probs[1], 3)
        },
        "reasons": reasons,
        "feature_contributions": explanation
    }
