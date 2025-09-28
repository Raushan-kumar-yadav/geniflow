import os
import tempfile
import time
import requests
import openpyxl
from bs4 import BeautifulSoup
import math
import pyautogui
import random
import yt_dlp
from PIL import Image
import threading
import asyncio
import sys
import urllib
import psutil
from datetime import datetime
import subprocess
import json
import nodriver as uc  


def activity_callback(queue, ldname, app, profile, current, others, log_type=None):
    """Callback to update process activity with optional logging"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if log_type:
        if queue is not None:
            queue.put(('UPDATE', ldname, app, profile, current, others, timestamp, log_type))
    else:
        if queue is not None:
            queue.put(('UPDATE', ldname, app, profile, current, others, timestamp))

def delete_callback(queue, ldname):
    """Callback to delete a process"""
    if queue is not None:
        queue.put(('DELETE', ldname))

def mark_finished_callback(queue, ldname, app, profile, current, others, log_type=None):
    """Callback to mark process as finished with optional logging"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if log_type:
        queue.put(('FINISHED', ldname, app, profile, current, others, timestamp, log_type))
    else:
        queue.put(('FINISHED', ldname, app, profile, current, others, timestamp))
    

def log_callback(queue, ldname, app, profile, current, others, log_type="s"):
    """Callback for standalone logging operations"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    queue.put(('LOG', ldname, app, profile, current, others, timestamp, log_type))




sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class UnifiedSocialMediaDownloader:
    """
    A unified class for downloading various content types (videos, shorts/reels, images)
    from different social media platforms. Refactored to use Nodriver [2].
    """
    
    CONTENT_TYPES = ["video", "short", "image", "reel", "story"]
    SUPPORTED_PLATFORMS = ["youtube", "instagram", "tiktok", "twitter", "pinterest"]
    
    def __init__(self, control_quit_callback, control_pause_callback, base_user_data_dir=None,proc_identifier=None,activity_queue=None,
                 profile_dir="Default", excelpath="", headless=False,
                 web_link="Youtube", keep_alive=False):
        """
        Initialize the downloader with browser settings and control callbacks.
        
        Args:
            control_quit_callback:  signal quitting
            control_pause_callback:  signal pausing
            base_user_data_dir: Chrome user data directory
            profile_dir: Chrome profile directory
            excelpath: Path to Excel file for tracking downloaded content
            headless: Whether to run browser in headless mode
            web_link: Default platform to open
        """
        
        if base_user_data_dir:
            self.base_user_data_dir = base_user_data_dir
        else:
            self.base_user_data_dir = tempfile.mkdtemp()
        
        self.proc_identifier = proc_identifier
        self.activity_queue = activity_queue
        self.profile_dir = profile_dir
        self.excelpath = excelpath
        self.headless = headless
        self.keep_alive = keep_alive
        self.web_link = web_link
        self.browser = None  
        self.parent_process = None
        self.child_processes = None

        if self.headless:
            self.headless = True 

        # For pause/resume/quit control
        self.pause_event = control_pause_callback
        self.quit_event = control_quit_callback

        # Start a thread to monitor the quit 
        quit_thread = threading.Thread(target=self.monitor_quit, daemon=True)
        quit_thread.start()

    async def __ainit__(self):
        # Because nodriver have async function so we have to run as loop and initialize with await and await means it will wait till something will load 
        activity_callback(self.activity_queue, self.proc_identifier, "Browser", "", "Setting Browser Config", "None","ds")
        await self.initialize_browser()

    def _kill_existing_processes(self):
        """Enhanced process cleanup to prevent multiple browser instances"""
        try:
            print("Cleaning up existing Chrome processes...")
            
            # Save all chrome process in list for tracking and quiting them if need 
            chrome_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] and ('chrome' in proc.info['name'].lower() or 
                                              'chromedriver' in proc.info['name'].lower()):
                        chrome_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Terminate all the chrome with pid 
            for proc in chrome_processes:
                try:
                    proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # wiat for terminate for 3 sec if not terminated or faid to close then it will close all the browser
            time.sleep(3)
            
            # Force kill 
            for proc in chrome_processes:
                try:
                    if proc.is_running():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            print("Chrome processes cleaned up successfully")
            
        except Exception as e:
            print(f"Error during process cleanup: {e}")

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
                # For Linux 
                result = subprocess.run(['google-chrome', '--version'], 
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    version = result.stdout.strip().split()[-1]
                    return int(version.split('.')[0])
            except:
                pass
        
        # Default fallback 
        return None

    async def initialize_browser(self):
        """Initialize Nodriver browser with smart detection [2]"""
        print("Initializing Nodriver browser...")
        
        # Clean up any existing processes first // dont uncomment this it will close all the chrome frist when run 
        #self._kill_existing_processes()
        #time.sleep(2)
        
        # config NoDriver 
        config = uc.Config(
            headless=self.headless,
            user_data_dir=self.base_user_data_dir,
            profile=self.profile_dir
        )
        
        # Start Nodriver browser 
        self.browser = await uc.start(config=config)
        print(" Nodriver browser initialized successfully!")
        self._capture_process_info()
    
    def _capture_process_info(self):
        """Capture process information for cleanup"""
        print("Process info capture adapted for Nodriver.")

    async def arrange_chrome_instance(self):
        """Calculate positions and arrange the window"""
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
        """Continuously monitor quit if event will set """
        if self.quit_event is not None:
            while not self.quit_event.is_set():
                time.sleep(0.1)
            
            uc.loop().run_until_complete(self.quit())
        
    async def start_browser(self):
        """Start the browser and open the initial page """
        if self.browser is None:
            print("Browser not initialized. Aborting start_browser.")
            return None
        try:
            tab = await self.browser.get(self.web_link)  
            print(f"Browser started successfully! Opening {self.web_link}")
            activity_callback(self.activity_queue, self.proc_identifier, "Browser", "", "Opening Browser ", "None","ds")
            return tab
        except Exception as e:
            print(f"Error starting browser: {e}")
            return None

    async def get_cookies(self):
        """
        Get cookies from Nodriver browser session 
        Returns cookies in a format  with yt-dlp.
        """
        if self.browser is None:
            print("Browser not initialized")
            return []

        try:
            
            if hasattr(self.browser, 'cookies') and self.browser.cookies:
                cookies = self.browser.cookies
                if isinstance(cookies, list):
                    print(f"Retrieved {len(cookies)} cookies via direct access")
                    return cookies

            print("All cookie retrieval methods failed")
            return []

        except Exception as e:
            print(f"Error getting cookies: {e}")
            return []


    async def save_cookies_to_netscape(self, Chrome_base_path):
        """
        Save browser cookies in proper Netscape format for yt-dlp.
        """
        cookies = await self.get_cookies()
        cookies_path = os.path.join(Chrome_base_path, "cookies.txt")

        try:
            with open(cookies_path, "w", encoding="utf-8") as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# This file was generated by UnifiedSocialMediaDownloader\n")
                
                if not cookies:
                    print("No cookies found")
                    f.write("# No cookies available\n")
                    return cookies_path

                valid_cookies = 0
                for cookie in cookies:
                    try:
                        domain = cookie.get("domain", "").strip()
                        if not domain or not cookie.get("name"):
                            continue

                        include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
                        path = cookie.get("path", "/").strip()
                        secure = "TRUE" if cookie.get("secure", False) else "FALSE"
                        expiry = cookie.get("expires", 0)
                        try:
                            expiry = int(float(expiry))
                        except (ValueError, TypeError):
                            expiry = 0
                        name = cookie.get("name", "").strip()
                        value = cookie.get("value", "").strip()

                        line = f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n"
                        f.write(line)
                        valid_cookies += 1
                    except Exception as cookie_error:
                        print(f"Error processing cookie: {cookie_error}")
                        continue

                print(f"Saved {valid_cookies} valid cookies to: {cookies_path}")
                if valid_cookies == 0:
                    f.write("# No valid cookies found\n")

            # Verify file creation
            if os.path.exists(cookies_path):
                with open(cookies_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        print(f"Cookie file created successfully: {cookies_path}")
                    else:
                        print("Cookie file is empty")
            return cookies_path

        except Exception as e:
            print(f"Error writing cookies to file: {e}")
            try:
                with open(cookies_path, "w", encoding="utf-8") as f:
                    f.write("# Netscape HTTP Cookie File\n")
                    f.write("# Error occurred during cookie generation\n")
            except:
                pass
            return cookies_path



    async def search(self, query):
        """Search on the website using the provided query ."""
        if self.browser is None or self.browser.main_tab is None:
            print("Browser or main tab not available for search.")
            return
        try:
            # Assuming current tab
            search_box = await self.browser.main_tab.select('.ytSearchboxComponentInputBox')  #  selector
            await search_box.send_keys(query + '\n')
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




    async def fetch_image_url(self, partial_url):
        """
        Properly async Pinterest image URL fetcher that works within existing event loop.
        """

        # Construct the full Pinterest URL
        if partial_url.startswith('http'):
            pinterest_url = partial_url
        else:
            pinterest_url = "https://www.pinterest.com" + partial_url

        print(f"Opening Pinterest URL in browser: {pinterest_url}")

        
        try:
            if self.browser is not None:
                
                tab = await self.browser.get(pinterest_url)

                # Wait for page  load
                await asyncio.sleep(random.uniform(4.0, 6.0))

                # List of selectors for Pinterest images
                image_selectors = [
                    'img[src*="pinimg.com"]',          
                    'img.hCL',                          
                    'img[alt*="This may contain:"]',    
                    'img.GrowthUnauthPinImage',         
                    'img[data-test-id="pin-image"]',    
                    '.mainContainer img[src*="pinimg.com"]' 
                ]

                
                for selector in image_selectors:
                    try:
                        img_elements = await tab.select_all(selector)
                        for img_element in img_elements:
                            src = img_element.attrs.get('src')
                            if src and 'pinimg.com' in src and not src.endswith('.gif'):
                                
                                if src.startswith('//'):
                                    src = 'https:' + src

                                
                                quality_upgrades = {
                                    '236x': '736x',
                                    '474x': '736x',
                                    '564x': '736x',
                                    '/236/': '/736/',
                                    '/474/': '/736/',
                                    '/564/': '/736/'
                                }

                                for old, new in quality_upgrades.items():
                                    if old in src:
                                        src = src.replace(old, new)
                                        break
                                    
                                print(f"Found image via browser: {src}")
                                return src
                    except Exception as e:
                        print(f"Selector {selector} failed: {e}")
                        continue
                    
                print("No images found via browser method")

        except Exception as e:
            print(f"Browser method failed: {e}")

        
        print("Falling back to requests method...")

        try:
            session = requests.Session()

            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Referer': 'https://www.pinterest.com/'
            }

            
            await asyncio.sleep(random.uniform(2.0, 4.0))

            
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = session.get(pinterest_url, headers=headers, timeout=25, allow_redirects=True)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise e
                    await asyncio.sleep(random.uniform(1.0, 3.0))

            # multiple encoding strategies
            content = None
            content_bytes = response.content

            #  multiple encoding approaches
            encoding_strategies = [
                ('utf-8', 'strict'),
                ('utf-8', 'ignore'),
                ('utf-8', 'replace'),
                ('latin-1', 'ignore'),
                ('iso-8859-1', 'ignore')
            ]

            for encoding, error_handling in encoding_strategies:
                try:
                    content = content_bytes.decode(encoding, errors=error_handling)
                    if content and len(content.strip()) > 100:  
                        break
                except (UnicodeDecodeError, LookupError):
                    continue
                
            if not content:
                # Last resort
                try:
                    content = response.text
                except Exception:
                    print("All encoding methods failed")
                    return None

            #  BeautifulSoup parsing 
            soup = None
            parsers = ['html.parser', 'lxml', 'html5lib']

            for parser in parsers:
                try:
                    soup = BeautifulSoup(content, parser)
                    
                    if soup and soup.find():
                        break
                except Exception as e:
                    print(f"Parser {parser} failed: {e}")
                    continue
                
            if not soup:
                print("All HTML parsers failed")
                return None

            #  Pinterest  multiple approaches
            image_search_strategies = [
               
                lambda s: s.find_all('img', src=True),
                
                lambda s: s.find_all('script', type='application/ld+json'),
            
                lambda s: s.find_all('script')
            ]

            #Direct image search
            try:
                img_tags = soup.find_all('img', src=True)
                for img in img_tags:
                    src = img.get('src')
                    if src and 'pinimg.com' in src and not src.endswith('.gif'):
                       
                        if src.startswith('//'):
                            src = 'https:' + src

                        
                        for old, new in [('236x', '736x'), ('474x', '736x'), ('564x', '736x')]:
                            if old in src:
                                src = src.replace(old, new)
                                break
                            
                        print(f" Found image via direct search: {src}")
                        return src
            except Exception as e:
                print(f"Direct image search failed: {e}")

            #JSON-LD search
            try:
                import json as json_module
                scripts = soup.find_all('script', type='application/ld+json')
                for script in scripts:
                    if script.string:
                        try:
                            data = json_module.loads(script.string)

                            def extract_image_from_json(obj):
                                if isinstance(obj, dict):
                                    if 'image' in obj:
                                        img_data = obj['image']
                                        if isinstance(img_data, str) and 'pinimg.com' in img_data:
                                            return img_data
                                        elif isinstance(img_data, dict) and 'url' in img_data:
                                            return img_data['url']
                                        elif isinstance(img_data, list) and img_data:
                                            return extract_image_from_json(img_data[0])

                                    # Search nested objects
                                    for value in obj.values():
                                        if isinstance(value, (dict, list)):
                                            result = extract_image_from_json(value)
                                            if result:
                                                return result

                                elif isinstance(obj, list):
                                    for item in obj:
                                        result = extract_image_from_json(item)
                                        if result:
                                            return result

                                return None

                            image_url = extract_image_from_json(data)
                            if image_url:
                                print(f"Found image via JSON-LD: {image_url}")
                                return image_url

                        except json_module.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"JSON-LD search failed: {e}")

            #  Regex search in all script content
            try:
                import re
                all_scripts = soup.find_all('script')
                pinimg_pattern = r'https://[^"\']*pinimg\.com[^"\']*\.(?:jpg|jpeg|png|webp)'

                for script in all_scripts:
                    if script.string:
                        matches = re.findall(pinimg_pattern, script.string, re.IGNORECASE)
                        for match in matches:
                            if not match.endswith('.gif'):
                                # Quality 
                                for old, new in [('236x', '736x'), ('474x', '736x')]:
                                    if old in match:
                                        match = match.replace(old, new)
                                        break
                                print(f"✓ Found image via regex: {match}")
                                return match
            except Exception as e:
                print(f"Regex search failed: {e}")

        except Exception as e:
            print(f"Requests method failed: {e}")

        print(f"❌ Could not find image URL for: {pinterest_url}")
        return None




    

    async def get_links_generic(self, selector, max_number_of_links=1, base_url=""):
        """Enhanced generic method with smart scrolling for better content discovery."""
        if self.browser is None or self.browser.main_tab is None:
            print("Browser or main tab not available for getting links.")
            return []

        href_links = []
        seen_links = set()
        max_iterations = 99999 
        iterations = 0
        tab = self.browser.main_tab
        no_new_links_count = 0
        last_page_height = 0

        # Wait for initial page load
        await asyncio.sleep(random.uniform(3.0, 5.0))

        while len(href_links) < max_number_of_links and iterations < max_iterations:
            if self.quit_event.is_set():
                print(f"Quit event set. Aborting link collection with selector {selector}.")
                await self.close_browser()
                return href_links

            if not await self.wait_for_resume():
                return href_links

            
            current_height = await self.smart_scroll(tab, strategy=iterations % 3)

            
            if current_height == last_page_height and iterations > 2:
                print("Page not scrolling, trying alternative methods...")
                await self.force_scroll_methods(tab)
            last_page_height = current_height

            # Wait scroll
            await asyncio.sleep(random.uniform(3.0, 6.0))

            try:
                link_elements = await tab.select_all(selector)
            except Exception as e:
                print(f"CAN'T FIND ELEMENT with selector {selector}: {e}")
                # content loading
                await self.trigger_content_load(tab)
                continue

            new_links_found = False
            for link_element in link_elements:
                try:
                    link_url = link_element.attrs.get("href")
                    if link_url:
                        # Convert to full URL if relative
                        if link_url.startswith('/'):
                            link_url = base_url + link_url

                        if link_url not in seen_links:
                            seen_links.add(link_url)
                            print(f"Found link: {link_url}")
                            if link_url not in href_links and self.match_href_in_excel(search_string=link_url):
                                href_links.append(link_url)
                                self.insert_href_into_excel(link_url)
                                new_links_found = True
                                if len(href_links) >= max_number_of_links:
                                    return href_links
                except Exception as e:
                    print(f"Error processing element: {e}")
                    continue

            if not new_links_found:
                no_new_links_count += 1
                if no_new_links_count >= 4:  
                    print("No new links found in 4 consecutive iterations. Trying end-of-page detection...")
                    if await self.check_end_of_content(tab):
                        print("Reached end of content.")
                        break
            else:
                no_new_links_count = 0

            iterations += 1

        print(f"Link collection completed: {len(href_links)} links found in {iterations} iterations")
        return href_links



    async def smart_scroll(self, tab, strategy=0):
        """
        Advanced scrolling with multiple strategies for different website types.
        Returns current page height to detect if scrolling worked.
        """
        try:
            # Get current page height
            current_height = await tab.evaluate("document.body.scrollHeight")

            if strategy == 0:
                #  Standard smooth scroll
                await tab.evaluate("""
                    window.scrollBy({
                        top: window.innerHeight * 0.8,
                        behavior: 'smooth'
                    });
                """)

            elif strategy == 1:
                #  Aggressive scroll to bottom
                await tab.evaluate("window.scrollTo(0, document.body.scrollHeight);")

            elif strategy == 2:
                # Multiple small scrolls
                for i in range(3):
                    await tab.evaluate("window.scrollBy(0, 300);")
                    await asyncio.sleep(0.5)

            # Wait
            await asyncio.sleep(random.uniform(1.0, 2.0))

            # Return new height
            new_height = await tab.evaluate("document.body.scrollHeight")
            return new_height

        except Exception as e:
            print(f"Smart scroll failed: {e}")
            # Fallback to basic scroll
            try:
                await tab.scroll_down()
                return await tab.evaluate("document.body.scrollHeight")
            except:
                return current_height

    async def force_scroll_methods(self, tab):
        """Aggressive scrolling methods when standard scrolling fails."""
        try:
            #  infinite scroll loaders
            await tab.evaluate("""
                // Look for common infinite scroll triggers
                const triggers = document.querySelectorAll('[class*="load"], [class*="more"], [id*="load"], [id*="more"]');
                triggers.forEach(trigger => {
                    if (trigger.scrollIntoView) {
                        trigger.scrollIntoView();
                    }
                });
            """)
            await asyncio.sleep(2)

            #  user scrolling behavior
            await tab.evaluate("""
                // Simulate multiple scroll events
                for(let i = 0; i < 5; i++) {
                    window.dispatchEvent(new Event('scroll'));
                    window.scrollBy(0, 200);
                }
            """)
            await asyncio.sleep(2)

            # page end scroll
            await tab.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(3)

        except Exception as e:
            print(f"Force scroll methods failed: {e}")

    async def trigger_content_load(self, tab):
        """Trigger lazy loading and dynamic content."""
        try:
            #  lazy loading 
            await tab.evaluate("""
                // Find and trigger lazy loading elements
                const lazyElements = document.querySelectorAll('[data-src], [loading="lazy"], .lazy');
                lazyElements.forEach(element => {
                    if (element.scrollIntoView) {
                        element.scrollIntoView();
                    }
                    // Trigger common lazy loading events
                    element.dispatchEvent(new Event('load'));
                    element.dispatchEvent(new Event('scroll'));
                });
            """)

            # Click "Load more" buttons if visible
            load_more_selectors = [
                "button:contains('Load more')",
                "button:contains('Show more')",
                "[data-test-id*='load']",
                "[data-test-id*='more']",
                ".load-more",
                ".show-more"
            ]

            for selector in load_more_selectors:
                try:
                    button = await tab.find(selector, best_match=True)
                    if button:
                        await button.click()
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                        break
                except:
                    continue

        except Exception as e:
            print(f"Content load trigger failed: {e}")

    async def check_end_of_content(self, tab):
        """Check if we've reached the end of scrollable content."""
        try:
            #Check scroll position
            result = await tab.evaluate("""
                (window.innerHeight + window.scrollY) >= document.body.offsetHeight - 100
            """)

            if result:
                return True

            #   "no more content" 
            end_indicators = await tab.evaluate("""
                const indicators = [
                    'No more', 'End of', 'That\\'s all', 'Nothing more',
                    'All caught up', 'You\\'ve reached the end'
                ];

                return indicators.some(indicator => 
                    document.body.textContent.toLowerCase().includes(indicator.toLowerCase())
                );
            """)

            return end_indicators

        except Exception as e:
            print(f"End of content check failed: {e}")
            return False



    async def get_youtube_shorts(self, max_number_of_links=1):
        """Get YouTube shorts links"""
        return await self.get_links_generic("a[href*='/shorts/']", max_number_of_links, base_url="https://www.youtube.com")
    


    async def get_link_pinterest(self, max_number_of_links=1):
        """Extract pin links from search results for pinterest with better error handling using Nodriver."""
        if self.browser is None or self.browser.main_tab is None:
            print("Browser or main tab not available for Pinterest link collection.")
            return []

        href_links = []
        max_iterations = 15  
        iterations = 0
        last_page_height = 0
        tab = self.browser.main_tab  

        # Wait for page to load initially
        await asyncio.sleep(random.uniform(3.0, 6.0))

        while len(href_links) < max_number_of_links and iterations < max_iterations:
            if self.quit_event.is_set():
                print(f"Quit event set. Aborting link collection for Pinterest.")
                await self.close_browser()
                return href_links

            if not await self.wait_for_resume():
                return href_links
            

            current_height = await self.smart_scroll(tab, strategy=iterations % 3)

            # Check if page  scrolled
            if current_height == last_page_height and iterations > 2:
                print("Page not scrolling, trying alternative methods...")
                await self.force_scroll_methods(tab)
            last_page_height = current_height

            # Wait for content
            await asyncio.sleep(random.uniform(3.0, 6.0))



            #  XPath patterns to CSS selectors
            css_selectors = [
                "a[href*='/pin/']",
                ".pinWrapper a[href*='/pin/']", 
                "[data-test-id*='pin'] a[href*='/pin/']"
            ]

            found_new_links = False

            for css_selector in css_selectors:
                try:
                    link_elements = await tab.select_all(css_selector)
                    print(f"Found {len(link_elements)} elements with selector: {css_selector}")

                    for link_element in link_elements:
                        try:
                            link_url = link_element.attrs.get("href")
                            if link_url and '/pin/' in link_url:
                                # Clean the URL
                                if '?' in link_url:
                                    link_url = link_url.split('?')[0]

                                # Convert to full URL if relative
                                if link_url.startswith('/'):
                                    link_url = "https://www.pinterest.com" + link_url

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
                        break  # Found links with this selector

                except Exception as e:
                    print(f"Error finding elements with selector {css_selector}: {e}")
                    continue

            iterations += 1

            #  try clicking "Show more"
            if not found_new_links and iterations > 5:
                try:
                    #  "Show more" button
                    show_more_selectors = [
                        "button:contains('Show more')",
                        "[data-test-id*='show-more']",
                        "button[aria-label*='more']"
                    ]

                    for selector in show_more_selectors:
                        try:
                            show_more_button = await tab.find(selector, best_match=True)
                            if show_more_button:
                                await show_more_button.click()
                                await asyncio.sleep(random.uniform(3.0, 5.0))
                                break
                        except Exception as e:
                            continue

                except Exception as e:
                    print(f"Error clicking show more button: {e}")
                    pass
                
        print(f"Pinterest link collection completed. Found {len(href_links)} links in {iterations} iterations.")
        return href_links

    

    
    
    async def get_youtube_videos(self, max_number_of_links=1):
        """Get regular YouTube video links"""
        return await self.get_links_generic("a[href*='/watch?']", max_number_of_links, base_url="https://www.youtube.com")
        
    async def get_instagram_reels(self, max_number_of_links=1):
        """Get Instagram reels links"""
        return await self.get_links_generic("a[href*='/reel/']", max_number_of_links, base_url="https://www.instagram.com")
        
    async def get_instagram_posts(self, max_number_of_links=1):
        """Get Instagram post links"""
        return await self.get_links_generic("a[href*='/p/']", max_number_of_links, base_url="https://www.instagram.com")
        
    async def get_tiktok_videos(self, max_number_of_links=1):
        """Get TikTok video links"""
        return await self.get_links_generic("a[href*='/www.tiktok.com/']", max_number_of_links, base_url="https://www.tiktok.com")
        
    async def get_twitter_videos(self, max_number_of_links=1):
        """Get Twitter video links"""
        return await self.get_links_generic("a[href*='/video/']", max_number_of_links, base_url="https://x.com")

    async def image_save(self, image_urls=None, save_dir='.', filename=None,identifier=None):
        """
        Save one or more images from the provided URL list to a specified directory.
        Enhanced with better error handling and retry logic.
        """
        if not image_urls:
            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "No Image Link Found", f"None","ds")
            print("No image URLs provided.")
            return []
    
        saved_paths = []
        os.makedirs(save_dir, exist_ok=True)

        for idx, url in enumerate(image_urls):
            max_retries = 3
            retry_count = 0
            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "Getting Png URL", f"Count:{idx}","ds")
            while retry_count < max_retries:
                try:
                    
                    image_link = await self.fetch_image_url(url)
    
                    if not image_link:
                        print(f"Could not find image in {url}")
                        break
                    
                    print(f"Found image link: {image_link}")
    
                    #  extension
                    ext = os.path.splitext(image_link.split('?')[0])[1] or '.jpg'
                    if not ext.startswith('.'):
                        ext = '.' + ext
    
                    #  filename 
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
    
                    # Download and save image
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
    
                    #  delay between retries
                    if retry_count > 0:
                        await asyncio.sleep(random.uniform(2.0, 5.0))  
    
                    response = session.get(image_link, stream=True, timeout=30, headers=headers, allow_redirects=True)
                    response.raise_for_status()
    
                    # Check  for actual image data
                    content_type = response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        print(f"Warning: Response doesn't appear to be an image (content-type: {content_type})")
    
                    if response.status_code == 200 and len(response.content) > 0:
                        with open(full_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                if chunk:
                                    f.write(chunk)
    
                        
                        try:
                            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "Saving Png ", f"Count:{idx}","ds")
                            with Image.open(full_path) as img:
                                img.verify()
                            print(f"Image {idx} saved successfully to: {full_path}")
                            saved_paths.append(full_path)
                            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "Saved Png successfully", f"Count:{idx}","ds")
                            break  
                        except Exception as img_error:
                            print(f"Saved file is not a valid image: {img_error}")
                            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "Saving Faild ", f"Error:{img_error}","s")
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
                activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "Faild to Download Png ", f"Count:{idx}","ds")
    
        return saved_paths
    
    

    async def save_videos(self, path_to_save, video_links=None,identifier=None):
        """Download videos using yt-dlp with the provided links (unchanged)"""
        if not video_links:
            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "No Video Link Found", f"None","ds")
            print("No video links provided.")
            return False

        Chrome_base_path = self.base_user_data_dir
        cookies_path = await self.save_cookies_to_netscape(Chrome_base_path=Chrome_base_path)

        if not os.path.exists(path_to_save):
            os.makedirs(path_to_save)

        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(path_to_save, '%(title).100s_PRE%(id)s_POST.%(ext)s'),
            'ffmpeg_location': './ffmpeg/bin',
            'noplaylist': True,
            'ignoreerrors': True,
            'cookiefile': cookies_path,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
        }
        
        if self.quit_event.is_set():
            print("Quit event set. Aborting save_videos.")
            await self.close_browser()
            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "Closing Browser", f"None","ds")
            return False

        if not await self.wait_for_resume():
            return False

        try:
            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "Downloading All Videos....", f"None","ds")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(video_links)
                activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{identifier}", "All Videos Downloaded", f"None","ds")
            return True
        except Exception as e:
            print(f"Error downloading videos: {e}")
            activity_callback(self.activity_queue, self.proc_identifier, "", f"{identifier}", "Videos Downloader", f"Error:{e}","ds")
            return False
    
    def check_for_login_screen(self, login_element, platform_name):
        """Check for login screen and take proper actions (placeholder, adapt if needed)."""
        pass

    def pinterest_search_url(self, query: str, region: str = "in") -> str:
        """Construct a Pinterest search URL (unchanged)."""
        encoded = urllib.parse.quote_plus(query)
        return f"https://{region}.pinterest.com/search/pins/?q={encoded}&rs=typed"
    

    def get_platform_url(self, user_id, platform, content_type):
        """Generate the appropriate URL based on platform and content type (unchanged)."""
        platform = platform.lower()
        content_type = content_type.lower()

        if platform == "youtube":
            if content_type in ["short", "reel", "story"]:
                return f"https://www.youtube.com/@{user_id}/shorts"
            else:
                return f"https://www.youtube.com/@{user_id}/videos"

        elif platform == "instagram":
            if content_type in ["short", "reel", "story"]:
                return f"https://www.instagram.com/{user_id}/reels/"
            elif content_type == "image":
                return f"https://www.instagram.com/{user_id}/"
            else:
                return f"https://www.instagram.com/{user_id}/"

        elif platform == "tiktok":
            return f"https://www.tiktok.com/@{user_id}"

        elif platform == "twitter":
            return f"https://x.com/{user_id}/media"
        elif platform == "pinterest":
            return self.pinterest_search_url(query=user_id)

        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def get_content_links(self, platform, content_type, max_number_of_links):
        """Get content links based on platform and content type with Nodriver [2]."""
        platform = platform.lower()
        content_type = content_type.lower()
        
        if platform == "youtube":
            if content_type in ["short", "reel", "story"]:
                return await self.get_youtube_shorts(max_number_of_links)
            else:
                return await self.get_youtube_videos(max_number_of_links)
        
        elif platform == "instagram":
            if content_type in ["short", "reel", "story"]:
                return await self.get_instagram_reels(max_number_of_links)
            elif content_type == "image":
                return await self.get_instagram_posts(max_number_of_links)
            else:
                return await self.get_instagram_posts(max_number_of_links)
        
        elif platform == "tiktok":
            return await self.get_tiktok_videos(max_number_of_links)
        
        elif platform == "twitter":
            return await self.get_twitter_videos(max_number_of_links)
        elif platform == "pinterest":
            return await self.get_link_pinterest(max_number_of_links)
        else:
            print(f"No valid downloader method found for {platform} - {content_type}")
            return []

    async def download_content(self, user_id="", platform_name="", content_type="video", no_of_items=0, save_path="",identifier=None):
        """
        Main method to download content from various platforms with Nodriver [2].
        """
        if self.quit_event.is_set():
            print("Quit event set. Aborting download_content.")
            await self.close_browser()
            return False
        
        if not await self.wait_for_resume():
            return False

        if not platform_name:
            print("Platform name is required.")
            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Missing PlatFrom Name", "Error","ds")
            return False

        try:
            platform = platform_name.lower()
            if platform not in self.SUPPORTED_PLATFORMS:
                activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Unsupported platform", f"Error:{platform_name}","ds")
                print(f"Unsupported platform: {platform_name}")
                return False

            if content_type.lower() not in self.CONTENT_TYPES:
                print(f"Unsupported content type: {content_type}")
                activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Unsupported content type", f"Error:{content_type}","ds")
                return False

            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Getting URL", "None","ds")
            web_link = self.get_platform_url(user_id, platform, content_type)
            self.web_link = web_link
            print(f"Opening URL: {web_link}")
            await self.start_browser()
            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Opening URL", "None","ds")
            if platform == "pinterest":
                print("Waiting for Pinterest to load...")
                activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Waiting To Load URL", "None","ds")
                time.sleep(random.uniform(5.0, 8.0))

            activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Getting New Content Link", "None","ds")
            links = await self.get_content_links(platform, content_type, no_of_items)

            if not links:
                print("No new links found to download.")
                activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "No New Link Found", f"Error","s")
                return False

            if content_type.lower() == "image":
                activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Process to Saving Image", f"None","s")
                await self.image_save(image_urls=links, save_dir=save_path,identifier=identifier)
                return True
            else:
                activity_callback(self.activity_queue, self.proc_identifier, "Browser", f"{str(identifier)}", "Process to Saving Video", f"None","s")
                return await self.save_videos(path_to_save=save_path, video_links=links,identifier=identifier)

        except Exception as e:
            print(f"Error in download_content: {e}")
            return False

    async def process_multiple_profiles(self, download_config_profile_list=[]):
        """
        Process and download content for multiple profiles (adapted for async Nodriver [2]).
        """
        try:
            for profile in download_config_profile_list:
                if self.quit_event.is_set():
                    print("Quit event set. Aborting process_multiple_profiles.")
                    await self.close_browser()
                    break

                if not await self.wait_for_resume():
                    return False

                if len(profile) == 5:
                    user_id, platform_name, no_of_items, save_path, content_type = profile
                elif len(profile) == 6:
                    user_id, platform_name, no_of_items, save_path, content_type,identifier = profile
                elif len(profile) == 4:
                    user_id, platform_name, no_of_items, save_path = profile
                    content_type = "video"
                else:
                    print(f"Invalid profile configuration: {profile}")
                    continue
                    
                await self.download_content(
                    user_id=user_id,
                    platform_name=platform_name,
                    content_type=content_type,
                    no_of_items=no_of_items,
                    save_path=save_path,
                    identifier = identifier
                )
                
                time.sleep(random.uniform(2.0, 4.0))

            await self.close_browser()
            return True
            
        except Exception as e:
            print(f"Error in process_multiple_profiles: {e}")
            await self.close_browser()
            return False

    async def close_browser(self):
        """Close the browser if it was started with Nodriver [2].""" 
        try:
            if self.keep_alive:
                print("Keep-alive is enabled; not closing browser.")
                return
            
            if self.browser:
                activity_callback(self.activity_queue, self.proc_identifier, "Geni", f"", "Cloasing Browser", "None","ds")
                print("Closing browser...")

               
                try:
                    self.browser.stop() 
                    print("Browser closed gracefully")
                except Exception as browser_error:
                    print(f"Error closing browser gracefully: {browser_error}")

                # Wait
                await asyncio.sleep(2)

                # Force terminate processes
                self.terminate_process_with_pid()

                # Clear browser reference
                self.browser = None

                print("Browser closed successfully.")

        except Exception as e:
            print(f"Error closing browser: {e}")
            
            self.force_quit_all_chrome()


    def force_quit_all_chrome(self):
        """Kill all Chrome processes (unchanged)."""
        try:
            os.system("taskkill /f /im chrome.exe")
            print("All Chrome processes terminated.")
        except Exception as e:
            print(f"Error terminating Chrome processes: {e}")

    async def wait_for_resume(self):
        """Wait until resume while checking quit."""
        while not self.pause_event.wait(timeout=0.1):
            if self.quit_event.is_set():
                print("Quit event set while waiting to resume. Aborting.")
                await self.close_browser()
                return False
        return True

    def terminate_process_with_pid(self):
        """Terminate Chrome processes associated with this profile"""
        try:
            target_path = f"--user-data-dir={self.base_user_data_dir}"
            processes_to_kill = []

           
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(name in proc_name for name in ['chrome', 'chromium']):
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline']).lower()
                            if target_path.lower() in cmdline:
                                processes_to_kill.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                
            
            for proc in processes_to_kill:
                try:
                    print(f"Terminating Chrome PID: {proc.pid}")
                    proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                
            # Wait 
            time.sleep(3)

            # Force kill if still running
            for proc in processes_to_kill:
                try:
                    if proc.is_running():
                        print(f"Force killing Chrome PID: {proc.pid}")
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        except Exception as e:
            print(f"Error terminating processes: {e}")

            


    def pause(self):
        """Callback to pause the download process."""
        self.pause_event.clear()
        print("Download process paused.")

    def resume(self):
        """Callback to resume the download process."""
        self.pause_event.set()
        print("Download process resumed.")

    async def quit(self):
        """Callback to quit the download process."""
        self.quit_event.set()
        self.pause_event.set()
        print("Download process quitting now.")
        await self.close_browser()


