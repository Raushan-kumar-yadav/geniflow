from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree

def fetch_image_url_with_selenium(partial_url="/pin/1138918193270170546/"):
    options = Options()
    options.headless = True  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    base_url = "https://pinterest.com" + partial_url
    driver.get(base_url)

    try:
        # Wait for the image to load (adjust the timeout as needed)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//img"))
        )

        # Print the page source for debugging
        page_source = driver.page_source
        print(page_source)  # This will help you see the actual HTML

        # Parse the page source
        dom = etree.HTML(page_source)

        # Use the specific XPath expression
        xpath_expression = "//img[contains(@alt='This may contain:')]/@src"
        links = dom.xpath(xpath_expression)

        if links:
            return links[0]  # Return the first matching URL
        else:
            print("No image found with the specified alt text.")

    except Exception as e:
        print("An error occurred:", e)
    finally:
        driver.quit()

    return None

image_url = fetch_image_url_with_selenium()
print(image_url)