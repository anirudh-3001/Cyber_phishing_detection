import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import model_manager


def train_and_save():
    """
    Train ML model ONLY on dataset_train.csv
    No evaluation here (paper-safe).
    """

    # ---------- LOAD TRAIN DATA ----------
    df = pd.read_csv("dataset_train.csv")

    print("\n=== Training Dataset Analysis ===")
    print(f"Total samples: {len(df)}")
    print(f"Legitimate (1): {(df['label'] == 1).sum()}")
    print(f"Phishing (0): {(df['label'] == 0).sum()}")
    print(f"Class balance: {(df['label'] == 1).sum() / len(df) * 100:.1f}% legit\n")

    # ---------- FEATURES ----------
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

    X_train = df[FEATURES]
    y_train = df["label"]

    # ---------- TRAIN MODEL ----------
    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=18,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    print("✅ Model trained successfully")

    # ---------- SAVE MODEL ----------
    versioned_path = model_manager.save_model_version(
        model,
        {"note": "Evaluation on unseen test set"}
    )

    joblib.dump(model, "rf_model.pkl")

    print(f"✅ Versioned model saved: {versioned_path}")
    print("✅ rf_model.pkl saved (compatibility)")

    return versioned_path


if __name__ == "__main__":
    train_and_save()
