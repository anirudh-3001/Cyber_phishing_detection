from sync_openphish import sync_openphish
import add_features
import train_model
import reputation


def run_full_pipeline() -> dict:
    """Run the full pipeline: sync openphish -> generate ML dataset -> train model -> reload reputation.

    Returns a status dict with counts and metrics.
    """
    result = {"synced": 0, "model_path": None, "metrics": {}}

    # 1) sync openphish entries into phase CSV
    try:
        added = sync_openphish()
        result["synced"] = added
    except Exception as e:
        result["error_sync"] = str(e)

    # 2) generate ML dataset (uses add_features.generate_ml_dataset)
    try:
        add_features.generate_ml_dataset()
    except Exception as e:
        result["error_prepare"] = str(e)

    # 3) train model
    try:
        model_path, metrics = train_model.train_and_save()
        result["model_path"] = model_path
        result["metrics"] = metrics
    except Exception as e:
        result["error_train"] = str(e)

    # 4) reload reputation prefixes
    try:
        reputation.load_phishing_prefixes()
    except Exception:
        pass

    return result


if __name__ == "__main__":
    print(run_full_pipeline())
