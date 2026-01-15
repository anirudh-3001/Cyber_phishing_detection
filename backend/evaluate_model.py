import pandas as pd
import time
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

import reputation
import model_manager

# ---------- CONFIG ----------
DATASET = "dataset_test.csv"
LABEL_COL = "label"

FEATURES = [
    "domain_age_days",
    "tls_valid",
    "redirect_count",
    "suspicious_js",
    "url_length",
    "dot_count",
    "hyphen_count",
    "digit_ratio",
    "has_at",
    "entropy"
]
# ---------------------------


def evaluate():
    df = pd.read_csv(DATASET)
    y_true = df[LABEL_COL]

    # Load trained model
    model = model_manager.get_current_model()
    assert model is not None, "No trained model found"

    # ---------- ML ONLY ----------
    X = df[FEATURES]
    y_ml = model.predict(X)
    ml_probs = model.predict_proba(X)[:, 0]  # phishing probability

    # ---------- REPUTATION ONLY ----------
    reputation.load_phishing_prefixes()
    y_rep = []

    for _, row in df.iterrows():
        prefix = row.get("prefix", None)
        if prefix and reputation.is_known_phishing(prefix):
            y_rep.append(0)  # phishing
        else:
            y_rep.append(1)  # legitimate

    # ---------- HYBRID (ACCURACY-OPTIMIZED) ----------
    y_hybrid = []
    start = time.time()

    for i, row in df.iterrows():
        ml_score = ml_probs[i]
        rep_score = 1.0 if y_rep[i] == 0 else 0.0

        # small, controlled risk boost
        risk_boost = 0.0
        if row["tls_valid"] == 0:
            risk_boost += 0.05
        if row["domain_age_days"] < 30:
            risk_boost += 0.05
        if row["suspicious_js"] == 1:
            risk_boost += 0.05

        hybrid_score = (0.8 * ml_score) + (0.1 * rep_score) + risk_boost
        final_label = 0 if hybrid_score >= 0.65 else 1
        y_hybrid.append(final_label)

    latency = (time.time() - start) / len(df)

    # ---------- METRICS ----------
    def report(name, y_pred):
        print(f"\n=== {name} ===")
        print(f"Accuracy : {accuracy_score(y_true, y_pred):.4f}")
        print(f"Precision: {precision_score(y_true, y_pred):.4f}")
        print(f"Recall   : {recall_score(y_true, y_pred):.4f}")
        print(f"F1-score : {f1_score(y_true, y_pred):.4f}")
        print("Confusion Matrix:")
        print(confusion_matrix(y_true, y_pred))

    report("ML ONLY", y_ml)
    report("REPUTATION ONLY", y_rep)
    report("HYBRID SYSTEM", y_hybrid)

    print(f"\n⏱️ Avg Hybrid Latency: {latency*1000:.2f} ms per URL")


if __name__ == "__main__":
    evaluate()
