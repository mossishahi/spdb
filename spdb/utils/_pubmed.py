import requests
from spdb.utils._keys import NCBI_API_KEY, TOOL, EMAIL


def get_pubmed_abstract(doi: str) -> str:
    """
    Given a DOI, return the PubMed abstract (if available).
    Requires an environment variable NCBI_API_KEY with your key.
    """
    api_key = NCBI_API_KEY
    if not api_key:
        raise RuntimeError("Please set the NCBI_API_KEY environment variable")

    # 1) DOI -> PMID
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": f"{doi}[doi]",
        "retmode": "json",
        "tool": TOOL,
        "email": EMAIL,
        "api_key": api_key,
    }
    r = requests.get(search_url, params=params)
    r.raise_for_status()
    ids = r.json().get("esearchresult", {}).get("idlist", [])
    if not ids:
        raise ValueError(f"No PubMed entry found for DOI {doi}")
    pmid = ids[0]

    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "json",
        "tool": TOOL,
        "email": EMAIL,
        "api_key": api_key,
    }
    s = requests.get(summary_url, params=params)
    s.raise_for_status()
    docsum = s.json()["result"][pmid]
    abstract = docsum.get("abstract", "")
    if not abstract:
        fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": pmid,
            "retmode": "xml",
            "tool": TOOL,
            "email": EMAIL,
            "api_key": api_key,
        }
        f = requests.get(fetch_url, params=params)
        f.raise_for_status()
        # Simple XML extraction
        import xml.etree.ElementTree as ET
        root = ET.fromstring(f.text)
        abst_elems = root.findall(".//AbstractText")
        abstract = "\n".join(a.text for a in abst_elems if a.text)

    return abstract.strip()
