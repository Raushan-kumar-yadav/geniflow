
import multiprocessing
import random
import subprocess
from subprocess import CREATE_NO_WINDOW
from tabnanny import check
import time
import uiautomator2 as u2
import shutil
import json
from PySide6.QtWidgets import QMessageBox
import cv2
import pytesseract
from pytesseract import Output
from rapidfuzz import fuzz
import difflib
import uiautomator2 as u2
from lxml import etree
import os
import tempfile
import logging
import re
from collections import OrderedDict
from pyaxmlparser import APK
from typing import Optional, Dict, Any
from pathlib import Path
import base64
#ldController.Ldcontroller_adb.
from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten

    
class LdAdbController():
    def __init__(self, device_serial="emulator-5556", local_output_file_path="",download_folder=None):
        self.device_serial = device_serial
        self.adb_path = r"platform-tools\adb.exe"
        self.page_manager_json = r"User_Data\Page_manager.json"
        self.device_settings_json_path = r"User_Data\Devices_Setting.json"
        self.local_output_file_path = local_output_file_path
        self.download_folder = download_folder
        self.initialization_success = True

        # Initialize device config first
        if not self._validate_path(self.device_settings_json_path, "Device settings JSON"):
            self.initialization_success = False
            return

        try:
            self.device_config_dic = DeviceSettingsFlatten(self.device_settings_json_path)
            self.ld_path = self.get_ld_Player_path()
        except Exception as e:
            logging.error(f"Failed to initialize device configuration: {e}")
            self.initialization_success = False
            return

        # Validate all critical paths
        self._validate_critical_paths()

    def _validate_path(self, path, path_description):
        """Validate if a file or directory exists and log error if missing."""
        if not os.path.exists(path):
            logging.error(f"Critical path missing: {path_description} at '{path}'")
            return False
        return True

    def _validate_critical_paths(self):
        """Validate all critical paths and set initialization status."""
        critical_paths = [
            (self.adb_path, "ADB executable"),
            (self.ld_path, "LD Player path"),
            (self.page_manager_json, "Page manager JSON"),
            (self.device_settings_json_path, "Device settings JSON")
        ]

        missing_paths = []

        for path, description in critical_paths:
            if not path or not self._validate_path(path, description):
                missing_paths.append(f"{description}: {path}")

        if missing_paths:
            logging.error("Critical paths missing during initialization:")
            for missing in missing_paths:
                logging.error(f"  - {missing}")
            self.initialization_success = False

    def get_ld_Player_path(self):
        try:
            ld_path = self.device_config_dic.flatten_json()["LD Location"]
            return ld_path if ld_path else None
        except (KeyError, AttributeError) as e:
            logging.error(f"Failed to get LD Player path: {e}")
            return None

    def check_for_call_and_pause(self,id_or_page="id",pause_event_callback=None):

        pause_event_callback.wait()
        if id_or_page == "id":
            call_decline_xpath ="//node[@content-desc='DECLINE']"
            self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)

    def makeAbolutePath(self,path=""):
        """
        Given a relative path, returns the absolute path.
        """
        return path.replace("/", os.sep).replace("\\", os.sep)
    
    def clean_name(self,text):
        """
        Remove all types of newline/carriage return combinations and return the clean name.

        Args:
            text (str): Input string containing name with newline characters

        Returns:
            str: Clean name without any newline characters
        """
        # Remove all combinations of \r and \n
        cleaned = text.replace('\r\n', '').replace('\n\r', '').replace('\r', '').replace('\n', '')

        # Strip whitespace and return the full clean name
        return cleaned.strip()


    def CheckDeviceInternetConnection(self,host="google.com",count=3):
        """
        Checks if the connected Android device has internet connectivity by executing a ping command via ADB.
        
        Parameters:
            host (str): The host to ping (default is "google.com").
            count (int): Number of ping packets to send (default is 3).
        
        Returns:
            bool: True if the device successfully pings the host (indicating internet connectivity), False otherwise.
        """
        # Construct the adb command.
        cmd = [str(self.adb_path),"-s",str(self.device_serial),"shell", "ping", "-c", str(count), host]
        
        try:
            # Execute the command and capture the output.
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10) 
            output = result.stdout
            # If the command succeeds, check for successful ping output.
            if result.returncode == 0:
                # A common sign of success is 0% packet loss.
                if "0% packet loss" in output or "0% loss" in output:
                    print("Device has internet connectivity!")
                    return True
            return False
        except Exception as e:
            print("Error while checking internet connection:", e)
            return

    def clickByCoordinate(self,x,y):

        # Construct the command to tap at (x, y)
        cmd = [str(self.adb_path),"-s", str(self.device_serial),"shell", "input", "tap", str(x), str(y)]
        # Run the command and capture output if needed
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("LdcontrollerABD -> clickByCoordinate -> Error sending coordinate", result.stderr)
            return False
        else:
            print("Clicked Send")
            return True

    def ScrollByCoordinate(self,x_start,y_start,x_end,y_end,Duration = 350,message="Swiped"):

        #Defining coordinate 
        x1,y1 = x_start,y_start #starting point 
        x2,y2 = x_end,y_end #ending point
        duration = Duration #time of scrolling

        #construct the cmd to scroll
        
        cmd = [str(self.adb_path),"-s", str(self.device_serial),"shell", "input", "swipe", str(x1), str(y1),str(x2),str(y2),str(duration)]

        #run the command

        result = subprocess.run(cmd,capture_output=True,text=True)

        if result.returncode != 0:
            print("LdControllerADB -> ScrollByCoordinate -> Error sending swipe",result.stderr)

            return False

        else:
            print(message)

            return True


    def TakeScreenCap(self, Image_name="screen.png", folder_name=None, sub_folder_name=None, Phone_path="/sdcard/"):

        # Define config
        pc_folder_main_folder = self.local_output_file_path
        
        Pc_path = os.path.dirname(pc_folder_main_folder)
        full_path_on_phone = os.path.join(Phone_path, Image_name)

        # Determine the target folder path on PC
        if folder_name is not None:
            folder_pc_path = os.path.join(Pc_path, folder_name)
        else:
            folder_pc_path = Pc_path

        if sub_folder_name is not None:
            sub_folder_pc_path = os.path.join(folder_pc_path, sub_folder_name)
        else:
            sub_folder_pc_path = folder_pc_path

        # Ensure the target directory exists (create if it doesn't)
        os.makedirs(sub_folder_pc_path, exist_ok=True)
        full_path_on_pc = os.path.join(sub_folder_pc_path, Image_name)

        # Construct the command to capture the screen on the phone
        cmd = [str(self.adb_path), "-s", str(self.device_serial), "shell", "screencap", "-p", full_path_on_phone]
        screenCap = subprocess.run(cmd, capture_output=True, text=True)

        # Wait a random short duration
        time.sleep(random.uniform(1.1, 2.0))

        # Construct the command to pull the screenshot from the phone to PC
        cmd1 = [str(self.adb_path), "-s", str(self.device_serial), "pull", full_path_on_phone, full_path_on_pc]
        pull_screencap = subprocess.run(cmd1, capture_output=True, text=True)

        # Check if any of the commands failed
        if screenCap.returncode != 0 or pull_screencap.returncode != 0:
            # Assuming result.stderr should be replaced with the actual error output variable from your subprocess calls.
            print("LdControllerADB -> TakeScreenCap -> Error capturing:", screenCap.stderr, pull_screencap.stderr)
            return False
        else:
            print("Capture and pulled")
            return full_path_on_pc

        
    def find_text_coordinates(self,image_path, search_text, conf_threshold=95, min_fuzzy_ratio=95):
        """
        Given an image file and a search text, this function performs OCR on the image,
        then searches the detected text (with fuzzy matching) and returns a list of dictionaries.
        Each dictionary contains:
          - 'text': the OCR text for the detected word
          - 'x', 'y': top-left coordinates of the bounding box
          - 'w', 'h': width and height of the bounding box
          - 'conf': confidence value provided by Tesseract
          - 'ratio': the fuzzy matching ratio between the detected text and the search_text
        """
        # Load the image using OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image at path: " + image_path)

        # Run OCR using Tesseract and get detailed data (each word/line)
        ocr_data = pytesseract.image_to_data(image, output_type=Output.DICT)

        results = []
        n_boxes = len(ocr_data['text'])
        for i in range(n_boxes):
            # Get the recognized text and its confidence
            text = ocr_data['text'][i].strip()
            try:
                conf = int(ocr_data['conf'][i])
            except ValueError:
                conf = 0

            # If the OCR confidence is above threshold and text is non-empty
            if conf >= conf_threshold and text:
                # Compute fuzzy matching ratio between the search_text and the detected text.
                ratio = fuzz.partial_ratio(search_text.lower(), text.lower())
                if ratio >= min_fuzzy_ratio:
                    # Get bounding box: left, top, width, and height
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    results.append({
                        'text': text,
                        'x': x,
                        'y': y,
                        'w': w,
                        'h': h,
                        'conf': conf,
                        'ratio': ratio
                    })
        return results
    
    def MatchText(self,paragraph,allowed_words=[],threshold=0.9):

        """
        Check if every word in the paragraph is present (or similar enough) in the allowed_words list.

        Args:
            paragraph (str): The full paragraph text.
            allowed_words (list of str): List of allowed words.
            threshold (float): Similarity ratio threshold (default is 0.9).

        Returns:
            bool: True if every word in the paragraph finds at least one allowed word
                  with a similarity ratio >= threshold; otherwise, False.
        """
        # Normalize allowed words to lower-case.
        normalized_allowed = [word.lower() for word in allowed_words]
        # Extract words from the paragraph (using a regex that matches alphanumeric sequences).
        paragraph_words = re.findall(r'\w+', paragraph.lower())

        # If no words were extracted, you might choose to return False.
        if not paragraph_words:
            return False

        # For each word in the paragraph, check if there is at least one allowed word that's similar enough.
        for para_word in paragraph_words:
            if not any(
                difflib.SequenceMatcher(None, para_word, allowed).ratio() >= threshold 
                for allowed in normalized_allowed
            ):
                # If any paragraph word does not have a close match in allowed_words, return False.
                return False
        return True
    
    def ClickOnTextByImage(self,Text,confi = 90,Text_Match_threshold = 0.95):

        screencap = self.TakeScreenCap()
        time.sleep(2)
        text_coordinates = self.find_text_coordinates(screencap,Text)
        Text_name_and_coordiante = []
        Text_list = []

        for coord in text_coordinates:
            text_name = coord.get('text')
            Text_list.append(text_name)
            print("this is text decected",text_name)

        print("this is deceted text ",Text_list)
        for coord in text_coordinates:
            print("running")
            text_name = coord.get('text')
            confidante = coord.get('conf')
            coordinate_x = coord.get('x')
            coordinate_y = coord.get('y')
            print(text_name,coordinate_x,coordinate_y,confidante)
            

            if self.MatchText(Text, Text_list, Text_Match_threshold) and confidante >= confi :
                print(Text_list)
                click_command = [str(self.adb_path), "-s", str(self.device_serial), "shell", "input", "tap", str(coordinate_x), str(coordinate_y)]
                subprocess.run(click_command, check=True)
                Text_name_and_coordiante.append(text_name)
                Text_name_and_coordiante.append(coordinate_x)
                Text_name_and_coordiante.append(coordinate_y)
                break
                    
            
        return Text_name_and_coordiante
    

    def VerifyTextUsingOcrAllowedWords(self,search_text, conf_threshold=95, min_fuzzy_ratio=95, match_threshold=0.9):
        """
        Uses the full OCR output as the source for allowed words, then verifies if any text candidate 
        matching the search_text passes the allowed-words check.

        Returns:
            bool: True if a valid candidate is found that passes the allowed-words check; otherwise, False.
            
        """
        image_path =self.TakeScreenCap()

        # Load the image using OpenCV
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Could not load image at path: " + image_path)

        # Extract full OCR text from the image and build allowed_words list.
        full_text = pytesseract.image_to_string(image)
        allowed_words = re.findall(r'\w+', full_text.lower())

        # Find candidate text regions in the image using your OCR coordinate method.
        candidates = self.find_text_coordinates(image_path, search_text, conf_threshold, min_fuzzy_ratio)

        # Iterate over candidate texts and check if each meets the allowed_words criteria.
        for candidate in candidates:
            candidate_text = candidate['text']
            if self.MatchText(candidate_text, allowed_words, threshold=match_threshold):
                return True  # Return as soon as a valid match is found.

        return False  # No candidate text passed the allowed-words check.
    

    def MoveFileWithCaption(self,download_folder="", media_type='all', sub_folder=None):
        """
        Moves the first media file (sorted by modification date) from download_folder
        to local_output_file_path, and returns its caption (filename without extension).

        Args:
            media_type (str): 'image', 'video', or 'all'
            sub_folder (str): Optional subfolder within local_output_file_path
        Returns:
            str or None: Caption of the moved file, or None if no matching file found.
        """
        current_download_folder = ""
        if download_folder:
            current_download_folder = download_folder
        else:
            current_download_folder = self.download_folder

        final_path = self.local_output_file_path
        if sub_folder is not None:
            final_path = os.path.join(self.local_output_file_path, sub_folder)

        Path(final_path).mkdir(parents=True, exist_ok=True)

        img_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        vid_exts = {'.mp4', '.avi', '.mov', '.mkv', '.wmv'}

        if media_type == 'image':
            exts = img_exts
        elif media_type == 'video':
            exts = vid_exts
        else:
            exts = img_exts | vid_exts

        files = [p for p in Path(current_download_folder).iterdir()
                 if p.is_file() and p.suffix.lower() in exts]

        if not files:
            print(f"No {media_type} files found in source.")
            return False

        files.sort(key=lambda p: p.stat().st_mtime)
        first = files[0]


        dst = Path(final_path) / first.name
        shutil.move(first, dst)
        print(f"Moved '{first.name}' ({media_type}) to '{final_path}'")

        caption = first.stem  
        return caption
        





    def PullText(self, Text=""):
        """
        Sends text to device via ADBKeyBoard, stripping custom markers and encoding in Base64.

        Args:
            Text (str): The text to send.

        Returns:
            bool: True if text was sent successfully, False otherwise.
        """
        # Remove any _PRE..._POST markers
        processed_text = re.sub(r"_PRE.*?_POST", "", Text)

        # Encode to Base64 without the leading "b'"
        charsb64 = base64.b64encode(processed_text.encode("utf-8")).decode("utf-8")

        # Enable the ADBKeyBoard IME
        for action in ("ime enable", "ime set"):
            subprocess.run([
                self.adb_path, "-s", self.device_serial,
                "shell", *action.split(), "com.android.adbkeyboard/.AdbIME"
            ], capture_output=True, text=True)
            time.sleep(1)

        time.sleep(random.uniform(a=3,b=4))
        # Send the Base64 text via broadcast intent
        result = subprocess.run([
            self.adb_path, "-s", self.device_serial,
            "shell", "am", "broadcast",
            "-a", "ADB_INPUT_B64",
            "--es", "msg", f"%{charsb64}"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Failed to send text: {result.stderr.strip()}")
            return False

        print("Text sent successfully.")
        return True



    def InstallAndCheckAPK(self, app_name="ADBKeyBoard", apk_path=r"platform-tools\ADBKeyboard.apk", timeout=60):
        """
        Install APK and wait until the app appears in the emulator.
        
        Args:
            app_name (str): Display name of the app to check for
            apk_path (str): Path to the APK file
            timeout (int): Maximum time to wait in seconds (default: 60)
        
        Returns:
            bool: True if installation successful and app found, False otherwise
        """
        
        # Install the APK
        print(f"Installing APK: {apk_path}")
        result = subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "install", apk_path], 
                              capture_output=True, text=True)
        
        # Check if installation was successful
        if result.returncode != 0:
            print(f"Installation failed: {result.stderr}")
            return False
        
        print("Installation completed successfully")
        
        time.sleep(3)
        return True
       

    def check_device_Adb_connection(self):
        """
        Checks if any Android device or emulator is connected.
        """
        result = subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "get-state"], capture_output=True, text=True)
        if "device" not in result.stdout:
            print("Ldcontroller -> LdADB -> LDAdbController -> check_device_Adb_connection : Error cheacking Devices" )
            raise Exception("No Android device/emulator found. Please connect a device/emulator.")
            return False
        else:
            return self.device_serial

    def dump_ui(self,retries=1, delay=1):
        """
        Dumps the current UI hierarchy from the device using uiautomator2.
        This version uses the correct path and verifies file creation.
        """
        
        # Connect to the device using uiautomator2
        d = u2.connect(self.device_serial)  # Create actual device connection
        remote_output_file = "/data/local/tmp/window_dump.xml"  
        local_output_file = os.path.join(self.local_output_file_path, "window_dump.xml") 

        for attempt in range(1, retries + 1):
            try:
                # Ensure directory exists
                subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "shell", "mkdir", "-p", "/data/local/tmp"], check=True)

                # Clear any existing dump file
                subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "shell", "rm", "-f", remote_output_file], check=True)

                # Dump the UI hierarchy to a file
                print(f"Attempt {attempt}: Dumping UI hierarchy...")
                xml_content = d.dump_hierarchy()  # Now this will work on the device object

                # Write XML content to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.xml', encoding='utf-8') as temp_file:
                    temp_file.write(xml_content)
                    temp_file_path = temp_file.name

                # Push the temporary file to the device
                subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "push", temp_file_path, remote_output_file], check=True)
                os.remove(temp_file_path)  # Clean up the temporary file
                print("UI dump successful.")

                # Verify file exists and has content
                result = subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "shell", f"ls -l {remote_output_file}"],
                                     capture_output=True, text=True)
                if "No such file" in result.stdout:
                    raise Exception(f"Failed to create dump file at {remote_output_file}")

                # Pull the file from the device
                subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "pull", remote_output_file, local_output_file], check=True)

                if not os.path.exists(local_output_file):
                    raise Exception("Failed to pull dump file to local machine")

                return local_output_file

            except Exception as e:
                print(f"UI dump failed: {e}")
                if attempt < retries:
                    print(f"Retrying after {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception("Failed to dump UI after multiple attempts.") from e
                
    def activity_dump_ui(self, retries=1, delay=1):
        """
        Dumps the current UI hierarchy from the device using uiautomator2,
        excluding the notification/status bar area.
        """
       
        #device_id = self.check_device_Adb_connection()
        d = u2.connect(self.device_serial) # Connect to the device
        remote_output_file = "/data/local/tmp/window_dump.xml" 
        local_output_file = os.path.join(self.local_output_file_path, "window_dump.xml")  
    
        for attempt in range(1, retries + 1):
            try:
                # Ensure directory exists
                subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "shell", "mkdir", "-p", "/data/local/tmp"], check=True)
    
                # Clear any existing dump file
                subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "shell", "rm", "-f", remote_output_file], check=True)
    
                # Dump the UI hierarchy focusing on app content only
                print(f"Attempt {attempt}: Dumping UI hierarchy (app content only)...")
    
                # Use dumpWindowHierarchy with package filter if possible
                # This gets the current focused app package
                focused_app = d.app_current()
                app_package = focused_app['package']
    
                # Option 1: Filter directly with uiautomator2
                xml_content = d.dump_hierarchy()
    
                # Parse the XML to filter out notification area
                from xml.etree import ElementTree as ET
                root = ET.fromstring(xml_content)
    
                # Find and remove nodes related to system UI (status bar)
                system_ui_nodes = root.findall(".//node[@package='com.android.systemui']")
                for node in system_ui_nodes:
                    # Find the parent element
                    for potential_parent in root.findall('.//*'):
                        if node in list(potential_parent):
                            potential_parent.remove(node)
                            break
                        
                # Convert back to string
                filtered_xml = ET.tostring(root, encoding='unicode')
    
                # Write filtered XML content to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.xml', encoding='utf-8') as temp_file:
                    temp_file.write(filtered_xml)
                    temp_file_path = temp_file.name
    
                # Push the temporary file to the device
                subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "push", temp_file_path, remote_output_file], check=True)
                os.remove(temp_file_path)  # Clean up the temporary file
                print("UI dump successful (notifications excluded).")
    
                # Pull the file from the device
                subprocess.run([str(self.adb_path), "-s", str(self.device_serial), "pull", remote_output_file, local_output_file], check=True)
    
                if not os.path.exists(local_output_file):
                    raise Exception("Failed to pull dump file to local machine")
    
                return local_output_file
    
            except Exception as e:
                print(f"UI dump failed: {e}")
                if attempt < retries:
                    print(f"Retrying after {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise Exception("Failed to dump UI after multiple attempts.") from e
    
           

    def get_center_from_bounds(self,bounds_str):
        """
        Given a bounds string in the format "[x1,y1][x2,y2]", return the center (x, y).
        """
        numbers = re.findall(r'\d+', bounds_str)
        if len(numbers) == 4:
            x1, y1, x2, y2 = map(int, numbers)
            return (x1 + x2) // 2, (y1 + y2) // 2
        else:
            raise ValueError("Bounds string format is incorrect.")

    def tap_on_coordinates(self,x, y):
        """
        Simulates a tap on the device screen at the given coordinates.
        """
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "input", "tap", str(x), str(y)], check=True)
        print(f"Tapped at coordinates ({x}, {y}).")

    
    def long_press_on_coord(self,x,y,mili_second=2000):

        """simulates long press with scroll method"""

        cmd = [str(self.adb_path),"-s",str(self.device_serial),"shell","input","swipe",str(x),str(y),str(x),str(y),str(mili_second)]

        subprocess.run(cmd,check=True)

        print("Long pressed")

    def check_is_package_installed(self, package_name):
        """
        Check if a package is installed on the Android device.

        Args:
            package_name (str): The package name to check (e.g., 'com.android.chrome')

        Returns:
            bool: True if the package is installed, False otherwise
        """
        try:
            # package is installed
            cmd = [str(self.adb_path), "-s", str(self.device_serial), "shell", "pm", "list", "packages", package_name]

            # Execute the command
            result = subprocess.run(cmd, capture_output=True, text=True)

            # Check package name
            if result.returncode == 0 and package_name in result.stdout:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error checking if package is installed: {e}")
            return False


    def long_press_on_element(self,xpath_expr,max_attempts=1,mili_second=5000):

        """
        Dumps the UI, finds an element by the provided XPath, computes its center from the 'bounds' attribute,
        and simulates a tap on that element.
        """

        for attempt in range(max_attempts):
            xml_file = self.dump_ui()  
            print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
            tree = etree.parse(xml_file)
            elements = tree.xpath(xpath_expr)

            if elements:
              
                element = elements[0]
                bounds = element.get("bounds")
                if not bounds:
                    raise Exception("Element does not have 'bounds' attribute!")

                try:
                  
                    bounds = bounds.strip('[]')
                    parts = bounds.split('][')
                    x1, y1 = map(int, parts[0].split(','))
                    x2, y2 = map(int, parts[1].split(','))
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                except Exception as e:
                    raise Exception(f"Error parsing bounds '{bounds}': {e}")

              
                self.long_press_on_coord(center_x, center_y,mili_second=mili_second)
                print(f"Tapped element at center coordinates: ({center_x}, {center_y})")
                return  
            else:
                print("Element not found, retrying...")
                time.sleep(0.3)

       
        raise Exception(f"Element not found with the provided XPath after {max_attempts} attempts!")
    
    def long_press_on_element_if_visible(self,xpath_expr,max_attempts=1):

        """
        Dumps the UI, finds an element by the provided XPath, computes its center from the 'bounds' attribute,
        and simulates a tap on that element.
        """
        for attempt in range(max_attempts):
            xml_file = self.dump_ui()  
            print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
            tree = etree.parse(xml_file)
            elements = tree.xpath(xpath_expr)

            if elements:
              
                element = elements[0]
                bounds = element.get("bounds")
                if not bounds:
                    raise Exception("Element does not have 'bounds' attribute!")
                    
                try:
                  
                    bounds = bounds.strip('[]')
                    parts = bounds.split('][')
                    x1, y1 = map(int, parts[0].split(','))
                    x2, y2 = map(int, parts[1].split(','))
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                except Exception as e:
                    raise Exception(f"Error parsing bounds '{bounds}': {e}")

              
                self.long_press_on_coord(center_x, center_y,mili_second=4000)
                print(f"Tapped element at center coordinates: ({center_x}, {center_y})")
                return True
            else:
                print("Element not found, retrying...")
                time.sleep(0.0)

        return False
       
    

    def click_element(self,xpath_expr,max_attempts=1):
        """
        Dumps the UI, finds an element by the provided XPath, computes its center from the 'bounds' attribute,
        and simulates a tap on that element.
        """
        for attempt in range(max_attempts):
            xml_file = self.dump_ui()  
            print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
            tree = etree.parse(xml_file)
            elements = tree.xpath(xpath_expr)

            if elements:
                
                element = elements[0]
                bounds = element.get("bounds")
                if not bounds:
                    raise Exception("Element does not have 'bounds' attribute!")

                try:
                   
                    bounds = bounds.strip('[]')
                    parts = bounds.split('][')
                    x1, y1 = map(int, parts[0].split(','))
                    x2, y2 = map(int, parts[1].split(','))
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                except Exception as e:
                    raise Exception(f"Error parsing bounds '{bounds}': {e}")

               

                self.tap_on_coordinates(center_x, center_y)
                print(f"Tapped element at center coordinates: ({center_x}, {center_y})")
                return True
            else:
                print("Element not found, retrying...")
                
                if max_attempts == 1:
                    pass
                else:
                    time.sleep(0.3)

        
        raise Exception(f"Element not found with the provided XPath after {max_attempts} attempts!")
    

    def click_element_if_visibale(self,xpath_expr):
        """
        Dumps the UI, finds an element by the provided XPath, computes its center from the 'bounds' attribute,
        and simulates a tap on that element.
        """
        
        xml_file = self.dump_ui()  
        tree = etree.parse(xml_file)
        elements = tree.xpath(xpath_expr)
        if elements:
            
            element = elements[0]
            bounds = element.get("bounds")
            if not bounds:
                raise Exception("Element does not have 'bounds' attribute!")
            try:
               
                bounds = bounds.strip('[]')
                parts = bounds.split('][')
                x1, y1 = map(int, parts[0].split(','))
                x2, y2 = map(int, parts[1].split(','))
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
            except Exception as e:
                raise Exception(f"Error parsing bounds '{bounds}': {e}")
           
            self.tap_on_coordinates(center_x, center_y)
            print(f"Tapped element at center coordinates: ({center_x}, {center_y})")
            return True
        else:
            print("Element not found....")
            return False
           

        
       
    
    def check_for_call(self,xpath="//node[@content-desc='DECLINE']"):

        """
        Dumps the UI, finds an element by the provided XPath, and check for calls if its decetact call then decline
        :Args: xpath
        :Retun: Nothing just check for call if not found then do nothing


        """
        
        xml_file = self.dump_ui() 
        tree = etree.parse(xml_file)
        elements = tree.xpath(xpath)
        if elements:
          
            element = elements[0]
            bounds = element.get("bounds")
            if not bounds:
                raise Exception("Call Element does not have 'bounds' attribute!")
            try:
               
                bounds = bounds.strip('[]')
                parts = bounds.split('][')
                x1, y1 = map(int, parts[0].split(','))
                x2, y2 = map(int, parts[1].split(','))
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
            except Exception as e:
                raise Exception(f"Error parsing bounds '{bounds}': {e}")
           
            self.tap_on_coordinates(center_x, center_y)
            print("Incoming Call detected!,Decline")
            return  
        else:
            print("No incoming call...Continued")
             

    def select_video_on_fb_gallry(self,content_num=1):

        content_btn_xpath = "//node[contains(@content-desc,'Video taken on')]"

        current_content_btn_num = (content_num * 2 ) - 1

        self.click_element_btn_number(xpath_expr=content_btn_xpath,btn_number=current_content_btn_num)


    def select_photo_on_fb_gallry(self,content_num=1):

        content_btn_xpath = "//node[contains(@content-desc,'Photo taken on')]"

        current_content_btn_num = (content_num * 2 ) - 1

        self.click_element_btn_number(xpath_expr=content_btn_xpath,btn_number=current_content_btn_num)


    def set_dnd_mode(self, enable=True):
        
        self.startApp(app_package="com.android.settings")
        
        time.sleep(random.uniform(1,2))

        self.click_element(xpath_expr="//node[@text='Sound']")

        time.sleep(random.uniform(1,2))

        self.click_element(xpath_expr="//node[@text='Do Not Disturb']")

        time.sleep(random.uniform(1,2))

        is_clicked =self.scroll_and_click_on_element(scroll_x_coord=300,scroll_y_coordinate=500,element_xpath="//node[@text='TURN ON NOW']",max_no_attempt=3)

        time.sleep(random.uniform(1,2))

        for p in range(5):
            self.BackButton()
            



    def allow_all_permission(self,app_name="facebook",num_of_permission = 7,package_name="com.facebook.katana"):

        self.startApp(app_package="com.android.settings")
        time.sleep(random.uniform(1,2))
        self.click_element(xpath_expr="//node[@text='Search settings']")
        time.sleep(random.uniform(1,2))
        self.PullText(Text=app_name)
        time.sleep(random.uniform(4,6))
        self.click_element(xpath_expr=f"//node[@text='App info']")
        time.sleep(random.uniform(1,2))
        self.click_element(xpath_expr="//node[@text='Permissions']")
        time.sleep(random.uniform(1,2))
        
        for s in range(num_of_permission):
            self.click_element_if_visibale(xpath_expr="//node[@text='OFF']")
            time.sleep(1)

        self.stopApp(app_package="com.android.settings")
        
 
    def click_element_btn_number(self,xpath_expr,btn_number = 0,max_attempts=1):
        """
        Dumps the UI, finds an element by the provided XPath, computes its center from the 'bounds' attribute,
        and simulates a tap on that element and if multiple btn found then it will take given number of btn.
        """
        for attempt in range(max_attempts):
            xml_file = self.dump_ui()  
            print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
            tree = etree.parse(xml_file)
            elements = tree.xpath(xpath_expr)

            if elements:
             
                element = elements[btn_number]
                bounds = element.get("bounds")
                if not bounds:
                    raise Exception("Element does not have 'bounds' attribute!")

                try:
                   
                    bounds = bounds.strip('[]')
                    parts = bounds.split('][')
                    x1, y1 = map(int, parts[0].split(','))
                    x2, y2 = map(int, parts[1].split(','))
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                except Exception as e:
                    raise Exception(f"Error parsing bounds '{bounds}': {e}")

 
                self.tap_on_coordinates(center_x, center_y)
                print(f"Tapped element at center coordinates: ({center_x}, {center_y})")
                return  
            else:
                print("Element not found, retrying...")
                time.sleep(0.5)

       
        raise Exception(f"Element not found with the provided XPath after {max_attempts} attempts!")
    
    def click_list_element_if_visible(self, xpath_list):
        """
        Dumps the UI, finds elements by the provided XPath list, computes their center from the 'bounds' attribute,
        and simulates a tap on the first found element. Tries each XPath in the list until one is found.

        Args:
            xpath_list (list): List of XPath expressions to try

        Returns:
            bool: True if any element was found and clicked, False if none were found
        """

        xml_file = self.dump_ui()  
        tree = etree.parse(xml_file)

        for xpath_expr in xpath_list:
            elements = tree.xpath(xpath_expr)
            if elements:
                element = elements[0]
                bounds = element.get("bounds")
                if not bounds:
                    print(f"Element found with XPath '{xpath_expr}' but does not have 'bounds' attribute!")
                    continue
                
                try:
                    bounds = bounds.strip('[]')
                    parts = bounds.split('][')
                    x1, y1 = map(int, parts[0].split(','))
                    x2, y2 = map(int, parts[1].split(','))
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                except Exception as e:
                    print(f"Error parsing bounds '{bounds}' for XPath '{xpath_expr}': {e}")
                    continue
                
                self.tap_on_coordinates(center_x, center_y)
                print(f"Tapped element at center coordinates: ({center_x}, {center_y}) using XPath: '{xpath_expr}'")
                return True

        print("None of the elements were found or clickable.")
        return False


    def long_press_element_btn_number(self,xpath_expr,btn_number = 0,max_attempts=3):
        """
        Dumps the UI, finds an element by the provided XPath, computes its center from the 'bounds' attribute,
        and simulates a tap on that element and if multiple btn found then it will take given number of btn.
        """
        for attempt in range(max_attempts):
            xml_file = self.dump_ui()  
            print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
            tree = etree.parse(xml_file)
            elements = tree.xpath(xpath_expr)

            if elements:
             
                element = elements[btn_number]
                bounds = element.get("bounds")
                if not bounds:
                    raise Exception("Element does not have 'bounds' attribute!")

                try:
                   
                    bounds = bounds.strip('[]')
                    parts = bounds.split('][')
                    x1, y1 = map(int, parts[0].split(','))
                    x2, y2 = map(int, parts[1].split(','))
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                except Exception as e:
                    raise Exception(f"Error parsing bounds '{bounds}': {e}")

 
                self.long_press_on_coord(x=center_x, y=center_y)
                print(f"Long pressed element at center coordinates: ({center_x}, {center_y})")
                return  
            else:
                print("Element not found, retrying...")
                time.sleep(0.3)

       
        raise Exception(f"Element not found with the provided XPath after {max_attempts} attempts!")
    
    
    def check_content_btn_number_visiable_on_fb_gellary(self, xpath_expr, btn_number=0, max_attempts=1):
        """
        Dumps the UI and checks if an element matching the provided XPath exists at the given index.
        Returns True if the element at btn_number is found within max_attempts, False otherwise.
        """

        current_btn_num = (btn_number * 2 ) - 1

        for attempt in range(1, max_attempts + 1):
            xml_file = self.dump_ui()
            print(f"Attempt {attempt}/{max_attempts}: Dumped UI XML file path: {xml_file}")

            tree = etree.parse(xml_file)
            elements = tree.xpath(xpath_expr)

            if len(elements) > current_btn_num:
                print(f"Element at index {btn_number} found (total elements: {len(elements)}).")
                return True
            else:
                print(f"Element at index {btn_number} not found (found {len(elements)} elements), retrying...")
                time.sleep(0.3)

        print(f"Element not found at index {btn_number} after {max_attempts} attempts.")
        return False

    def check_content_btn_number_visiable(self, xpath_expr, btn_number=0, max_attempts=1):
        """
        Dumps the UI and checks if an element matching the provided XPath exists at the given index.
        Returns True if the element at btn_number is found within max_attempts, False otherwise.
        """

        current_btn_num = btn_number

        for attempt in range(1, max_attempts + 1):
            xml_file = self.dump_ui()
            print(f"Attempt {attempt}/{max_attempts}: Dumped UI XML file path: {xml_file}")

            tree = etree.parse(xml_file)
            elements = tree.xpath(xpath_expr)

            if len(elements) > current_btn_num:
                print(f"Element at index {btn_number} found (total elements: {len(elements)}).")
                return True
            else:
                print(f"Element at index {btn_number} not found (found {len(elements)} elements), retrying...")
                time.sleep(0.3)

        print(f"Element not found at index {btn_number} after {max_attempts} attempts.")
        return False
    

    def click_element_btn_with_random_bounds_offest(self,xpath_expr,max_attempts=3):
        """
        Dumps the UI, finds an element by the provided XPath, computes its center from the 'bounds' attribute,
        and simulates a tap on that element and if multiple btn found then it will take given number of btn.
        """
        for attempt in range(max_attempts):
            xml_file = self.dump_ui()  
            print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
            tree = etree.parse(xml_file)
            elements = tree.xpath(xpath_expr)

            if elements:
                # Randomly select an element from the list of elements

                random_element = random.choice(elements)
                bounds = random_element.get("bounds")
                if not bounds:
                    raise Exception("Element does not have 'bounds' attribute!")

                try:
                    
                    bounds = bounds.strip('[]')
                    parts = bounds.split('][')
                    x1, y1 = map(int, parts[0].split(','))
                    x2, y2 = map(int, parts[1].split(','))
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    center_x_f = center_x - 100
                    center_y_f = center_y
                except Exception as e:
                    raise Exception(f"Error parsing bounds '{bounds}': {e}")

               
                self.tap_on_coordinates(center_x_f, center_y_f)
                print(f"Tapped element at center coordinates: ({center_x}, {center_y})")
                return  
            else:
                print("Element not found, retrying...")
                time.sleep(0.3)

       
        raise Exception(f"Element not found with the provided XPath after {max_attempts} attempts!")

    def random_scroll(self):
        width = 540
        height = 960

        
        x = random.randint(int(width * 0.2), int(width * 0.8))
        y1 = random.randint(int(height * 0.7), int(height * 0.9))
        y2 = random.randint(int(height * 0.1), int(height * 0.3))
        duration = random.randint(300, 1000)

        cmd = [
            str(self.adb_path),
            "-s",
            str(self.device_serial),
            "shell",
            "input",
            "swipe",
            str(x),
            str(y1),
            str(x),
            str(y2),
            str(duration)
        ]

        subprocess.run(cmd, shell=True)
    
    def check_loading_screen_gone(self, 
                             after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                             max_attempts=1, 
                             delay=1):
        """
        Checks if the loading screen has disappeared by searching for a specific UI element.

        Parameters:
            after_loading_screen_element (str): XPath for the element indicating loading is complete.
            max_attempts (int): Number of attempts before giving up.
            delay (int): Seconds to wait between attempts.

        Returns:
            bool: True if the element is found, otherwise False.
        """
        if max_attempts ==1:
            delay = 0
            
        for attempt in range(max_attempts):
            try:
                xml_file = self.dump_ui()  # Dump the UI XML.
                print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
                tree = etree.parse(xml_file)
                elements = tree.xpath(after_loading_screen_element)

                if elements:
                    element = elements[0]
                    bounds = element.get("bounds")
                    print(f"Element found with bounds: {bounds}")
                    return True  # Element is found, exit the function.
                else:
                    print("Loading screen still visible, waiting...")

            except Exception as e:
                print(f"Attempt {attempt + 1} encountered an error: {e}")

            time.sleep(delay)

        print("Element not found after maximum attempts.")
        return False
    

    def CheckLoadingScreenGoneListElements(self, 
                             after_loading_screen_elements=["//node[@content-desc='Create, Double tap to create a new post, story, or reel']"],
                             max_attempts=1, 
                             delay=1):
        """
        Checks if the loading screen has disappeared by searching for specific UI elements.

        Parameters:
            after_loading_screen_elements (list): List of XPaths for elements indicating loading is complete.
            max_attempts (int): Number of attempts before giving up.
            delay (int): Seconds to wait between attempts.

        Returns:
            bool: True if any element is found, otherwise False.
        """
        if max_attempts == 1:
            delay = 0

        for attempt in range(max_attempts):
            try:
                xml_file = self.dump_ui()  # Dump the UI XML.
                print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
                tree = etree.parse(xml_file)

                # Check all provided XPaths
                for xpath in after_loading_screen_elements:
                    elements = tree.xpath(xpath)

                    if elements:
                        element = elements[0]
                        bounds = element.get("bounds")
                        print(f"Element found with XPath '{xpath}' and bounds: {bounds}")
                        return True  # Any element is found, exit the function.

                print("Loading screen still visible, none of the target elements found, waiting...")

            except Exception as e:
                print(f"Attempt {attempt + 1} encountered an error: {e}")

            time.sleep(delay)

        print("No elements found after maximum attempts.")
        return False




    def check_element_visiable(self, 
                             element_to_be_visiable="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                             max_attempts=1, 
                             delay=1):
        """
        Checks if the elment is visible or not .

        Parameters:
            after_loading_screen_element (str): XPath for the element indicating loading is complete.
            max_attempts (int): Number of attempts before giving up.
            delay (int): Seconds to wait between attempts.

        Returns:
            bool: True if the element is found, otherwise False.
        """

        for attempt in range(max_attempts):
            try:
                xml_file = self.dump_ui()  # Dump the UI XML.
                print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
                tree = etree.parse(xml_file)
                elements = tree.xpath(element_to_be_visiable)

                if elements:
                    element = elements[0]
                    bounds = element.get("bounds")
                    print(f"Element found with bounds: {bounds}")
                    return True  

            except Exception as e:
                print(f"Attempt {attempt + 1} encountered an error: {e}")

            time.sleep(delay)

        print("Element not found after maximum attempts.")
        return False


    def find_and_get_element_value(self,xpath,value_key,value_num=0):
        """
        Finds an element by xpath from the dumped UI XML.

        :param xpath: XPath string to locate the element.
        :return: The first element matching the xpath if found, otherwise None.
        """
        for attempt in range(3):
            try:
                xml_file = self.dump_ui()
                if not os.path.exists(xml_file):
                    print(f"Attempt {attempt + 1}: XML file not found at {xml_file}.")
                    time.sleep(0.3)
                    continue

                print(f"Attempt {attempt + 1}: Dumped UI XML file path: {xml_file}")
                tree = etree.parse(xml_file)
                elements = tree.xpath(xpath)
                #elements_div = etree.tostring(elements[0], pretty_print=True).decode("utf-8")
                try:
                    elements_text = elements[value_num].get(value_key)

                except Exception as e:
                    print(e)
                    


                if elements_text:
                    return elements_text
                else:
                    print("Element not visible in the current dump, retrying...")

            except Exception as e:
                print(f"Attempt {attempt + 1} encountered an error: {e}")

            time.sleep(0.3)

        print("Element not found after maximum attempts.")
        return None

        

    def scroll_and_click_on_element(self, scroll_x_coord, scroll_y_coordinate, element_xpath,max_no_attempt,delay = 0.3,offset=100):
        """
        Tries to find and click an element by its XPath.
        If the element is not found, performs an upward swipe (scroll from the bottom upward)
        and tries again, up to 10 times.

        Parameters:
          scroll_x_coord: The x coordinate from which to start the swipe.
          scroll_y_coordinate: The initial y coordinate (assumed to be near the bottom).
          element_xpath: The XPath of the element to locate and click.
        """
        # Define the vertical distance (in pixels) to swipe upward each time.
        scroll_offset = offset

        for attempt in range(int(max_no_attempt)):
            try:
                # Attempt to click the element using the existing click_element method.
                # Using max_attempts=1 for a quick check.
                self.click_element(element_xpath, max_attempts=1)
                print("Element clicked successfully.")
                return True  
            except Exception as e:
                print(f"Attempt {attempt + 1}: Element not found, scrolling upward. Reason: {e}")
                
                new_y = scroll_y_coordinate - scroll_offset
               
                if not self.ScrollByCoordinate(scroll_x_coord, scroll_y_coordinate, scroll_x_coord, new_y):
                    print("Scrolling failed.")
              
                time.sleep(delay)
                # Don't return True here! Continue the loop to try again.

        print("Could not find the given element after scrolling 10 times.")
        return False
    
    def scroll_and_find_element(self, scroll_x_coord, scroll_y_coordinate, element_xpath, max_no_attempt):
        """
        Tries to find and click an element by its XPath.
        If the element is not found, performs an upward swipe (scroll from the bottom upward)
        and tries again, up to max_no_attempt times.

        Parameters:
          scroll_x_coord: The x coordinate from which to start the swipe.
          scroll_y_coordinate: The initial y coordinate (assumed to be near the bottom).
          element_xpath: The XPath of the element to locate and click.
          max_no_attempt: Maximum number of scroll attempts before giving up.
        """
        # Define the vertical distance (in pixels) to swipe upward each time.
        scroll_offset = 100

        for attempt in range(int(max_no_attempt)):
            is_element_visible = self.check_element_visiable(element_to_be_visiable=element_xpath, max_attempts=1)

            if is_element_visible:
                print("Element found successfully.")
                return True
            else:
                print(f"Attempt {attempt + 1}: Element not visible, scrolling upward.")
                new_y = scroll_y_coordinate - scroll_offset

                if not self.ScrollByCoordinate(scroll_x_coord, scroll_y_coordinate, scroll_x_coord, new_y):
                    print("Scrolling failed.")

                time.sleep(0.3)

        print(f"Could not find the given element after scrolling {max_no_attempt} times.")
        return False
    

    def scroll_with_scroll_offset_and_click_on_element(self, scroll_x_coord, scroll_y_coordinate, element_xpath,max_no_attempt,scroll_offset = -100):
        """
        Tries to find and click an element by its XPath.
        If the element is not found, performs an upward swipe (scroll from the bottom upward)
        and tries again, up to 10 times.

        Parameters:
          scroll_x_coord: The x coordinate from which to start the swipe.
          scroll_y_coordinate: The initial y coordinate (assumed to be near the bottom).
          element_xpath: The XPath of the element to locate and click.
        """
        # Define the vertical distance (in pixels) to swipe upward each time.
        scroll_offset = scroll_offset

        for attempt in range(int(max_no_attempt)):
            try:

                self.click_element(element_xpath, max_attempts=1)
                print("Element clicked successfully.")
                return True  
            except Exception as e:
                print(f"Attempt {attempt + 1}: Element not found, scrolling upward. Reason: {e}")
                new_y = scroll_y_coordinate - scroll_offset
                if not self.ScrollByCoordinate(scroll_x_coord, scroll_y_coordinate, scroll_x_coord, new_y):
                    print("Scrolling failed.")
                time.sleep(0.3)


        print("Could not find the given element after scrolling 10 times.")
        return False
    
    def start_adb_server(self):
        """
        Restarts the adb server to clear any lingering connections.
        """

        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "start-server"], check=True)
        print("ADB server started for device: ", self.device_serial)

    def startApp(self,app_package="com.facebook.katana"):
        """
        Starts an app on the device using its package name.
        """
        try:
            subprocess.run([
                            str(self.adb_path),
                            "-s", str(self.device_serial),
                            "shell",
                            "monkey",
                            "-p", app_package,
                            "-c", "android.intent.category.LAUNCHER",
                            "1"
                            ], check=True)
            print(f"App with package name '{app_package}' started.")
            time.sleep(random.uniform(5.0, 10.0))
        except subprocess.CalledProcessError as e:
            print(f"Error starting app {app_package} on device {self.device_serial}:")
            print("Stdout:", e.stdout)
            print("Stderr:", e.stderr)

    def check_popup_on_home_fb(self,max_attempt=4):
        
        for a in range(max_attempt):
            is_popup_gone = self.check_loading_screen_gone(max_attempts=1)
            if is_popup_gone:
                print("NO such Pop-Up found....")
                break
            else:
                print("Pop-Up found swipe down....")
                self.ScrollByCoordinate(x_start=265,y_start=372,x_end=278,y_end=850,Duration=100)
                print(f"#{a} Pop-Up removed.....")
                time.sleep(random.uniform(1,2))



    def stopApp(self,app_package="com.facebook.katana"):
        """
        Stops an app on the device using its package name.
        """
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "am", "force-stop", app_package], check=True)
        print(f"App with package name '{app_package}' stopped.")

    def switchApp(self,Switch_to_app_package="free.vpn.unblock.proxy.turbovpn.lite"):
        """
        Switches to a running app on the device using its package name.
        """
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "monkey", "-p", Switch_to_app_package, "-c", "android.intent.category.LAUNCHER", "1"], check=True)
        print(f"Switched to app with package name '{Switch_to_app_package}'.")
    def BackButton(self):
        """
        Simulates a press of the back button.
        """
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "input", "keyevent", "KEYCODE_BACK"], check=True)
        print("Pressed the back button.")

    def action_by_keycode(self,keycode):
        """
        Simulates a press of the back button.
        """
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "input", "keyevent", str(keycode)], check=True)
        print(f"code simulatd")

    def HomeButton(self):
        """
        Simulates a press of the home button.
        """
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "input", "keyevent", "KEYCODE_HOME"], check=True)
        print("Pressed the home button.")

    def Delete_text_from_back(self,text_num=2):
        """
        Simulates a press of the back space.
        """
        #move cursor to back
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "input", "keyevent", "input keyevent 123"], check=True)

        time.sleep(random.uniform(0.5,1))

        for _ in range(text_num):
            subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "input", "keyevent", "input keyevent 67"], check=True)
        print("Pressed the back button.")


    def get_ld_list(self, ld_console_folder_paths):
        """
        Get the list of LDPlayer devices.

        Returns:
            list: A list of LDPlayer device information, or None if an error occurs.

        Args:
            ld_console_folder_paths (str): The path to the folder containing ldconsole.exe.
        """
        ld_list = []

        try:
            # Use the provided folder path to build the full command path
            cmd = [os.path.join(ld_console_folder_paths, "ldconsole.exe"), "list2"]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            decoded_output = output.decode("utf-8")

        except subprocess.CalledProcessError as e:
            print("Error while getting the list of ld player:", e)
            print("Error output:", e.output.decode())
            return None

        # Parse the output into a list of lists
        for line in decoded_output.splitlines():
            if ',' in line:
                parts = line.strip().split(',')
                idx,name = parts[0],parts[1]
                new_list = [idx,name]
                ld_list.append(new_list)

        return ld_list
    
    def set_pc_shared_folder(self,id_frame_idx=None):
        with open(self.page_manager_json, mode="r", encoding="utf-8") as file:
            data = json.loads(file.read())

        key = f"Id_information.{id_frame_idx}"

        if key not in data:
            print("ID information not found.")
            return (False,"ID information not found.")

        id_frame_info = data[key]
        ld_player_name = id_frame_info.get("Ld_name", "")
        main_folder_path = id_frame_info.get("Main_folder_path", "")

        print(id_frame_info, ld_player_name, main_folder_path)

        # Check if the required values are present (non-empty)
        if not ld_player_name:
            #messagebox.showerror("Error","Please fill LdPlayer Name in page manager")
            return (False,"Please fill LdPlayer Name in page manager")
        if not main_folder_path:
            #messagebox.showerror("Error","Please select main folder frist")
            return (False,"Please select main folder frist")

        ld_instance_list = self.get_ld_list(self.ld_path)
        ld_found = False
        for ld in ld_instance_list:
            ld_idx, ld_name = ld
            if ld_player_name == ld_name:
                ld_found = True
                self.update_shared_folder(
                    ld_player_path=self.ld_path,
                    ld_player_idx=ld_idx,
                    main_folder_path=main_folder_path
                )

                time.sleep(2)

                return (True,"good")
                


        if not ld_found:
            #messagebox.showerror("Error", f"LD instance with name '{ld_player_name}' not found")
            return (False,"LD instance with name not found")


    

    def update_shared_folder(self,ld_player_path,ld_player_idx,main_folder_path):

        key = "statusSettings.sharedPictures"

        config_path = os.path.join(ld_player_path,"vms","config", f"leidian{ld_player_idx}.config")
        
        if not os.path.exists(config_path):
            print("Error","Config file not found")
            return
        
        with open(config_path, "r", encoding="utf-8") as file:
            try:
                config_data = json.load(file)
            except json.JSONDecodeError:
                print("Error","The config file is not in valid JSON format.")
                return
        if key in config_data:
            
            config_data["statusSettings.sharedPictures"] = main_folder_path

            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(config_data, file, indent=4)

        else:
            
            new_config = self.insert_key_after_n_keys(config=config_data,key_to_insert=key,value_to_insert=main_folder_path,after_keys=6)

            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(new_config, file, indent=4)


    def insert_key_after_n_keys(self,config, key_to_insert, value_to_insert, after_keys=6):
        new_config = OrderedDict()
        current_index = 0
        for key, value in config.items():
            new_config[key] = value
            current_index += 1
            if current_index == after_keys:
                # Insert new key-value pair immediately after the 6th key.
                new_config[key_to_insert] = value_to_insert
        # If there were fewer keys than expected, just append at the end.
        if current_index < after_keys:
            new_config[key_to_insert] = value_to_insert
        return new_config
    
    def switch_appliction(self, app_name_to_switch="Files", app_package_name_to_switch="com.android.documentsui"):
        # First check if the app is already running
        running_apps_cmd = [
            str(self.adb_path), "-s", str(self.device_serial), 
            "shell", "dumpsys", "activity", "activities", 
            "|", "grep", "mResumedActivity"
        ]

        result = subprocess.run(running_apps_cmd, capture_output=True, text=True, shell=True)
        current_app = result.stdout.strip()

        # If the app is already in foreground, do nothing
        if app_package_name_to_switch in current_app:
            return True

        # Check if app is running but not in foreground
        ps_cmd = [
            str(self.adb_path), "-s", str(self.device_serial),
            "shell", "ps", "|", "grep", app_package_name_to_switch
        ]

        result = subprocess.run(ps_cmd, capture_output=True, text=True, shell=True)
        is_app_running = bool(result.stdout.strip())

        if is_app_running:
            # If app is running but not in foreground, directly bring it to front
            bring_to_front_cmd = [
                str(self.adb_path), "-s", str(self.device_serial),
                "shell", "am", "start", "-a", "android.intent.action.MAIN",
                "-c", "android.intent.category.LAUNCHER",
                "-n", f"{app_package_name_to_switch}/.{self.get_main_activity(app_package_name_to_switch)}",
                "--activity-single-top"
            ]
            subprocess.run(bring_to_front_cmd, check=True)
            return True

        # If app is not running, start it fresh
        self.startApp(app_package=app_package_name_to_switch)
        return True

    def get_main_activity(self, package_name):
        # Get the main activity for the package
        cmd = [
            str(self.adb_path), "-s", str(self.device_serial),
            "shell", "cmd", "package", "resolve-activity",
            "--brief", package_name, "|", "tail", "-n", "1"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        activity = result.stdout.strip().split('/')[-1]
        return activity

    
    def click_on_cursor(self):

        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "input", "keyevent", "66"], check=True)

    def set_open_loacl_adb(self,id_frame_idx=None):

        with open(self.page_manager_json, mode="r", encoding="utf-8") as file:
            data = json.loads(file.read())

        key = f"Id_information.{id_frame_idx}"

        if key not in data:
            print("ID information not found.")
            return (False,"ID information not found ")

        id_frame_info = data[key]
        ld_player_name = id_frame_info.get("Ld_name", "")
        main_folder_path = id_frame_info.get("Main_folder_path", "")

        print(id_frame_info, ld_player_name, main_folder_path)

        # Check if the required values are present (non-empty)
        if not ld_player_name:
            #messagebox.showerror("Error","Please fill LdPlayer Name in page manager")
            return (False,"Please fill LdPlayer Name in page manager")
        if not main_folder_path:
            #messagebox.showerror("Error","Please select main folder frist")
            return (False,"Please select main folder frist")

        ld_instance_list = self.get_ld_list(self.ld_path)
        ld_found = False
        for ld in ld_instance_list:
            ld_idx, ld_name = ld
            if ld_player_name == ld_name:
                ld_found = True
                self.update_open_loacl_adb(
                    ld_player_idx=ld_idx
                    )

                time.sleep(2)
                return (True,"good")

                
        if not ld_found:
            #messagebox.showerror("Error", f"LD instance with name '{ld_player_name}' not found")
            return (False,"LD instance with name not found")
        
    

    def set_open_loacl_adb_with_name(self,ld_player_name):

        if not ld_player_name:
            #messagebox.showerror("Error","Please fill LdPlayer Name in page manager")
            return (False,"Please fill LdPlayer Name in page manager")

        ld_instance_list = self.get_ld_list(self.ld_path)
        ld_found = False
        for ld in ld_instance_list:
            ld_idx, ld_name = ld
            if ld_player_name == ld_name:
                ld_found = True
                self.update_open_loacl_adb(
                    ld_player_idx=ld_idx
                    )

                time.sleep(2)
                return (True,"good")

                
        if not ld_found:
            #messagebox.showerror("Error", f"LD instance with name '{ld_player_name}' not found")
            return (False,"LD instance with name not found")
        

    def set_ld_multi_player_config(self,key="windowsRowCount",to_set_value=5,if_key_not_avl_after_val =29):

        key_f = key
        
        config_path = os.path.join(self.ld_path,"vms","config", "leidians.config")
        
        if not os.path.exists(config_path):
            print("Error","Config file not found")
            return
        
        with open(config_path, "r", encoding="utf-8") as file:
            try:
                config_data = json.load(file)
            except json.JSONDecodeError:
                print("Error","The config file is not in valid JSON format.")
                return
        if str(key_f) in config_data:
            
            config_data[str(key_f)] = to_set_value

            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(config_data, file,indent=4)

        else:
            
            new_config = self.insert_key_after_n_keys(config=config_data,key_to_insert=str(key_f),value_to_insert=to_set_value,after_keys=if_key_not_avl_after_val)

            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(new_config, file,indent=4)

    def update_open_loacl_adb(self,ld_player_idx):
        

        key = "basicSettings.adbDebug"

        config_path = os.path.join(self.ld_path,"vms","config", f"leidian{ld_player_idx}.config")
        
        if not os.path.exists(config_path):
            print("Error","Config file not found")
            return
        
        with open(config_path, "r", encoding="utf-8") as file:
            try:
                config_data = json.load(file)
            except json.JSONDecodeError:
                print("Error","The config file is not in valid JSON format.")
                return
        if key in config_data:
            
            config_data["basicSettings.adbDebug"] = 1

            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(config_data, file, indent=4)

        else:
            
            new_config = self.insert_key_after_n_keys(config=config_data,key_to_insert=key,value_to_insert=1,after_keys=7)

            with open(config_path, "w", encoding="utf-8") as file:
                json.dump(new_config, file, indent=4)


    def restart_ld_instance(self ,id_info_idx):
        """
        Restart an LDPlayer instance using the LD command line tool.
        This function will:
          1. Start the LDPlayer instance by invoking ldconsole.exe with a 'launch' command.
          2. Wait a few seconds for the instance to initialize.
          3. Close the instance by invoking ldconsole.exe with a 'quit' command.

        Parameters:
          ld_inst_name (str): The name of the LDPlayer instance to restart.
        """

        ld_player_name, main_folder_path = self.get_id_info(id_info_idx)
        
        
        start_cmd = [os.path.join(self.ld_path, "ldconsole.exe"), "launch","--name",ld_player_name]
        
        try:
            subprocess.run(start_cmd, shell=True, check=True)
            print(f"LDPlayer instance '{ld_player_name}' started successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error starting instance '{ld_player_name}': {e}")
            return

        
        time.sleep(10) 

        
        close_cmd = [os.path.join(self.ld_path, "ldconsole.exe"), "quit","--name",ld_player_name]
        
        try:
            subprocess.run(close_cmd, shell=True, check=True)
            print(f"LDPlayer instance '{ld_player_name}' closed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error closing instance '{ld_player_name}': {e}")

    def start_ld_inst(self,id_info_idx): 

        ld_player_name, main_folder_path = self.get_id_info(id_info_idx)
        
        
        start_cmd = [os.path.join(self.ld_path, "ldconsole.exe"), "launch","--name",ld_player_name]
        
        try:
            subprocess.run(start_cmd, shell=True, check=True)
            print(f"LDPlayer instance '{ld_player_name}' started successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error starting instance '{ld_player_name}': {e}")
            return
        
    def close_ld_inst(self,id_info_idx):

        ld_player_name, main_folder_path = self.get_id_info(id_info_idx)

        close_cmd = [os.path.join(self.ld_path, "ldconsole.exe"), "quit","--name",ld_player_name]
        
        try:
            subprocess.run(close_cmd, shell=True, check=True)
            print(f"LDPlayer instance '{ld_player_name}' closed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error closing instance '{ld_player_name}': {e}")


    def get_ld_path_from_device_json(self,Device_settings_json_path=r"User_Data\Devices_Setting.json"):
        
        with open(Device_settings_json_path, mode="r", encoding="utf-8") as file:
            data = json.loads(file.read())

        
        Ld_path = data["Loctions"].get("LD Location")
        geni_data_path =data["Loctions"].get("Geni Data","User_Data\Page_manager.json")

        return[Ld_path,geni_data_path]
    
    def get_id_info(self,id_information):

        with open(self.page_manager_json, mode="r", encoding="utf-8") as file:
            data = json.loads(file.read())

        key = f"Id_information.{id_information}"

        if key not in data:
            print("ID information not found.")
            return

        id_frame_info = data[key]
        ld_player_name = id_frame_info.get("Ld_name", "")
        main_folder_path = id_frame_info.get("Main_folder_path", "")

        return(ld_player_name, main_folder_path)
    
    def set_ld_instance_prop(self, ld_name):
        
        with open( self.device_settings_json_path, mode="r", encoding="utf-8") as file:
            device_settings = json.load(file)

        
        ld_path = device_settings.get("Locations", {}).get("LD Location", "")
        LDPlayer_Settings = device_settings.get("LDPlayer Settings", {})
        Ld_Settings = LDPlayer_Settings.get("Ld Settings", {})
        Settings_Enable_Disable = LDPlayer_Settings.get("Settings Enable/Disable", {})

        # Check if we should apply the LD config
        apply_ld_config = Settings_Enable_Disable.get("Check and apply ld config", True)

        if apply_ld_config:
            # Resolution setup
            res = Ld_Settings.get("Resolution", "540x960 (Recomended)")
            f_res_dic = {
                "540x960 (Recomended)": "540,960,240",
                "1080x1920": "1080,1920,240",
                "900x1600": "900,1600,240",
                "720x1280": "720,180,240"
            }
       
            f_res = f_res_dic.get(res, "540,960,240")

            # CPU setup
            cpu = Ld_Settings.get("CPU", "2 Cores  (Recomended)")
            f_cpu = cpu.split()[0]

            # RAM setup: extract numeric part from "1024MB  (Recomended)"
            RAM = Ld_Settings.get("RAM", "1024MB  (Recomended)")
            match = re.match(r"(\d+)", RAM)
            if match:
                f_ram = match.group(1)
            else:
                f_ram = "1024"  # default fallback

            # Build the command
            command = [
                os.path.join(ld_path, "ldconsole.exe"),
                "modify",
                "--name", str(ld_name),
                "--resolution", str(f_res),
                "--cpu", str(f_cpu),
                "--memory", str(f_ram),
                "--imei", "auto"
            ]

            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                print("Command executed successfully:")
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print("Error", f"Error executing command: {e}")

    def ld_inst_adb_serial_of_selected_frame_without_war(self,id_frame_idx):

        with open(self.page_manager_json, mode="r", encoding="utf-8") as file:
            data = json.loads(file.read())

        key = f"Id_information.{id_frame_idx}"

        if key not in data:
            print("ID information not found.")
            return

        id_frame_info = data[key]
        ld_player_name = id_frame_info.get("Ld_name", "")
        main_folder_path = id_frame_info.get("Main_folder_path", "")

        print(id_frame_info, ld_player_name, main_folder_path)

        # Check if the required values are present (non-empty)
        if not ld_player_name:
            return ("Please Fill LD-Player Name","error")

        ld_instance_idx = 0

        ld_instance_list = self.get_ld_list(self.ld_path)
        
        for ld in ld_instance_list:
            ld_idx, ld_name = ld
            if ld_player_name == ld_name:

                ld_instance_idx = int(ld_idx)
                break

        base_port = 5554
        # Each emulator instance increases the port number by 2
        adb_serial = f"emulator-{base_port + ld_instance_idx * 2}"

        return (adb_serial,None)


    def ld_inst_adb_serial__of_selected_frame(self,id_frame_idx):

        with open(self.page_manager_json, mode="r", encoding="utf-8") as file:
            data = json.loads(file.read())

        key = f"Id_information.{id_frame_idx}"

        if key not in data:
            print("ID information not found.")
            return

        id_frame_info = data[key]
        ld_player_name = id_frame_info.get("Ld_name", "")
        main_folder_path = id_frame_info.get("Main_folder_path", "")

        print(id_frame_info, ld_player_name, main_folder_path)

        # Check if the required values are present (non-empty)
        if not ld_player_name:
            QMessageBox.warning(None,"Error","Please fill LdPlayer Name in page manager")
            return

        ld_instance_idx = 0

        ld_instance_list = self.get_ld_list(self.ld_path)
        
        for ld in ld_instance_list:
            ld_idx, ld_name = ld
            if ld_player_name == ld_name:

                ld_instance_idx = int(ld_idx)
                break

        base_port = 5554
        # Each emulator instance increases the port number by 2
        adb_serial = f"emulator-{base_port + ld_instance_idx * 2}"

        return adb_serial


    def cheack_ld_instance_open_or_not_for_20sec(self, id_frame_idx):
        target_serial = self.ld_inst_adb_serial__of_selected_frame(id_frame_idx)
        timeout = 240  # seconds
        start_time = time.time()

        while True:
            # Run the "adb devices" command and capture its output.
            result = subprocess.run([str(self.adb_path), "devices"], stdout=subprocess.PIPE, text=True)
            output = result.stdout

            # Split the output into lines (skip the header if necessary)
            lines = output.splitlines()
            for line in lines:
                if target_serial in line:
                    # Check that the state is "device" and not "offline"
                    if "device" in line and "offline" not in line:
                        print("emulator found")
                        return True

            # Check if timeout has been reached.
            if time.time() - start_time >= timeout:
                print("unable to find emulator")
                return False

            # Wait for a second before checking again.
            time.sleep(0.3)

        
    def get_installed_packages(self, ld_name):
            """
            Retrieves the list of installed package names from the LDPlayer instance.
            It uses the adb command via ldconsole.exe.
            """
            command = [
                os.path.join(self.ld_path, "ldconsole.exe"),
                "adb",
                "--name", str(ld_name),
                "--command", "shell pm list packages"
            ]
            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                # The output lines are like "package:com.example.app"
                packages = []
                for line in result.stdout.splitlines():
                    if line.startswith("package:"):
                        packages.append(line.split(":", 1)[1].strip())
                return packages
            except subprocess.CalledProcessError as e:
                print("Error getting installed packages:", e.stderr)
                return []

    def get_package_name(self, apk_file_path):
        """
        Extracts the package name from the APK file using Androguard.
        """
        try:
            apk = APK(apk_file_path)
            return apk.get_package()
        except Exception as e:
            print("Error parsing APK:", e)
            return None

    def install_apk(self, apk_file_path, ld_name=""):
        """
        Installs the APK using ldconsole.exe.
        The command used is:
          ldconsole.exe installapp --name <ld_name> --filename <apk_file_path>
        """
        command = [
            os.path.join(self.ld_path, "ldconsole.exe"),
            "installapp",
            "--name", str(ld_name),
            "--filename", str(apk_file_path)
        ]
        try:
            subprocess.run(command, capture_output=True, text=True, check=True)
            print("APK installed successfully.")
        except subprocess.CalledProcessError as e:
            print("Error installing APK:", e.stderr)

    def check_and_install_app(self, apk_path, ld_name):
        """
        Checks if the APK is already installed and installs it if not.
        """
        package_name = self.get_package_name(apk_path)
        if not package_name:
            print("Cannot determine package name from APK.")
            return

        print("Extracted package name:", package_name)
        installed_packages = self.get_installed_packages(ld_name)
        print("Installed packages:", installed_packages)

        if package_name in installed_packages:
            print("Package is already installed. No action taken.")
        else:
            print("Package not installed. Installing APK...")
            self.install_apk(apk_path, ld_name)

    def check_and_install_list_of_apps(self, id_information_idx):
        """
        Checks and installs a list of default apps based on device settings.
        Waits for apps to be installed and visible with a 5-minute timeout.
        """
        with open(self.device_settings_json_path, mode="r", encoding="utf-8") as file:
            device_settings = json.load(file)

        is_install_default_apps = device_settings["LD Instance Settings"].get("Install defaut apps", False)
        default_app_list = device_settings.get("Detalut Apps", [])

        ld_player_name, main_folder_path = self.get_id_info(id_information_idx)

        if is_install_default_apps:
            if self.cheack_ld_instance_open_or_not_for_20sec(id_information_idx):
                # Install all apps first
                installation_results = []
                for app in default_app_list:
                    result = self.check_and_install_app(apk_path=app, ld_name=ld_player_name)
                    installation_results.append((app, result))

                # Wait for all apps to be visible with 5-minute timeout
                timeout_seconds = 5 * 60  # 5 minutes
                start_time = time.time()
                check_interval = 10  # Check every 10 seconds

                while time.time() - start_time < timeout_seconds:
                    all_apps_visible = True

                    for app in default_app_list:
                        if not self.is_app_visible_on_device(app, ld_player_name):
                            all_apps_visible = False
                            break
                        
                    if all_apps_visible:
                        return (True, "All default apps installed and visible")

                    # Wait before next check
                    time.sleep(check_interval)

                # Timeout reached
                return (False, f"Timeout: Not all apps became visible within {timeout_seconds/60} minutes")

            else:
                return (False, "Unable to install the default apps - LD instance not ready")

        return (True, "No default apps to install")
    
    def is_app_visible_on_device(self, apk_path, ld_name):
        """
        Helper method to check if an app is visible/installed on the device.
        You'll need to implement this based on your specific method of checking app visibility.

        This could involve:
        - Checking if the app appears in the app list
        - Using ADB commands to verify installation
        - Checking for app icons on the home screen
        - Using LD Player's API to verify app presence
        """
        try:


            package_name = self.get_package_name(apk_path)
            if package_name:
                return self.check_is_package_installed(package_name)

            return False
        except Exception as e:
            print(f"Error checking app visibility: {e}")
            return False
            

    def dump_ui_uiautomator(self):
        """Dumps the UI hierarchy to an XML file and pulls it to the local machine"""
        # Define file paths
        dump_file = "/sdcard/window_dump.xml"
        local_xml_path = os.path.join(self.local_output_file_path, "window_dump.xml")
        
        # Execute UI dump command
        dump_cmd = [self.adb_path, "-s", self.device_serial, 
                   "shell", "uiautomator", "dump", dump_file]
        try:
            result = subprocess.run(dump_cmd, capture_output=True, text=True, check=True)
            print("Dump Output:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error during uiautomator dump:")
            print(e.stderr)
            return None

        # Wait to ensure file is written
        time.sleep(0.5)
        
        # Ensure local destination directory exists
        if not os.path.exists(self.local_output_file_path):
            os.makedirs(self.local_output_file_path)
            
        # Pull the file from device to local machine
        pull_cmd = [self.adb_path, "-s", self.device_serial, 
                   "pull", dump_file, local_xml_path]
        try:
            result = subprocess.run(pull_cmd, capture_output=True, text=True, check=True)
            print(f"XML file pulled to: {local_xml_path}")
            return local_xml_path
        except subprocess.CalledProcessError as e:
            print("Error during adb pull:")
            print(e.stderr)
            return None
        

    def set_schedule_time(self,day,hour,min):
        #click on schedule for later by coordinate 
        schedule_for_later_x_coord = 300
        schedule_for_later_y_coord = 400

        day_picker_element_xpath ="//node[@resource-id='android:id/date_picker_day_picker']"
        is_day_picker_visiable = self.check_loading_screen_gone(after_loading_screen_element=day_picker_element_xpath)
        ok_btn_xpath = "//node[@content-desc='OK']"

        custom_day_btn_xpath =f"//node[@content-desc='{day}']"

        if is_day_picker_visiable:
            print("hh")
            
            if day == None:
                print("current day selected")
                self.click_element(xpath_expr=ok_btn_xpath)
            else:
                print("custom day selected")
                self.click_element(xpath_expr=custom_day_btn_xpath)
                
        else:
            print("do something else ")

    def wait_till_element_visiable(self,element_xpath="//node[@text='Facebook upload']",max_wait = 14400000):

        till_waited = 0
        is_element_visiable = True
        while is_element_visiable:
            print("element still visiable")
            time.sleep(2)
            element_visiable = self.check_element_visiable(element_to_be_visiable=element_xpath,max_attempts=1)
            till_waited +=2
            if not element_visiable:
                is_element_visiable = False
            if till_waited > max_wait:
                is_element_visiable = False
                
    def wait_till_list_element_visiable_in_fb(self, cheack_for_call_and_pause, id_or_page, element_xpath_list=None, max_wait=14400000):
        """
        Wait until any element from a list becomes invisible in Facebook

        Args:
            check_for_call_and_pause: Function to check for calls and pause
            id_or_page: ID or page identifier
            element_xpath_list: List of XPaths to check for (default: Facebook upload indicators)
            max_wait: Maximum wait time in seconds (default: 4 hours)

        Returns:
            bool: True if all elements disappeared, False if timeout occurred
        """
        # Default list of XPaths if none provided
        if element_xpath_list is None:
            element_xpath_list = [
                "//node[@content-desc='Posting…']",
                "//node[@content-desc='Row showing that your post is finishing up']"
            ]

        till_waited = 0

        while till_waited <= max_wait:
            print("Still Posting")
            cheack_for_call_and_pause(id_or_page)
            self.short_scroll_down_num(check_for_call_and_pause=cheack_for_call_and_pause, id_or_page=id_or_page)
            time.sleep(2)
            till_waited += 2
            cheack_for_call_and_pause(id_or_page)

            # Check each xpath in the list
            any_element_visible = False
            for xpath in element_xpath_list:
                element_visible = self.check_element_visiable(element_to_be_visiable=xpath, max_attempts=1)
                if element_visible:
                    any_element_visible = True
                    print(f"Element still visible: {xpath}")
                    break  # No need to check other elements if one is found

            # If no elements are visible, posting is complete
            if not any_element_visible:
                print("Posting completed - no elements are visible")
                return True

        # Timeout occurred
        print(f"Timeout occurred after {max_wait} seconds")
        return False
    

    def set_ld_prop_in_info_fetcher(self,ld_name):

        self.set_open_loacl_adb_with_name(ld_player_name=ld_name)
        time.sleep(random.uniform(2,4))
        self.set_ld_instance_prop(ld_name=ld_name)
    
    def wait_till_element_visiable_in_fb(self,cheack_for_call_and_pause,id_or_page,element_xpath="//node[@content-desc='Posting…']",max_wait = 14400000):

        """
        Wait until an element becomes invisible in Facebook

        Args:
            check_for_call_and_pause: Function to check for calls and pause
            id_or_page: ID or page identifier
            element_xpath: XPath of element to wait for (default: Facebook upload indicator)
            max_wait: Maximum wait time in seconds (default: 4 hours)

        Returns:
            bool: True if element disappeared, False if timeout occurred
        """
        till_waited = 0

        while till_waited <= max_wait:
            print("Still Posting")
            cheack_for_call_and_pause(id_or_page)
            self.short_scroll_down_num(check_for_call_and_pause=cheack_for_call_and_pause, id_or_page=id_or_page)
            time.sleep(2)
            till_waited += 2
            cheack_for_call_and_pause(id_or_page)

            element_visible = self.check_element_visiable(element_to_be_visiable=element_xpath, max_attempts=1)

            # If element is no longer visible, posting is complete
            if not element_visible:
                print("Posting completed - element no longer visible")
                return True

        # Timeout occurred
        print(f"Timeout occurred after {max_wait} seconds")
        return False

    def scroll_down_num(self,check_for_call_and_pause,id_or_page,scroll_down_num=1,delay=0):
        for r in range(scroll_down_num):
            check_for_call_and_pause(id_or_page)
            self.ScrollByCoordinate(x_start=400,y_start=418,x_end=400,y_end=860,Duration=410,message="Swiped Down...")
            time.sleep(delay)

    def short_scroll_down_num(self,check_for_call_and_pause,id_or_page,scroll_down_num=1,delay=0):
        for r in range(scroll_down_num):
            check_for_call_and_pause(id_or_page)
            self.ScrollByCoordinate(x_start=260,y_start=418,x_end=400,y_end=860,Duration=410,message="Short Swiped Down...")
            time.sleep(delay)

    def long_scroll_down_num(self,check_for_call_and_pause,id_or_page,scroll_down_num=1,delay=0):
        for r in range(scroll_down_num):
            check_for_call_and_pause(id_or_page)
            self.ScrollByCoordinate(x_start=400,y_start=200,x_end=400,y_end=860,Duration=400,message="Swiped Down...")

    def clear_notifications(self):

        clear_notifiactions_xpath = "//node[@text='CLEAR ALL']"
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "service", "call" ,"statusbar","1"], check=True)

        time.sleep(random.uniform(0.5,1))

        is_notification_avl = self.check_element_visiable(element_to_be_visiable=clear_notifiactions_xpath)

        if is_notification_avl:
            self.click_element(xpath_expr=clear_notifiactions_xpath)
        else:
            subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "service", "call" ,"statusbar","2"], check=True)



    def open_notifications_check_uploading(self,cheack_for_call_and_pause,id_or_page,max_wait=14400000):

        clear_notifiactions_xpath = "//node[@text='CLEAR ALL']"
        manage_notifiactions_xpath = "//node[@text='Manage notifications']"

        self.scroll_down_num(scroll_down_num=3,delay=1,check_for_call_and_pause=cheack_for_call_and_pause,id_or_page=id_or_page)

        time.sleep(random.uniform(2,4))
        
        subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "service", "call" ,"statusbar","1"], check=True)

        time.sleep(random.uniform(1,2))
        
        cheack_for_call_and_pause(id_or_page)
        is_manage_notification_avl = self.check_element_visiable(element_to_be_visiable=manage_notifiactions_xpath,max_attempts=2)

        if is_manage_notification_avl :
            cheack_for_call_and_pause(id_or_page)
            self.wait_till_element_visiable(element_xpath="//node[@text='Facebook upload']",max_wait=max_wait)
            cheack_for_call_and_pause(id_or_page)
            self.wait_till_element_visiable(element_xpath="//node[@text='Uploading video']",max_wait=max_wait)
            cheack_for_call_and_pause(id_or_page)
            self.wait_till_element_visiable(element_xpath="//node[@text='Uploading post']",max_wait=max_wait)
            cheack_for_call_and_pause(id_or_page)
            self.click_element_if_visibale(xpath_expr=clear_notifiactions_xpath)
            subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "service", "call" ,"statusbar","2"], check=True)
        else:
            subprocess.run([str(self.adb_path),"-s",str(self.device_serial), "shell", "service", "call" ,"statusbar","2"], check=True)

        posting_banner_xpath = "//node[@content-desc='Posting…']"
        finishing_banner_xpath = "//node[@content-desc='Row showing that your post is finishing up']"
        time.sleep(random.uniform(2,4))
        self.wait_till_element_visiable_in_fb(element_xpath=posting_banner_xpath,max_wait=max_wait,cheack_for_call_and_pause=cheack_for_call_and_pause,id_or_page=id_or_page)
        self.wait_till_element_visiable_in_fb(element_xpath=finishing_banner_xpath,max_wait=max_wait,cheack_for_call_and_pause=cheack_for_call_and_pause,id_or_page=id_or_page)

        print("Uploaded.....")



    def select_folder_in_file(self,check_for_call_and_pause,id_or_page,profile_name,folder_subfix,folder_type):
        
        folder_type_for_xpath = "Videos"

        if folder_type.lower() == "video":
            folder_type_for_xpath ="Videos"
        else:
            folder_type_for_xpath = "Images"

        check_for_call_and_pause(id_or_page)
        show_roots_btn_xpath = "//node[@content-desc='Show roots']"
        is_clickded = self.click_element_if_visibale(xpath_expr=show_roots_btn_xpath)

        if not is_clickded:
            self.BackButton()
        
        check_for_call_and_pause(id_or_page)

        file_type_btn_xpath = f"//node[@text='{folder_type_for_xpath}']"
        check_for_call_and_pause(id_or_page)
        self.click_element_btn_number(xpath_expr=file_type_btn_xpath,btn_number=-1)

        check_for_call_and_pause(id_or_page)

        list_view_xpath =  "//node[@content-desc='List view']"
        is_list_view_visiable = self.click_element_if_visibale(xpath_expr=list_view_xpath)
        check_for_call_and_pause(id_or_page)


        folder_name = self.clean_name(profile_name) + folder_subfix
        folder_btn_xpath = f"//node[@text='{folder_name}']"
        check_for_call_and_pause(id_or_page)

        is_folder_visiable = self.scroll_and_click_on_element(element_xpath=folder_btn_xpath,scroll_x_coord=200,scroll_y_coordinate=400,max_no_attempt=40)
        
        if is_folder_visiable:
            return True
        else:
            return False       

    def verify_opend_folder_and_select_folder_in_file(self,cheack_for_call_and_pause,id_or_page,profile_name,folder_subfix,folder_type):
        
        list_view_xpath =  "//node[@content-desc='List view']"
        folder_type_for_xpath = "Videos"



        if folder_type.lower() == "video":
            folder_type_for_xpath ="Videos"
        else:
            folder_type_for_xpath = "Images"

        selected_elment = "//node[@text='1 selected']"
        is_any_selected = self.check_element_visiable(element_to_be_visiable=selected_elment)

        if is_any_selected:
            self.BackButton()
            cheack_for_call_and_pause(id_or_page)

        folder_name = self.clean_name(profile_name) + folder_subfix

        video_btn_xpath = "//node[@resource-id='android:id/title']"
        
        cheack_for_call_and_pause(id_or_page)
        is_profile_folder_opend = self.find_and_get_element_value(xpath=video_btn_xpath,value_num=0,value_key="text")

        if is_profile_folder_opend == folder_name:
            cheack_for_call_and_pause(id_or_page)
            is_list_view_visiable = self.check_element_visiable(element_to_be_visiable=list_view_xpath,max_attempts=1)
            if is_list_view_visiable:
                cheack_for_call_and_pause(id_or_page)
                self.click_element(xpath_expr=list_view_xpath)
                time.sleep(random.uniform(1,2))
            return True
        else:

            show_roots_btn_xpath = "//node[@content-desc='Show roots']"
            cheack_for_call_and_pause(id_or_page)
            is_clickded =self.click_element_if_visibale(xpath_expr=show_roots_btn_xpath)

            if not is_clickded:
                self.BackButton()
                is_clickded2 =self.click_element_if_visibale(xpath_expr=show_roots_btn_xpath)

                if not is_clickded2:
                    self.stopApp(app_package="com.android.documentsui")
                    cheack_for_call_and_pause(id_or_page)
                    self.switch_appliction()
                    cheack_for_call_and_pause(id_or_page)
                    self.click_element_if_visibale(xpath_expr=show_roots_btn_xpath)


            time.sleep(random.uniform(1,2))


            file_type_btn_xpath = f"//node[@text='{folder_type_for_xpath}']"
            cheack_for_call_and_pause(id_or_page)
            self.click_element_btn_number(xpath_expr=file_type_btn_xpath,btn_number=-1)
            time.sleep(random.uniform(1,2))

            cheack_for_call_and_pause(id_or_page)
            is_list_view_visiable = self.check_element_visiable(element_to_be_visiable=list_view_xpath,max_attempts=1)
            if is_list_view_visiable:
                cheack_for_call_and_pause(id_or_page)
                self.click_element(xpath_expr=list_view_xpath)
                time.sleep(random.uniform(1,2))


            
            folder_btn_xpath = f"//node[@text='{folder_name}']"
            cheack_for_call_and_pause(id_or_page)
            is_folder_visiable = self.scroll_and_click_on_element(element_xpath=folder_btn_xpath,scroll_x_coord=200,scroll_y_coordinate=400,max_no_attempt=40)
            if is_folder_visiable:
                return True
            else:
                return False


    def select_content_and_share(self,check_for_call_and_pause,id_or_page,video_num,share_to):
        
        f_share_to = share_to
        f_video_num = video_num

        if video_num == 0:
            f_video_num = 1
        
        if share_to.lower() == "reel":
            f_share_to = "Reels"
        elif share_to.lower() == "video":
            f_share_to = "News Feed"
        elif share_to.lower() == "image":
            f_share_to = "News Feed"
        elif share_to.lower() == "group":
            f_share_to = "Your groups"
        elif share_to.lower() == "story":
            f_share_to = "Your Story"
        else:
            print("unexpected sharing optoins")

        share_to_btn_xpath = f"//node[@text='{f_share_to}']"
        video_btn_xpath = "//node[@resource-id='android:id/title']"
        is_any_file_selected_xpath = "//node[contains(@text,'selected')]"

        check_for_call_and_pause(id_or_page)
        is_any_file_selected = self.check_element_visiable(element_to_be_visiable=is_any_file_selected_xpath,max_attempts=1)

        if is_any_file_selected:
            self.BackButton()
        check_for_call_and_pause(id_or_page)
        video_captions = self.find_and_get_element_value(xpath=video_btn_xpath,value_key="text",value_num=f_video_num)
        check_for_call_and_pause(id_or_page)
        self.long_press_element_btn_number(xpath_expr=video_btn_xpath,btn_number=f_video_num)


        check_for_call_and_pause(id_or_page)
        self.click_element(xpath_expr="//node[@content-desc='Share']")


        check_for_call_and_pause(id_or_page)
        self.click_element(xpath_expr=share_to_btn_xpath)

        check_for_call_and_pause(id_or_page)

        only_caption = root, ext = os.path.splitext(video_captions)

        return root


    def select_content_and_delete(self,video_num,check_for_call_and_pause,id_or_page):
        
        f_video_num = video_num

        if video_num == 0:
            f_video_num = 1

        video_btn_xpath = "//node[@resource-id='android:id/title']"
        is_any_file_selected_xpath = "//node[contains(@text,'selected')]"

        check_for_call_and_pause(id_or_page)
        is_any_file_selected = self.check_element_visiable(element_to_be_visiable=is_any_file_selected_xpath,max_attempts=1)

        if is_any_file_selected:
            check_for_call_and_pause(id_or_page)
            self.click_element(xpath_expr="//node[@content-desc='Delete']",max_attempts=1)
            time.sleep(random.uniform(1,2))
            check_for_call_and_pause(id_or_page)
            self.click_element(xpath_expr="//node[@text='OK']",max_attempts=2)
            time.sleep(random.uniform(2,3))
            #refrace the ui to update
            check_for_call_and_pause(id_or_page)
            self.ScrollByCoordinate(x_start=200,y_start=500,x_end=200,y_end=800,Duration=1000)
        else:
            check_for_call_and_pause(id_or_page)
            self.long_press_element_btn_number(xpath_expr=video_btn_xpath,btn_number=f_video_num)
            time.sleep(random.uniform(2,3))
            check_for_call_and_pause(id_or_page)
            self.click_element(xpath_expr="//node[@content-desc='Delete']",max_attempts=1)

            time.sleep(random.uniform(1,2))
            check_for_call_and_pause(id_or_page)
            self.click_element(xpath_expr="//node[@text='OK']",max_attempts=2)
            time.sleep(random.uniform(2,3))
            #refrace the ui to update
            check_for_call_and_pause(id_or_page)
            self.ScrollByCoordinate(x_start=200,y_start=500,x_end=200,y_end=800,Duration=1000)


       

     
    

    def select_folder_form_file_and_share_and_return_caption(self,check_for_pause_and_call,id_or_page,video_num,share_to,profile_name,folder_subfix,folder_type):
        
        folder_name = self.clean_name(profile_name) + folder_subfix
        video_btn_xpath = "//node[@resource-id='android:id/title']"
        folder_btn_xpath = f"//node[@text='{folder_name}']"  
        caontent_caption = ""

        check_for_pause_and_call(id_or_page)
        is_profile_folder_opend = self.find_and_get_element_value(xpath=video_btn_xpath,value_num=0,value_key="text")

        if is_profile_folder_opend == folder_name:
            check_for_pause_and_call(id_or_page)
            caontent_caption = self.select_content_and_share(video_num=video_num,share_to=share_to,check_for_call_and_pause=check_for_pause_and_call,id_or_page=id_or_page)

        else:
            check_for_pause_and_call(id_or_page)
            self.select_folder_in_file(profile_name=profile_name,folder_subfix=folder_subfix,folder_type=folder_type,check_for_call_and_pause=check_for_pause_and_call,id_or_page=id_or_page)

            time.sleep(random.uniform(1,2))
            check_for_pause_and_call(id_or_page)
            caontent_caption = self.select_content_and_share(video_num=video_num,share_to=share_to,check_for_call_and_pause=check_for_pause_and_call,id_or_page=id_or_page)

        return caontent_caption
    
    def select_folder_form_file_and_delete(self,check_for_call_and_pause,id_or_page,video_num,profile_name,folder_subfix,folder_type):
        
        folder_name = self.clean_name(profile_name) + folder_subfix
        video_btn_xpath = "//node[@resource-id='android:id/title']"
        folder_btn_xpath = f"//node[@text='{folder_name}']"  
        
        check_for_call_and_pause(id_or_page)
        is_profile_folder_opend =self.find_and_get_element_value(xpath=video_btn_xpath,value_num=0,value_key="text")

        if is_profile_folder_opend == folder_name:
            self.select_content_and_delete(video_num=video_num,check_for_call_and_pause=check_for_call_and_pause,id_or_page=id_or_page)

        else:
            self.select_folder_in_file(profile_name=profile_name,folder_subfix=folder_subfix,folder_type=folder_type,check_for_call_and_pause=check_for_call_and_pause,id_or_page=id_or_page)
            time.sleep(random.uniform(1,2))
            self.select_content_and_delete(video_num=video_num,check_for_call_and_pause=check_for_call_and_pause,id_or_page=id_or_page)

    def discard_story(self):

        close_elment = "//node[@content-desc='Close']"
        discard_video_elment = "//node[@content-desc='Discard story']"

        if self.click_element_if_visibale(xpath_expr=discard_video_elment):
    
            is_colosed = self.click_element_if_visibale(xpath_expr=close_elment)
            if not is_colosed:
                self.BackButton()


    def discard_post(self):

        discard_post_elment = "//node[@content-desc='Discard post']"
        back_elment = "//node[@content-desc='Back']"

        if self.click_element_if_visibale(xpath_expr=back_elment):
            self.click_element_if_visibale(xpath_expr=discard_post_elment)
            

    def back_btn_untill_home(self,pause_and_cheack_call_back ,id_or_page,delay=1,back_btn_num=6):
        id_or_page = id_or_page
        for r in range(back_btn_num):
            is_home_btn = self.check_loading_screen_gone(delay=0)
            if not is_home_btn:
                pause_and_cheack_call_back(id_or_page)
                self.BackButton()
            else:
                break
    
    def discard_post_and_story(self,cheack_for_call_and_pause_callback,id_or_page):

        self.discard_post()
        cheack_for_call_and_pause_callback(id_or_page)
        self.discard_story()
    
    def back_btn_untill_discard_btn(self, pause_and_cheack_call_back, id_or_page, delay=1, back_btn_num=6):
        """
        Navigate back until discard button is found, then click it.
        """
        discard_post_btn = "//node[@content-desc='DISCARD']"
        discard_post_post_btn = "//node[@content-desc='Discard post']"

        for r in range(back_btn_num):
            print(f"Attempt {r+1}: Checking for discard buttons...")

            # Check if either discard button is visible
            pause_and_cheack_call_back(id_or_page)
            is_discard_btn = self.check_element_visiable(
                element_to_be_visiable=discard_post_btn, 
                max_attempts=1, 
                delay=0
            )
            pause_and_cheack_call_back(id_or_page)
            is_discard_post_btn = self.check_element_visiable(
                element_to_be_visiable=discard_post_post_btn, 
                max_attempts=1, 
                delay=0
            )

            print(f"DISCARD button visible: {is_discard_btn}")
            print(f"Discard post button visible: {is_discard_post_btn}")

            # If either button is visible, click it
            if is_discard_btn or is_discard_post_btn:
                print("Found discard button, attempting to click...")
                try:
                    # Priority: click 'DISCARD' first, then 'Discard post'
                    if is_discard_post_btn:
                        print("Clicking DISCARD button")
                        pause_and_cheack_call_back(id_or_page)
                        self.click_element(xpath_expr=discard_post_post_btn)
                    elif is_discard_btn :
                        print("Clicking Discard post button")
                        pause_and_cheack_call_back(id_or_page)
                        self.click_element(xpath_expr=discard_post_btn)

                    # Verify click was successful (optional)
                    time.sleep(1)  # Wait for UI to respond
                    print("Successfully clicked discard button")
                    break

                except Exception as e:
                    print(f"Error clicking discard button: {e}")
                    # Continue to back button if click fails

            # If no discard button found or click failed, go back
            print("No discard button found or click failed, pressing back...")
            if pause_and_cheack_call_back:
                pause_and_cheack_call_back(id_or_page)

            self.BackButton()
            time.sleep(delay)  # Wait between back button presses

        print(f"Completed after {back_btn_num} attempts")

    def back_btn_untill_discard_changes_btn1(self,pause_and_cheack_call_back ,id_or_page,delay=2,back_btn_num=6):
        """
        Navigate back until 'Discard changes' button is found, then click it.
        """
        discard_changes_btn = "//node[@content-desc='Discard changes']"

        for r in range(back_btn_num):
            print(f"Attempt {r+1}: Checking for 'Discard changes' button...")

            # Check if discard changes button is visible
            is_discard_btn = self.check_element_visiable(
                element_to_be_visiable=discard_changes_btn, 
                max_attempts=1, 
                delay=0
            )

            print(f"'Discard changes' button visible: {is_discard_btn}")

            # If button is visible, click it
            if is_discard_btn:
                print("Found 'Discard changes' button, attempting to click...")
                try:
                    #pause_and_cheack_call_back(id_or_page)
                    self.click_element_if_visibale(xpath_expr=discard_changes_btn)
                    time.sleep(1)  # Wait for UI to respond
                    print("Successfully clicked 'Discard changes' button")
                    break

                except Exception as e:
                    print(f"Error clicking 'Discard changes' button: {e}")
                    # Continue to back button if click fails

            # If button not found or click failed, go back
            print("'Discard changes' button not found or click failed, pressing back...")
   
            self.BackButton()
            time.sleep(delay) 
    
        print(f"Completed after {back_btn_num} attempts")

        
    def back_btn_untill_discard_changes_btn(self,pause_and_cheack_call_back ,id_or_page,delay=3,back_btn_num=10):
        """
        Navigate back until 'Discard changes' button is found, then click it.
        """
        discard_changes = "//node[contains(@text,'Discard changes?,')]"
        discard_changes_btn = "//node[@text='Discard changes']"

        for r in range(back_btn_num):
            print(f"Attempt {r+1}: Checking for 'Discard changes' button...")

            # Check if discard changes button is visible
            is_discard_btn = self.check_element_visiable(
                element_to_be_visiable=discard_changes, 
                max_attempts=1, 
                delay=0
            )

            print(f"'Discard changes' button visible: {is_discard_btn}")

            # If button is visible, click it
            if is_discard_btn:
                print("Found 'Discard changes' button, attempting to click...")
                try:
                    #pause_and_cheack_call_back(id_or_page)
                    is_clicked_discard_chnages_btn =self.click_element_if_visibale(xpath_expr=discard_changes_btn)

                    if not is_clicked_discard_chnages_btn:
                        print("Discard Changes Btn not found Clicking by coordinate")
                        self.clickByCoordinate(x=195,y=910)
                    time.sleep(1)  # Wait for UI to respond
                    print("Successfully clicked 'Discard changes' button")
                    break

                except Exception as e:
                    print(f"Error clicking 'Discard changes' button: {e}")
                    # Continue to back button if click fails

            # If button not found or click failed, go back
            print("'Discard changes' button not found or click failed, pressing back...")
            #pause_and_cheack_call_back(id_or_page)
            self.BackButton()
            time.sleep(delay)  # Wait between back button presses
    
        print(f"Completed after {back_btn_num} attempts")


    def random_time(self,from_time = None,to_time = None):

        max_random_delay = self.device_config_dic.flatten_json()["Anythings Delay"]
        min_random_delay = max_random_delay/2



        if from_time is None:
            min_random_delay = min_random_delay

        else:
            min_random_delay = from_time

        if to_time is None:
            max_random_delay =max_random_delay

        else:
            max_random_delay = to_time

        time.sleep(random.uniform(float(min_random_delay),float(max_random_delay)))




    def empty_folders(self, folder_input=False,subfolder=False):   
        """
        Safely empties each folder in the provided list or single folder path by deleting all files and subdirectories.
        Includes multiple security checks to prevent accidental deletion of system folders or drives.
    
        Args:
            folder_input (list or str): A list of folder paths or a single folder path string to be emptied.
        """


        folder_path = folder_input

        if folder_input == False:
            folder_path = self.local_output_file_path

        # If have any subfolder then add path if not then do nothing 
        if subfolder != False:
           folder_path = os.path.join(folder_path,subfolder)

        # Convert string input to list for uniform processing
        if isinstance(folder_path, str):
            folder_list = [folder_path]
        else:
            folder_list = folder_path
        
        # Define protected directories and drives
        PROTECTED_PATHS = {
            'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)',
            'C:\\System32', 'C:\\Users\\Public', '/bin', '/boot', '/etc',
            '/lib', '/proc', '/root', '/sbin', '/sys', '/usr', '/var'
        }
        
        # Define drive roots to protect (Windows)
        DRIVE_ROOTS = {'C:\\', 'D:\\', 'E:\\', 'F:\\', 'G:\\', 'H:\\', 'I:\\', 'J:\\', 'K:\\', 'L:\\', 'M:\\', 'N:\\', 'O:\\', 'P:\\', 'Q:\\', 'R:\\', 'S:\\', 'T:\\', 'U:\\',      'V:\\', 'W:\\', 'X:\\', 'Y:\\', 'Z:\\'}
        
        for folder in folder_list:
            try:
                # Normalize the path to handle mixed separators
                normalized_path = os.path.normpath(folder)
                absolute_path = os.path.abspath(normalized_path)
                
                print(f"Processing: {absolute_path}")
                
                # Security Check 1: Verify it's not a drive root
                if absolute_path.rstrip('\\').rstrip('/') + '\\' in DRIVE_ROOTS:
                    print(f"SECURITY WARNING: Attempted to empty drive root '{absolute_path}'. Operation blocked!")
                    continue
                
                # Security Check 2: Verify it's not a system/protected directory
                if any(absolute_path.lower().startswith(protected.lower()) for protected in PROTECTED_PATHS):
                    print(f"SECURITY WARNING: Attempted to empty protected directory '{absolute_path}'. Operation blocked!")
                    continue
                
                # Security Check 3: Verify path depth (must be at least 3 levels deep)
                path_parts = Path(absolute_path).parts
                if len(path_parts) < 3:
                    print(f"SECURITY WARNING: Path too shallow '{absolute_path}'. Must be at least 3 levels deep. Operation blocked!")
                    continue
                
                # Security Check 4: Verify directory exists and is actually a directory
                if not os.path.exists(absolute_path):
                    print(f"Directory does not exist: '{absolute_path}'")
                    continue
                    
                if not os.path.isdir(absolute_path):
                    print(f"'{absolute_path}' is not a valid directory.")
                    continue
                
                # Security Check 5: Verify we have write permissions
                if not os.access(absolute_path, os.W_OK):
                    print(f"No write permission for directory: '{absolute_path}'")
                    continue
                
                # Additional confirmation for critical operations
                folder_name = os.path.basename(absolute_path)
                if len(folder_name) < 3:  # Very short folder names might be risky
                    print(f"SECURITY WARNING: Folder name too short '{folder_name}'. Operation blocked!")
                    continue
                
                # Proceed with emptying the folder
                print(f"Emptying folder: {absolute_path}")
                files_deleted = 0
                dirs_deleted = 0
                
                for filename in os.listdir(absolute_path):
                    file_path = os.path.join(absolute_path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.remove(file_path)
                            files_deleted += 1
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            dirs_deleted += 1
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")
                
                print(f"Successfully emptied '{absolute_path}': {files_deleted} files and {dirs_deleted} directories deleted.")
                
            except Exception as e:
                print(f"Error processing folder '{folder}': {e}")







    """Profile Switching"""

    def check_selected_profile(self,cheack_for_call_and_pause_callback,id_or_page):

        #click on profile menu button 

        cheack_for_call_and_pause_callback(id_or_page)

        profile_x_coord=503
        profile_y_coord=147

        home_btn_xpath = "//node[contains(@content-desc,'Home, tab')]"
        menu_btn_xpath = "//node[contains(@content-desc,'Menu, tab')]"

        is_menu_btn_clicked = self.click_element_if_visibale(xpath_expr=menu_btn_xpath)
        if not is_menu_btn_clicked:
            cheack_for_call_and_pause_callback(id_or_page)
            self.clickByCoordinate(x=profile_x_coord,y=profile_y_coord)

        cheack_for_call_and_pause_callback(id_or_page)


        #click on profile_downarrow button

        profile_down_arrow_x = 470
        profile_down_arrow_y = 241

        long_pressed_on_elment = self.long_press_on_element_if_visible(xpath_expr=menu_btn_xpath)

        if not long_pressed_on_elment:
            self.clickByCoordinate(x=profile_down_arrow_x,y=profile_down_arrow_y)

        cheack_for_call_and_pause_callback(id_or_page)

        #dump ui to get current profile name 
        
        max_account_switching_delay = self.device_config_dic.flatten_json()["Account Switching Delay"]
        min_account_switching_delay = int(max_account_switching_delay)*0.9


        self.random_time(from_time=min_account_switching_delay,to_time=max_account_switching_delay)

        cheack_for_call_and_pause_callback(id_or_page)

        dumped_xml_path = self.dump_ui()

        # Parse the XML file
        tree = etree.parse(dumped_xml_path)
       
        all_selected = tree.xpath("//*[@" "selected" "]")
        print(f"Found {len(all_selected)} elements with a 'selected' attribute.")
       
        selected_nodes = tree.xpath("//*[translate(@selected, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='true'][@text!='']")
        if selected_nodes:
            
            element_name = selected_nodes[0].get("text")
            print("Selected Profile: ", element_name.strip())
            return element_name.strip()
        else:
            print("Unable to check selected Profile.")
            return None
        
    def switch_profle_to(self,profile_name,cheack_for_call_and_pause_callback,id_or_page="id"):

        clean_profile_name = profile_name.strip()

        go_to_profile_tab_btn_xpath = "//node[@content-desc='Go to profile']"
        home_btn_xpath = "//node[contains(@content-desc,'Home, tab')]"
        menu_btn_xpath = "//node[contains(@content-desc,'Menu, tab')]"
        profile_x_coord=503
        profile_y_coord=147
        go_to_profile_from_menu_x_coord = 220
        go_to_profile_from_menu_y_coord = 240
        profile_down_arrow_x = 470
        profile_down_arrow_y = 241



        try:

            # Go to profile tab 
            cheack_for_call_and_pause_callback(id_or_page)
            click_on_profile_tab = self.click_element_if_visibale(xpath_expr=go_to_profile_tab_btn_xpath)
            if not click_on_profile_tab:
                cheack_for_call_and_pause_callback(id_or_page)
                is_menu_btn_clicked = self.click_element_if_visibale(xpath_expr=menu_btn_xpath)
                if not is_menu_btn_clicked:
                    cheack_for_call_and_pause_callback(id_or_page)
                    self.clickByCoordinate(x=profile_x_coord,y=profile_y_coord)
                cheack_for_call_and_pause_callback(id_or_page)
                self.clickByCoordinate(x=go_to_profile_from_menu_x_coord,y=go_to_profile_from_menu_y_coord)



            # Check if current selected profile found in facebook or not if not then go to menu tab and switch
            profile_xpath_btn = f"//node[contains(@content-desc,'{clean_profile_name}')]"
            cheack_for_call_and_pause_callback(id_or_page)
            is_profile_name_visible = self.check_element_visiable(element_to_be_visiable=profile_xpath_btn)
            if is_profile_name_visible:
                cheack_for_call_and_pause_callback(id_or_page)
                self.BackButton()
                return True
            


            else:


                cheack_for_call_and_pause_callback(id_or_page)
                self.BackButton()
                cheack_for_call_and_pause_callback(id_or_page)
                is_menu_btn_clicked = self.click_element_if_visibale(xpath_expr=menu_btn_xpath)
                if not is_menu_btn_clicked:
                    cheack_for_call_and_pause_callback(id_or_page)
                    self.clickByCoordinate(x=profile_x_coord,y=profile_y_coord)




                cheack_for_call_and_pause_callback(id_or_page)
                long_pressed_on_elment = self.long_press_on_element_if_visible(xpath_expr=menu_btn_xpath)
                if not long_pressed_on_elment:
                    cheack_for_call_and_pause_callback(id_or_page)
                    self.clickByCoordinate(x=profile_down_arrow_x,y=profile_down_arrow_y)




                # Click on profile button in profile switching window
                is_switched = self.scroll_and_click_on_element(scroll_x_coord=random.uniform(300,400),scroll_y_coordinate=random.uniform(600,700),  element_xpath=f"//node[contains(@text,'{clean_profile_name}')]",max_no_attempt=6,delay=1)
                cheack_for_call_and_pause_callback(id_or_page)




                if is_switched:
                    return True
                

                if not is_switched:
                    cheack_for_call_and_pause_callback(id_or_page)
                    is_see_all_clicked = self.scroll_and_click_on_element(scroll_x_coord=random.uniform(300,400),scroll_y_coordinate=random.uniform (600,700),element_xpath="//node[contains(@content-desc,'See all')]",max_no_attempt=5,delay=1)
                    cheack_for_call_and_pause_callback(id_or_page)
                    is_final_switched = self.scroll_and_click_on_element(scroll_x_coord=random.uniform(300,400),scroll_y_coordinate=random.uniform  (600,700),element_xpath=f"//node[contains(@text,'{clean_profile_name}')]",max_no_attempt=6,delay=1)

                    if not is_final_switched:
                        print("Faild to Switch profile ")



        except Exception as e :
            print(f"Error at switching profile: {e}")
            return False
    


    def RandomScrollAndClickElement(self,element_xpath,max_no_attempt,check_for_call_and_pause_callback,id_or_page,delay = 0.3,offset=100,random_scroll=True):
        """
        Tries to find and click an element by its XPath.
        If the element is not found, performs an upward swipe (scroll from the bottom upward)
        and tries again, up to 10 times.

        Parameters:
          scroll_x_coord: The x coordinate from which to start the swipe.
          scroll_y_coordinate: The initial y coordinate (assumed to be near the bottom).
          element_xpath: The XPath of the element to locate and click.
        """
        width = 540
        height = 960

        x = random.randint(int(width * 0.2), int(width * 0.8))
        y1 = random.randint(int(height * 0.7), int(height * 0.9))
        y2 = random.randint(int(height * 0.1), int(height * 0.3))
        duration = random.randint(300, 1000)


        # Define the vertical distance (in pixels) to swipe upward each time.
        scroll_offset = offset

        for attempt in range(int(max_no_attempt)):
            try:
                # Attempt to click the element using the existing click_element method.
                # Using max_attempts=1 for a quick check.
                check_for_call_and_pause_callback(id_or_page)
                self.click_element(element_xpath, max_attempts=1)
                print("Element clicked successfully.")
                return True  
            except Exception as e:
                print(f"Attempt {attempt + 1}: Element not found, scrolling upward. Reason: {e}")
                
               
                check_for_call_and_pause_callback(id_or_page)

                cmd = [str(self.adb_path),"-s",str(self.device_serial),"shell","input","swipe",str(x),str(y1),str(x),str(y2),str(duration)]
                subprocess.run(cmd, shell=True)
                time.sleep(delay)

                

        print("Could not find the given element after scrolling 10 times.")
        return False

    def WaitAndClickElementIfVisible(self,element_xpath,max_no_attempt,check_for_call_and_pause_callback,id_or_page,delay = 0.3):
        """
        Tries to find and click an element by its XPath.

        """


        
        
        for attempt in range(int(max_no_attempt)):
            try:
                # Using max_attempts=1 for a quick check.
                check_for_call_and_pause_callback(id_or_page)
                self.click_element_if_visibale(element_xpath)
                print("Element clicked successfully.")
                return True  
            
            except Exception as e:
                print(f"Attempt {attempt + 1}: Element not found, scrolling upward. Reason: {e}")
                check_for_call_and_pause_callback(id_or_page)
                time.sleep(delay)

        print("Could not find the given element after scrolling 10 times.")
        return False
    
    def RandomScrollAndClickListElement(self,element_xpath,max_no_attempt,check_for_call_and_pause_callback,id_or_page,delay = 0.3,offset=100,random_scroll=True):
        """
        Tries to find and click an element by its XPath.
        If the element is not found, performs an upward swipe (scroll from the bottom upward)
        and tries again, up to max_no_attempt times.
        """
        width = 540
        height = 960

        x = random.randint(int(width * 0.2), int(width * 0.8))
        y1 = random.randint(int(height * 0.7), int(height * 0.9))
        y2 = random.randint(int(height * 0.1), int(height * 0.3))
        duration = random.randint(300, 1000)

        for attempt in range(int(max_no_attempt)):
            check_for_call_and_pause_callback(id_or_page)

            # Check if element was found and clicked
            if self.click_list_element_if_visible(xpath_list=element_xpath):
                print("Element clicked successfully.")
                return True

            print(f"Attempt {attempt + 1}: Element not found, scrolling upward.")

            # Perform scroll
            check_for_call_and_pause_callback(id_or_page)

            
            cmd = [str(self.adb_path),"-s",str(self.device_serial),"shell","input","swipe",str(x),str(y1),str(x),str(y2),str(duration)]
            subprocess.run(cmd, shell=True)

            time.sleep(delay)

        print(f"Could not find the given element after scrolling {max_no_attempt} times.")
        return False
    


    def SplitByComma(self, text=""):
        return [item.strip() for item in text.split(",")]


    def SharePostToGroups(self,num_of_share,ignore_name,groups_name,check_for_call_and_pause_callback,id_or_page,is_image=False):
        
        if not ignore_name and not groups_name:
            print("No Group Names Provided so skipping group sharing")
            return
            
        group_name_list = self.SplitByComma(text=groups_name)
        more_settings_btn_xpath = "//node[@content-desc='See more settings']"
        share_to_group_btn_xpath = "//node[@content-desc='Share to groups']"
        sharing_to_fb_group_xpath = "//node[contains(@content-desc,'Sharing to Facebook Groups')]"
        back_btn_xpath = "//node[@content-desc='Back']"

        if is_image:
            groups_members_xpath = "//node[contains(@content-desc,'Members')]"
        else:
            groups_members_xpath = "//node[contains(@content-desc,'members')]"

        save_btn_xpath = "//node[@content-desc='Save']"
        final_save_btn_xpath ="//node[@content-desc='Save']"
        No_group_foun_xpath ="//node[contains(@content-desc,'No groups found')]"

        # Go to share to group
        if not is_image:
            
            check_for_call_and_pause_callback(id_or_page)
            is_clicekd_on_view_more = self.RandomScrollAndClickElement(element_xpath=more_settings_btn_xpath,max_no_attempt=3,delay=1,
            check_for_call_and_pause_callback=check_for_call_and_pause_callback,id_or_page=id_or_page)
            if not is_clicekd_on_view_more:
                return
            
        check_for_call_and_pause_callback(id_or_page)
        is_clicked = self.RandomScrollAndClickListElement(element_xpath=[share_to_group_btn_xpath,sharing_to_fb_group_xpath],max_no_attempt=2,delay=1,check_for_call_and_pause_callback=check_for_call_and_pause_callback,id_or_page=id_or_page)
        if not is_clicked:
            return
        
        check_for_call_and_pause_callback(id_or_page)
        group_not_found = self.check_element_visiable(element_to_be_visiable=No_group_foun_xpath)


        if group_not_found:
            check_for_call_and_pause_callback(id_or_page)
            self.click_element(xpath_expr=back_btn_xpath)
            print("No group found")
            return

        group_btn_num = 0
        if ignore_name:
            for share in range(num_of_share):
                group_btn_num += 2
                time.sleep(random.uniform(1.5,2.5))
                check_for_call_and_pause_callback(id_or_page)
                self.click_element_btn_number(xpath_expr=groups_members_xpath,btn_number=group_btn_num)
                check_for_call_and_pause_callback(id_or_page)
                time.sleep(random.uniform(1.5,2.5))
                if not is_image:
                    is_save_btn_clicked = self.WaitAndClickElementIfVisible(element_xpath=save_btn_xpath,max_no_attempt=3,delay=1,  check_for_call_and_pause_callback=check_for_call_and_pause_callback,id_or_page=id_or_page)
                    if not is_save_btn_clicked:
                        self.scroll_down_num(check_for_call_and_pause=check_for_call_and_pause_callback,id_or_page=id_or_page,scroll_down_num=2)
                self.check_loading_screen_gone(after_loading_screen_element=groups_members_xpath,max_attempts=3,delay=1.5)

            check_for_call_and_pause_callback(id_or_page)
            is_save_btn_clicked = self.click_element_if_visibale(xpath_expr=final_save_btn_xpath)
            if not is_save_btn_clicked:
                self.click_element(xpath_expr=back_btn_xpath)

        else:
            
            current_itration = 0
            for group in group_name_list:
                group_namebtn_xpath = f"//node[contains(@content-desc,'{group}')]"
                print(group_namebtn_xpath)
                check_for_call_and_pause_callback(id_or_page)
                is_clicked_on_group_btn = self.click_element_if_visibale(xpath_expr=group_namebtn_xpath)
                check_for_call_and_pause_callback(id_or_page)
                
                if not is_image:
                    if is_clicked_on_group_btn:
                        time.sleep(random.uniform(1.5,2.5))
                        is_save_btn_clicked = self.WaitAndClickElementIfVisible(element_xpath=save_btn_xpath,max_no_attempt=3,delay=1,  check_for_call_and_pause_callback=check_for_call_and_pause_callback,id_or_page=id_or_page)
                        if not is_save_btn_clicked:
                            self.scroll_down_num(check_for_call_and_pause=check_for_call_and_pause_callback,id_or_page=id_or_page,scroll_down_num=2)
    
                if current_itration >= num_of_share:
                    break
                else:
                    current_itration += 1
                time.sleep(random.uniform(1.5,2.5))

            check_for_call_and_pause_callback(id_or_page)
            is_save_btn_clicked = self.click_element_if_visibale(xpath_expr=final_save_btn_xpath)
            if not is_save_btn_clicked:
                self.click_element(xpath_expr=back_btn_xpath)


    def save_you_login_info(self):

        is_save_login_info_xpath = "//node[contains(@content-desc,'Save your login info?')]"
        save_btn_xpath = "//node[@content-desc='Save']"
        is_save_you_login_info_visible = self.check_element_visiable(element_to_be_visiable=is_save_login_info_xpath)
        
        if is_save_you_login_info_visible:
            is_clicked = self.click_element_if_visibale(xpath_expr=save_btn_xpath)
            if not is_clicked:
                self.stopApp()
                time.sleep(random.uniform(a=2,b=4))
                self.startApp()

        

class VPNMonitor:
    def __init__(self, device_id: Optional[str] = None, timeout: int = 300, local_output_file_path="", pause_callback=None):
        """
        Initialize VPN Monitor
        
        Args:
            device_id: ADB device ID (optional, uses default device if None)
            timeout: Maximum time to wait for VPN connection in seconds
        """
        self.device_id = device_id
        self.timeout = timeout
        self.pause_event = pause_callback
        self.adb_path = r"platform-tools\adb.exe"
        self.page_manager_json = r"User_Data\Page_manager.json"
        self.device_settings_json_path = r"User_Data\Devices_Setting.json"
        self.local_output_file_path = local_output_file_path
        self.device_config_dic = DeviceSettingsFlatten(self.device_settings_json_path)
        self.adb_prefix = f"{self.adb_path} -s {device_id}" if device_id else "adb"
        self.ld_adb_controller = LdAdbController(device_serial=self.device_id, local_output_file_path=self.local_output_file_path)

    def execute_adb_command(self, command: str) -> tuple[bool, str]:
        """Execute ADB command and return success status and output"""
        try:
            full_command = f"{self.adb_prefix} {command}"
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, str(e)

    def check_is_paused(self):
        """Check if execution should be paused"""
        if not self.pause_event.is_set():
            self.pause_event.wait()

    def is_vpn_connected(self) -> bool:
        """
        Check if VPN is currently connected using multiple methods
        Returns True if VPN is connected, False otherwise
        """
        # Method 1: Check VPN connection manager status
        success, output = self.execute_adb_command("shell dumpsys connectivity")
        if success and output:
            active_vpn_patterns = [
                'VPN connected', 'VPN is connected', 'Active VPN',
                'VPN: connected', 'VPN status: connected'
            ]
            if any(pattern in output for pattern in active_vpn_patterns):
                return True

        # Method 2: Check VPN service
        success, output = self.execute_adb_command("shell dumpsys vpn")
        if success and output:
            if any(indicator in output for indicator in [
                'mVpnRunner', 'VPN is running', 'Connected users:', 'LegacyVpnRunner'
            ]) and 'Disconnected' not in output:
                return True

        # Method 3: Check default route for VPN interface
        success, output = self.execute_adb_command("shell ip route show default")
        if success:
            for line in output.split('\n'):
                if any(vpn_name in line.lower() for vpn_name in ['tun', 'ppp']) and 'default' in line:
                    interface_match = re.search(r'dev (\w+)', line)
                    if interface_match:
                        interface = interface_match.group(1)
                        success2, ip_output = self.execute_adb_command(f"shell ip addr show {interface}")
                        if success2 and 'inet ' in ip_output and 'UP' in ip_output:
                            return True

        # Method 4: Check for active VPN processes (without grep)
        success, output = self.execute_adb_command("shell ps")
        if success and output:
            vpn_processes = []
            for line in output.split('\n'):
                line_lower = line.lower()
                if line.strip() and any(vpn_proc in line_lower for vpn_proc in [
                    'vpn', 'tun', 'openvpn', 'strongswan', 'racoon', 'vpnservice', 'l2tp'
                ]):
                    if not any(exclude in line_lower for exclude in ['grep', 'shell']):
                        vpn_processes.append(line.strip())
            
            if vpn_processes:
                # Check for VPN ports without grep
                success2, netstat_output = self.execute_adb_command("shell netstat -an")
                if success2 and netstat_output:
                    vpn_ports = [':1194', ':500', ':4500', ':1701']
                    if any(port in netstat_output for port in vpn_ports):
                        return True

        return False

    def get_vpn_package(self) -> Optional[str]:
        """Get VPN package name from device configuration"""
        vpn_dict = {
            "HMA Pro": "com.hidemyass.hidemyassprovpn",
            "Surfshark": "com.surfshark.vpnclient.android",
            "VPN super": "com.free.vpn.super.hotspot.open",
            "Turbo VPN": "free.vpn.unblock.proxy.turbovpn"
        }

        try:
            vpn = self.device_config_dic.flatten_json()["vpn_app_name"]
            if vpn in vpn_dict:
                return vpn_dict.get(vpn)
            else:
                print(f"VPN '{vpn}' not found in supported VPN list")
                return None
        except KeyError:
            print("VPN configuration not found in device settings")
            return None

    def start_vpn_app(self, vpn_package_name: str) -> bool:
        """
        Start VPN application
        
        Args:
            vpn_package_name: Package name of VPN app
            
        Returns:
            True if app started successfully
        """
        if not vpn_package_name:
            print("VPN package name is required")
            return False

        # Check if VPN app package exists (without using grep)
        success, output = self.execute_adb_command("shell pm list packages")
        if not success:
            print("Failed to get package list")
            return False
        
        if vpn_package_name not in output:
            print(f"VPN package '{vpn_package_name}' not found on device")
            return False

        # Check if package is enabled (without using grep)
        success, output = self.execute_adb_command("shell pm list packages -e")
        if not success:
            print("Failed to get enabled packages list")
            return False
            
        if vpn_package_name not in output:
            print(f"VPN package '{vpn_package_name}' is disabled")
            return False

        # Try to start VPN app
        print(f"Starting VPN app: {vpn_package_name}")
        
        success, output = self.execute_adb_command(f"shell monkey -p {vpn_package_name} -c android.intent.category.LAUNCHER 1")
        if success:
            print("VPN app started using monkey command")
        else:
            print("Failed to start VPN app")
            return False


        return success

    def wait_for_vpn_connection(self, check_interval: int = 5) -> bool:
        """
        Wait for VPN to connect within the timeout period
        
        Args:
            check_interval: Time between checks in seconds
            
        Returns:
            True if VPN connected within timeout, False otherwise
        """
        start_time = time.time()
        attempt = 0
        
        print(f"Waiting for VPN connection (timeout: {self.timeout}s, check interval: {check_interval}s)")
        
        while time.time() - start_time < self.timeout:
            attempt += 1
            elapsed = time.time() - start_time
            
            if self.is_vpn_connected():
                print(f"VPN connected successfully after {elapsed:.1f}s (attempt {attempt})")
                return True
            
            print(f"Attempt {attempt}: VPN not connected yet ({elapsed:.1f}s elapsed)")
            
            # Check for pause before sleeping
            self.check_is_paused()
            time.sleep(check_interval)

        print(f"VPN connection timeout after {self.timeout}s")
        return False

    def ensure_vpn_connection(self) -> bool:
        """
        Main method to ensure VPN connection
        
        Returns:
            True if VPN is connected, False otherwise
        """
        print("=== VPN Connection Monitor ===")
        
        # Step 1: Check if VPN is already connected
        print("1. Checking current VPN status...")
        if self.is_vpn_connected():
            print("   VPN is already connected!")
            self.ld_adb_controller.check_for_call()
            self.ld_adb_controller.HomeButton()
            return True
        
        print("   VPN is not connected")
        
        # Step 2: Get VPN package name
        print("2. Getting VPN package information...")
        vpn_package = self.get_vpn_package()
        if not vpn_package:
            print("   Failed to get VPN package name")
            return False
        
        print(f"   VPN package: {vpn_package}")
        
        # Step 3: Start VPN app
        print("3. Starting VPN application...")
        if not self.start_vpn_app(vpn_package):
            print("   Failed to start VPN app")
            return False
        
       
        print("4. Waiting for VPN connection...")
        if self.wait_for_vpn_connection(check_interval=3):
            print("   VPN connection established successfully!")
            self.ld_adb_controller.check_for_call()
            self.ld_adb_controller.HomeButton()
            return True
        else:
            print("   VPN connection failed or timed out")
            self.ld_adb_controller.check_for_call()  
            self.ld_adb_controller.HomeButton()
            return False

    def main(self) -> bool:
        """
        Main execution method - simplified interface
        
        Returns:
            True if VPN is connected, False otherwise
        """
        return self.ensure_vpn_connection()


class AdbFbPopUp():

    def __init__(self,device_serial="emulator-5558",local_output_file_path="",pause_callback=None):

        self.device_serial = device_serial
        self.pause_callback = pause_callback
        self.adb_path = r"platform-tools\adb.exe"
        self.page_manager_json = r"User_Data\Page_manager.json"
        self.device_settings_json_path=r"User_Data\Devices_Setting.json"
        self.local_output_file_path = local_output_file_path
        self.ld_adb_controller = LdAdbController(device_serial=self.device_serial,local_output_file_path=local_output_file_path)
        try:
            self.device_config_dic = DeviceSettingsFlatten(self.device_settings_json_path)
            self.ld_path = self.get_ld_Player_path()
        except Exception as e:
            logging.error(f"Failed to initialize device configuration: {e}")
        

    def check_is_paused(self):

        if not self.pause_callback.is_set():
            self.pause_callback.wait()


    def AddCallNowBtnOnCreatePost(self):
        make_it_easier_to_contact_element_xpath = "//node[@content-desc='Not now']"
        not_now_btn_xpath = "//node[@content-desc='Not now']"
        check_is_add_call_visiable = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=make_it_easier_to_contact_element_xpath,max_attempts=1)
        if check_is_add_call_visiable:

            self.ld_adb_controller.check_for_call()
            self.check_is_paused()
            self.ld_adb_controller.click_element(xpath_expr=not_now_btn_xpath)
        
    def IncreaseYourReachOnHomeScreen(self):
        increase_your_reach_element_xpath = "//node[contains(@content-desc,'Increase your reach')]" 
        closer_btn_xpath = "//node[@content-desc='Close']"

        is_increase_your_reach_element_vasible = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=increase_your_reach_element_xpath,max_attempts=1)

        if is_increase_your_reach_element_vasible:
            
            self.ld_adb_controller.check_for_call()
            self.check_is_paused()
            self.ld_adb_controller.clickByCoordinate(x=494,y=919)
            self.ld_adb_controller.check_for_call()
            self.check_is_paused()
            self.ld_adb_controller.click_element(xpath_expr=closer_btn_xpath)


        


        

