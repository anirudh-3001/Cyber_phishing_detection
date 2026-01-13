from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
from reputation import load_phishing_prefixes, is_known_phishing
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
import pipeline
import model_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS for frontend demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
model = None
scheduler = None
RETRAIN_INTERVAL_HOURS = 24  # Retrain every 24 hours


def load_model(path: str = "rf_model.pkl"):
	"""Load the trained model from disk."""
	global model
	try:
		model = joblib.load(path)
		logger.info(f"Model loaded from {path}")
	except Exception as e:
		logger.error(f"Failed to load model: {e}")
		model = None


def retrain_job():
	"""Background job to retrain model automatically."""
	logger.info(f"[{datetime.now()}] Starting scheduled model retraining...")
	try:
		# Run full pipeline: sync, feature extraction, training
		status = pipeline.run_full_pipeline()
		# Reload the updated model
		load_model()
		reputation.load_phishing_prefixes()
		logger.info(f"[{datetime.now()}] Retraining completed. Status: {status}")
	except Exception as e:
		logger.error(f"[{datetime.now()}] Retraining failed: {e}")


def start_scheduler():
	"""Start background scheduler for periodic retraining."""
	global scheduler
	try:
		scheduler = BackgroundScheduler()
		scheduler.add_job(
			retrain_job,
			'interval',
			hours=RETRAIN_INTERVAL_HOURS,
			id='model_retrain',
			name='Model Retraining Job'
		)
		scheduler.start()
		logger.info(f"Scheduler started. Model will retrain every {RETRAIN_INTERVAL_HOURS} hours.")
	except Exception as e:
		logger.error(f"Failed to start scheduler: {e}")


def stop_scheduler():
	"""Stop background scheduler."""
	global scheduler
	if scheduler and scheduler.running:
		scheduler.shutdown()
		logger.info("Scheduler stopped.")


# Load model and reputation data on startup
load_model()
load_phishing_prefixes()

from canonicalize import canonicalize_url
from fingerprint import generate_fingerprint, get_prefix


# FastAPI startup and shutdown events
@app.on_event("startup")
def startup_event():
	"""Initialize scheduler when API starts."""
	start_scheduler()


@app.on_event("shutdown")
def shutdown_event():
	"""Stop scheduler when API shuts down."""
	stop_scheduler()


@app.post("/fingerprint")
def fingerprint_url(payload: dict):
    url = payload["url"]

    canonical = canonicalize_url(url)
    fp = generate_fingerprint(canonical)
    prefix = get_prefix(fp)

    # Extract REAL features from the URL
    from urllib.parse import urlparse
    import re
    
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    
    # Feature 1: Domain Age (estimate from domain characteristics)
    # Real domains: old TLDs, longer, no numbers/dashes
    # Phishing: new TLDs, short, with numbers/dashes
    suspicious_patterns = 0
    if re.search(r'\d+', domain):
        suspicious_patterns += 1
    if '-' in domain:
        suspicious_patterns += 1
    if len(domain) < 8:
        suspicious_patterns += 1
    
    phishing_tlds = ['.click', '.tk', '.ml', '.cf', '.ga', '.work', '.download', '.zip', '.date', '.bid']
    if any(domain.endswith(tld) for tld in phishing_tlds):
        domain_age_days = 0  # Brand new = phishing indicator
    elif suspicious_patterns >= 2:
        domain_age_days = 5
    elif suspicious_patterns == 1:
        domain_age_days = 25
    else:
        domain_age_days = 90  # Assume old/legitimate domain
    
    # Feature 2: TLS/HTTPS Valid
    tls_valid = 1 if parsed.scheme == 'https' else 0
    
    # Feature 3: Redirect Count (estimate from URL length and path)
    # Complex URLs with query params might indicate redirects
    redirect_count = 0
    if parsed.query:
        redirect_count = 1
    if parsed.fragment:
        redirect_count = min(redirect_count + 1, 2)
    
    # Feature 4: Suspicious JS (estimate from domain/URL patterns)
    # Check for common phishing URL patterns
    suspicious_js = 0
    if 'confirm' in url.lower() or 'verify' in url.lower() or 'update' in url.lower():
        suspicious_js = 1
    if 'login' in url.lower() or 'signin' in url.lower():
        suspicious_js = 1
    
    # destroy URL from memory
    del url
    del canonical

    return {
        "fingerprint": fp,
        "prefix": prefix,
        "domain_age_days": domain_age_days,
        "tls_valid": tls_valid,
        "redirect_count": redirect_count,
        "suspicious_js": suspicious_js
    }


