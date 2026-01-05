import hmac
import hashlib

SECRET_KEY = b"final_phase1_secret_key"

def generate_fingerprint(canonical_url: str) -> str:
    return hmac.new(
        SECRET_KEY,
        canonical_url.encode(),
        hashlib.sha512
    ).hexdigest()

def get_prefix(fingerprint: str, length=12) -> str:
    return fingerprint[:length]


if __name__ == "__main__":
    url = "https://example.com/Login"
    fp = generate_fingerprint(url)
    print("Fingerprint:", fp)
    print("Prefix:", get_prefix(fp))
