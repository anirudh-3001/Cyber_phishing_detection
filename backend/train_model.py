import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
import joblib
import model_manager
from typing import Tuple

# Load dataset
df = pd.read_csv("dataset_ml.csv")

# Check class distribution
print("\n=== Dataset Analysis ===")
print(f"Total samples: {len(df)}")
print(f"Legitimate (1): {(df['label'] == 1).sum()}")
print(f"Phishing (0): {(df['label'] == 0).sum()}")
print(f"Class balance: {(df['label'] == 1).sum() / len(df) * 100:.1f}% legitimate\n")

X = df[
    ["domain_age_days", "tls_valid", "redirect_count", "suspicious_js"]
]
y = df["label"]

# Train-test split (stratified to maintain class balance)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {len(X_train)} samples")
print(f"Test set: {len(X_test)} samples\n")

# Train IMPROVED model with better hyperparameters
model = RandomForestClassifier(
    n_estimators=200,           # More trees for better accuracy
    max_depth=15,               # Prevent overfitting
    min_samples_split=5,        # Better decision boundaries
    min_samples_leaf=2,
    random_state=42,
    class_weight='balanced',    # Handle class imbalance
    n_jobs=-1                   # Use all CPU cores
)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

print("=== Model Performance ===")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1-score : {f1:.4f}")

# Cross-validation score
cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1_weighted')
print(f"Cross-validation F1: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})\n")

# Confusion matrix
print("=== Confusion Matrix ===")
cm = confusion_matrix(y_test, y_pred)
print(f"True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
print(f"False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}\n")

# Feature importance
print("=== Feature Importance ===")
features = ["Domain Age (days)", "TLS/HTTPS Valid", "HTTP Redirects", "Suspicious JS"]
for feat, imp in zip(features, model.feature_importances_):
    print(f"{feat}: {imp:.4f}")
print()

# Save metrics
metrics = {
	"accuracy": float(accuracy),
	"precision": float(precision),
	"recall": float(recall),
	"f1": float(f1)
}

# Save versioned model
versioned_path = model_manager.save_model_version(model, metrics)
print(f"Versioned model saved as: {versioned_path}")

# Also save to default path for backward compatibility
joblib.dump(model, "rf_model.pkl")
print("Model saved as rf_model.pkl (for backward compatibility)")

# Clean up old models (keep last 10)
model_manager.delete_old_models(keep_count=10)

