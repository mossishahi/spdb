import re
import urllib.parse as up
import requests
from typing import Optional, Dict, Any
from spdb.utils._keys import ELSEVIER_API_KEY

PII_REGEX = re.compile(r"\bS\d{16}\b", re.IGNORECASE)

def extract_elsevier_pii_from_url(url: str) -> Optional[str]:
    """
    Extracts an Elsevier PII (e.g., S0092867423012229) from common publisher URLs:
    - https://linkinghub.elsevier.com/retrieve/pii/S0092867423012229
    - https://www.sciencedirect.com/science/article/pii/S0092867423012229
    - cell.com URLs that include the Elsevier PII in the query (_returnURL=.../pii/S...)
    """
    parsed = up.urlparse(url)
    # Check path and query together
    haystack = " ".join([parsed.path, parsed.query, up.unquote(parsed.query)])
    m = PII_REGEX.search(haystack)
    return m.group(0) if m else None

def _pick_abstract_from_payload(payload: Dict[str, Any]) -> Optional[str]:
    """
    Tries several common locations where Elsevier returns the abstract.
    Priority order based on typical responses.
    """
    ftr = payload.get("full-text-retrieval-response") or {}

    core = ftr.get("coredata") or {}
    abstract = core.get("dc:description")
    if abstract:
        return abstract.strip()

    for key in ("originalText", "description", "abstracts"):
        val = ftr.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, dict):
            for k2 in ("abstract", "description"):
                if isinstance(val.get(k2), str) and val.get(k2).strip():
                    return val.get(k2).strip()

    arr = payload.get("abstracts-retrieval-response") or {}
    if isinstance(arr, dict):
        core2 = arr.get("coredata") or {}
        if isinstance(core2.get("dc:description"), str):
            return core2["dc:description"].strip()
        if isinstance(arr.get("item"), dict):
            item = arr["item"]
            try:
                txt = item["bibrecord"]["head"]["abstracts"]["abstract"]["abstracttext"]
                if isinstance(txt, str) and txt.strip():
                    return txt.strip()
            except Exception:
                pass

    return None

def get_elsevier_abstract_from_url(url: str, *, timeout: int = 15) -> Dict[str, Any]:
    """
    Returns a dict:
      {
        "status": "ok" | "no_pii" | "not_found" | "no_abstract" | "auth_error" | "rate_limited" | "error",
        "pii": "S0092867423012229" or None,
        "abstract": "..." or None,
        "message": "... optional explanation ..."
      }
    """
    if not ELSEVIER_API_KEY:
        return {
            "status": "error",
            "pii": None,
            "abstract": None,
            "message": "ELSEVIER_API_KEY environment variable is missing."
        }

    pii = extract_elsevier_pii_from_url(url)
    if not pii:
        return {
            "status": "no_pii",
            "pii": None,
            "abstract": None,
            "message": "Could not find an Elsevier PII in the URL."
        }

    api_url = f"https://api.elsevier.com/content/article/pii/{pii}"
    headers = {
        "X-ELS-APIKey": ELSEVIER_API_KEY,
        "Accept": "application/json",
    }
    params = {"httpAccept": "application/json"}  # explicit, though Accept header is enough

    try:
        r = requests.get(api_url, headers=headers, params=params, timeout=timeout)
        if r.status_code == 401 or r.status_code == 403:
            return {
                "status": "auth_error",
                "pii": pii,
                "abstract": None,
                "message": f"Authorization error ({r.status_code}). Check your Elsevier API key and entitlements."
            }
        if r.status_code == 429:
            return {
                "status": "rate_limited",
                "pii": pii,
                "abstract": None,
                "message": "Rate limited by Elsevier API (HTTP 429). Try again later."
            }
        if r.status_code == 404:
            return {
                "status": "not_found",
                "pii": pii,
                "abstract": None,
                "message": "No record found for this PII."
            }
        r.raise_for_status()
        data = r.json()
    except requests.RequestException as e:
        return {
            "status": "error",
            "pii": pii,
            "abstract": None,
            "message": f"Request failed: {e}"
        }

    abstract = _pick_abstract_from_payload(data)
    if abstract:
        return abstract
    else:
        return None