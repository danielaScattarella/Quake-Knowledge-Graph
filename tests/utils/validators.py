# utils/validators.py

import os
import re
from urllib.parse import urlparse, parse_qs

def validate_ingv_dataset_url(url: str) -> bool:
    """Validate URLs pointing to INGV datasets or static earthquake datasets."""
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Must be http or https
    if parsed.scheme not in ("http", "https"):
        return False

    url_lower = url.lower()

    # ✅ 1) Accept static dataset files from ANY domain (.csv .json .xml .txt)
    static_exts = (".csv", ".json", ".xml", ".txt")
    if url_lower.endswith(static_exts):
        return True

    # ✅ 2) Accept INGV FDSN dynamic API endpoints (no extension required)
    allowed_domains = ("ingv.it", "webservices.ingv.it")

    if any(parsed.netloc.endswith(domain) for domain in allowed_domains):

        valid_paths = (
            "/fdsnws/event/1/query",
            "/fdsnws/station/1/query",
        )

        if any(parsed.path.startswith(p) for p in valid_paths):
            query = parse_qs(parsed.query)
            fmt = query.get("format", ["text"])[0].lower()

            valid_formats = {"text", "csv", "json", "xml", "geocsv"}

            return fmt in valid_formats

    # ❌ Otherwise invalid
    return False

# ------------------------------------------------------------
# 2) VALIDAZIONE PERCORSI LOCALI (DATASET)
# ------------------------------------------------------------
def validate_local_dataset_path(path: str) -> bool:
    """
    Accept only safe relative paths.
    Reject traversal attempts like '../' on Unix systems.
    """
    if not path or not isinstance(path, str):
        return False

    # Prevent directory traversal (*nix)
    if os.sep == "/" and (".." in Path(path).parts):
        return False

    # Must end with valid dataset extension
    if not any(path.lower().endswith(ext) for ext in (".txt", ".csv", ".xml", ".json")):
        return False

    return True


# ------------------------------------------------------------
# 3) SANITIZZAZIONE INPUT
# ------------------------------------------------------------
def sanitize_input(text: str) -> str:
    """Removes null bytes and trims whitespace."""
    if not isinstance(text, str):
        return ""

    text = text.replace("\0", "")
    return text.strip()


# ------------------------------------------------------------
# 4) VALIDAZIONE NOME DATASET
# ------------------------------------------------------------
def validate_dataset_name(name: str) -> bool:
    """
    Accept dataset names that contain:
    - letters
    - numbers
    - spaces
    - underscores
    - hyphens
    """
    if not name:
        return False

    pattern = r"^[A-Za-z0-9 _-]+$"
    return bool(re.match(pattern, name))