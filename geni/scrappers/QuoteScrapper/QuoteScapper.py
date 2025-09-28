
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time



class QuoteScraper():

    def __init__(self,url, element_selector):
        self.url = url
        self.element_selector = element_selector
        
    def scrape_text_from_website(self):
        """
        Scrapes text from a website using Selenium.
        Parameters:
            url (str): The URL of the website to scrape.
            element_selector (str): The CSS selector for the element containing the desired text.
        Returns:
            str: The scraped text.
        """
        # Configure Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in headless mode
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
    
        # Automatically manage and update the ChromeDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
        try:
            # Open the website
            driver.get(self.url)
            time.sleep(2)  # Wait for the page to load
    
            # Find the element and extract text
            element = driver.find_element(By.CSS_SELECTOR, self.element_selector)
            scraped_text = element.text
    
        finally:
            # Close the WebDriver
            driver.quit()
    
        return scraped_text
    