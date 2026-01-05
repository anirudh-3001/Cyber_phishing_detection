from urllib.parse import urlparse, urlunparse

def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)

    scheme = "https"
    netloc = parsed.netloc.lower()

    if netloc.startswith("www."):
        netloc = netloc[4:]

    netloc = netloc.replace(":443", "").replace(":80", "")
    path = parsed.path.rstrip("/")

    return urlunparse((scheme, netloc, path, "", "", ""))


# quick test
if __name__ == "__main__":
    print(canonicalize_url(
        "HTTP://WWW.Example.com:443/Login/?utm=123"
    ))
