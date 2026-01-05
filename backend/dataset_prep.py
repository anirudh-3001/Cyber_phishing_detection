import pandas as pd
from canonicalize import canonicalize_url
from fingerprint import generate_fingerprint, get_prefix

def process_file(input_file, label, rows, limit=None):
    count = 0
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if limit is not None and count >= limit:
                break

            url = line.strip()
            if not url:
                continue

            try:
                canonical = canonicalize_url(url)
                fingerprint = generate_fingerprint(canonical)
                prefix = get_prefix(fingerprint)

                # destroy URL immediately
                del url
                del canonical

                rows.append([fingerprint, prefix, label])
                count += 1

            except Exception:
                continue

    return count


def build_dataset(phish_file, legit_file, output_file):
    rows = []

    print("Processing phishing URLs...")
    phish_count = process_file(phish_file, 1, rows)
    print(f"Phishing samples: {phish_count}")

    print("Processing legitimate URLs (balanced)...")
    legit_count = process_file(legit_file, 0, rows, limit=phish_count)
    print(f"Legitimate samples: {legit_count}")

    df = pd.DataFrame(
        rows,
        columns=["fingerprint", "prefix", "label"]
    )

    df.to_csv(output_file, index=False)
    print("Dataset created:", output_file)
    print("Total samples:", len(df))


if __name__ == "__main__":
    build_dataset(
        "openphish.txt",
        "tranco.txt",
        "dataset_phase1.csv"
    )