# Example usage 
if __name__ == "__main__":
    async def prepare_task():
        
        """"""
        download_config_profile_list = [
            [(r"E:\facebook_ld\raushan\chrome", r"p",r"E:\facebook_ld\raushan\chrome\reels_history.xlsx")], # so this is list of structure on index 0 here is basic chrome setup data like chrome base path means where is chrome profile and inside that chrome folder we can create multiple profile so "p" menas its profile name and when we click on create chrome in geniflow bellow the restart ld button then its create that folde and also create a profile name called p or p1 that why we used p for profile name here and excel file is to save downloaded video image and more content so it not repeat 

            [('cars', 'pinterest', 5, r'E:\facebook_ld\raushan\Rekha Kumari\Rekha Kumari_download_img', 'image'), #inside these list there is a tupple in that frist is chennal name or id name and at index 1 is platform name and at index2 is number of content and at index3 is path where its have to save and last is content type its help code to deside which saving method shoul i run for saving like shoul i run save video or save image method if its find image on that place then it will run as per given data 
             ('MrBeast', 'Youtube', 4, r'E:\facebook_ld\raushan\Rekha Kumari\videos', 'video')] # here are repect we can as many tupple as we want it will loop throught every tupple and download one by one 
        ]

        browser_config = download_config_profile_list[0][0] # Get the element from idex
        profile_config = download_config_profile_list[1]
        base_user_data_dir, profile_dir, excelpath = browser_config # Unpacked it
        
        quit_event = threading.Event()  # just a dummmy event for args 
        pause_event = threading.Event()
        pause_event.set() # paused is set() so by default it will not paused 
        
        downloader = UnifiedSocialMediaDownloader(
            control_quit_callback=quit_event, # Passed the requred args
            control_pause_callback=pause_event,
            base_user_data_dir=base_user_data_dir,
            profile_dir=profile_dir,
            excelpath=excelpath
        )
        await downloader.__ainit__()  # created object of that class in ram 
        
        
        result = await downloader.process_multiple_profiles(download_config_profile_list=profile_config) # RUn the Process_multiple_profile method inside the downloader class with requred args 
        
        if result:
            print("Download process completed successfully!")
        else:
            print("Download process encountered an error.")

    uc.loop().run_until_complete(prepare_task())  # Nodriver loop
