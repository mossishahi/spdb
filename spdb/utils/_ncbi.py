import time
import re
import requests
import xml.etree.ElementTree as ET
from spdb.utils._keys import NCBI_API_KEY
from bs4 import BeautifulSoup
from spdb.utils._browse import _make_driver
from spdb.utils._html import _visible_text_of_element
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PMID_RE = re.compile(r"\bPMID\s*[:#]?\s*(\d{7,8})\b", re.I)


def pmid_to_doi(pmid: str) -> str | None:
    """
    Return the DOI for a PubMed article, or None if not found.
    """
    api_key = NCBI_API_KEY
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "xml",
    }
    if api_key:
        params["api_key"] = api_key

    r = requests.get(url, params=params)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    for eloc in root.findall(".//ELocationID"):
        if eloc.attrib.get("EIdType") == "doi":
            return eloc.text
    return None


def get_pmids_from_geo(geo_url: str) -> list[str]:
    """
    Given a GEO dataset URL (e.g. https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE250346),
    return a list of PubMed IDs mentioned on that page.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(geo_url, headers=headers)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # --- Option 1: look for links to PubMed ---
    pmids = set()
    for a in soup.select("a[href*='pubmed.ncbi.nlm.nih.gov']"):
        m = re.search(r"(\d+)", a.get("href"))
        if m:
            pmids.add(m.group(1))

    # --- Option 2: look for plain "PMID 12345678" text ---
    if not pmids:
        text = soup.get_text(" ", strip=True)
        pmids.update(re.findall(r"PMID\s*(\d+)", text))

    return sorted(pmids)


def get_pmids_from_geo_with_selenium(geo_url: str, browser: str = "firefox", timeout: int = 10) -> List[str]:
    """
    Load a GEO dataset page with Selenium and return a list of PubMed IDs found on the page.
    Robust to interstitials; looks for both PubMed links and literal 'PMID 12345678' text.
    """
    drv = _make_driver(browser=browser)
    pmids = set()
    try:
        drv.get(geo_url)
        wait = WebDriverWait(drv, timeout)
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table#scope")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "table")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#EntrezForm")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
        )

        time.sleep(1.0)

        anchors = drv.find_elements(By.CSS_SELECTOR, "a[href*='pubmed.ncbi.nlm.nih.gov'], a[href*='/pubmed/']")
        for a in anchors:
            href = a.get_attribute("href") or ""
            m = re.search(r"/(\d{7,8})(?:/|$)", href)
            if m:
                pmids.add(m.group(1))

        body_text = _visible_text_of_element(drv.find_element(By.TAG_NAME, "body"))
        for m in PMID_RE.finditer(body_text):
            pmids.add(m.group(1))

        if not pmids:
            rows = drv.find_elements(By.CSS_SELECTOR, "table tr")
            for row in rows:
                try:
                    th = row.find_element(By.TAG_NAME, "th")
                    if "citation" in th.text.lower():
                        links = row.find_elements(By.CSS_SELECTOR, "a[href]")
                        for a in links:
                            href = a.get_attribute("href") or ""
                            m = re.search(r"/(\d{7,8})(?:/|$)", href)
                            if m:
                                pmids.add(m.group(1))
                except Exception:
                    continue

        return sorted(pmids)
    finally:
        try:
            drv.quit()
        except Exception:
            pass

def fetch_pubmed_meta(pmids):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "json"}
    if NCBI_API_KEY:
        params["api_key"] = NCBI_API_KEY
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()["result"]

def sort_pmids_by_date(pmids):
    meta = fetch_pubmed_meta(pmids)
    # skip the 'uids' key
    records = []
    for pid in pmids:
        rec = meta.get(pid, {})
        sortdate = rec.get("sortpubdate") or rec.get("pubdate") or rec.get("epubdate")
        records.append((pid, sortdate))
    # convert to comparable: 'YYYY/MM/DD' → tuple
    def key(x):
        d = x[1]
        if not d:
            return (0,0,0)
        parts = d.split()[0].split("/")
        try:
            return tuple(map(int, parts[:3]))  # Y, M, D
        except:
            return (0,0,0)
    return sorted(records, key=key, reverse=True)[0]  # newest first