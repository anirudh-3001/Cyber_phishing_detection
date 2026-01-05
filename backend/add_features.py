import pandas as pd
import random

df = pd.read_csv("dataset_phase1.csv")

df["domain_age_days"] = [random.randint(1, 1500) for _ in range(len(df))]
df["tls_valid"] = [random.randint(0, 1) for _ in range(len(df))]
df["redirect_count"] = [random.randint(0, 5) for _ in range(len(df))]
df["suspicious_js"] = [random.randint(0, 1) for _ in range(len(df))]

df.to_csv("dataset_ml.csv", index=False)
print("ML dataset created: dataset_ml.csv")
