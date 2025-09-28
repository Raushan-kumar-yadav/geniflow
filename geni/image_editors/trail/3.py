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
from lxml import etree
from PIL import Image
from io import BytesIO
import pytesseract

class PinterestImageScrapper:
    def __init__(self, user_data_dir, profile_dir, excelpath="", headless="None"):
        self.user_data_dir = user_data_dir
        self.profile_dir = profile_dir
        self.driver = None
        self.options = Options()
        self.excelpath = excelpath
        self.headless = headless
        
        """Configure Chrome options for user profile and other settings."""
        self.options.add_argument(f"--user-data-dir={self.user_data_dir}")
        self.options.add_argument(f"--profile-directory={self.profile_dir}")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--remote-debugging-port=9222")
        self.options.add_argument("--disable-gpu")  # Optional, useful for headless or restricted environments
        self.options.add_argument("--verbose")  # Enable verbose logging
        if self.headless.lower() == "headless":
            self.options.add_argument("--headless")

    def start_browser(self, link):
        """Initialize and start the Chrome WebDriver with the configured options."""
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
            self.driver.get(link)
            print("Chrome with profile started successfully!")
        except Exception as e:
            print(f"Error: {e}")

    def serch(self, query):
        """
        This method will return image link as per search.

        Args:
        query (str): What to search on Pinterest.
        """
        try:
            pinterest_search_box = self.driver.find_element(By.XPATH, "//input[@placeholder='Search']")
            pinterest_search_box.send_keys(query)
            pinterest_search_box.send_keys(Keys.RETURN)
            time.sleep(2)
        except Exception as e:
            print(f"Error during search: {e}")

    def match_href_in_excel(self, search_string):
        """
        Searches for a specific string in an Excel file.

        Args:
            search_string (str): The string to search for.

        Returns:
            bool: True if the string is found, False otherwise.
        """
        try:
            workbook = openpyxl.load_workbook(self.excelpath)
            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                for row in sheet.iter_rows(values_only=True):
                    for cell in row:
                        if cell and search_string in str(cell):
                            return False
            return True
        except Exception as e:
            print(f"Error: {e}")
            return True

    def insert_href_into_excel(self, input_string):
        """
        Inserts a string into the first empty cell of the first sheet in an Excel file.

        Args:
            input_string (str): The string to insert.

        Returns:
            bool: True if insertion was successful, False otherwise.
        """
        try:
            workbook = openpyxl.load_workbook(self.excelpath)
            sheet = workbook.active
            for row in sheet.iter_rows():
                for cell in row:
                    if cell.value is None:
                        cell.value = input_string
                        workbook.save(self.excelpath)
                        print(f"Inserted '{input_string}' into cell {cell.coordinate}.")
                        return True
            sheet.append([input_string])
            workbook.save(self.excelpath)
            print(f"No empty cell found. Inserted '{input_string}' into a new row.")
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def fetch_image_url(self, partial_url):
        """
        Complete and fetch the image URL using XPath expressions.

        Args:
            partial_url (str): Relative image URL.

        Returns:
            str: Full image URL or None if not found.
        """
        xpath_expressions = ["//img[starts-with(@alt, 'This may contain:')]/@src", "//img[@alt='Story pin image']/@src"]
        base_url = "https://pinterest.com" + partial_url
        print("this is base url ", base_url)
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        dom = etree.HTML(str(soup))
        for xpath in xpath_expressions:
            links = dom.xpath(xpath)
            if links:
                return links[0]
        return None

    def cheack_size(self, ImageUrl, WebSiteName="pinpinterest", imagewidth=500, imageheight=500):
        """
        Calculate image height and width.

        Args:
            ImageUrl (str): Image URL.
            WebSiteName (str): Website name.
            imagewidth (int): Image width.
            imageheight (int): Image height.

        Returns:
            bool: True if image size is greater than specified dimensions, False otherwise.
        """
        try:
            print("checking size for this url ", self.fetch_image_url(partial_url=ImageUrl))
            image = requests.get(self.fetch_image_url(partial_url=ImageUrl))
            img = Image.open(BytesIO(image.content))
            width, height = img.size
            print(width, height)
            return width > imagewidth and height > imageheight
        except Exception as e:
            print(f"Error checking image size: {e}")
            return False

    def extract_text_from_image(self, imageURL):
        """
        Extracts text from the provided image using Tesseract OCR.

        Args:
            imageURL (str): Image URL.

        Returns:
            bool: False if text is found, True otherwise.
        """
        try:
            print("checking for text in image ", self.fetch_image_url(partial_url=imageURL))
            image = requests.get(self.fetch_image_url(partial_url=imageURL))
            image_extension = os.path.splitext(self.fetch_image_url(partial_url=imageURL))[1]
            if image.status_code == 200:
                with open(f"0234765xfddgd{image_extension}", "wb") as file:
                    file.write(image.content)
                print("Image successfully downloaded and saved!")
            else:
                print(f"Failed to download the image. Status code: {image.status_code}")
                return True
            image_path = f"0234765xfddgd{image_extension}"
            cvimage = Image.open(image_path)
            text = pytesseract.image_to_string(cvimage)
            return not bool(text)
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return True

    def get_link(self, max_number_of_links=1):
        """
        Extract image links from Pinterest search results.

        Args:
            max_number_of_links (int): Maximum number of image links to extract.

        Returns:
            list: A list of extracted image URLs.
        """
        href_links = []
        max_iterations = 10  # Set a maximum number of iterations to avoid infinite loop
        iterations = 0

        while len(href_links) < max_number_of_links and iterations < max_iterations:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            link_elements = self.driver.find_elements(By.XPATH, "//div[@data-test-id='pin']")
            for link_element in link_elements:
                try:
                    outer_html = link_element.get_attribute('outerHTML')
                    soup = BeautifulSoup(outer_html, 'html.parser')
                    a_tag = soup.find('a', href=True)
                    img_tag = soup.find('img')
                    if a_tag and img_tag:
                        href = a_tag['href']
                        print("this is link of image", href)
                        if href not in href_links and self.match_href_in_excel(search_string=href) and self.cheack_size(href) and self.extract_text_from_image(href):
                            href_links.append(href)
                            self.insert_href_into_excel(href)
                            if len(href_links) >= max_number_of_links:
                                return href_links
                except Exception as e:
                    print(f"Error processing element: {e}")
                    continue
            iterations += 1

        return href_links

    def ImageSave(self, imageURL=[]):
        """
        Save the image from the provided URL.

        Args:
            imageURL (list): List of image URLs.
        """
        if not imageURL:
            print("No image URLs provided.")
            return

        web = "https://pinterest.com"
        full_image_url = web + imageURL[0]
        try:
            image_link = requests.get(full_image_url)
            soup = BeautifulSoup(image_link.content, 'html.parser')
            dom = etree.HTML(str(soup))
            xpath_expression = "//img[@alt='Story pin image']/@src"
            link = dom.xpath(xpath_expression)
            if link:
                first_link = link[0]
                print(f"First image link: {first_link}")
            else:
                print("The image list is empty.")
                return
            image_extension = os.path.splitext(first_link)[1]
            image = requests.get(first_link)
            if image.status_code == 200:
                with open(f"downloaded_image{image_extension}", "wb") as file:
                    file.write(image.content)
                print("Image successfully downloaded and saved!")
            else:
                print(f"Failed to download the image. Status code: {image.status_code}")
        except Exception as e:
            print(f"Error saving image: {e}")

    def close_browser(self):
        """Close the browser if it was started."""
        if self.driver:
            self.driver.quit()

    def force_quit_all_chrome(self):
        """Kill all ChromeDriver processes."""
        try:
            os.system("taskkill /f /im chrome.exe")
            print("Quitting all chrome")
        except Exception as e:
            print(f"Error quitting chrome: {e}")

# Example usage:
if __name__ == "__main__":
    user_data_dir = "C:/Users/raush/AppData/Local/Google/Chrome/User Data"  # Replace with your actual path
    profile_dir = "Profile 7"  # Replace with your profile name (e.g., "Default", "Profile 1")
    excel_path = r"csv\used_image_from_pin.xlsx"
    chrome_profile = PinterestImageScrapper(user_data_dir, profile_dir, excelpath=excel_path)
    chrome_profile.force_quit_all_chrome()
    chrome_profile.start_browser(link="https://in.pinterest.com/")
    time.sleep(3)
    chrome_profile.serch(query="quote images")
    time.sleep(5)
    imageLink = chrome_profile.get_link()
    if imageLink:
        print("this is image link" + imageLink[0])
        chrome_profile.ImageSave(imageURL=imageLink)
    else:
        print("No image links found.")
    time.sleep(5)
    chrome_profile.close_browser()