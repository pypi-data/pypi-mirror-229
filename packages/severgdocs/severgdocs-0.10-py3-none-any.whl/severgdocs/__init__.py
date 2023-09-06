import json
import re
import bs4
import requests
from a_selenium_iframes_crawler import Iframes
from flatten_any_dict_iterable_or_whatsoever import fla_tu
from kthread_sleep import sleep
import undetected_chromedriver as uc
from passprotecttxt import encrypt_text
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import lxml


def _get_text_with_requests(doclink):
    res = requests.get(doclink)
    allscripts = bs4.BeautifulSoup(res.content, "lxml").find_all("script")
    resultreq = ""
    for x in allscripts:
        if "DOCS_modelChunk = " in x.text:
            e = str(x.next_element)
            ef = re.findall(r"\[.*\]", e)
            eff = json.loads(ef[0])
            resultreq = [q[0] for q in (fla_tu(eff)) if "s" in q[-1]][0]
    return resultreq


def update_text(text, password, doclink, **kwargs):
    """
    Updates the text content in a Google Docs document using Selenium and encrypts the new text.

    This function automates the process of updating the content of a Google Docs document. It uses
    Selenium to interact with the document, including navigating through iframes and updating the
    text content. The updated text is encrypted using the provided password.

    Args:
        text (str): The new text content to be added or updated.
        password (str): The password used for encryption.
        doclink (str): The URL of the Google Docs document.
        **kwargs: Additional keyword arguments for configuring the Chrome WebDriver.

    Returns:
        str: The updated and encrypted text content of the Google Docs document.

    Raises:
        Any exceptions raised during the Selenium interaction with the document.

    Example:
        from severgdocs import update_text
        nt = update_text(
            text="babudada",
            password="bibidudu",
            doclink="https://docs.google.com/document/d/1xxxxx/edit",
        )
        print(nt)
    """
    driver = uc.Chrome(headless=True, **kwargs)
    driver.get(doclink)
    newtext = encrypt_text(text, password)
    getiframes = lambda: Iframes(
        driver,
        By,
        WebDriverWait,
        expected_conditions,
        seperator_for_duplicated_iframe="Ç",
        ignore_google_ads=True,
    )

    resultreq = _get_text_with_requests(doclink)
    while resultreq != newtext:
        didweclick = False
        driver.switch_to.default_content()
        iframes = getiframes()
        for ini, iframe in enumerate(iframes.iframes):
            if didweclick:
                break
            try:
                iframes.switch_to(iframe)
                elemethods = driver.find_elements(
                    By.CSS_SELECTOR,
                    r"""div[role="textbox"][aria-multiline="true"][contenteditable="true"]""",
                )
                for ele in elemethods:
                    try:
                        ele.send_keys(Keys.PAGE_DOWN)
                        ele.send_keys(Keys.END)
                        try:
                            ele.send_keys(Keys.BACKSPACE * len(resultreq) * 2)
                        except Exception:
                            pass
                        sleep(1)
                        ele.send_keys(newtext)
                        didweclick = True
                        break
                    except Exception:
                        continue
            except Exception:
                continue
        resultreq = _get_text_with_requests(doclink)
    driver.close()
    driver.quit()
    return newtext

