# Jerrybuilt data exchange through Google Docs - client 

## Tested against Windows 10 / Python 3.10 / Anaconda

## pip install clientgdocs

```python
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

# server module 
from severgdocs import update_text
nt = update_text(
    text="babudada",
    password="bibidudu",
    doclink="https://docs.google.com/document/d/xxxx/edit",
)
print(nt)

# this module 
from clientgdocs import get_text_from_google_docs
doclink = "https://docs.google.com/document/d/xxxx/edit"
password = "bibidudu"
text = get_text_from_google_docs(doclink, password, timeout=30)
print(text)

```