from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.firefox.service import Service as FFService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
import shutil, os

def _make_driver(browser='firefox'):
    if browser=='firefox':
        return _make_driver_firefox(headless=True)
    elif browser=='chrome':
        return _make_driver_chrome()
    else:
        raise ValueError(f"Invalid browser: {browser}")

def _make_driver_firefox(headless: bool = True, user_agent: str | None = None):
    opts = FFOptions()
    if headless:
        opts.add_argument("-headless")
    # A modern desktop UA helps with CF heuristics
    ua = user_agent or "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "\
                       "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    opts.set_preference("general.useragent.override", ua)

    # Make sure scripts/cookies work and tracking protection doesn’t block
    opts.set_preference("privacy.trackingprotection.enabled", False)
    opts.set_preference("privacy.resistFingerprinting", False)
    opts.set_preference("network.http.referer.spoofSource", False)
    opts.set_preference("dom.disable_open_during_load", False)
    opts.set_preference("network.cookie.cookieBehavior", 0)  # allow all
    opts.set_preference("intl.accept_languages", "en-US,en")
    driver = webdriver.Firefox(options=opts)
    driver.set_page_load_timeout(60)
    driver.implicitly_wait(3)
    return driver

def _make_driver_chrome(headless: bool = True, user_agent: str | None = None):
    CHROME_BIN = os.getenv("CHROME_BINARY_PATH")
    CHROMEDRIVER = os.getenv("CHROMEDRIVER_PATH")
    HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

    if CHROME_BIN and CHROMEDRIVER:
        copts = ChromeOptions()
        copts.add_argument("--no-sandbox")
        copts.add_argument("--disable-dev-shm-usage")
        copts.add_argument("--window-size=1440,900")
        if HEADLESS:
            copts.add_argument("--headless=new")
        copts.binary_location = CHROME_BIN

        drv = webdriver.Chrome(service=ChromeService(CHROMEDRIVER), options=copts)
        drv.set_page_load_timeout(60); drv.implicitly_wait(2)
        return drv


    ffopts = FFOptions()
    if HEADLESS:
        ffopts.add_argument("-headless")
    # If geckodriver is in PATH (conda-forge puts it there), service can be omitted
    try:
        drv = webdriver.Firefox(options=ffopts)
    except Exception:
        import shutil
        gd = shutil.which("geckodriver")  # explicit service if needed
        drv = webdriver.Firefox(service=FFService(executable_path=gd), options=ffopts)

    drv.set_page_load_timeout(60); drv.implicitly_wait(2)
    return drv