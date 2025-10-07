from spdb.utils._browse import _make_driver
from spdb.utils._html import _extract_abstract_generic
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

def scrape_dataset_abstract(
    url: str,
    wait_seconds: int = 10
) -> str:
    """
    Inputs:
        url            : landing url (dataset page, 10x page, or the paper itself)
        dataset_title  : optional human-readable dataset title (improves LLM fallback)
        wait_seconds   : max wait for page interactive elements

    Returns:
        abstract text
    """
    driver = _make_driver()
    driver.get(url)
    WebDriverWait(driver, wait_seconds).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(1.0)
    abstract = _extract_abstract_generic(driver)
    driver.quit()
    return abstract

