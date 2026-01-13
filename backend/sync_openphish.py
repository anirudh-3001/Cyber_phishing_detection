import os
from typing import Optional

from canonicalize import canonicalize_url
from fingerprint import generate_fingerprint, get_prefix


def sync_openphish(openphish_file: str = "openphish.txt", phase_csv: str = "dataset_phase1.csv") -> int:
    """Ensure every URL in `openphish_file` has an entry in `phase_csv` with label=1.

    Returns the number of new entries appended.
    """
    import csv

    if not os.path.exists(openphish_file):
        return 0

    existing_prefixes = set()
    # Read existing phase CSV prefixes
    if os.path.exists(phase_csv):
        try:
            with open(phase_csv, "r", newline="", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    if "prefix" in row:
                        existing_prefixes.add(row["prefix"])
        except Exception:
            existing_prefixes = set()

    new_rows = []
    with open(openphish_file, "r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            url = line.strip()
            if not url:
                continue
            try:
                canonical = canonicalize_url(url)
                fp = generate_fingerprint(canonical)
                prefix = get_prefix(fp)
            except Exception:
                continue

            if prefix not in existing_prefixes:
                new_rows.append((fp, prefix, "1"))
                existing_prefixes.add(prefix)

    if not new_rows:
        return 0

    # Append to CSV
    write_header = not os.path.exists(phase_csv)
    with open(phase_csv, "a", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if write_header:
            writer.writerow(["fingerprint", "prefix", "label"])
        for r in new_rows:
            writer.writerow(r)

    return len(new_rows)


if __name__ == "__main__":
    added = sync_openphish()
    print(f"Added {added} new entries to dataset_phase1.csv")
