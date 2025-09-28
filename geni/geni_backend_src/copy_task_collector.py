import json
import os
import re
import random
import queue
import subprocess
from subprocess import CREATE_NO_WINDOW
import sys
import fnmatch
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
from geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten

# Configure logging
def setup_logger():
    """Configure and return a logger with file and console handlers."""
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a unique log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"reels_copy_{timestamp}.log")
    
    # Configure logger
    logger = logging.getLogger("ReelsCopyTaskCollector")
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

class CopyTaskCollector:
    """Collects and manages tasks for copying content from download folders to LDPlayer folders."""
    
    def __init__(self):
        self.logger = setup_logger()
        self.logger.info("Initializing ReelsCopyTaskCollector")
        self.geni_setting_json_path = r"User_Data\Devices_Setting.json"
        self.geni_page_manager_path = r"User_Data\Page_manager.json"

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
        self.logger.debug(f"Set geni_page_manager_path: {self.geni_page_manager_path}")

    def get_ld_player_path(self):
        """Get LDPlayer path from settings JSON file."""
        try:
            self.logger.debug(f"Reading LDPlayer path from: {self.geni_setting_json_path}")
            with open(self.geni_setting_json_path, mode='r', encoding="utf-8") as f:
                data = json.load(f)

            locations_dict = data.get("Locations", {})
            self.ld_player_path = locations_dict.get("LD Location", None)
            self.logger.info(f"LDPlayer path: {self.ld_player_path}")
        except Exception as e:
            self.logger.exception(f"Error getting LDPlayer path: {e}")


    def get_ld_list(self, ld_console_folder_path: str) -> List[List[str]]:
        """Get list of LDPlayer instances."""
        self.logger.info(f"Getting LDPlayer list from: {ld_console_folder_path}")
        ld_list = []
        
        if not ld_console_folder_path or not os.path.exists(ld_console_folder_path):
            self.logger.error(f"LDPlayer folder not found: {ld_console_folder_path}")
            return ld_list
        
        try:
            cmd = [os.path.join(ld_console_folder_path, "ldconsole.exe"), "list2"]
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
        except subprocess.CalledProcessError as e:
            self.logger.exception(f"Error while getting the list of LDPlayer: {e}")
            self.logger.error(f"Error output: {e.output.decode() if hasattr(e, 'output') else 'No output'}")
        except Exception as e:
            self.logger.exception(f"Unexpected error in get_ld_list: {e}")
        
        return ld_list

    def check_files_in_folder(self, 
                             folder_path: str, 
                             extensions: List[str], 
                             num_of_files: int = 1) -> bool:
        """Check if folder contains minimum number of files with specified extensions."""
        self.logger.info(f"Checking files in folder: {folder_path}")
        self.logger.debug(f"Looking for extensions: {extensions}, required count: {num_of_files}")
        
        if not folder_path or not os.path.exists(folder_path):
            self.logger.error(f"Folder not found: {folder_path}")
            return False
        
        try:
            files_found = 0
            file_paths = []
            
            for root, dirs, files in os.walk(folder_path):
                for extension in extensions:
                    for filename in fnmatch.filter(files, extension):
                        file_path = os.path.join(root, filename)
                        files_found += 1
                        file_paths.append(file_path)
                        self.logger.debug(f"Found file: {file_path}")
                        
                        if files_found >= num_of_files:
                            self.logger.info(f"Found {files_found} files (requested: {num_of_files})")
                            return True
            
            self.logger.warning(f"Found only {files_found} files (requested: {num_of_files})")
            if files_found == 0:
                self.logger.warning("No matching files found")
                
            return files_found >= num_of_files
        except Exception as e:
            self.logger.exception(f"Error checking files in folder: {e}")
            return False

    def check_video_available_in_folder(self, folder_path: str, num_of_videos: int = 1) -> bool:
        """Check if folder contains minimum number of video files."""
        self.logger.info(f"Checking for {num_of_videos} videos in folder: {folder_path}")
        video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv', '*.wmv']
        return self.check_files_in_folder(folder_path, video_extensions, num_of_videos)

    def check_image_available_in_folder(self, folder_path: str, num_of_images: int = 1) -> bool:
        """Check if folder contains minimum number of image files."""
        self.logger.info(f"Checking for {num_of_images} images in folder: {folder_path}")
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp']
        return self.check_files_in_folder(folder_path, image_extensions, num_of_images)

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

    def give_video_count_compare_schudle_and_normal(self, schudle_count: int, normal_count: int) -> int:
        """Return the max of schedule count and normal count."""
        result = max(schudle_count, normal_count)
        self.logger.debug(f"Content count calculation: max({schudle_count}, {normal_count}) = {result}")
        return result

    def process_content_copy_config(self, 
                                   content_config: Dict, 
                                   content_type: str, 
                                   upload_enabled: bool) -> Optional[Tuple]:
        """Process configuration for a specific content type and determine if copy is needed."""
        self.logger.info(f"Processing {content_type} copy configuration")
        self.logger.debug(f"Upload enabled: {upload_enabled}")
        
        if not content_config:
            self.logger.warning(f"No configuration found for {content_type}")
            return None
        
        # Get folder paths
        download_folder = content_config.get("download_folder", "")
        ld_folder = content_config.get("ld_folder", "")
        
        if not download_folder or not ld_folder:
            self.logger.warning(f"Missing folder paths for {content_type} - download: {download_folder}, ld: {ld_folder}")
            return None
        
        # Calculate how many files to copy based on schedule
        num_to_copy = 1  # Default value
        schedule_config = content_config.get("schedule_config", {})
        is_schedule_enabled = schedule_config.get("schedule_enable", False)
        schedule_count = 0
        
        if is_schedule_enabled:
            schedule_time_dict = schedule_config.get("schedule_time", {})
            schedule_count = len(schedule_time_dict)
            self.logger.debug(f"Schedule enabled with {schedule_count} entries")
        
        num_to_copy = max(schedule_count, num_to_copy)
        self.logger.debug(f"Files to copy: {num_to_copy}")
        
        # Check if we need to copy (files exist in download folder but not in LD folder)
        check_func = self.check_video_available_in_folder if content_type in ["reel", "video","short","story"] else self.check_image_available_in_folder
        
        if upload_enabled and check_func(download_folder, num_to_copy) and not check_func(ld_folder, num_to_copy):
            self.logger.info(f"Need to copy {num_to_copy} {content_type}(s) from {download_folder} to {ld_folder}")
            return (download_folder, ld_folder, num_to_copy, content_type)
        
        return None

    def collect_tasks_from_json_for_copy(self) -> queue.Queue:
        """Collect tasks from the JSON file and populate the main queue."""
        self.logger.info("Collecting copy tasks from JSON configuration")

        try:
            self.logger.debug(f"Reading configuration from: {self.geni_page_manager_path}")
            with open(self.geni_page_manager_path, mode="r", encoding="utf-8") as file:
                geni_data = json.load(file)

            self.logger.info(f"Processing {len(geni_data)} ID entries")
            ids_processed = 0
            ids_with_tasks = 0

            
            for id_key, id_info in geni_data.items():
                self.logger.debug(f"Processing ID: {id_key}")
                ids_processed += 1

                upload_enabled = id_info.get("Upload", False)
                id_active_enabled = id_info.get("id_active_enable", False)
                id_active_dict = id_info.get("id_active",{})

               
                if not upload_enabled and not id_active_enabled:
                    self.logger.debug(f"Skipping ID {id_key}: Neither Upload nor id_active_enable is enabled")
                    continue
                
                self.logger.debug(f"ID {id_key} - Upload: {upload_enabled}, id_active_enable: {id_active_enabled}")

                copy_config_list = []

                if self.is_global_upload_enable:
                    # Process Upload logic if Upload is enabled
                    if upload_enabled:
                        self.logger.debug(f"Processing Upload collector logic for ID {id_key}")
                        upload_tasks = self.process_upload_collector_logic(id_key, id_info)
                        if upload_tasks:
                            copy_config_list.extend(upload_tasks)

                if self.is_global_id_active_enable:
                    # Process id_active logic if id_active_enable is enabled
                    if id_active_enabled:
                        self.logger.debug(f"Processing id_active collector logic for ID {id_key}")
                        id_active_tasks = self.process_id_active_collector_logic(id_key, id_active_dict)
                        if id_active_tasks:
                            copy_config_list.extend(id_active_tasks)

                # Add tasks to the queue if any were found
                if copy_config_list:
                    ids_with_tasks += 1
                    self.logger.info(f"Adding {len(copy_config_list)} copy tasks to queue for ID {id_key}")
                    self.main_queue.put(copy_config_list)

            self.logger.info(f"Task collection summary: {ids_processed} IDs processed, {ids_with_tasks} IDs with tasks")
            return self.main_queue
        except FileNotFoundError:
            self.logger.exception(f"File not found: {self.geni_page_manager_path}")
        except json.JSONDecodeError as e:
            self.logger.exception(f"Error parsing JSON file: {e}")
        except Exception as e:
            self.logger.exception(f"Unexpected error in collect_tasks_from_json_for_copy: {e}")

        self.logger.warning("Returning empty queue due to errors")
        return self.main_queue

    def process_upload_collector_logic(self, id_key, id_info):
        """Process upload collector logic for a given ID."""
        copy_config_list = []

        # Get ID info
        id_info_dict = id_info.get("ID_info", {})
        upload_types = id_info_dict.get("set_upload_types", {})

        # Get upload settings
        reels_upload = upload_types.get("reels_upload", False)
        video_upload = upload_types.get("video_upload", False)
        image_upload = upload_types.get("image_upload", False)
        story_upload = upload_types.get("story_upload", False)

        self.logger.debug(f"ID {id_key} upload settings - Reels: {reels_upload}, Video: {video_upload}, "
                         f"Image: {image_upload}, Story: {story_upload}")

        # Process content types for ID level
        content_types = {
            "reel": {
                "config_key": "reels_config",
                "upload_enabled": reels_upload
            },
            "video": {
                "config_key": "videos_config",
                "upload_enabled": video_upload
            },
            "image": {
                "config_key": "image_config",
                "upload_enabled": image_upload
            },
            "story": {
                "config_key": "story_config",
                "upload_enabled": story_upload
            }
        }

        # Process each content type at ID level
        for content_type, type_info in content_types.items():
            content_config = id_info_dict.get(type_info["config_key"], {})
            upload_enabled = type_info["upload_enabled"]

            self.logger.debug(f"Processing ID {id_key} {content_type} configuration")
            copy_tuple = self.process_content_copy_config(
                content_config,
                content_type,
                upload_enabled
            )

            if copy_tuple:
                self.logger.info(f"Added {content_type} copy task for ID {id_key}")
                copy_config_list.append(copy_tuple)

        # Process page-level information
        page_info_dict = id_info.get("pages_information", {})
        self.logger.debug(f"Processing {len(page_info_dict)} pages for ID {id_key}")

        for page_key, page_info in page_info_dict.items():
            page_name = page_info.get("Page_Name", "")
            self.logger.debug(f"Processing page: {page_name} ({page_key})")

            # Get page upload settings
            page_upload_types = page_info.get("set_upload_types", {})
            page_reels_upload = page_upload_types.get("reels_upload", False)
            page_video_upload = page_upload_types.get("video_upload", False)
            page_image_upload = page_upload_types.get("image_upload", False)
            page_story_upload = page_upload_types.get("story_upload", False)

            self.logger.debug(f"Page {page_name} upload settings - Reels: {page_reels_upload}, "
                             f"Video: {page_video_upload}, Image: {page_image_upload}, "
                             f"Story: {page_story_upload}")

            # Process page-level content types
            page_content_types = {
                "reel": {
                    "config_key": "reels_config",
                    "upload_enabled": page_reels_upload
                },
                "video": {
                    "config_key": "videos_config",
                    "upload_enabled": page_video_upload
                },
                "image": {
                    "config_key": "image_config",
                    "upload_enabled": page_image_upload
                },
                "story": {
                    "config_key": "story_config",
                    "upload_enabled": page_story_upload
                }
            }

            # Process each content type at page level
            for content_type, type_info in page_content_types.items():
                content_config = page_info.get(type_info["config_key"], {})
                upload_enabled = type_info["upload_enabled"]

                self.logger.debug(f"Processing page {page_name} {content_type} configuration")
                copy_tuple = self.process_content_copy_config(
                    content_config,
                    content_type,
                    upload_enabled
                )

                if copy_tuple:
                    self.logger.info(f"Added {content_type} copy task for page {page_name}")
                    copy_config_list.append(copy_tuple)

        return copy_config_list

    def process_id_active_collector_logic(self, id_key, id_active_dict):
        """Process id_active collector logic for a given ID."""
        copy_config_list = []

        self.logger.debug(f"Processing id_active collector logic for ID {id_key}")

        post_photo_config = id_active_dict.get("post_photo",{})
        is_post_photo_enable = post_photo_config.get("post_photo_enable",False)

        checkin_post_config = id_active_dict.get("post_checkin",{})
        is_checkin_post_enable = checkin_post_config.get("post_checkin_enable",False)

        story_post_config = id_active_dict.get("create_story",{})
        is_story_post_enable = story_post_config.get("create_story_enable",False)

        if is_post_photo_enable:
            post_photo_config = post_photo_config.get("post_photo_config",{})
            download_folder = post_photo_config.get("post_photo_download_folder","")
            ld_folder = post_photo_config.get("post_photo_ld_folder","")

            copy_config_list.append((download_folder,ld_folder,1,"image"))

        if is_checkin_post_enable:
            checkin_config = checkin_post_config.get("post_checkin_config",{})
            checkin_donwload_folder = checkin_config.get("post_checkin_photo_download_folder","")
            checkin_ld_folder = checkin_config.get("post_checkin_ld_photo_folder","")

            copy_config_list.append((checkin_donwload_folder,checkin_ld_folder,1,"image"))

        if is_story_post_enable:
            create_story_config = story_post_config.get("create_story_config",{})
            create_story_download_folder = create_story_config.get("create_story_video_download_folder","")
            create_story_ld_folder = create_story_config.get("create_story_video_folder","")

            copy_config_list.append((create_story_download_folder,create_story_ld_folder,1,"video"))


        return copy_config_list


    def get_next_task(self) -> Optional[List]:
        """Get the next task from the main queue."""
        if self.main_queue.empty():
            self.logger.warning("No tasks available in queue")
            return None
        
        task = self.main_queue.get()
        self.logger.info(f"Retrieved task with {len(task)} copy operations")
        return task

    def execute_tasks(self, callback=None):
        """
        Execute tasks from the main queue.
        
        Args:
            callback: Optional function to call after each task is executed.
        """
        if self.main_queue.empty():
            self.logger.warning("No tasks to execute")
            return

        tasks_completed = 0
        while not self.main_queue.empty():
            copy_config_list = self.main_queue.get()
            if not copy_config_list:
                continue
            
            for task_idx, copy_tuple in enumerate(copy_config_list, 1):
                try:
                    if len(copy_tuple) != 4:
                        self.logger.error(f"Invalid copy tuple format: {copy_tuple}")
                        continue
                    
                    src_folder, dst_folder, num_files, content_type = copy_tuple
                    self.logger.info(f"Executing copy task {tasks_completed + 1}.{task_idx}: "
                                    f"Copy {num_files} {content_type}(s) from {src_folder} to {dst_folder}")
                    
                    # Here you would implement the actual file copy operation
                    # For example: self._copy_files(src_folder, dst_folder, num_files, content_type)
                    
                    if callback:
                        callback(copy_tuple)
                except Exception as e:
                    self.logger.exception(f"Error executing copy task: {e}")
            
            tasks_completed += 1
        
        self.logger.info(f"All tasks completed: {tasks_completed} task groups processed")


# Example usage:
if __name__ == "__main__":
    collector = CopyTaskCollector()
    task_queue = collector.collect_tasks_from_json_for_copy()
    
    if task_queue.empty():
        collector.logger.warning("No copy tasks available")
    else:
        collector.logger.info(f"Queue size: {task_queue.qsize()}")
        tasks_processed = 0
        
        while not task_queue.empty():
            tasks_processed += 1
            task_list = task_queue.get()
            collector.logger.info(f"Task group {tasks_processed} - Copy tasks: {len(task_list)}")
            
            for i, copy_task in enumerate(task_list, 1):
                collector.logger.info(f"Task {tasks_processed}.{i} - {copy_task}")
        
        collector.logger.info("All tasks processed")