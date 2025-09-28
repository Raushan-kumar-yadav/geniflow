import json
import os
import re
import random
import queue
import subprocess
from subprocess import CREATE_NO_WINDOW
import fnmatch
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
#geni_backend_src.
from geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten

# Configure logging
def setup_logger():
    """Configure and return a logger with file and console handlers."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a unique log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"downloader_{timestamp}.log")
    
    # Configure logger
    logger = logging.getLogger("DownloaderTaskCollector")
    logger.setLevel(logging.DEBUG)
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler with less detailed formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


class DownloaderTaskCollector:
    """Collects and manages download tasks based on configuration in JSON files."""
    
    def __init__(self):
        self.logger = setup_logger()
        self.logger.info("Initializing DownloaderTaskCollector")
        self.geni_setting_json_path = r"User_Data\Devices_Setting.json"
        self.page_manager_path = r"User_Data\Page_manager.json"
        self.is_global_upload_enable = True
        self.is_global_id_active_enable = True

        try:
            device_settings_flatten_obj = DeviceSettingsFlatten( self.geni_setting_json_path)
            flatten_data = device_settings_flatten_obj.flatten_json()
            self.is_global_upload_enable = flatten_data["is_auto_upload_enabled"]
            self.is_global_id_active_enable = flatten_data["is_id_active_enabled"]
        except Exception as e :
            print("Faild to fatch gloabl id active and auto upload settings")

        self.main_queue = queue.Queue()
        self.ld_player_path = None  
        self.get_ld_player_path()
        self.logger.debug(f"Set geni_setting_json_path: {self.geni_setting_json_path}")
        self.logger.debug(f"Set page_manager_path: {self.page_manager_path}")
        
    def get_ld_player_path(self):

        with open(self.geni_setting_json_path,mode='r',encoding="utf-8") as f :
            data = json.load(f)

        Loctions_dict = data.get("Loctions",{})
        self.ld_player_path = Loctions_dict.get("LD Location",None)
    
    def clean_name(self,name: str) -> str:
        """Clean a name by removing unwanted characters and normalizing whitespace."""
        if not name:
            return ""

        
        cleaned = name.strip().replace('\r', '').replace('\n', '').replace('\t', '')

        
        cleaned = ' '.join(cleaned.split()) 

        return cleaned

    def get_video_captions(self, 
                          caption_source: str, 
                          video_folder_path: str, 
                          txt_file_path: str, 
                          text_box_content: str, 
                          text_random: bool = False) -> str:
        """Get captions based on specified source."""
        self.logger.info(f"Getting video captions from source: {caption_source}")
        try:
            if caption_source == "From Original Video":
                self.logger.debug(f"Looking for video files in: {video_folder_path}")
                video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
                video_files = [f for f in os.listdir(video_folder_path) if f.lower().endswith(video_extensions)]
                
                if len(video_files) == 1:
                    caption = os.path.splitext(video_files[0])[0]
                    self.logger.debug(f"Using video filename as caption: {caption}")
                    return caption
                else:
                    self.logger.warning(f"Found {len(video_files)} video files, expected 1")
            
            elif caption_source == "From Text Box":
                self.logger.debug(f"Using text box content: {text_box_content[:50]}...")
                return str(text_box_content)
            
            elif caption_source == "From text file":
                self.logger.debug(f"Reading captions from text file: {txt_file_path}")
                if not os.path.exists(txt_file_path):
                    self.logger.error(f"Text file not found: {txt_file_path}")
                    return ""
                    
                try:
                    with open(txt_file_path, mode="r", encoding="utf-8") as file:
                        content = file.read()
                    
                    if text_random:
                        self.logger.debug("Selecting random text block")
                        blocks = re.split(r'\n\s*\n', content.strip())
                        blocks = [block for block in blocks if block.strip()]
                        if blocks:
                            selected_block = random.choice(blocks)
                            self.logger.debug(f"Selected random block: {selected_block[:50]}...")
                            return selected_block
                        else:
                            self.logger.warning("No text blocks found in file")
                            return ""
                    else:
                        self.logger.debug("Taking first text block")
                        text_block = []
                        for line in content.splitlines():
                            if line.strip() == "":
                                break
                            text_block.append(line)
                        result = "\n".join(text_block)
                        self.logger.debug(f"First text block: {result[:50]}...")
                        return result
                except Exception as e:
                    self.logger.exception(f"Error reading text file: {e}")
                    return ""
            else:
                self.logger.warning(f"Unknown caption source: {caption_source}")
        except Exception as e:
            self.logger.exception(f"Error getting video captions: {e}")
        
        self.logger.debug("Returning empty caption")
        return ""
    
    def get_ld_list(self, ld_console_folder_path: str) -> List[List[str]]:
        """Get list of LDPlayer instances."""
        self.logger.info(f"Getting LDPlayer list from: {ld_console_folder_path}")
        ld_list = []
        try:
            ldconsole_path = os.path.join(ld_console_folder_path, "ldconsole.exe")
            if not os.path.exists(ldconsole_path):
                self.logger.error(f"LDConsole not found at: {ldconsole_path}")
                return []
                
            cmd = [ldconsole_path, "list2"]
            self.logger.debug(f"Executing command: {' '.join(cmd)}")
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            decoded_output = output.decode("utf-8")
            
            for line in decoded_output.splitlines():
                if ',' in line:
                    parts = line.strip().split(',')
                    if len(parts) >= 2:
                        ld_list.append([parts[0], parts[1]])
                        self.logger.debug(f"Found LDPlayer instance: {parts[0]}, {parts[1]}")
            
            self.logger.info(f"Found {len(ld_list)} LDPlayer instances")
            return ld_list
        except subprocess.CalledProcessError as e:
            self.logger.exception(f"Error executing LDConsole: {e}")
            self.logger.error(f"Error output: {e.output.decode() if hasattr(e, 'output') else 'No output'}")
        except Exception as e:
            self.logger.exception(f"Unexpected error in get_ld_list: {e}")
        
        return []
    
    def ld_inst_adb_serial_by_name(self, ld_player_name: str) -> Optional[str]:
        """Get ADB serial for LDPlayer by name."""
        self.logger.info(f"Getting ADB serial for LDPlayer: {ld_player_name}")
        if not ld_player_name:
            self.logger.error("No LDPlayer name provided")
            return None
            
        if not self.ld_player_path:
            self.logger.error("LDPlayer path not configured")
            return None
            
        ld_instance_list = self.get_ld_list(self.ld_player_path)
        if not ld_instance_list:
            self.logger.error("No LDPlayer instances found")
            return None
        
        for ld_idx, ld_name in ld_instance_list:
            if ld_player_name == ld_name:
                base_port = 5554
                adb_serial = f"emulator-{base_port + int(ld_idx) * 2}"
                self.logger.info(f"Found ADB serial for '{ld_player_name}': {adb_serial}")
                return adb_serial
                
        self.logger.error(f"LDPlayer with name '{ld_player_name}' not found")
        return None
    
    def check_files_in_folder(self, 
                             folder_path: str, 
                             extensions: List[str], 
                             required_count: int = 2) -> bool:
        """Check if folder contains minimum number of files with specified extensions."""
        self.logger.info(f"Checking files in folder: {folder_path}")
        self.logger.debug(f"Looking for extensions: {extensions}, required count: {required_count}")
        
        if not folder_path or not os.path.exists(folder_path):
            self.logger.error(f"Folder not found: {folder_path}")
            return False
            
        try:
            files_count = 0
            matched_files = []
            
            for root, _, files in os.walk(folder_path):
                for extension in extensions:
                    for filename in fnmatch.filter(files, extension):
                        file_path = os.path.join(root, filename)
                        matched_files.append(file_path)
                        files_count += 1
                        self.logger.debug(f"Found matching file: {file_path}")
            
            if files_count == 0:
                self.logger.warning("No matching files found")
                return False
            elif files_count < required_count:
                self.logger.warning(f"Found only {files_count} files, but {required_count} were required")
                return False
            else:
                self.logger.info(f"Found {files_count} files, which meets or exceeds the requirement of {required_count}")
                return True
        except Exception as e:
            self.logger.exception(f"Error checking files in folder: {e}")
            return False
    
    def check_video_available_in_folder(self, folder_path: str, num_of_video: int = 2) -> bool:
        """Check if folder contains minimum number of video files."""
        self.logger.info(f"Checking for {num_of_video} videos in folder: {folder_path}")
        video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv']
        return self.check_files_in_folder(folder_path, video_extensions, num_of_video)
    
    def check_image_available_in_folder(self, folder_path: str, num_of_img: int = 2) -> bool:
        """Check if folder contains minimum number of image files."""
        self.logger.info(f"Checking for {num_of_img} images in folder: {folder_path}")
        image_extensions = ['*.png', '*.jpeg', '*.jpg']
        return self.check_files_in_folder(folder_path, image_extensions, num_of_img)
    
    def count_schedule_entries(self, data: Dict) -> int:
        """Count the number of dictionary entries in the schedule_time object."""
        self.logger.debug("Counting schedule entries")
        if not data or 'schedule_time' not in data:
            self.logger.debug("No schedule_time data found")
            return 0
            
        schedule_time = data.get('schedule_time', {})
        count = len(schedule_time)
        self.logger.debug(f"Found {count} schedule entries")
        return count
    
    def get_content_count(self, schedule_count: int, normal_count: int) -> int:
        """Return the larger of schedule count and normal count."""
        result = max(schedule_count, normal_count)
        self.logger.debug(f"Content count calculation: max({schedule_count}, {normal_count}) = {result}")
        return result
    
    def is_valid_download_config(self, config_tuple: Tuple) -> bool:
        """Check if all required download configuration parameters are valid."""
        self.logger.debug(f"Validating download config: {config_tuple}")
        if not config_tuple or len(config_tuple) != 6:
            self.logger.error(f"Invalid config tuple length: {len(config_tuple) if config_tuple else 0}, expected 6")
            return False
            
        channel_link, download_from, num_content_needed, download_folder, content_type ,identifier = config_tuple
        
        # Check if any of the required parameters are missing or invalid
        if not channel_link:
            self.logger.error(f"Skipping task: Missing channel link for {content_type}")
            return False
            
        if not download_from:
            self.logger.error(f"Skipping task: Missing download source for {content_type}")
            return False
            
        if not num_content_needed or num_content_needed <= 0:
            self.logger.error(f"Skipping task: Invalid number of content needed ({num_content_needed}) for {content_type}")
            return False
            
        if not download_folder or not os.path.exists(download_folder):
            self.logger.error(f"Skipping task: Invalid or non-existent download folder ({download_folder}) for {content_type}")
            return False
            
        if not content_type or content_type not in ["reel", "short","video", "image", "story"]:
            self.logger.error(f"Skipping task: Invalid content type ({content_type})")
            return False
            
        self.logger.info(f"Valid download config for {content_type}: {num_content_needed} items from {download_from}")
        return True
    
    def process_content_type_config(self, 
                                   content_config: Dict, 
                                   content_type: str, 
                                   upload_enabled: bool, 
                                   auto_download_enabled: bool) -> Optional[Tuple]:
        """Process configuration for a specific content type and determine if download is needed."""
        self.logger.info(f"Processing {content_type} configuration")
        self.logger.debug(f"Upload enabled: {upload_enabled}, Auto download enabled: {auto_download_enabled}")
        
        if not content_config:
            self.logger.warning(f"No configuration found for {content_type}")
            return None
            
        download_folder = content_config.get("download_folder", "")
        num_of_content = content_config.get("num",1)
        download_config = content_config.get("download_configuration", {})
        schedule_config = content_config.get("schedule_config", {})
        
        # Check if local download is enabled
        is_local_download_enabled = download_config.get("auto_download", False)
        self.logger.debug(f"Local download enabled: {is_local_download_enabled}")
        
        if not (upload_enabled and auto_download_enabled and is_local_download_enabled):
            self.logger.info(f"Skipping {content_type} download: upload or auto-download not enabled")
            return None
            
        # Get download parameters
        download_from = download_config.get("download_from", "")
        channel_link = download_config.get("channel_link", "")
        num_content_default = download_config.get("num_of_content_download", 5)
        
        self.logger.debug(f"Download from: {download_from}, Channel link: {channel_link}")
        self.logger.debug(f"Default content count: {num_content_default}")
        
        # Handle numeric values stored as strings
        if isinstance(num_content_default, str):
            try:
                num_content_default = int(num_content_default)
                self.logger.debug(f"Converted string content count to int: {num_content_default}")
            except ValueError:
                self.logger.warning(f"Failed to convert content count '{num_content_default}' to integer, using default 5")
                num_content_default = 5
                
        # Calculate number of content items needed based on schedule
        is_schedule_enabled = schedule_config.get("schedule_enable", False)
        schedule_count = 0
        if is_schedule_enabled:
            schedule_dict = schedule_config.get("schedule_time", {})
            schedule_count = len(schedule_dict)
            self.logger.debug(f"Schedule enabled with {schedule_count} entries")
        else:
            schedule_count = num_of_content

        num_content_needed = max(schedule_count, num_content_default)
        self.logger.debug(f"Calculated content needed: {num_content_needed}")
        
        # Check if we need to download (not enough content available)
        check_func = self.check_video_available_in_folder if content_type in ["reel", "video","story"] else self.check_image_available_in_folder
        if not check_func(download_folder, num_content_needed):
            self.logger.info(f"Need to download {num_content_needed} {content_type}(s) to {download_folder}")
            return (channel_link, download_from, num_content_needed, download_folder, content_type)
        else:
            self.logger.info(f"Sufficient {content_type} content already available in {download_folder}")
            
        return None
    
    def is_valid_instance_info(self, instance_info: Tuple) -> bool:
        """Check if the instance information is valid."""
        self.logger.debug(f"Validating instance info: {instance_info}")
        if not instance_info or len(instance_info) != 4:
            self.logger.error(f"Invalid instance info length: {len(instance_info) if instance_info else 0}, expected 4")
            return False
            
        chrome_instance_path, profile, global_history_excel_path,ld_name  = instance_info
        
        # Check required parameters
        if not chrome_instance_path:
            self.logger.error("Skipping task: Missing Chrome instance path")
            return False
            
        if not profile:
            self.logger.error("Skipping task: Missing profile information")
            return False
            
        # Global history Excel path is optional, but log if missing
        if not global_history_excel_path:
            self.logger.warning("Warning: Global history Excel path is missing")
            
        self.logger.info(f"Valid instance info: {chrome_instance_path}, {profile}")
        return True
    
    def collect_tasks_from_json_for_download(self) -> queue.Queue:
        """Collect tasks from the JSON file and populate the main queue."""
        self.logger.info("Collecting download tasks from JSON configuration")
        try:
            self.logger.debug(f"Reading configuration from: {self.page_manager_path}")
            with open(self.page_manager_path, mode="r", encoding="utf-8") as file:
                geni_data = json.load(file)
                
            self.logger.info(f"Processing {len(geni_data)} ID entries")
            ids_processed = 0
            ids_with_tasks = 0
            total_tasks = 0
            
            if self.is_global_upload_enable:
                # Process only those entries where "Upload" is True
                for id_key, id_info in geni_data.items():

                    Ld_name = id_info.get("Ld_name","")
                    id_name = id_info.get("id_name","")
                    self.logger.debug(f"Processing ID: {id_key}")
                    ids_processed += 1

                    if id_info.get("Upload") is not True:
                        self.logger.debug(f"Skipping ID {id_key}: Upload not enabled")
                        continue

                    chrome_instance_path = id_info.get("chrome_instance_path", "")
                    global_history_excel_path = ""

                    # Check if chrome_instance_path is available
                    if not chrome_instance_path:
                        self.logger.warning(f"Skipping ID {id_key}: Missing Chrome instance path")
                        continue
                    
                    # Extract global history path if available
                    id_info_dict = id_info.get("ID_info", {})
                    configure_download_dict = id_info_dict.get("configure_download_bonus_edits_video_edits", {})
                    download_config_dict = configure_download_dict.get("Download Configurations", {})
                    global_history_excel_path = download_config_dict.get("Save downloaded video history", "")

                    # Get auto download setting
                    is_auto_download = configure_download_dict.get("auto_download", False)
                    self.logger.debug(f"ID {id_key} auto download: {is_auto_download}")

                    # Setup for download configurations
                    instance_info = (chrome_instance_path, r"Profile 1", global_history_excel_path,Ld_name)
                    download_profile_config_list = [
                        [instance_info],  # Instance info
                        []  # Content download configurations
                    ]

                    # Get upload types from ID info
                    upload_types = id_info_dict.get("set_upload_types", {})
                    reels_upload = upload_types.get("reels_upload", False)
                    video_upload = upload_types.get("video_upload", False)
                    image_upload = upload_types.get("image_upload", False)
                    story_upload = upload_types.get("story_upload", False)

                    self.logger.debug(f"ID {id_key} upload types - Reels: {reels_upload}, Video: {video_upload}, "
                                     f"Image: {image_upload}, Story: {story_upload}")

                    # Process ID-level content configurations
                    content_types = {
                        "reel": {
                            "config_key": "reels_config", 
                            "upload_key": "reels_upload", 
                            "enabled": reels_upload
                        },
                        "video": {
                            "config_key": "videos_config", 
                            "upload_key": "video_upload", 
                            "enabled": video_upload
                        },
                        "image": {
                            "config_key": "image_config", 
                            "upload_key": "image_upload", 
                            "enabled": image_upload
                        },
                        "story": {
                            "config_key": "story_config", 
                            "upload_key": "story_upload", 
                            "enabled": story_upload
                        }
                    }

                    # Process ID-level content
                    for content_type, type_info in content_types.items():
                        content_config = id_info_dict.get(type_info["config_key"], {})
                        upload_enabled = type_info["enabled"]

                        self.logger.debug(f"Processing ID {id_key} {content_type} configuration")
                        config_tuple = self.process_content_type_config(
                            content_config, 
                            content_type, 
                            upload_enabled, 
                            is_auto_download
                        )
                        
                        # Validate config before adding to the list
                        if config_tuple:
                            config_tuple_f = config_tuple + (self.clean_name(id_name),)
                            if self.is_valid_download_config(config_tuple_f):
                                self.logger.info(f"Added valid {content_type} download task for ID {id_key}")

                                download_profile_config_list[1].append(config_tuple_f) 

                    # Process page-level information
                    page_info_dict = id_info.get("pages_information", {})
                    self.logger.debug(f"Processing {len(page_info_dict)} pages for ID {id_key}")

                    for page_key, page_info in page_info_dict.items():
                        self.logger.debug(f"Processing page: {page_key}")

                        page_name = page_info.get("Page_Name","")
                        # Get page upload types
                        page_upload_types = page_info.get("set_upload_types", {})
                        page_reels_upload = page_upload_types.get("reels_upload", False)
                        page_video_upload = page_upload_types.get("video_upload", False)
                        page_image_upload = page_upload_types.get("image_upload", False)
                        page_story_upload = page_upload_types.get("story_upload", False)

                        self.logger.debug(f"Page {page_key} upload types - Reels: {page_reels_upload}, Video: {page_video_upload}, "
                                         f"Image: {page_image_upload}, Story: {page_story_upload}")

                        # Get page auto download setting
                        page_config_dict = page_info.get("configure_download_bonus_edits_video_edits", {})
                        page_is_auto_download = page_config_dict.get("auto_download", False)
                        self.logger.debug(f"Page {page_key} auto download: {page_is_auto_download}")

                        # Configure content types for page
                        page_content_types = {
                            "reel": {
                                "config_key": "reels_config", 
                                "upload_key": "reels_upload", 
                                "enabled": page_reels_upload
                            },
                            "video": {
                                "config_key": "videos_config", 
                                "upload_key": "video_upload", 
                                "enabled": page_video_upload
                            },
                            "image": {
                                "config_key": "image_config", 
                                "upload_key": "image_upload", 
                                "enabled": page_image_upload
                            },
                            "story": {
                                "config_key": "story_config", 
                                "upload_key": "story_upload", 
                                "enabled": page_story_upload
                            }
                        }

                        # Process page-level content
                        for content_type, type_info in page_content_types.items():
                            content_config = page_info.get(type_info["config_key"], {})
                            upload_enabled = type_info["enabled"]

                            self.logger.debug(f"Processing page {page_key} {content_type} configuration")
                            config_tuple = self.process_content_type_config(
                                content_config, 
                                content_type, 
                                upload_enabled, 
                                page_is_auto_download
                            )

                            if config_tuple:
                                config_tuple_f = config_tuple + (self.clean_name(page_name),)
                                # Validate config before adding to the list
                                if self.is_valid_download_config(config_tuple_f):
                                    self.logger.info(f"Added valid {content_type} download task for page {page_key}")

                                    download_profile_config_list[1].append(config_tuple_f) 

                    # Only add to queue if there are valid download tasks and instance info
                    if download_profile_config_list[1] and self.is_valid_instance_info(instance_info):
                        ids_with_tasks += 1
                        total_tasks += len(download_profile_config_list[1])
                        self.logger.info(f"Adding {len(download_profile_config_list[1])} tasks to queue for ID {id_key}")
                        self.main_queue.put(download_profile_config_list)
                    else:
                        self.logger.warning(f"Skipping task for ID {id_key}: No valid download tasks or instance info")
            
            self.logger.info(f"Task collection summary: {ids_processed} IDs processed, {ids_with_tasks} IDs with tasks, {total_tasks} total tasks")
            return self.main_queue
        except FileNotFoundError:
            self.logger.exception(f"File not found: {self.page_manager_path}")
        except json.JSONDecodeError as e:
            self.logger.exception(f"Error parsing JSON file: {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error in collect_tasks_from_json_for_download: {e}")
            
        self.logger.warning("Returning empty queue due to errors")
        return self.main_queue

# Example usage
if __name__ == "__main__":
    collector = DownloaderTaskCollector()
    task_queue = collector.collect_tasks_from_json_for_download()
    
    # Print queue contents
    collector.logger.info(f"Queue size: {task_queue.qsize()}")
    tasks_processed = 0
    
    while not task_queue.empty():
        tasks_processed += 1
        task = task_queue.get()
        collector.logger.info(f"Task {tasks_processed} - Instance info: {task[0]}")
        collector.logger.info(f"Task {tasks_processed} - Download tasks: {len(task[1])}")
        for i, download_task in enumerate(task[1], 1):
            collector.logger.info(f"Task {tasks_processed}.{i} - {download_task}")
    
    collector.logger.info("All tasks processed")