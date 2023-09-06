import json
import re
import time
import lxml
import bs4
import requests
from flatten_any_dict_iterable_or_whatsoever import fla_tu
from passprotecttxt import decrypt_text
from pfehler import pfehler


def get_text_from_google_docs(doclink, password, timeout=30):
    """
    This module provides a function for extracting text content from a Google Docs link
    protected by a password. It uses BeautifulSoup, requests, and other libraries to
    retrieve and decrypt the content.
    
    Functions:
        get_text_from_google_docs(doclink, password, timeout=30):
            Retrieves and decrypts the text content from a Google Docs link protected by a password.
    
    Parameters:
        doclink (str): The URL of the Google Docs document.
        password (str): The password used to decrypt the document.
        timeout (int, optional): The maximum time (in seconds) to wait for the document to load. Defaults to 30 seconds.
    
    Returns:
        str: The decrypted text content of the Google Docs document.
    
    Example:
        from clientgdocs import get_text_from_google_docs
        doclink = "https://docs.google.com/document/d/1xxxxx/edit"
        password = "bibidudu"
        text = get_text_from_google_docs(doclink, password, timeout=30)
        print(text)
    """
    decrypted_text = ""
    timeoutfinal = time.time() + timeout
    found = False
    while (time.time() < timeoutfinal) and not found:
        try:
            res = requests.get(doclink)
            allscripts = bs4.BeautifulSoup(res.content, "lxml").find_all("script")
            for x in allscripts:
                try:
                    if "DOCS_modelChunk = " in x.text:
                        e = str(x.next_element)
                        ef = re.findall(r"\[.*\]", e)
                        eff = json.loads(ef[0])
                        encrypted_text = [q[0] for q in (fla_tu(eff)) if "s" in q[-1]][
                            0
                        ]
                        decrypted_text = decrypt_text(encrypted_text, password)
                        found = True
                        break
                except Exception:
                    pfehler()
        except Exception:
            pfehler()
    return decrypted_text

