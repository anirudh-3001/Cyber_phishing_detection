import os
from typing import Optional

# simple in-memory blacklist (Phase-2A)
KNOWN_PHISHING_PREFIXES = set()


def load_phishing_prefixes(csv_file: str = "dataset_phase1.csv", openphish_file: Optional[str] = "openphish.txt"):
    """Load known phishing prefixes from the phase CSV and optionally from an openphish feed file.

    - csv_file: CSV that contains a `prefix` column and `label` (1=phish).
    - openphish_file: newline-separated URLs to canonicalize + fingerprint and add as phishing prefixes.
    """
    import pandas as pd
    from canonicalize import canonicalize_url
    from fingerprint import generate_fingerprint, get_prefix

    # Load CSV-based prefixes (existing behaviour)
    if os.path.exists(csv_file):
        try:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                try:
                    if int(row.get("label", 0)) == 1 and "prefix" in row:
                        KNOWN_PHISHING_PREFIXES.add(str(row["prefix"]))
                except Exception:
                    continue
        except Exception:
            # ignore CSV errors; continue to attempt loading openphish
            pass

    # Also ingest simple text feed of URLs (one URL per line)
    if openphish_file and os.path.exists(openphish_file):
        try:
            with open(openphish_file, "r", encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    url = line.strip()
                    if not url:
                        continue
                    try:
                        canonical = canonicalize_url(url)
                        fp = generate_fingerprint(canonical)
                        prefix = get_prefix(fp)
                        KNOWN_PHISHING_PREFIXES.add(prefix)
                    except Exception:
                        # skip malformed URLs
                        continue
        except Exception:
            pass


def is_known_phishing(prefix: str) -> bool:
    return prefix in KNOWN_PHISHING_PREFIXES
