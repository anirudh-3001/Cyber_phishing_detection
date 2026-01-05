from canonicalize import canonicalize_url
from fingerprint import generate_fingerprint, get_prefix

def process_url(url: str):
    print("Original URL:", url)

    # Step 1: Canonicalize
    canonical = canonicalize_url(url)
    print("Canonical URL:", canonical)

    # Step 2: Fingerprint
    fingerprint = generate_fingerprint(canonical)
    prefix = get_prefix(fingerprint)

    # 🔥 Step 3: Destroy URL
    del url
    del canonical

    print("\nURL destroyed ✅")
    print("Fingerprint:", fingerprint)
    print("Prefix:", prefix)

    return fingerprint, prefix


if __name__ == "__main__":
    process_url("https://secure-login.example.com/verify?utm=123")