import multiprocessing
import time

# Create a global pause event
pause_event = multiprocessing.Event()

def pause_callback(id_or_page=None):
    """
    Pause callback function that checks if the process should be paused.
    If paused, it will wait until the pause is cleared.
    
    Args:
        id_or_page: Optional identifier for the current page/process
    """
    if pause_event.is_set():
        print(f"Process paused for {id_or_page if id_or_page else 'unknown page'}")
        # Wait until the pause event is cleared
        while pause_event.is_set():
            time.sleep(2)  # Small delay to prevent busy waiting
        print(f"Process resumed for {id_or_page if id_or_page else 'unknown page'}")

def pause_process():
    """Function to pause the process"""
    pause_event.set()
    print("Process paused!")

def resume_process():
    """Function to resume the process"""
    pause_event.clear()
    print("Process resumed!")

def is_paused():
    """Check if the process is currently paused"""
    return pause_event.is_set()

# Example usage with your existing code:
if __name__ == "__main__":
    # Your existing code
    q = LdAdbController(local_output_file_path=r"E:\facebook_ld\raushan\main_folder", 
                       device_serial="emulator-5554")
    
    # XPath definitions
    home_btn_xpath = "//node[contains(@content-desc,'Home, tab')]"
    menu_btn_xpath = "//node[contains(@content-desc,'Menu, tab')]"
    discard_post_elment = "//node[@content-desc='Cancel']"
    back_elment = "//node[@content-desc='Discard story']"
    discard_chnages_elment = "//node[@content-desc='Discard changes']"
    x = "//node[@content-desc='See more settings']"
    
    # Use the pause callback in your SharePostToGroups method
    q.SharePostToGroups(
        num_of_share=3,
        ignore_name=False,
        groups_name="Divya Singh,Riya Kumari",
        check_for_call_and_pause_callback=pause_callback,
        id_or_page="page",
        is_image=False
    )


    x = "//node[@content-desc='See more settings']"
    
    #q.save_you_login_info()               
    #q.dump_ui()


    #q.back_btn_untill_discard_changes_btn(pause_and_cheack_call_back=None,id_or_page="id",delay=3)

    #video_btn_xpath = "//node[@resource-id='android:id/title']"
        

    # is_profile_folder_opend = q.find_and_get_element_value(xpath=video_btn_xpath,value_num=0,value_key="text")
    
    # print(is_profile_folder_opend)
    
    #q.click_element_if_visibale(xpath_expr=discard_post_elment)

    
    #q.click_element(xpath_expr="//node[contains(@content-desc,'Menu, tab')]")
    #q.open_notifications_check_uploading()
    #print("done")
    #q.click_element(xpath_expr="//node[@content-desc='Back']")
    #q.action_by_keycode(keycode="KEYCODE_REFRESH")
    #q.clear_notifications()
    
    #q.ScrollByCoordinate(x_start=200,y_start=500,x_end=200,y_end=800)

    #q.click_element_if_visibale(xpath_expr="//node[contains(@hint,'Describe your video')]")


    #video_num = 2
    """ 
    for r in range(2):
        caption=q.select_folder_form_file_and_share_and_return_caption(video_num=video_num,share_to="video",profile_name="Brucelee",folder_subfix="_reel",folder_type="video")
        print(caption)
        time.sleep(5)
        
        q.BackButton()
        q.click_element(xpath_expr="//node[@text='DISCARD']")

        q.select_folder_form_file_and_delete(video_num=video_num,profile_name="Brucelee",folder_subfix="_reel",folder_type="video")
        video_num += 1  """




    #q.switch_appliction()
    #q.select_content_on_fb_gallry(content_num=4)
    #q.Delete_text_from_back()
    #h = q.check_element_visiable(element_to_be_visiable="//node[@resource-id='android:id/date_picker_day_picker']")
    #print(h)
    #q.ClickOnTextByImage(Text="schedule")

    #p =q.click_element_btn_with_random_bounds_offest(xpath_expr="//node[contains(@content-desc,'Confirm friend request')]")
    
    #print(p)

    #q.dump_ui_uiautomator()

    #profle_name_with_suffix = "Kajal Kumari_img"

    #p = "//node[@class='android.widget.RelativeLayout' and @resource-id='com.android.gallery3d:id/gallery_root']//node[@class='android.widget.ImageView']"
    #q.click_element(p)


    #commennt_entry_xpath = f"//node[contains(@text,'Comment as')]"

    #p = "//node[@content-desc='List view']"
    #q.click_element(p)


    #v= q.find_and_get_element_value(xpath="//node[@resource-id='android:id/title']",value_key="text",value_num=1)
   

    #q.long_press_element_btn_number(xpath_expr="//node[@resource-id='android:id/title']",btn_number=1)

    #xpath ="//node[contains(@content-desc,'Video taken on')]"
    #q.click_element_btn_number(xpath_expr=xpath,btn_number=6)

    #q.check_for_call(xpath="//node[@content-desc='Suggestions']")
    #q.click_element_btn_number(xpath_expr="//node[@text='See all']",btn_number=1)


    #"//node[contains(@text,' Views')]"


    #c = q.VerifyTextUsingOcrAllowedWords("Available")

    #print(c)

    #q.check_for_call()

    #print("does call cut?")


    #e = q.find_and_get_element_value("//node[contains(@text,'Say something about this photo')]",value_key="text")
    #print(e)

    #c=q.check_loading_screen_gone("//node[@text='Available to set up']")
    #print(c)


"""     is_share_now_btn = q.check_loading_screen_gone(after_loading_screen_element="//node[@content-desc='Share now']")

        
    if is_share_now_btn:
        q.click_element("//node[@content-desc='Share now']")
            """


"""     q.startApp()

    q.clickByCoordinate(369,66)
    time.sleep(random.uniform(1.0,2.5))
    q.clickByCoordinate(337,295)
    time.sleep(random.uniform(1.0,2.5))
    q.clickByCoordinate(77,260)
    time.sleep(5)
    q2 =q.click_element("//node[@content-desc='Select album, Letstrythisagain']")
    time.sleep(random.uniform(1.0,2.5))
    time.sleep(5)
    q.HomeButton()
    time.sleep(2)
    q.startApp("free.vpn.unblock.proxy.turbovpn.lite")
    time.sleep(2)
    q.switchApp("com.facebook.katana")
    time.sleep(2)
    q.switchApp("free.vpn.unblock.proxy.turbovpn.lite")
    time.sleep(2)
    q.stopApp("free.vpn.unblock.proxy.turbovpn.lite")
    time.sleep(2)
    q.switchApp("com.facebook.katana")
    time.sleep(2)

    q.stopApp()
    
    



    print(q2)  """

    