@app.post("/detect")
def detect(payload: dict):
    prefix = payload["prefix"]

    # Stage 1: reputation check
    if is_known_phishing(prefix):
        return {"result": "phishing", "method": "reputation"}

    # Stage 2: ML detection
    features = [[
        payload["domain_age_days"],
        payload["tls_valid"],
        payload["redirect_count"],
        payload["suspicious_js"]
    ]]

    prediction = model.predict(features)[0]

    # CORRECT MAPPING:
    # prediction == 1 → Legitimate (label 1 in training)
    # prediction == 0 → Phishing (label 0 in training)
    return {
        "result": "legitimate" if prediction == 1 else "phishing",
        "method": "machine_learning"
    }

@app.post("/reload")
def reload_pipeline():
	"""Run full sync+train pipeline and reload model/reputation in memory."""
	status = pipeline.run_full_pipeline()
	load_model()
	load_phishing_prefixes()
	status["model_loaded"] = model is not None
	return status


@app.get("/scheduler/status")
def get_scheduler_status():
	"""Get current scheduler status and next retraining time."""
	if scheduler is None:
		return {"status": "not_initialized"}
	
	return {
		"status": "running" if scheduler.running else "stopped",
		"retrain_interval_hours": RETRAIN_INTERVAL_HOURS,
		"jobs": [
			{
				"id": job.id,
				"name": job.name,
				"next_run_time": str(job.next_run_time) if job.next_run_time else None
			}
			for job in scheduler.get_jobs()
		]
	}


@app.post("/scheduler/pause")
def pause_scheduler():
	"""Pause the retraining scheduler."""
	global scheduler
	if scheduler and scheduler.running:
		scheduler.pause()
		logger.info("Scheduler paused.")
		return {"status": "paused"}
	return {"status": "not_running"}


@app.post("/scheduler/resume")
def resume_scheduler():
	"""Resume the retraining scheduler."""
	global scheduler
	if scheduler and not scheduler.running:
		scheduler.resume()
		logger.info("Scheduler resumed.")
		return {"status": "resumed"}
	return {"status": "already_running"}


# ============ Model Versioning & Rollback Endpoints ============

@app.get("/models/history")
def get_model_history(limit: int = 10):
	"""Get list of trained models with their metrics."""
	history = model_manager.get_model_history(limit)
	return {
		"total_models": len(history),
		"models": history
	}


@app.get("/models/metrics-comparison")
def get_metrics_comparison():
	"""Compare metrics across all model versions."""
	return model_manager.get_model_metrics_comparison()


@app.post("/models/rollback/{timestamp}")
def rollback_model(timestamp: str):
	"""Rollback to a previous model version by timestamp."""
	model_path = model_manager.rollback_to_model(timestamp)
	if model_path:
		load_model(model_path)
		return {
			"status": "success",
			"model_path": model_path,
			"timestamp": timestamp
		}
	return {
		"status": "failed",
		"message": f"Could not rollback to model with timestamp {timestamp}"
	}


@app.delete("/models/cleanup")
def cleanup_old_models(keep_count: int = 5):
	"""Delete old model versions, keeping only the most recent N."""
	model_manager.delete_old_models(keep_count)
	return {
		"status": "success",
		"message": f"Cleaned up old models. Keeping {keep_count} recent versions."
	}


@app.get("/models/current")
def get_current_model_info():
	"""Get info about currently active model."""
	metadata = model_manager.load_metadata()
	current_path = metadata.get("current")
	
	current_info = None
	for m in metadata.get("models", []):
		if m.get("path") == current_path:
			current_info = m
			break
	
	if current_info:
		return {
			"status": "loaded",
			"current_model": current_info
		}
	return {
		"status": "not_loaded"
	}