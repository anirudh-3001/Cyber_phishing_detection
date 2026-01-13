import os
import json
import joblib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

MODELS_DIR = "models"
METADATA_FILE = os.path.join(MODELS_DIR, "models_metadata.json")


def initialize_models_directory():
	"""Create models directory if it doesn't exist."""
	Path(MODELS_DIR).mkdir(exist_ok=True)
	if not os.path.exists(METADATA_FILE):
		with open(METADATA_FILE, "w") as f:
			json.dump({"models": [], "current": None}, f, indent=2)


def get_model_version_path(timestamp: str = None) -> str:
	"""Generate versioned model filename with timestamp."""
	if timestamp is None:
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	return os.path.join(MODELS_DIR, f"rf_model_{timestamp}.pkl")


def save_model_version(model, metrics: Dict) -> str:
	"""Save model with version and metadata."""
	initialize_models_directory()
	
	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	model_path = get_model_version_path(timestamp)
	
	joblib.dump(model, model_path)
	logger.info(f"Model saved to {model_path}")
	
	metadata = load_metadata()
	model_info = {
		"timestamp": timestamp,
		"path": model_path,
		"created_at": datetime.now().isoformat(),
		"metrics": metrics,
		"status": "active"
	}
	metadata["models"].append(model_info)
	metadata["current"] = model_path
	
	save_metadata(metadata)
	logger.info(f"Model metadata updated. Current model: {model_path}")
	
	return model_path


def load_metadata() -> Dict:
	"""Load models metadata from JSON file."""
	initialize_models_directory()
	try:
		with open(METADATA_FILE, "r") as f:
			return json.load(f)
	except Exception as e:
		logger.error(f"Failed to load metadata: {e}")
		return {"models": [], "current": None}


def save_metadata(metadata: Dict):
	"""Save models metadata to JSON file."""
	try:
		with open(METADATA_FILE, "w") as f:
			json.dump(metadata, f, indent=2)
	except Exception as e:
		logger.error(f"Failed to save metadata: {e}")


def get_current_model():
	"""Load the current active model."""
	metadata = load_metadata()
	current_path = metadata.get("current")
	
	if current_path and os.path.exists(current_path):
		try:
			model = joblib.load(current_path)
			logger.info(f"Loaded current model from {current_path}")
			return model
		except Exception as e:
			logger.error(f"Failed to load current model: {e}")
	
	return None


def get_model_history(limit: int = 10) -> List[Dict]:
	"""Get list of all trained models with their metrics."""
	metadata = load_metadata()
	models = sorted(metadata.get("models", []), 
				   key=lambda x: x.get("timestamp", ""), 
				   reverse=True)
	return models[:limit]


def rollback_to_model(timestamp: str) -> Optional[str]:
	"""Rollback to a previous model version."""
	metadata = load_metadata()
	
	target_model = None
	for model_info in metadata["models"]:
		if model_info.get("timestamp") == timestamp:
			target_model = model_info
			break
	
	if not target_model:
		logger.error(f"Model with timestamp {timestamp} not found")
		return None
	
	model_path = target_model.get("path")
	if not os.path.exists(model_path):
		logger.error(f"Model file not found: {model_path}")
		return None
	
	metadata["current"] = model_path
	save_metadata(metadata)
	logger.info(f"Rolled back to model: {model_path}")
	
	return model_path


def delete_old_models(keep_count: int = 5):
	"""Clean up old model files, keeping only the most recent N versions."""
	metadata = load_metadata()
	models = sorted(metadata.get("models", []), 
				   key=lambda x: x.get("timestamp", ""), 
				   reverse=True)
	
	models_to_keep = models[:keep_count]
	models_to_delete = models[keep_count:]
	
	for model_info in models_to_delete:
		model_path = model_info.get("path")
		try:
			if os.path.exists(model_path):
				os.remove(model_path)
				logger.info(f"Deleted old model: {model_path}")
		except Exception as e:
			logger.error(f"Failed to delete {model_path}: {e}")
	
	metadata["models"] = models_to_keep
	save_metadata(metadata)
	logger.info(f"Cleanup complete. Kept {len(models_to_keep)} recent models.")


def get_model_metrics_comparison() -> Dict:
	"""Compare metrics across all model versions."""
	history = get_model_history(limit=100)
	
	comparison = {
		"total_models": len(history),
		"current_model_timestamp": None,
		"current_model_metrics": None,
		"best_model": None,
		"models": []
	}
	
	best_accuracy = -1
	best_model_info = None
	
	metadata = load_metadata()
	current_path = metadata.get("current")
	
	for model_info in history:
		metrics = model_info.get("metrics", {})
		accuracy = metrics.get("accuracy", 0)
		
		model_data = {
			"timestamp": model_info.get("timestamp"),
			"created_at": model_info.get("created_at"),
			"metrics": metrics,
			"is_current": model_info.get("path") == current_path
		}
		comparison["models"].append(model_data)
		
		if model_info.get("path") == current_path:
			comparison["current_model_timestamp"] = model_info.get("timestamp")
			comparison["current_model_metrics"] = metrics
		
		if accuracy > best_accuracy:
			best_accuracy = accuracy
			best_model_info = model_info
	
	if best_model_info:
		comparison["best_model"] = {
			"timestamp": best_model_info.get("timestamp"),
			"metrics": best_model_info.get("metrics"),
			"accuracy": best_accuracy
		}
	
	return comparison
