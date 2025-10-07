from typing import Optional
from selenium.webdriver.common.by import By
import re

def _visible_text_of_element(el) -> str:
    # Use textContent to preserve hidden-but-structured content, then normalize.
    txt = (el.get_attribute("textContent") or "").strip()
    return re.sub(r"[ \t\r\f\v]+", " ", txt)

def _clean_text(t: str) -> str:
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t)     # collapse multiple blank lines
    t = re.sub(r"[ \t]+", " ", t)               # collapse internal spaces
    return t.strip()

def _extract_abstract_generic(driver) -> Optional[str]:
    # Try common labels
    candidate_selectors = [
        # Structured selectors
        "section#Abs1 div.abstract", "section#abstract", "section.abstract",
        "div.abstract", "div#abstract", "div.article__abstract",
        "[data-test='abstract']",
        # PubMed
        "div.abstract-content.selected", "div.abstract-content",
        # bioRxiv/medRxiv
        "div.section#abstract", "div#abstract p",
        # Nature/Cell variants
        "article section#Abs1 p", "article section#abstract p",
        # Science/AAAS
        "div.article__body section.abstract", "div#abstracts",
        # PNAS
        "div.abstract p",
        # Wiley/Springer/Elsevier (sciencedirect)
        "section.ArticleBody_abstract", "div.Abstracts", "div#as0001",
        # ArXiv
        "blockquote.abstract",
    ]
    for css in candidate_selectors:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, css)
            texts = []
            for e in els:
                try:
                    ps = e.find_elements(By.CSS_SELECTOR, "p")
                    if ps:
                        texts.extend(_visible_text_of_element(p) for p in ps)
                    else:
                        texts.append(_visible_text_of_element(e))
                except Exception:
                    continue
            texts = [t for t in texts if len(t) > 40]
            if texts:
                return _clean_text(" ".join(texts))
        except Exception:
            continue

    try:
        headings = driver.find_elements(By.XPATH, "//*[self::h1 or self::h2 or self::h3][contains(translate(., 'ABSTRACT', 'abstract'), 'abstract')]")
        for h in headings:
            # Collect paragraphs until the next heading sibling
            paras = []
            nodes = h.find_elements(By.XPATH, "following-sibling::*")
            for n in nodes:
                tag = (n.tag_name or "").lower()
                if tag in ("h1", "h2", "h3"):
                    break
                if tag == "p":
                    paras.append(n)
                else:
                    paras.extend(n.find_elements(By.XPATH, ".//p"))
            if paras:
                txt = " ".join(_visible_text_of_element(p) for p in paras[:8])
                if len(txt) > 60:
                    return _clean_text(txt)
    except Exception:
        pass

    return None
