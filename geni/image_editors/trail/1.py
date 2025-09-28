from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from bs4 import BeautifulSoup
import openpyxl
import requests
import lxml
from lxml import etree,html
from PIL import Image
from io import BytesIO
import pytesseract
    


def fetch_image_url( partial_url="/pin/1138918193270170546/" ):
        """
        Complete and fetch the image URL using XPath expressions.

        Args:
            partial_url (str): Relative image URL.
            xpath_expressions (list): List of XPath expressions to evaluate.

        Returns:
            str: Full image URL or None if not found.
        """

        xpath_expressions = ['//img[contains(@alt, "This may contain")]/@src',"//img[@alt='Story pin image']/@src"]
        base_url = "https://pinterest.com" + partial_url
        print("this is base url ",base_url)
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        dom = html.fromstring(soup)

        for xpath in xpath_expressions:
            links = dom.xpath(xpath)
            if links:
                return links[0]  # Return the first matching URL
        return None

iamgeurl = fetch_image_url()
print(iamgeurl)
