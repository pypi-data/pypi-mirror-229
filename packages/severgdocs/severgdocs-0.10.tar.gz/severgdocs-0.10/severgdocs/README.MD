# Jerrybuilt data exchange through Google Docs - server 

## Tested against Windows 10 / Python 3.10 / Anaconda

## pip install severgdocs

```python
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

# this module 
from severgdocs import update_text
nt = update_text(
    text="babudada",
    password="bibidudu",
    doclink="https://docs.google.com/document/d/xxxx/edit",
)
print(nt)

# client module
from clientgdocs import get_text_from_google_docs
doclink = "https://docs.google.com/document/d/xxxx/edit"
password = "bibidudu"
text = get_text_from_google_docs(doclink, password, timeout=30)
print(text)

```