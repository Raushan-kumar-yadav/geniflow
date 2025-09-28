import undetected_chromedriver as uc
import multiprocessing as mp
from multiprocessing import Process, Queue, Manager
import time
import random
import os
import tempfile
import shutil
import threading
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import sys
import re
import uuid

class ChromeDriverManager:
    """Manages Chrome driver instances with proper isolation and version handling"""
    
    def __init__(self, process_id):
        self.process_id = process_id
        self.driver = None
        self.temp_dir = None
        self.is_ready = False
        self.unique_id = str(uuid.uuid4())[:8]  # Unique identifier
    
    def get_chrome_version(self):
        """Get installed Chrome version with improved parsing"""
        try:
            # Try different methods to get Chrome version
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME'))
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    try:
                        result = subprocess.run([chrome_path, '--version'], 
                                              capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            version_output = result.stdout.strip()
                            print(f"Chrome version output: {version_output}")
                            
                            # Extract version number more carefully
                            # Look for pattern like "Google Chrome 134.0.6998.89"
                            match = re.search(r'(\d+)\.(\d+)\.(\d+)\.(\d+)', version_output)
                            if match:
                                major_version = int(match.group(1))
                                print(f"Extracted major version: {major_version}")
                                return major_version
                            
                            # Fallback: try to find any number sequence
                            numbers = re.findall(r'\d+', version_output)
                            if numbers:
                                major_version = int(numbers[0])
                                print(f"Fallback major version: {major_version}")
                                return major_version
                                
                    except subprocess.TimeoutExpired:
                        print(f"Timeout getting version from {chrome_path}")
                        continue
                    except Exception as e:
                        print(f"Error getting version from {chrome_path}: {e}")
                        continue
        except Exception as e:
            print(f"Could not detect Chrome version: {e}")
        
        return None
    
    def create_driver(self):
        """Create Chrome driver with version-specific handling"""
        try:
            # Create unique temporary directory with UUID
            self.temp_dir = tempfile.mkdtemp(prefix=f"chrome_{self.process_id}_{self.unique_id}_")
            
            # Get Chrome version
            chrome_version = self.get_chrome_version()
            print(f"Worker {self.process_id}: Detected Chrome version: {chrome_version}")
            
            # Create fresh ChromeOptions for each driver
            options = uc.ChromeOptions()
            
            # Essential options
            options.add_argument(f"--user-data-dir={self.temp_dir}")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--headless=new")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Use unique debugging port
            debug_port = 9222 + self.process_id * 1000 + random.randint(100, 999)
            options.add_argument(f"--remote-debugging-port={debug_port}")
            
            # Memory and performance optimizations
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")
            options.add_argument("--disable-features=TranslateUI")
            options.add_argument("--disable-ipc-flooding-protection")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            
            # Add unique user agent to avoid conflicts
            options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Worker{self.process_id}")
            
            print(f"Worker {self.process_id}: Creating driver with debug port {debug_port}")
            
            # Try multiple approaches to create driver
            driver_created = False
            attempts = [
                # Attempt 1: With detected version
                lambda: uc.Chrome(
                    options=options,
                    version_main=chrome_version if chrome_version else None,
                    use_subprocess=False,
                    headless=True,
                    driver_executable_path=None  # Let it auto-download
                ),
                # Attempt 2: Without version specification
                lambda: uc.Chrome(
                    options=options,
                    use_subprocess=False,
                    headless=True
                ),
                # Attempt 3: With specific version override for common mismatch
                lambda: uc.Chrome(
                    options=options,
                    version_main=134,  # Your detected Chrome version
                    use_subprocess=False,
                    headless=True
                )
            ]
            
            for i, attempt_func in enumerate(attempts, 1):
                try:
                    print(f"Worker {self.process_id}: Driver creation attempt {i}")
                    self.driver = attempt_func()
                    driver_created = True
                    break
                except Exception as e:
                    print(f"Worker {self.process_id}: Attempt {i} failed: {e}")
                    if i < len(attempts):
                        time.sleep(2)  # Wait before next attempt
                        # Create fresh options for next attempt
                        options = uc.ChromeOptions()
                        options.add_argument(f"--user-data-dir={self.temp_dir}")
                        options.add_argument("--no-sandbox")
                        options.add_argument("--disable-dev-shm-usage")
                        options.add_argument("--disable-gpu")
                        options.add_argument("--headless=new")
                        debug_port = 9222 + self.process_id * 1000 + random.randint(100, 999)
                        options.add_argument(f"--remote-debugging-port={debug_port}")
            
            if not driver_created:
                raise Exception("All driver creation attempts failed")
            
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            self.is_ready = True
            print(f"Worker {self.process_id}: Driver created successfully!")
            return True
            
        except Exception as e:
            print(f"Error creating driver for process {self.process_id}: {e}")
            self.cleanup()
            return False
    
    def get_page(self, url):
        """Navigate to URL and return page info"""
        if not self.is_ready or not self.driver:
            return {'error': 'Driver not ready', 'status': 'error'}
        
        try:
            print(f"Worker {self.process_id}: Navigating to {url}")
            self.driver.get(url)
            time.sleep(random.uniform(2, 4))  # Longer wait for stability
            
            # Get page info safely
            try:
                title = self.driver.title or "No title"
            except:
                title = "No title"
            
            try:
                current_url = self.driver.current_url or url
            except:
                current_url = url
            
            # Try to get page source length as a health check
            try:
                page_length = len(self.driver.page_source)
            except:
                page_length = 0
            
            return {
                'url': url,
                'title': title,
                'current_url': current_url,
                'page_length': page_length,
                'status': 'success'
            }
        except Exception as e:
            print(f"Worker {self.process_id}: Error getting page {url}: {e}")
            return {'url': url, 'error': str(e), 'status': 'error'}
    
    def cleanup(self):
        """Clean up driver and temporary files"""
        try:
            if self.driver:
                print(f"Worker {self.process_id}: Closing driver...")
                self.driver.quit()
                time.sleep(2)  # Give more time for cleanup
        except Exception as e:
            print(f"Warning: Error during driver cleanup: {e}")
        
        try:
            if self.temp_dir and os.path.exists(self.temp_dir):
                print(f"Worker {self.process_id}: Cleaning temp directory...")
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Error cleaning temp directory: {e}")
        
        self.is_ready = False

def worker_process(process_id, task_queue, result_queue, stop_event, tasks_completed):
    """Worker process that handles Chrome driver and processes tasks"""
    
    print(f"Worker {process_id} starting...")
    
    # Add startup delay to prevent simultaneous driver creation
    startup_delay = process_id * 3 + random.uniform(1, 3)
    print(f"Worker {process_id}: Waiting {startup_delay:.1f}s before starting...")
    time.sleep(startup_delay)
    
    # Create driver manager
    driver_manager = ChromeDriverManager(process_id)
    
    if not driver_manager.create_driver():
        result_queue.put({
            'worker_id': process_id,
            'error': 'Failed to create driver',
            'status': 'failed'
        })
        with tasks_completed.get_lock():
            tasks_completed.value = -1  # Signal failure
        return
    
    print(f"Worker {process_id} ready!")
    
    try:
        while not stop_event.is_set():
            try:
                # Get task from queue with timeout
                task = task_queue.get(timeout=5)
                if task is None:  # Poison pill
                    break
                
                task_id, url = task
                print(f"Worker {process_id}: Processing task {task_id} - {url}")
                
                # Process the URL
                result = driver_manager.get_page(url)
                result.update({
                    'task_id': task_id,
                    'worker_id': process_id,
                    'timestamp': time.time()
                })
                
                result_queue.put(result)
                
                # Increment completed tasks counter
                with tasks_completed.get_lock():
                    tasks_completed.value += 1
                
                # Random delay between tasks
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                if "Empty" not in str(e) and "timeout" not in str(e).lower():
                    print(f"Worker {process_id} task error: {e}")
                continue
    
    except Exception as e:
        print(f"Worker {process_id} error: {e}")
    
    finally:
        print(f"Worker {process_id} cleaning up...")
        driver_manager.cleanup()

def clean_chromedriver_thoroughly():
    """Thoroughly clean ChromeDriver cache and temporary files"""
    print("Performing thorough ChromeDriver cleanup...")
    
    # Common ChromeDriver cache locations
    cache_locations = [
        os.path.join(os.getenv('APPDATA', ''), 'undetected_chromedriver'),
        os.path.join(os.getenv('LOCALAPPDATA', ''), 'undetected_chromedriver'),
        os.path.join(tempfile.gettempdir(), 'undetected_chromedriver'),
        os.path.join(os.getenv('USERPROFILE', ''), '.cache', 'selenium'),
        os.path.join(os.getenv('TEMP', ''), 'chromedriver-*'),
    ]
    
    for location in cache_locations:
        try:
            if '*' in location:
                # Handle wildcard patterns
                import glob
                for path in glob.glob(location):
                    if os.path.exists(path):
                        if os.path.isdir(path):
                            shutil.rmtree(path, ignore_errors=True)
                        else:
                            os.remove(path)
                        print(f"Cleaned: {path}")
            else:
                if os.path.exists(location):
                    shutil.rmtree(location, ignore_errors=True)
                    print(f"Cleaned: {location}")
        except Exception as e:
            print(f"Warning cleaning {location}: {e}")
    
    # Also clean any chrome_* temp directories
    temp_dir = tempfile.gettempdir()
    try:
        for item in os.listdir(temp_dir):
            if item.startswith('chrome_') and os.path.isdir(os.path.join(temp_dir, item)):
                try:
                    shutil.rmtree(os.path.join(temp_dir, item), ignore_errors=True)
                    print(f"Cleaned temp: {item}")
                except:
                    pass
    except:
        pass

def example_robust_process_based():
    """Robust process-based multiprocessing"""
    
    print("=== Robust Process-based Example ===")
    
    # Test URLs - using simpler endpoints
    urls = [
        "https://httpbin.org/ip",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/headers",
        "https://httpbin.org/json"
    ]
    
    # Create queues and shared counter
    task_queue = Queue()
    result_queue = Queue()
    stop_event = mp.Event()
    tasks_completed = mp.Value('i', 0)
    
    # Add tasks to queue
    total_tasks = len(urls)
    for i, url in enumerate(urls):
        task_queue.put((i, url))
    
    # Create worker processes (reduced number for stability)
    num_workers = 2
    workers = []
    
    print(f"Starting {num_workers} worker processes...")
    
    for i in range(num_workers):
        worker = Process(
            target=worker_process,
            args=(i, task_queue, result_queue, stop_event, tasks_completed)
        )
        workers.append(worker)
        worker.start()
        time.sleep(2)  # Stagger process starts
    
    # Wait for all tasks to complete with extended timeout
    print(f"Waiting for {total_tasks} tasks to complete...")
    timeout = 180  # 3 minutes max
    start_time = time.time()
    
    while tasks_completed.value < total_tasks and time.time() - start_time < timeout:
        time.sleep(3)
        if tasks_completed.value >= 0:  # Not failed
            print(f"Progress: {tasks_completed.value}/{total_tasks} tasks completed")
        else:
            print("Worker initialization failed!")
            break
        
        # Check if all workers are dead
        alive_workers = [w for w in workers if w.is_alive()]
        if not alive_workers and tasks_completed.value < total_tasks:
            print("All workers died unexpectedly!")
            break
    
    if time.time() - start_time >= timeout:
        print("Timeout reached!")
    
    print("Shutting down workers...")
    
    # Signal workers to stop
    stop_event.set()
    for _ in range(num_workers):
        try:
            task_queue.put(None, timeout=2)
        except:
            pass
    
    # Wait for workers to finish
    for worker in workers:
        worker.join(timeout=15)
        if worker.is_alive():
            print(f"Force terminating worker {worker.pid}")
            worker.terminate()
            worker.join(timeout=5)
    
    # Collect results
    results = []
    while not result_queue.empty():
        try:
            result = result_queue.get_nowait()
            results.append(result)
        except:
            break
    
    # Display results
    successful = [r for r in results if r.get('status') == 'success']
    failed = [r for r in results if r.get('status') == 'error']
    
    print(f"\nProcess-based results:")
    print(f"  Total tasks: {total_tasks}")
    print(f"  Successful: {len(successful)}")
    print(f"  Failed: {len(failed)}")
    
    for result in successful:
        title = result.get('title', 'No title')[:50]
        page_len = result.get('page_length', 0)
        print(f"  ✓ Task {result.get('task_id')}: {result['url']} - {title}... ({page_len} chars)")
    
    for result in failed:
        error = result.get('error', 'Unknown error')[:100]
        print(f"  ✗ Task {result.get('task_id')}: {result['url']} - {error}")

def simple_single_test():
    """Test single ChromeDriver instance"""
    print("\n=== Single Driver Test ===")
    
    driver_manager = ChromeDriverManager(0)
    
    if driver_manager.create_driver():
        test_url = "https://httpbin.org/ip"
        result = driver_manager.get_page(test_url)
        
        if result.get('status') == 'success':
            print(f"✓ Successfully loaded: {test_url}")
            print(f"  Title: {result.get('title')}")
            print(f"  Page length: {result.get('page_length')} characters")
        else:
            print(f"✗ Failed to load: {test_url}")
            print(f"  Error: {result.get('error')}")
        
        driver_manager.cleanup()
        return True
    else:
        print("✗ Failed to create driver")
        return False

if __name__ == "__main__":
    # Set multiprocessing start method for Windows
    if hasattr(mp, 'set_start_method'):
        try:
            mp.set_start_method('spawn', force=True)
        except RuntimeError:
            pass
    
    print("Starting FIXED Chrome Multiprocessing Examples...")
    print("This version addresses version conflicts and file conflicts\n")
    
    try:
        # Thorough cleanup first
        clean_chromedriver_thoroughly()
        time.sleep(2)
        
        # Test single driver first
        if simple_single_test():
            time.sleep(5)
            
            # If single driver works, try multiprocessing
            example_robust_process_based()
        else:
            print("Single driver test failed - multiprocessing likely won't work")
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nScript completed!")