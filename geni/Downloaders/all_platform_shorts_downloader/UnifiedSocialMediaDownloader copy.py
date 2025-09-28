import os
import tempfile
import time
import requests
import openpyxl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from lxml import etree
from PIL import Image
import undetected_chromedriver as uc
import math
import pyautogui
import random
import yt_dlp
import threading
import sys
import urllib
import psutil
import subprocess

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class UnifiedSocialMediaDownloader:
    """
    A unified class for downloading various content types (videos, shorts/reels, images)
    from different social media platforms.
    """
    
    CONTENT_TYPES = ["video", "short", "image","reel","story"]
    SUPPORTED_PLATFORMS = ["youtube", "instagram", "tiktok", "twitter","pinterest"]
    
    def __init__(self, control_quit_callback, control_pause_callback, base_user_data_dir=None, 
                 profile_dir="Default", excelpath="", headless=False,
                 web_link="Youtube", uc_refrance=None):
        """
        Initialize the downloader with browser settings and control callbacks.
        
        Args:
            control_quit_callback: Event to signal quitting
            control_pause_callback: Event to signal pausing
            base_user_data_dir: Chrome user data directory
            profile_dir: Chrome profile directory
            excelpath: Path to Excel file for tracking downloaded content
            headless: Whether to run browser in headless mode
            web_link: Default platform to open
            uc_refrance: Chrome options reference
        """
        
        if base_user_data_dir:
            self.base_user_data_dir = base_user_data_dir
        else:
            self.base_user_data_dir = tempfile.mkdtemp()

        self.profile_dir = profile_dir
        self.options =  uc.ChromeOptions()  #uc_refrance if uc_refrance else
        self.excelpath = excelpath
        self.headless = headless
        self.web_link = web_link
        self.driver = None
        self.parent_process = None
        self.child_processes = None
        """         # Set up Chrome options
        self.options.add_argument(f"--user-data-dir={self.base_user_data_dir}")
        self.options.add_argument(f"--profile-directory={self.profile_dir}")
        self.options.add_argument("window-size=500x300") """

        if self.headless:
            self.options.add_argument("--headless")

        # For pause/resume/quit control
        self.pause_event = control_pause_callback
        self.quit_event = control_quit_callback

        # Start a thread to monitor the quit event
        quit_thread = threading.Thread(target=self.monitor_quit, daemon=True)
        quit_thread.start()

        # Initialize browser
        self.initialize_browser()

    def _kill_existing_processes(self):
        """Kill existing Chrome and ChromeDriver processes"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and ('chrome' in proc.info['name'].lower() or 
                                        'chromedriver' in proc.info['name'].lower()):
                    try:
                        proc.kill()
                        proc.wait(timeout=3)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                        pass
        except Exception as e:
            print(f"Error killing processes: {e}")

    def _get_chrome_version(self):
        """Get installed Chrome version"""
        try:
            import winreg
            # For Windows
            reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                version, _ = winreg.QueryValueEx(key, "version")
                return int(version.split('.')[0])
        except:
            try:
                # For Linux/Mac - alternative method
                result = subprocess.run(['google-chrome', '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split()[-1]
                    return int(version.split('.')[0])
            except:
                pass
        
        # Default fallback versions to try
        return None

    def initialize_browser(self):
        """Initialize Chrome browser with multiple fallback strategies"""
        print("Initializing undetected Chrome browser...")

        # Strategy 1: Try with explicit Chrome version
        try:
            print("Attempting with explicit Chrome version...")
            chrome_version = self._get_chrome_version()
            
            options = uc.ChromeOptions()
            
            # Essential options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--window-size=500,300")
            options.add_argument("--disable-logging")
            options.add_argument("--disable-gpu-logging")
            options.add_argument("--silent")

            # Profile options
            if self.base_user_data_dir:
                options.add_argument(f"--user-data-dir={self.base_user_data_dir}")
            if self.profile_dir:
                options.add_argument(f"--profile-directory={self.profile_dir}")

            if self.headless:
                options.add_argument("--headless=new")  # Use new headless mode

            # Try with explicit version if available
            if chrome_version:
                self.driver = uc.Chrome(
                    options=options,
                    version_main=chrome_version,
                    user_multi_procs=True,
                    use_subprocess=False
                )
            else:
                self.driver = uc.Chrome(
                    options=options,
                    version_main=None,  # Auto-detect
                    user_multi_procs=True,
                    use_subprocess=False
                )

            # Test if driver is working
            self.driver.set_window_size(500, 300)
            print("✓ Chrome initialized successfully with explicit version!")
            self._capture_process_info()
            return

        except Exception as e1:
            print(f"Explicit version failed: {e1}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

        # Strategy 2: Try with minimal options
        try:
            print("Attempting with minimal options...")
            
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=500,300")
            
            if self.headless:
                options.add_argument("--headless=new")

            self.driver = uc.Chrome(
                options=options,
                user_multi_procs=False,
                use_subprocess=True
            )

            self.driver.set_window_size(500, 300)
            print("✓ Chrome initialized successfully with minimal options!")
            self._capture_process_info()
            return

        except Exception as e2:
            print(f"Minimal options failed: {e2}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None

        # Strategy 3: Try downloading ChromeDriver manually
        try:
            print("Attempting manual ChromeDriver setup...")
            
            # Create a custom driver directory
            driver_dir = os.path.join(tempfile.gettempdir(), f"custom_chromedriver_{os.getpid()}")
            os.makedirs(driver_dir, exist_ok=True)
            
            options = uc.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=500,300")
            
            if self.headless:
                options.add_argument("--headless=new")

            self.driver = uc.Chrome(
                options=options,
                driver_executable_path=None,  # Let it auto-download
                browser_executable_path=None,  # Auto-detect Chrome
                user_multi_procs=False
            )

            self.driver.set_window_size(500, 300)
            print("✓ Chrome initialized successfully with manual setup!")
            self._capture_process_info()
            return

        except Exception as e3:
            print(f"Manual setup failed: {e3}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None



    def _capture_process_info(self):
        """Capture process information for cleanup"""
        try:
            if hasattr(self.driver, 'service') and hasattr(self.driver.service, 'process'):
                self.driver_pid = self.driver.service.process.pid
                print(f"ChromeDriver PID: {self.driver_pid}")
                
                self.parent_process = psutil.Process(self.driver_pid)
                self.child_processes = self.parent_process.children(recursive=True)
            else:
                print("Could not capture process info - service not available")
        except Exception as e:
            print(f"Unable to capture PID: {e}")

        
    def arrange_chrome_instance(self):
        """Calculate positions for multiple Chrome instances on screen"""
        screen_width, screen_height = pyautogui.size()
        no_of_instances = 2
        cols = math.ceil(math.sqrt(no_of_instances))
        rows = math.ceil(no_of_instances / cols)
        window_width = screen_width // cols
        window_height = screen_height // rows
        positions = []
        for i in range(no_of_instances):
            col = i % cols
            row = i // cols
            x = col * window_width
            y = row * window_height
            positions.append((x, y, window_width, window_height))
        return positions
    
    def monitor_quit(self):
        """Continuously monitor the quit event and trigger quit if set."""
        if self.quit_event is not None:
            while not self.quit_event.is_set():
                time.sleep(0.1)
            
            self.quit()
        
    def start_browser(self):
        """Initialize and start the Chrome WebDriver with the configured options."""
        try:
            #self.driver.set_window_size(500, 300)
            self.driver.get(self.web_link)
            print(f"Chrome with profile started successfully! Opening {self.web_link}")
        except Exception as e:
            print(f"Error starting browser: {e}")

    def get_cookies(self):
        """Get the cookies from the current browser session"""
        return self.driver.get_cookies()

    def save_cookies_to_netscape(self, Chrome_base_path):
        """Save browser cookies in Netscape format for use with yt-dlp"""
        cookies = self.get_cookies()
        time.sleep(random.uniform(2.0, 4.0))
        cookies_path = os.path.join(Chrome_base_path, "cookies.txt")
        with open(cookies_path, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# https://curl.se/docs/http-cookies.html\n")
            f.write("# This file was generated by Selenium\n\n")
            for cookie in cookies:
                domain = cookie.get('domain', '')
                flag = "TRUE" if domain.startswith('.') else "FALSE"
                path = cookie.get('path', '/')
                secure = "TRUE" if cookie.get('secure', False) else "FALSE"
                expiry = str(int(cookie.get('expiry', 0))) if cookie.get('expiry') else "0"
                name = cookie.get('name', '')
                value = cookie.get('value', '')
                line = "\t".join([domain, flag, path, secure, expiry, name, value]) + "\n"
                f.write(line)
        return cookies_path

    def search(self, query):
        """Search on the website using the provided query."""
        try:
            search_box = self.driver.find_element(By.XPATH, "//div[@class='ytSearchboxComponentInputBox ytSearchboxComponentInputBoxDark']")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            time.sleep(2)
        except Exception as e:
            print(f"Error during search: {e}")

    def match_href_in_excel(self, search_string):
        """Check if the given string exists in the Excel file."""
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
            print(f"Error checking Excel for match: {e}")
            return True

    def insert_href_into_excel(self, input_string):
        """Insert a string into the first empty cell of the active sheet in the Excel file."""
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
            print(f"Error inserting into Excel: {e}")
            return False

    def fetch_image_url(self, partial_url):
        """Fetch the complete image URL using multiple methods for Pinterest."""

        # Fix URL construction - check if partial_url is already a complete URL
        if partial_url.startswith('http'):
            base_url = partial_url
        else:
            base_url = "https://pinterest.com" + partial_url

        print("Base URL:", base_url)

        # Method 1: Try using Selenium to get the image from the current page
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.get(base_url)
                time.sleep(random.uniform(3.0, 5.0))

                # Multiple XPath patterns to find Pinterest images
                image_xpath_patterns = [
                    "//img[contains(@alt, 'This may contain:')]",
                    "//img[@alt='Story pin image']",
                    "//img[contains(@class, 'hCL')]",  # Pinterest's image class
                    "//img[contains(@src, 'pinimg.com')]",
                    "//div[contains(@class, 'mainContainer')]//img",
                    "//img[contains(@class, 'GrowthUnauthPinImage')]"
                ]

                for xpath in image_xpath_patterns:
                    try:
                        img_elements = self.driver.find_elements(By.XPATH, xpath)
                        for img_element in img_elements:
                            src = img_element.get_attribute('src')
                            if src and 'pinimg.com' in src:
                                # Get the highest quality version
                                if '236x' in src:
                                    src = src.replace('236x', '736x')
                                elif '474x' in src:
                                    src = src.replace('474x', '736x')
                                print(f"Found image via Selenium: {src}")
                                return src
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"Selenium method failed: {e}")

        # Method 2: Try requests with better headers and session
        try:
            session = requests.Session()

            # Mimic a real browser more closely
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }

            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1.0, 3.0))

            response = session.get(base_url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try multiple selectors for Pinterest images
            selectors = [
                'img[alt*="This may contain:"]',
                'img[alt="Story pin image"]',
                'img[src*="pinimg.com"]',
                'img.hCL',
                'img.GrowthUnauthPinImage'
            ]

            for selector in selectors:
                images = soup.select(selector)
                for img in images:
                    src = img.get('src')
                    if src and 'pinimg.com' in src:
                        # Get higher quality version
                        if '236x' in src:
                            src = src.replace('236x', '736x')
                        elif '474x' in src:
                            src = src.replace('474x', '736x')
                        print(f"Found image via requests: {src}")
                        return src

            # Try to find images in JSON-LD or script tags
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'image' in data:
                        image_url = data['image']
                        if isinstance(image_url, list):
                            image_url = image_url[0]
                        if isinstance(image_url, dict) and 'url' in image_url:
                            image_url = image_url['url']
                        if image_url and 'pinimg.com' in image_url:
                            return image_url
                except:
                    continue

        except requests.exceptions.RequestException as e:
            print(f"Network error fetching URL {base_url}: {e}")
        except Exception as e:
            print(f"Error parsing content from {base_url}: {e}")

        return None



    def get_links_generic(self, xpath_pattern, max_number_of_links=1):
        """Generic method to extract links based on an XPath pattern."""
        href_links = []
        max_iterations = 10
        iterations = 0
        
        while len(href_links) < max_number_of_links and iterations < max_iterations:
            if self.quit_event.is_set():
                print(f"Quit event set. Aborting link collection with pattern {xpath_pattern}.")
                self.close_browser()
                return href_links
                
            if not self.wait_for_resume():
                return href_links
                
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3.0, 6.0))
            
            try:
                link_elements = self.driver.find_elements(By.XPATH, xpath_pattern)
            except Exception as e:
                print(f"CAN'T FIND ELEMENT with pattern {xpath_pattern}: {e}")
                break
                
            for link_element in link_elements:
                try:
                    link_url = link_element.get_attribute("href")
                    if link_url:
                        print(f"Found link: {link_url}")
                        if link_url not in href_links and self.match_href_in_excel(search_string=link_url):
                            href_links.append(link_url)
                            self.insert_href_into_excel(link_url)
                            if len(href_links) >= max_number_of_links:
                                return href_links
                except Exception as e:
                    print(f"Error processing element: {e}")
                    continue
                    
            iterations += 1
            
        return href_links

    def get_youtube_shorts(self, max_number_of_links=1):
        """Get YouTube shorts links"""
        return self.get_links_generic("//a[contains(@href, '/shorts/')]", max_number_of_links)
    
    def get_link_pinterest(self, max_number_of_links=1):
        """Extract pin links from search results for pinterest with better error handling."""
        href_links = []
        max_iterations = 15  # Increased iterations for Pinterest
        iterations = 0
        
        # Wait for page to load initially
        time.sleep(random.uniform(3.0, 6.0))
        
        while len(href_links) < max_number_of_links and iterations < max_iterations:
            if self.quit_event.is_set():
                print(f"Quit event set. Aborting link collection for Pinterest.")
                self.close_browser()
                return href_links
                
            if not self.wait_for_resume():
                return href_links
                
            # Scroll with more patience for Pinterest
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(4.0, 7.0))  # Longer wait for Pinterest
            
            # Try multiple XPath patterns for Pinterest pins
            xpath_patterns = [
                "//a[contains(@href, '/pin/')]",
                "//div[contains(@class, 'pinWrapper')]//a[contains(@href, '/pin/')]",
                "//div[contains(@data-test-id, 'pin')]//a[contains(@href, '/pin/')]"
            ]
            
            found_new_links = False
            
            for xpath_pattern in xpath_patterns:
                try:
                    link_elements = self.driver.find_elements(By.XPATH, xpath_pattern)
                    print(f"Found {len(link_elements)} elements with pattern: {xpath_pattern}")
                    
                    for link_element in link_elements:
                        try:
                            link_url = link_element.get_attribute("href")
                            if link_url and '/pin/' in link_url:
                                # Clean the URL to remove unnecessary parameters
                                if '?' in link_url:
                                    link_url = link_url.split('?')[0]
                                
                                print(f"Found Pinterest pin: {link_url}")
                                if link_url not in href_links and self.match_href_in_excel(search_string=link_url):
                                    href_links.append(link_url)
                                    self.insert_href_into_excel(link_url)
                                    found_new_links = True
                                    if len(href_links) >= max_number_of_links:
                                        return href_links
                        except Exception as e:
                            print(f"Error processing Pinterest element: {e}")
                            continue
                            
                    if found_new_links:
                        break  # Found links with this pattern, no need to try others
                        
                except Exception as e:
                    print(f"Error finding elements with pattern {xpath_pattern}: {e}")
                    continue
                    
            iterations += 1
            
            # If no new links found in several iterations, try clicking "Show more" or similar
            if not found_new_links and iterations > 5:
                try:
                    show_more_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Show more')]")
                    if show_more_buttons:
                        show_more_buttons[0].click()
                        time.sleep(random.uniform(3.0, 5.0))
                except:
                    pass
                
        print(f"Pinterest link collection completed. Found {len(href_links)} links in {iterations} iterations.")
        return href_links
    
    
        
    def get_youtube_videos(self, max_number_of_links=1):
        """Get regular YouTube video links"""
        return self.get_links_generic("//a[contains(@href, '/watch?')]", max_number_of_links)
        
    def get_instagram_reels(self, max_number_of_links=1):
        """Get Instagram reels links"""
        return self.get_links_generic("//a[contains(@href, '/reel/')]", max_number_of_links)
        
    def get_instagram_posts(self, max_number_of_links=1):
        """Get Instagram post links"""
        return self.get_links_generic("//a[contains(@href, '/p/')]", max_number_of_links)
        
    def get_tiktok_videos(self, max_number_of_links=1):
        """Get TikTok video links"""
        return self.get_links_generic("//a[contains(@href, '/www.tiktok.com/')]", max_number_of_links)
        
    def get_twitter_videos(self, max_number_of_links=1):
        """Get Twitter video links"""
        return self.get_links_generic("//a[contains(@href, '/video/')]", max_number_of_links)

    def image_save(self, image_urls=None, save_dir='.', filename=None):
        """
        Save one or more images from the provided URL list to a specified directory.
        Enhanced with better error handling and retry logic.
        """
        if not image_urls:
            print("No image URLs provided.")
            return []

        saved_paths = []
        os.makedirs(save_dir, exist_ok=True)

        for idx, url in enumerate(image_urls):
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    # Fetch a valid image link
                    image_link = self.fetch_image_url(url)

                    if not image_link:
                        print(f"Could not find image in {url}")
                        break

                    print(f"Found image link: {image_link}")

                    # Determine extension
                    ext = os.path.splitext(image_link.split('?')[0])[1] or '.jpg'
                    if not ext.startswith('.'):
                        ext = '.' + ext

                    # Determine filename for this image
                    if filename:
                        root, base_ext = os.path.splitext(filename)
                        base_ext = base_ext or ext
                        if len(image_urls) > 1:
                            name = f"{root}_{idx}{base_ext}"
                        else:
                            name = filename
                    else:
                        name = f"pinterest_image_{idx}_{int(time.time())}{ext}"

                    full_path = os.path.join(save_dir, name)

                    # Download and save image with proper error handling
                    session = requests.Session()
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Sec-Fetch-Dest': 'image',
                        'Sec-Fetch-Mode': 'no-cors',
                        'Sec-Fetch-Site': 'cross-site',
                        'Referer': 'https://www.pinterest.com/'
                    }

                    # Add delay between retries
                    if retry_count > 0:
                        time.sleep(random.uniform(2.0, 5.0))

                    response = session.get(image_link, stream=True, timeout=30, headers=headers, allow_redirects=True)
                    response.raise_for_status()

                    # Check if response contains actual image data
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        print(f"Warning: Response doesn't appear to be an image (content-type: {content_type})")

                    if response.status_code == 200 and len(response.content) > 0:
                        with open(full_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                if chunk:
                                    f.write(chunk)

                        # Verify the saved file is a valid image
                        try:
                            with Image.open(full_path) as img:
                                img.verify()
                            print(f"Image {idx} saved successfully to: {full_path}")
                            saved_paths.append(full_path)
                            break  # Success, break out of retry loop
                        except Exception as img_error:
                            print(f"Saved file is not a valid image: {img_error}")
                            if os.path.exists(full_path):
                                os.remove(full_path)
                            retry_count += 1
                    else:
                        print(f"Failed to download image {idx}. Status code: {response.status_code}, Content length: {len(response.content)}")
                        retry_count += 1

                except requests.exceptions.RequestException as e:
                    print(f"Network error downloading image {idx} (attempt {retry_count + 1}): {e}")
                    retry_count += 1
                except Exception as e:
                    print(f"Error processing image {idx} from {url} (attempt {retry_count + 1}): {e}")
                    retry_count += 1

            if retry_count >= max_retries:
                print(f"Failed to download image {idx} after {max_retries} attempts")

        return saved_paths


    


    def save_videos(self, path_to_save, video_links=None):
        """Download videos using yt-dlp with the provided links"""
        if not video_links:
            print("No video links provided.")
            return False

        Chrome_base_path = self.base_user_data_dir
        cookies_path = self.save_cookies_to_netscape(Chrome_base_path=Chrome_base_path)

        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)

        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(path_to_save, '%(title).100s_PRE%(id)s_POST.%(ext)s'),
            'ffmpeg_location': './ffmpeg/bin',
            'noplaylist': True,
            # Removed the download_archive option
            'ignoreerrors': True,
            'cookiefile': cookies_path,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
        }

        if self.quit_event.is_set():
            print("Quit event set. Aborting save_videos.")
            self.close_browser()
            return False

        if not self.wait_for_resume():
            return False

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(video_links)
            return True
        except Exception as e:
            print(f"Error downloading videos: {e}")
            return False
    
    def check_for_login_screen(self, login_element, platform_name):
        """Check for login screen and take proper actions."""
        # This is a placeholder for login handling logic
        pass

    def pinterest_search_url(self, query: str, region: str = "in") -> str:
        """
        Construct a Pinterest search URL for the given query and region.
        """
        
        encoded = urllib.parse.quote_plus(query)
        return f"https://{region}.pinterest.com/search/pins/?q={encoded}&rs=typed"
    

    def get_platform_url(self, user_id, platform, content_type):
        """Generate the appropriate URL based on platform and content type"""
        platform = platform.lower()
        content_type = content_type.lower()

        if platform == "youtube":
            if content_type == "short" or content_type == "reel" or content_type =="story":
                return f"https://www.youtube.com/@{user_id}/shorts"
            else:  # video or any other
                return f"https://www.youtube.com/@{user_id}/videos"

        elif platform == "instagram":
            if content_type == "short" or content_type == "reel" or content_type =="story":
                return f"https://www.instagram.com/{user_id}/reels/"
            elif content_type == "image":
                return f"https://www.instagram.com/{user_id}/"
            else:  # video or any other
                return f"https://www.instagram.com/{user_id}/"

        elif platform == "tiktok":
            return f"https://www.tiktok.com/@{user_id}"

        elif platform == "twitter":
            return f"https://x.com/{user_id}/media"
        elif platform == "pinterest":
            
            if content_type == "image":
                return self.pinterest_search_url(query=user_id)
            else:
                return self.pinterest_search_url(query=user_id)

        else:
            raise ValueError(f"Unsupported platform: {platform}")

    def get_content_links(self, platform, content_type, max_number_of_links):
        """Get content links based on platform and content type"""
        platform = platform.lower()
        content_type = content_type.lower()
        
        # YouTube
        if platform == "youtube":
            if content_type == "short" or content_type == "reel" or content_type == "story":
                return self.get_youtube_shorts(max_number_of_links)
            else:  # video or any other
                return self.get_youtube_videos(max_number_of_links)
        
        # Instagram        
        elif platform == "instagram":
            if content_type == "short" or content_type == "reel" or content_type == "story":
                return self.get_instagram_reels(max_number_of_links)
            elif content_type == "image":
                return self.get_instagram_posts(max_number_of_links)
            else:  # video or any other
                return self.get_instagram_posts(max_number_of_links)
        
        # TikTok        
        elif platform == "tiktok":
            return self.get_tiktok_videos(max_number_of_links)
        
        # Twitter        
        elif platform == "twitter":
            return self.get_twitter_videos(max_number_of_links)
        elif platform == "pinterest":
            return self.get_link_pinterest(max_number_of_links)
        else:
            print(f"No valid downloader method found for {platform} - {content_type}")
            return []

    def download_content(self, user_id="", platform_name="", content_type="video", no_of_items=0, save_path=""):
        """
        Main method to download content from various platforms.
        """
        if self.quit_event.is_set():
            print("Quit event set. Aborting download_content.")
            self.close_browser()
            return False

        if not self.wait_for_resume():
            return False

        if not platform_name:
            print("Platform name is required.")
            return False

        try:
            # Validate platform
            platform = platform_name.lower()
            if platform not in self.SUPPORTED_PLATFORMS:
                print(f"Unsupported platform: {platform_name}")
                return False

            # Validate content type 
            if content_type.lower() not in self.CONTENT_TYPES:
                print(f"Unsupported content type: {content_type}")
                return False

            # Get the appropriate URL
            try:
                web_link = self.get_platform_url(user_id, platform, content_type)
                self.web_link = web_link
                print(f"Opening URL: {web_link}")  # Debug line to see URL
                self.start_browser()

                # Add a longer wait time for Pinterest specifically
                if platform == "pinterest":
                    print("Waiting for Pinterest to load...")
                    time.sleep(random.uniform(5.0, 8.0))
            except ValueError as e:
                print(e)
                return False

            # Get content links
            links = self.get_content_links(platform, content_type, no_of_items)

            if not links:
                print("No new links found to download.")
                return False

            # Process based on content type
            if content_type.lower() == "image":
                self.image_save(image_urls=links, save_dir=save_path)
                return True
            else:  # video or short
                return self.save_videos(path_to_save=save_path, video_links=links)

        except Exception as e:
            print(f"Error in download_content: {e}")
            return False

    def process_multiple_profiles(self, download_config_profile_list=[]):
        """
        Process and download content for multiple profiles
        
        Args:
            download_config_profile_list: List of profile configurations
                Each profile is a tuple: (user_id, platform_name, no_of_items, save_path, content_type)
                
        Returns:
            bool: True if all downloads completed, False otherwise
        """
        try:
            for profile in download_config_profile_list:
                if self.quit_event.is_set():
                    print("Quit event set. Aborting process_multiple_profiles.")
                    self.close_browser()
                    break

                if not self.wait_for_resume():
                    return False

                try:
                    # Extract profile info, with content_type defaulting to "video" if not provided
                    if len(profile) == 5:
                        user_id, platform_name, no_of_items, save_path, content_type = profile
                    elif len(profile) == 4:
                        user_id, platform_name, no_of_items, save_path = profile
                        content_type = "video"
                    else:
                        print(f"Invalid profile configuration: {profile}")
                        continue
                        
                    # Download content for this profile
                    self.download_content(
                        user_id=user_id,
                        platform_name=platform_name,
                        content_type=content_type,
                        no_of_items=no_of_items,
                        save_path=save_path
                    )
                    
                    # Random delay between profiles
                    time.sleep(random.uniform(2.0, 4.0))
                    
                except Exception as e:
                    print(f"Error processing profile {profile}: {e}")

            self.close_browser()
            return True
            
        except Exception as e:
            print(f"Error in process_multiple_profiles: {e}")
            self.close_browser()
            return False

    def close_browser(self):
        """Close the browser if it was started."""
        try:
            if self.driver:
                self.driver.quit()
                time.sleep(2)
                self.terminate_process_with_pid()
                print("Browser closed successfully.")
        except Exception as e:
            print(f"Error closing browser: {e}")

    def force_quit_all_chrome(self):
        """Kill all Chrome processes."""
        try:
            os.system("taskkill /f /im chrome.exe")
            print("All Chrome processes terminated.")
        except Exception as e:
            print(f"Error terminating Chrome processes: {e}")

    # --- Pause/Resume/Quit Callback Methods ---
    def wait_for_resume(self):
        """
        Wait until the pause_event is set (i.e. not paused) while checking if quit_event is set.
        Returns True if resumed, or False if a quit was requested.
        """
        while not self.pause_event.wait(timeout=0.1):
            if self.quit_event.is_set():
                print("Quit event set while waiting to resume. Aborting.")
                self.close_browser()
                return False
        return True

    def terminate_process_with_pid(self):

        target_path = f"--user-data-dir={self.base_user_data_dir}"
        # Find all Chrome processes that match the profile
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'chrome.exe' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']).lower()
                    if target_path.lower() in cmdline and self.profile_dir.lower() in cmdline:
                        print(f"Terminating Chrome PID: {proc.pid}")
                        proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            
        # Close the driver (safe shutdown)
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Driver quit error: {e}")


    def pause(self):
        """Callback to pause the download process."""
        self.pause_event.clear()
        print("Download process paused.")

    def resume(self):
        """Callback to resume the download process."""
        self.pause_event.set()
        print("Download process resumed.")

    def quit(self):
        """Callback to quit the download process."""
        self.quit_event.set()
        self.pause_event.set()  # Release waiting threads.
        print("Download process quitting now.")
        self.close_browser()


# Example usage
if __name__ == "__main__":
    def prepare_task():
        # Configuration structure:
        # [
        #     [(chrome_user_data_dir, profile_dir, excel_path)],
        #     [
        #         (user_id, platform_name, no_of_items, save_path, content_type),
        #         ...
        #     ]
        # ]
        download_config_profile_list = [
            [(r"E:\facebook_ld_player\LDPlayer0\chrome", r"p", r"E:\facebook_ld_player\LDPlayer0\chrome\reels_history.xlsx")],

            [   ('jaysmedia6410', 'pinterest', 5, r'E:\facebook_ld\ld_player0\Kajal Kumari\Kajal Kumari_download_img', 'image')
            ]
        ]

        """                         ("InspiringLion", "youtube", 1, r"E:\downloads\car_shorts", "video"),
                ("HumansNoContext", "twitter", 1, r"E:\downloads\human_videos", "video"),
                ("memes_ka_hutiapa", "instagram", 1, r"E:\downloads\meme_reels", "reel"),
                ("NatGeo", "instagram", 1, r"E:\downloads\natgeo_images", "reel") """
        # Extract configuration
        browser_config = download_config_profile_list[0][0]
        profile_config = download_config_profile_list[1]
        base_user_data_dir, profile_dir, excelpath = browser_config
        
        # Create control events
        quit_event = threading.Event()
        pause_event = threading.Event()
        pause_event.set()  # Start in non-paused state
        
        # Create downloader instance
        downloader = UnifiedSocialMediaDownloader(
            control_quit_callback=quit_event,
            control_pause_callback=pause_event,
            base_user_data_dir=base_user_data_dir,
            profile_dir=profile_dir,
            excelpath=excelpath
        )
        
        # Start a control thread to simulate pause/resume/quit callbacks


        
        # Start the download process
        result = downloader.process_multiple_profiles(download_config_profile_list=profile_config)
        
        if result:
            print("Download process completed successfully!")
        else:
            print("Download process encountered an error.")

    main_thread = threading.Thread(target=prepare_task, daemon=True)
    main_thread.start()
    main_thread.join()
    print("All tasks have been completed.")