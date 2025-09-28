import json
import os
import re
import random
import queue
import subprocess
from subprocess import CREATE_NO_WINDOW
import sys
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
    log_file = os.path.join(log_dir, f"task_collector_{timestamp}.log")
    
    # Configure logger
    logger = logging.getLogger("TaskCollector")
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

class TaskCollector:
    def __init__(self):
        self.logger = setup_logger()
        self.logger.info("Initializing TaskCollector")
        self.geni_setting_json_path = r"User_Data\Devices_Setting.json"
        self.page_manager_path = r"User_Data\Page_manager.json"
        self.ld_player_path, self.geni_data_path = self.open_data_paths()
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
        self.logger.debug(f"LD Player Path: {self.ld_player_path}")
        self.logger.debug(f"Geni Data Path: {self.geni_data_path}")

    def open_data_paths(self):
        """Read settings and return paths to LD player and Geni data."""
        self.logger.info("Reading data paths from settings")
        try:
            with open(self.geni_setting_json_path, mode='r', encoding="utf-8") as file:
                geni_setting = json.load(file)

            ld_player_path = geni_setting["Locations"].get("LD Location", "")
            geni_data_path = geni_setting["Locations"].get("Geni Data", "")

            # If geni_data_path is empty, use the default file.
            if not geni_data_path:
                self.logger.debug("Using default page manager path")
                main_geni_data_path = self.page_manager_path
            else:
                # Check if the provided path is a directory.
                if os.path.isdir(geni_data_path):
                    # Append the default filename to the directory.
                    main_geni_data_path = os.path.join(geni_data_path, "Page_manager.json")
                    self.logger.debug(f"Using path: {main_geni_data_path}")
                else:
                    main_geni_data_path = geni_data_path
                    self.logger.debug(f"Using provided file path: {main_geni_data_path}")

            return (ld_player_path, main_geni_data_path)
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
            return ("", self.page_manager_path)
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing settings JSON: {e}")
            return ("", self.page_manager_path)
        except Exception as e:
            self.logger.error(f"Unexpected error reading data paths: {e}")
            return ("", self.page_manager_path)

    def get_video_captions(self, from_where_to_get_captions, path_of_video_folder, path_of_txt_file, text_box_dic, text_random=False, num_of_caption=1):
            """Get captions based on specified source."""
            self.logger.info(f"Getting video captions from source: {from_where_to_get_captions}")
            captions = []
    
            try:
                if from_where_to_get_captions == "From Original Video":
                    self.logger.debug(f"Looking for video files in: {path_of_video_folder}")
                    files = os.listdir(path_of_video_folder)
                    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
                    video_files = [f for f in files if f.lower().endswith(video_extensions)]
    
                    # Get file names (without extensions) for the requested number of videos
                    for i in range(min(num_of_caption, len(video_files))):
                        file_name = os.path.splitext(video_files[i])[0]
                        captions.append(file_name)
                        self.logger.debug(f"Added caption from video: {file_name}")
    
                    # If we don't have enough videos, repeat the last one to meet the requested number
                    while len(captions) < num_of_caption and captions:
                        captions.append(captions[-1])
                        self.logger.debug("Repeated last caption to meet requested number")
    
                elif from_where_to_get_captions =="From Original Photo":
    
                    self.logger.debug(f"Looking for Photos files in: {path_of_video_folder}")
                    files = os.listdir(path_of_video_folder)
                    video_extensions = ('.png', '.jpg', '.jpeg')
                    video_files = [f for f in files if f.lower().endswith(video_extensions)]
    
                    # Get file names (without extensions) for the requested number of videos
                    for i in range(min(num_of_caption, len(video_files))):
                        file_name = os.path.splitext(video_files[i])[0]
                        captions.append(file_name)
                        self.logger.debug(f"Added caption from video: {file_name}")
    
                    # If we don't have enough videos, repeat the last one to meet the requested number
                    while len(captions) < num_of_caption and captions:
                        captions.append(captions[-1])
                        self.logger.debug("Repeated last caption to meet requested number")
    
    
                elif from_where_to_get_captions == "From Text Box":
                    text_content = str(text_box_dic)
                    self.logger.debug(f"Using text box content: {text_content[:50]}...")
                    # Repeat the same text for each caption requested
                    for _ in range(num_of_caption):
                        captions.append(text_content)
    
                elif from_where_to_get_captions == "From text file":
                    try:
                        self.logger.debug(f"Reading captions from text file: {path_of_txt_file}")
                        
                        # Check if file exists
                        if not os.path.exists(path_of_txt_file):
                            self.logger.error(f"Caption file not found: {path_of_txt_file}")
                            raise FileNotFoundError(f"Caption file not found: {path_of_txt_file}")
                        
                        with open(path_of_txt_file, mode="r", encoding="utf-8") as file:
                            content = file.read()
    
                        if not content.strip():
                            self.logger.warning("Caption file is empty")
                            return captions
    
                        # Split content by blank lines into blocks
                        blocks = re.split(r'\n\s*\n', content.strip())
                        blocks = [block.strip() for block in blocks if block.strip()]
                        
                        if not blocks:
                            self.logger.warning("No valid caption blocks found in file")
                            return captions
                        
                        self.logger.debug(f"Found {len(blocks)} caption blocks in file")
    
                        if text_random:
                            self.logger.debug("Using random selection mode")
                            # Shuffle the blocks first for truly random selection
                            shuffled_blocks = blocks.copy()
                            random.shuffle(shuffled_blocks)
                            self.logger.debug("Shuffled caption blocks for random selection")
                            
                            # Get random blocks up to the number requested
                            for i in range(num_of_caption):
                                # Use modulo to cycle through shuffled blocks if we need more than available
                                block_index = i % len(shuffled_blocks)
                                selected_block = shuffled_blocks[block_index]
                                captions.append(selected_block)
                                self.logger.debug(f"Added random caption {i+1}: {selected_block[:50]}...")
                        else:
                            self.logger.debug("Using sequential selection mode")
                            # Get sequential blocks up to the number requested
                            available_blocks = min(num_of_caption, len(blocks))
                            
                            for i in range(available_blocks):
                                captions.append(blocks[i])
                                self.logger.debug(f"Added sequential caption {i+1}: {blocks[i][:50]}...")
    
                            # If we need more captions than available blocks, cycle through them
                            if len(captions) < num_of_caption:
                                self.logger.debug(f"Need {num_of_caption - len(captions)} more captions, cycling through available blocks")
                                remaining_needed = num_of_caption - len(captions)
                                
                                for i in range(remaining_needed):
                                    block_index = i % len(blocks)
                                    captions.append(blocks[block_index])
                                    self.logger.debug(f"Added cycled caption: {blocks[block_index][:50]}...")
    
                    except FileNotFoundError as e:
                        self.logger.error(f"File not found: {e}")
                    except UnicodeDecodeError as e:
                        self.logger.error(f"Error reading file encoding: {e}")
                    except Exception as e:
                        self.logger.error(f"Error opening txt file: {e}")
                else:
                    self.logger.warning(f"Unknown caption source: {from_where_to_get_captions}")
    
               
                if not captions:
                    self.logger.warning("No captions found, using empty strings")
                    captions = [""] * num_of_caption
            except Exception as e:
                self.logger.error(f"Error in get_video_captions: {e}")
                captions = [""] * num_of_caption
    
            self.logger.info(f"Returning {len(captions)} captions")
            return captions
    
    

    def get_ld_list(self, ld_console_folder_path):
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
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT,creationflags=CREATE_NO_WINDOW,shell=True)
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
            self.logger.error(f"Error while getting the list of LDPlayer: {e}")
            self.logger.error(f"Error output: {e.output.decode() if hasattr(e, 'output') else 'No output'}")
        except Exception as e:
            self.logger.error(f"Unexpected error in get_ld_list: {e}")
        
        return []

    def ld_inst_adb_serial_by_name(self, ld_player_name):
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

        ld_instance_idx = None
        for ld in ld_instance_list:
            ld_idx, ld_name = ld
            if ld_player_name == ld_name:
                ld_instance_idx = int(ld_idx)
                self.logger.debug(f"Found LDPlayer instance index: {ld_instance_idx}")
                break
                
        if ld_instance_idx is None:
            self.logger.error(f"LDPlayer with name '{ld_player_name}' not found")
            return None

        base_port = 5554  # Base port for emulator instances
        adb_serial = f"emulator-{base_port + ld_instance_idx * 2}"
        self.logger.info(f"ADB serial for '{ld_player_name}': {adb_serial}")
        return adb_serial
    
    def count_schedule_entries(self, data):
        """Count the number of dictionary entries in the schedule_time object."""
        self.logger.debug("Counting schedule entries")
        if not data or not isinstance(data, dict) or 'schedule_time' not in data:
            self.logger.debug("No schedule_time data found")
            return 0
            
        schedule_time = data.get('schedule_time', {})
        count = len(schedule_time)
        self.logger.debug(f"Found {count} schedule entries")
        return count
    
    def give_video_count_compare_schudle_and_normal(self, schudle_count, normal_count):
        """Return the max of schedule count and normal count."""
        result = max(schudle_count, normal_count)
        self.logger.debug(f"Content count calculation: max({schudle_count}, {normal_count}) = {result}")
        return result
    
    def convert_schedule_time(self, schedule_time):
        """
        Convert schedule_time dictionary into a list of tuples.

        For each entry in schedule_time:
        - If day is "0", put None in the tuple
        - Add hour, minute, and ampm to the tuple

        Args:
            schedule_time (dict): Dictionary containing schedule time information

        Returns:
            list: List of tuples in format (day_value, hour, minute, ampm)
        """
        self.logger.debug("Converting schedule time dictionary to tuples")
        result = []

        try:
            for key, time_info in schedule_time.items():
                day_value = None if time_info["day"] == "0" else time_info["day"]
                hour = time_info["hour"]
                minute = time_info["minute"]
                ampm = time_info["ampm"]

                result.append((day_value, hour, minute, ampm))
                self.logger.debug(f"Added schedule time: {(day_value, hour, minute, ampm)}")
        except Exception as e:
            self.logger.error(f"Error converting schedule time: {e}")

        self.logger.debug(f"Converted {len(result)} schedule times")
        return result

    def check_media_available_in_folder(self, profile_name, folder, num_of_media=1, media_type="video"):
        """
        Check if a specific number of media files are available in the specified folder.

        Args:
            profile_name (str): Name of the profile for logging purposes
            folder (str): Path to the folder to check for media
            num_of_media (int): Minimum number of media required (default: 1)
            media_type (str): Type of media to check for ('video' or 'image')

        Returns:
            bool: True if at least num_of_media files are found, False otherwise
        """
        self.logger.info(f"Checking for {num_of_media} {media_type}(s) in folder: {folder} for profile: {profile_name}")
        
        if not folder:
            self.logger.error(f"No folder path provided for {profile_name}")
            return False
            
        if not os.path.exists(folder):
            self.logger.error(f"Folder not found for {profile_name}, folder path: {folder}")
            return False
            
        try:
            # Define extensions based on media type
            if media_type == "video":
                extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
            elif media_type == "image":
                extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            else:
                self.logger.error(f"Invalid media type: {media_type}")
                return False
                
            media_count = 0
            found_files = []

            for filename in os.listdir(folder):
                if filename.lower().endswith(extensions):
                    media_count += 1
                    found_files.append(filename)
                    
                    if media_count >= num_of_media:
                        self.logger.info(f"Found sufficient {media_type} files ({media_count}) for {profile_name}")
                        return True

            if media_count > 0:
                self.logger.warning(f"Only {media_count} {media_type}(s) available for {profile_name}, but {num_of_media} required.")
            else:
                self.logger.warning(f"No {media_type}s available for {profile_name} in folder: {folder}")

            return False

        except Exception as e:
            self.logger.error(f"Error checking {media_type} files in folder: {e}")
            return False

    def check_video_available_in_folder(self, profile_name, folder, num_of_video=1):
        """Check if a specific number of video files are available in the specified folder."""
        return self.check_media_available_in_folder(profile_name, folder, num_of_video, "video")
        
    def check_image_available_in_folder(self, profile_name, folder, num_of_image=1):
        """Check if a specific number of image files are available in the specified folder."""
        return self.check_media_available_in_folder(profile_name, folder, num_of_image, "image")

    def should_update_insight(self):
        """
        Reads the JSON file and compares the stored 'last_insights_updated' timestamp
        with the current datetime, returning True if the update delay is met.
        This method does not modify the JSON file.
        """
        self.logger.debug("Checking if insights should be updated")
        try:
            with open(self.geni_setting_json_path, mode="r", encoding="utf-8") as file:
                settings_data = json.load(file)

            # Get delay (in days) and last update time
            insight_update_delay_day = settings_data["Times Setting"].get("Update_insights_delay", 1)
            last_time_insight_updated = settings_data["Times Setting"].get("last_insights_updated", "")
            self.logger.debug(f"Update delay: {insight_update_delay_day} days, Last update: {last_time_insight_updated}")

            # If the timestamp is missing or empty, we assume an update is due.
            if not last_time_insight_updated:
                self.logger.info("No previous update timestamp found, update is due")
                return True

            try:
                last_updated_dt = datetime.strptime(last_time_insight_updated, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                self.logger.error(f"Invalid timestamp format: {e}")
                return False

            now = datetime.now()
            delta_days = (now - last_updated_dt).days
            should_update = delta_days >= insight_update_delay_day
            self.logger.info(f"Days since last update: {delta_days}, Should update: {should_update}")
            return should_update
        except Exception as e:
            self.logger.error(f"Error checking insight update status: {e}")
            return False

    def check_and_update_insight(self):
        """
        Reads the JSON file and validates the 'last_insights_updated' key.
        - If the key is missing or empty, updates it to today's datetime and returns False.
        - If the key is present but in an invalid format, updates it to today's datetime and returns False.
        - If the key is valid, compares it to the current datetime:
            - If the elapsed days are greater than or equal to the delay, updates the key and returns True.
            - Otherwise, returns False.
        """
        self.logger.debug("Checking and potentially updating insight timestamp")
        try:
            with open(self.geni_setting_json_path, mode="r", encoding="utf-8") as file: 
                settings_data = json.load(file)

            insight_update_delay_day = settings_data["Times Setting"].get("Update_insights_delay", 1)
            last_time_insight_updated = settings_data["Times Setting"].get("last_insights_updated", "")
            now = datetime.now()
            current_datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

            # Case: missing or empty key – update with current datetime and return False.
            if not last_time_insight_updated:
                self.logger.info("No previous update timestamp found, setting current time")
                settings_data["Times Setting"]["last_insights_updated"] = current_datetime_str
                with open(self.geni_setting_json_path, mode="w", encoding="utf-8") as file:
                    json.dump(settings_data, file, indent=4)
                return False

            try:
                last_updated_dt = datetime.strptime(last_time_insight_updated, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # If stored value is invalid, update with current datetime and return False.
                self.logger.warning(f"Invalid timestamp format: {last_time_insight_updated}, resetting")
                settings_data["Times Setting"]["last_insights_updated"] = current_datetime_str
                with open(self.geni_setting_json_path, mode="w", encoding="utf-8") as file:
                    json.dump(settings_data, file, indent=4)
                return False

            # Compare the current datetime with the stored datetime.
            delta_days = (now - last_updated_dt).days
            if delta_days >= insight_update_delay_day:
                self.logger.info(f"Update delay of {insight_update_delay_day} days met, updating timestamp")
                settings_data["Times Setting"]["last_insights_updated"] = current_datetime_str
                with open(self.geni_setting_json_path, mode="w", encoding="utf-8") as file:
                    json.dump(settings_data, file, indent=4)
                return True
            else:
                self.logger.info(f"Update delay not met ({delta_days}/{insight_update_delay_day} days)")
                return False
        except Exception as e:
            self.logger.error(f"Error checking and updating insight timestamp: {e}")
            return False

    def process_content_config(self, content_type, config_dict, profile_name, package_name,id_or_page="id"):
        """Process configuration for a specific content type (reels, videos, images, story)."""
        self.logger.info(f"Processing {content_type} configuration for {profile_name}")
        
        # Dictionary to store the results
        result = {
            'profile_list': [],
            'ld_folder_path':"",
            'captions_list': [],
            "captions_sources":"",
            'download_folder_path': "",
                                             #'schedule_time_list': [],
            'is_schedule_enable':False,
            'num_of_content':1,
            'is_group_sharing_enable':False,
            'group_list':"",
            'num_of_group_to_share':1,
            'ignore_name':False
        }

        if content_type == "story":
            result["story_type"] ="video"

        
        try:
            # No configuration for this content type
            if not config_dict:
                self.logger.warning(f"No {content_type} configuration found for {profile_name}")
                return result
                
            # Get folder path based on content type
            if content_type == "reels":
                download_folder_path = config_dict.get("download_folder", "")
                ld_folder = config_dict.get("ld_folder","")
            elif content_type == "videos":
                download_folder_path = config_dict.get("download_folder", "")
                ld_folder = config_dict.get("ld_folder","")
            elif content_type == "images":
                download_folder_path = config_dict.get("download_folder", "")
                ld_folder = config_dict.get("ld_folder","")
            elif content_type == "story":
                download_folder_path = config_dict.get("download_folder", "")
                ld_folder = config_dict.get("ld_folder","")
                story_type = config_dict.get("story_type","video")
            else:
                self.logger.error(f"Unknown content type: {content_type}")
                return result
                
            self.logger.debug(f"{content_type} folder path: {download_folder_path}")
            
            num_of_content = 1
            # Get number of video or image to upload 
            num_of_content_at_time = config_dict.get("num",1)

            # Get caption configuration
            captions_config = config_dict.get("captions", {})
            caption_source = captions_config.get("caption_from", "From Original Video")
            txt_file_path = captions_config.get("txt_file_path", "")
            txt_box_content = captions_config.get("caption_text_box", "")
            txt_random = captions_config.get("txt_random", False)
            
            # Get schedule configuration
            schedule_config = config_dict.get("schedule_config", {})
            is_schedule_enable = schedule_config.get("schedule_enable", False)
            schedule_time_dict = schedule_config.get("schedule_time", {})
            
            # Sharing config
            sharing_config = config_dict.get("group_sharing_config", {})
            is_group_sharing_enable = sharing_config.get("enable_sharing",False)
            group_list = sharing_config.get("groups_name","")
            num_of_group_to_share = sharing_config.get("num_of_share",1)
            ignore_names = sharing_config.get("ignore_name",False)

            
            
            # If schedule is enabled, adjust the number of content items
            result['is_schedule_enable'] = is_schedule_enable
            
            if is_schedule_enable:
                num_of_schedule = self.count_schedule_entries(schedule_time_dict)
                num_of_content = self.give_video_count_compare_schudle_and_normal(num_of_schedule, num_of_content)
                schedule_time_list = self.convert_schedule_time(schedule_time_dict)
                result['schedule_time_list'] = schedule_time_list
                self.logger.debug(f"Schedule enabled with {num_of_schedule} entries, total content needed: {num_of_content}")
            else:
                num_of_content = num_of_content_at_time
            
            # Check media availability based on content type
            media_available = False
            if content_type in ["reels", "videos","story"]:
                media_available = self.check_video_available_in_folder(profile_name, download_folder_path, num_of_content)
            elif content_type in ["images"]:
                media_available = self.check_image_available_in_folder(profile_name, download_folder_path, num_of_content)
                
            if media_available:
                # Get captions for the content
                captions = self.get_video_captions(
                    from_where_to_get_captions=caption_source,
                    path_of_video_folder=download_folder_path,
                    path_of_txt_file=txt_file_path,
                    text_box_dic=txt_box_content,
                    text_random=txt_random,
                    num_of_caption=num_of_content
                )
                
                # Add information to result
                result['profile_list'].append((profile_name, "id" if id_or_page == "id" else "page"))
                
                for c in captions:
                    result['captions_list'].append(c)
                    
                result['captions_sources'] = caption_source
                result['download_folder_path']=download_folder_path
                result['ld_folder_path'] =ld_folder
                result['num_of_content'] =num_of_content_at_time
                result['is_group_sharing_enable'] =is_group_sharing_enable
                result['group_list'] =group_list
                result['num_of_group_to_share'] =num_of_group_to_share
                result['ignore_name'] = ignore_names

                if content_type == "story":
                    result["story_type"] =story_type
                

                self.logger.info(f"Added {content_type} configuration for {profile_name}")
            else:
                self.logger.warning(f"Insufficient {content_type} media for {profile_name}, skipping")
                
        except Exception as e:
            self.logger.error(f"Error processing {content_type} configuration for {profile_name}: {e}")
            
        return result

    def process_id_active_data(self, id_active_dict, profile_name):
        """
        Process id_active dictionary and convert it into a standardized task dictionary format.

        Args:
            id_active_dict (dict): The id_active configuration dictionary
            profile_name (str): Name of the profile for logging and identification

        Returns:
            dict: Standardized task dictionary with all required configurations
        """
        self.logger.info(f"Processing ID active data for profile: {profile_name}")

        # Initialize the custom task dictionary with default values
        custom_task_dict = {
            "loops":{"num_of_loop":2,"loops_delay":3},
            "Photo_upload": {"enable": False, "profile_name": profile_name, "photo_caption": "","ld_folder":[]},
            "check_notifications": {"enable": False, "duration": 1},
            "confirm_friend_request": {"enable": False, "num_of_friends": 0},
            "add_friend": {"enable": False, "num_of_friends": 0},
            "check_msg_and_reply": {"enable": False, "duration": 0, "reply_text": []},
            "scroll_feed_and_activiy": {"enable": False, "duration": 0, "config_dict": {
                "like_post": {"enable": False, "weight": 0},
                "react_post": {"enable": False, "weight": 0},
                "comment_on_post": {"enable": False, "weight": 0, "caption": ""},
                "share_post_to_group": {"enable": False, "weight": 0, "group_list": []},
                "share_to_stroy": {"enable": False, "weight": 0}
            }},
            "scroll_reels_and_activiy": {"enable": False, "duration": 0, "config_dict": {
                "like_post": {"enable": False, "weight": 0},
                "comment_on_post": {"enable": False, "weight": 0, "caption": ""},
                "react_post": {"enable": False, "weight": 0},
                "share_post_to_group": {"enable": False, "weight": 0, "group_list": []},
                "share_to_stroy": {"enable": False, "weight": 0}
            }},
            "scroll_videos_and_activiy": {"enable": False, "duration": 0, "config_dict": {
                "like_post": {"enable": False, "weight": 0},
                "comment_on_post": {"enable": False, "weight": 0, "caption": ""},
                "react_post": {"enable": False, "weight": 0},
                "share_post_to_group": {"enable": False, "weight": 0, "group_list": []},
                "share_to_stroy": {"enable": False, "weight": 0}
            }},
            "post_checkin": {"enable": False, "profile_list": [], "video_captions": "", "checkin_location": [], "folders": [],"add_photo":False},
            "post_story":{"enable":False,"num_of_story":1,"profile_list":[],"video_captions":[],"folder":[]}
        }

        try:
            if not id_active_dict:
                self.logger.warning(f"No id_active data provided for {profile_name}")
                return custom_task_dict

            num_of_loops = id_active_dict.get("num_of_loop",1)
            loops_delay = id_active_dict.get("loop_delay",4)

            custom_task_dict["loops"]["num_of_loop"] = num_of_loops
            custom_task_dict["loops"]["loops_delay"] = loops_delay

            # Process scroll_reels_and_vid configuration
            scroll_reels_vid = id_active_dict.get("scroll_reels_and_vid", {})
            if scroll_reels_vid:
                self.logger.debug("Processing scroll_reels_and_vid configuration")

                # Process reels scrolling
                scroll_reels_enable = scroll_reels_vid.get("scroll_reels_enable", False)
                if scroll_reels_enable:
                    reels_min_min = scroll_reels_vid.get("scroll_reels_min_min", 1)
                    reels_max_min = scroll_reels_vid.get("scroll_reels_min_max", 2)
                    reels_duration = random.randint(reels_min_min, reels_max_min)

                    custom_task_dict["scroll_reels_and_activiy"]["enable"] = True
                    custom_task_dict["scroll_reels_and_activiy"]["duration"] = reels_duration

                    # Process reels activities
                    activity_config = scroll_reels_vid.get("activity", {})
                    self._process_activity_config(activity_config, custom_task_dict["scroll_reels_and_activiy"]["config_dict"])

                    self.logger.debug(f"Reels scrolling enabled with duration: {reels_duration} minutes")

                # Process videos scrolling
                scroll_vid_enable = scroll_reels_vid.get("scroll_vid_enable", False)
                if scroll_vid_enable:
                    vid_min_min = scroll_reels_vid.get("scroll_vid_min_min", 1)
                    vid_max_min = scroll_reels_vid.get("scroll_vid_min_max", 2)
                    vid_duration = random.randint(vid_min_min, vid_max_min)

                    custom_task_dict["scroll_videos_and_activiy"]["enable"] = True
                    custom_task_dict["scroll_videos_and_activiy"]["duration"] = vid_duration

                    # Process video activities (same as reels activities)
                    activity_config = scroll_reels_vid.get("activity", {})
                    self._process_activity_config(activity_config, custom_task_dict["scroll_videos_and_activiy"]["config_dict"])

                    self.logger.debug(f"Videos scrolling enabled with duration: {vid_duration} minutes")

            # Process scroll_feed configuration
            scroll_feed = id_active_dict.get("scroll_feed", {})
            if scroll_feed:
                self.logger.debug("Processing scroll_feed configuration")
                scroll_feed_enable = scroll_feed.get("scroll_feed_enable", False)

                if scroll_feed_enable:
                    feed_min_min = scroll_feed.get("scroll_feed_min_min", 1)
                    feed_max_min = scroll_feed.get("scroll_feed_max_min", 2)
                    feed_duration = random.randint(feed_min_min, feed_max_min)

                    custom_task_dict["scroll_feed_and_activiy"]["enable"] = True
                    custom_task_dict["scroll_feed_and_activiy"]["duration"] = feed_duration

                    # Process feed activities
                    activity_config = scroll_feed.get("activity", {})
                    self._process_activity_config(activity_config, custom_task_dict["scroll_feed_and_activiy"]["config_dict"])

                    self.logger.debug(f"Feed scrolling enabled with duration: {feed_duration} minutes")

            # Process check_msg configuration
            check_msg = id_active_dict.get("check_msg", {})
            if check_msg:
                self.logger.debug("Processing check_msg configuration")
                check_msg_enable = check_msg.get("check_msg_enable", False)

                if check_msg_enable:
                    msg_min_min = check_msg.get("check_msg_min_min", 3)
                    msg_max_min = check_msg.get("check_msg_max_min", 6)
                    msg_duration = random.randint(msg_min_min, msg_max_min)

                    custom_task_dict["check_msg_and_reply"]["enable"] = True
                    custom_task_dict["check_msg_and_reply"]["duration"] = msg_duration

                    # Process reply configuration
                    reply_msg_enable = check_msg.get("reply_msg_enable", False)
                    if reply_msg_enable:
                        reply_min_chat = check_msg.get("reply_msg_min_chat", 3)
                        reply_max_chat = check_msg.get("reply_msg_max_chat", 5)
                        num_replies = random.randint(reply_min_chat, reply_max_chat)

                        # Generate default reply texts
                        default_replies = ["Hello!", "How are you?", "Nice to meet you", "Thanks!", "Great!"]
                        custom_task_dict["check_msg_and_reply"]["reply_text"] = default_replies[:num_replies]

                    self.logger.debug(f"Message checking enabled with duration: {msg_duration} minutes")

            # Process add_and_confirm_friends configuration
            friends_config = id_active_dict.get("add_and_confirm_friends", {})
            if friends_config:
                self.logger.debug("Processing add_and_confirm_friends configuration")

                # Add friends
                add_friend_enable = friends_config.get("add_friend_enable", False)
                if add_friend_enable:
                    add_min_friends = friends_config.get("add_friend_min_frid", 1)
                    add_max_friends = friends_config.get("add_friend_max_frid", 6)
                    num_add_friends = random.randint(add_min_friends, add_max_friends)

                    custom_task_dict["add_friend"]["enable"] = True
                    custom_task_dict["add_friend"]["num_of_friends"] = num_add_friends

                    self.logger.debug(f"Add friends enabled: {num_add_friends} friends")

                # Confirm friends
                confirm_friend_enable = friends_config.get("confirm_friend_enable", False)
                if confirm_friend_enable:
                    confirm_min_friends = friends_config.get("confirm_friend_min_frid", 1)
                    confirm_max_friends = friends_config.get("confirm_friend_max_frid", 4)
                    num_confirm_friends = random.randint(confirm_min_friends, confirm_max_friends)

                    custom_task_dict["confirm_friend_request"]["enable"] = True
                    custom_task_dict["confirm_friend_request"]["num_of_friends"] = num_confirm_friends

                    self.logger.debug(f"Confirm friends enabled: {num_confirm_friends} friends")

            # Process post_photo configuration
            post_photo = id_active_dict.get("post_photo", {})
            if post_photo:
                self.logger.debug("Processing post_photo configuration")
                post_photo_enable = post_photo.get("post_photo_enable", False)
                num_of_post = post_photo.get("post_photo_num", 1)
                custom_task_dict["Photo_upload"]["profile_name"] = profile_name
                if post_photo_enable:

                    

                    # Get photo caption
                    photo_config = post_photo.get("post_photo_config", {})
                    ld_folder = photo_config.get("post_photo_download_folder", "")
                    caption_from = photo_config.get("post_photo_caption_from", "From Original Photo")
                    caption_text_box = photo_config.get("post_photo_caption_text_box", "")
                    caption_txt_path = photo_config.get("post_photo_caption_txt_path", "")
                    caption_txt_random = photo_config.get("post_photo_caption_txt_random", False)


                    # Get caption using existing method
                    is_media_ablaible_in_folder = self.check_media_available_in_folder(profile_name=profile_name,folder=ld_folder,num_of_media=num_of_post,media_type="image")

                    if is_media_ablaible_in_folder:
                        custom_task_dict["Photo_upload"]["enable"] = True
                    else:
                        custom_task_dict["Photo_upload"]["enable"] = False


                    
                    captions = self.get_video_captions(
                        from_where_to_get_captions=caption_from,
                        path_of_video_folder=ld_folder,
                        path_of_txt_file=caption_txt_path,
                        text_box_dic=caption_text_box,
                        text_random=caption_txt_random,
                        num_of_caption=num_of_post
                    )

                    custom_task_dict["Photo_upload"]["photo_caption"] = captions
                    custom_task_dict["Photo_upload"]["folder"]  = ld_folder
                    custom_task_dict["Photo_upload"]["caption_souce"]  = caption_from
                    custom_task_dict["Photo_upload"]["media_count"]  = num_of_post
                    self.logger.debug("Photo upload enabled")

            # Process post_checkin configuration
            post_checkin = id_active_dict.get("post_checkin", {})
            if post_checkin:
                self.logger.debug("Processing post_checkin configuration")

                checkin_enable = post_checkin.get("post_checkin_enable", False)
                
                checkin_config = post_checkin.get("post_checkin_config", {})
                download_folder = checkin_config.get("post_checkin_photo_download_folder", "")
                add_photo_to_checkin_post = checkin_config.get("add_photo_to_checkin_post", False)
                
                is_photo_avlaible_in_folder = self.check_media_available_in_folder(profile_name=profile_name,folder=download_folder,num_of_media=1,media_type="image")

                if add_photo_to_checkin_post:
                    if is_photo_avlaible_in_folder:
                        custom_task_dict["post_checkin"]["add_photo"] = True
                    else:
                        custom_task_dict["post_checkin"]["add_photo"] = False

                post_checin_loaction = post_checkin.get("post_checkin_location","")
                custom_task_dict["post_checkin"]["profile_list"] = profile_name

                if checkin_enable:
                    checkin_num = post_checkin.get("post_checkin_num", 1)
                    

                    custom_task_dict["post_checkin"]["enable"] = True
                     
                    # Get checkin captions
                    caption_from = checkin_config.get("post_checkin_caption_from", "From Original Photo")
                    caption_text_box = checkin_config.get("post_checkin_caption_text_box", "")
                    caption_txt_path = checkin_config.get("post_checkin_caption_txt_path", "")
                    caption_txt_random = checkin_config.get("post_checkin_caption_txt_random", False)

                    
                    captions = self.get_video_captions(
                        from_where_to_get_captions=caption_from,
                        path_of_video_folder=download_folder,
                        path_of_txt_file=caption_txt_path,
                        text_box_dic=caption_text_box,
                        text_random=caption_txt_random,
                        num_of_caption=checkin_num
                    )

                    f_caption = ""
                    if captions:
                        f_caption = captions[0]


                    custom_task_dict["post_checkin"]["video_captions"] = f_caption
                    custom_task_dict["post_checkin"]["caption_source"] = caption_from
                    custom_task_dict["post_checkin"]["folders"] = download_folder
                    custom_task_dict["post_checkin"]["checkin_location"] = post_checin_loaction
                    custom_task_dict["post_checkin"]["media_count"] = checkin_num

                    self.logger.debug(f"Post checkin enabled: {checkin_num} posts")

            # Process create_story configuration
            create_story = id_active_dict.get("create_story", {})

            if create_story:
                self.logger.debug("Processing create_story configuration")
                create_story_enable = create_story.get("create_story_enable", False)
                id_active_config = create_story.get("create_story_config",{})
                story_folder = id_active_config.get("create_story_video_download_folder","")

                custom_task_dict["post_story"]["profile_list"] = profile_name
                if create_story_enable:
                    self.logger.debug("Story creation enabled (handled separately)")
                    num_of_story = create_story.get("create_story_num",1)
                    

                    is_video_avlaible_in_folder = self.check_media_available_in_folder(profile_name=profile_name,folder=story_folder,num_of_media=num_of_story,media_type="video")

                    if is_video_avlaible_in_folder:
                        custom_task_dict["post_story"]["enable"] = True
                    else:
                        custom_task_dict["post_story"]["enable"] = False


                    custom_task_dict["post_story"]["num_of_story"] = num_of_story
                    story_caption_from = id_active_config.get("post_checkin_caption_from", "From Original Photo")
                    story_caption_text_box = id_active_config.get("post_checkin_caption_text_box", "")
                    story_caption_txt_path = id_active_config.get("post_checkin_caption_txt_path", "")
                    story_caption_txt_random = id_active_config.get("post_checkin_caption_txt_random", False)

                    
                    story_captions = self.get_video_captions(
                        from_where_to_get_captions=story_caption_from,
                        path_of_video_folder=story_folder,
                        path_of_txt_file=story_caption_txt_path,
                        text_box_dic=story_caption_text_box,
                        text_random=story_caption_txt_random,
                        num_of_caption=num_of_story
                    )

                    custom_task_dict["post_story"]["video_captions"] = story_captions
                    custom_task_dict["post_story"]["folder"] = story_folder
                    custom_task_dict["post_story"]["caption_souce"] = story_caption_from
                    custom_task_dict["post_story"]["media_cont"] = num_of_story

            # Process check_notification configuration
            check_notification = id_active_dict.get("check_notification", {})
            if check_notification:
                self.logger.debug("Processing check_notification configuration")
                check_notification_enable = check_notification.get("check_notification_enable", False)

                if check_notification_enable:
                    notif_min_min = check_notification.get("check_notification_min_min", 1)
                    notif_max_min = check_notification.get("check_notification_max_min", 1)
                    notif_duration = random.randint(notif_min_min, notif_max_min)

                    custom_task_dict["check_notifications"]["enable"] = True
                    custom_task_dict["check_notifications"]["duration"] = notif_duration

                    self.logger.debug(f"Check notifications enabled with duration: {notif_duration} minutes")

            self.logger.info(f"Successfully processed ID active data for {profile_name}")
            return custom_task_dict

        except Exception as e:
            self.logger.error(f"Error processing ID active data for {profile_name}: {e}")
            return custom_task_dict

    def _process_activity_config(self, activity_config, target_config_dict):
        """
        Helper method to process activity configuration for scrolling tasks.

        Args:
            activity_config (dict): Activity configuration from JSON
            target_config_dict (dict): Target configuration dictionary to update
        """
        self.logger.debug("Processing activity configuration")

        try:
            # Process like_post activity
            like_post = activity_config.get("like_post", {})
            if like_post.get("like_post_enable", False):
                target_config_dict["like_post"]["enable"] = True
                like_prob = like_post.get("like_post_prob", 1.0)
                target_config_dict["like_post"]["weight"] = int(like_prob * 3)  # Convert probability to weight

            # Process react_post activity
            react_post = activity_config.get("react_post", {})
            if react_post.get("react_post_enable", False):
                target_config_dict["react_post"]["enable"] = True
                react_prob = react_post.get("react_post_prob", 1.0)
                target_config_dict["react_post"]["weight"] = int(react_prob * 2)  # Convert probability to weight

            # Process comment_post activity
            comment_post = activity_config.get("comment_post", {})
            if comment_post.get("comment_post_enable", False):
                target_config_dict["comment_on_post"]["enable"] = True
                comment_prob = comment_post.get("comment_post_prob", 1.0)
                target_config_dict["comment_on_post"]["weight"] = int(comment_prob * 2)

                # Get comment text
                comment_config = comment_post.get("comment_config", {})
                comment_from = comment_config.get("comment_from", "From Text Box")
                comment_text_box = comment_config.get("comment_text_box", "")
                comment_txt_path = comment_config.get("comment_txt_path", "")
                comment_random = comment_config.get("comment_random", False)

                # Get comment caption using existing method
                if comment_from == "From Text Box" and comment_text_box:
                    target_config_dict["comment_on_post"]["caption"] = comment_text_box
                elif comment_from == "From text file" and comment_txt_path:
                    comments = self.get_video_captions(
                        from_where_to_get_captions=comment_from,
                        path_of_video_folder="",
                        path_of_txt_file=comment_txt_path,
                        text_box_dic="",
                        text_random=comment_random,
                        num_of_caption=1
                    )
                    target_config_dict["comment_on_post"]["caption"] = comments[0] if comments else "Great post!"
                else:
                    target_config_dict["comment_on_post"]["caption"] = "Great post!"

            # Process share_post_to_group activity
            share_group = activity_config.get("share_post_to_group", {})
            if share_group.get("share_post_to_group_enable", False):
                target_config_dict["share_post_to_group"]["enable"] = True
                share_group_prob = share_group.get("share_post_to_group_prob", 1.0)
                target_config_dict["share_post_to_group"]["weight"] = int(share_group_prob * 1)

                # Get group list
                share_config = share_group.get("share_post_to_group_config", {})
                group_text_box = share_config.get("share_post_to_group_text_box", "")
                if group_text_box:
                    group_list = [group.strip() for group in group_text_box.split(",") if group.strip()]
                    target_config_dict["share_post_to_group"]["group_list"] = group_list

            # Process share_post_to_story activity
            share_story = activity_config.get("share_post_to_story", {})
            if share_story.get("share_post_to_story_enable", False):
                target_config_dict["share_to_stroy"]["enable"] = True
                share_story_prob = share_story.get("share_post_to_story_prob", 1.0)
                target_config_dict["share_to_stroy"]["weight"] = int(share_story_prob * 1)

            self.logger.debug("Activity configuration processed successfully")

        except Exception as e:
            self.logger.error(f"Error processing activity configuration: {e}")


        
    def collect_tasks_from_json(self):
        """Collect tasks from the JSON file and populate the main queue."""
        self.logger.info("Collecting tasks from JSON configuration")
        try:
            with open(self.page_manager_path, mode="r", encoding="utf-8") as file:
                geni_data = json.load(file)

            self.logger.info(f"Processing {len(geni_data)} ID and Pages entries")
            ids_processed = 0
            ids_with_tasks = 0

            

            # Process entries based on Upload and id_active_enable flags
            for id_key, id_info in geni_data.items():
                ids_processed += 1
                self.logger.debug(f"Processing ID: {id_key}")
                all_profiles = []
                # Check both flags
                upload_enabled = id_info.get("Upload") is True
                id_active_enabled = id_info.get("id_active_enable") is True

                # Skip if neither flag is true
                if not upload_enabled and not id_active_enabled:
                    self.logger.debug(f"Skipping ID {id_key}: Neither Upload nor ID Active is enabled")
                    continue
                
                self.logger.debug(f"ID {id_key} - Upload: {upload_enabled}, ID Active: {id_active_enabled}")

                # Create an inner queue for tasks related to this ID.
                inner_queue = queue.Queue()
                id_information_idx = id_key
                id_name = id_info.get("id_name", "")
                upload_method = id_info.get("upload_method", "Without Apps Switch")
                package_name = id_info.get("package_name", "")
                ld_player_instance_name = id_info.get("Ld_name", "")
                main_folder_path = id_info.get("Main_folder_path", "")

                self.logger.debug(f"ID {id_key} details - Name: {id_name}, Package: {package_name}, LDPlayer: {ld_player_instance_name}")

                # Add current profile name into all profile list
                all_profiles.append(id_name)

                # Get ID info dictionary
                id_info_dict = id_info.get("ID_info", {})
                id_active_dict = id_info.get("id_active", {})
                if not id_info_dict and not id_active_dict:
                    self.logger.warning(f"No ID_info or id_active dictionary found for {id_key}, skipping")
                    continue
                
                # Main profile configuration dictionary - profile name as key
                profiles_config = {}
                tasks_added = False

                # Process Upload tasks if Upload is enabled
                if self.is_global_upload_enable and upload_enabled:
                    self.logger.info(f"Processing upload tasks for ID {id_key}")

                    # Get all upload type flags
                    upload_types = id_info_dict.get("set_upload_types", {})
                    reels_upload_enabled = upload_types.get("reels_upload", False)
                    videos_upload_enabled = upload_types.get("video_upload", False)
                    images_upload_enabled = upload_types.get("image_upload", False)
                    story_upload_enabled = upload_types.get("story_upload", False)

                    self.logger.debug(f"ID {id_key} upload types - Reels: {reels_upload_enabled}, Video: {videos_upload_enabled}, "
                                     f"Image: {images_upload_enabled}, Story: {story_upload_enabled}")

                    # Initialize ID profile configuration only if needed
                    id_profile_has_content = False
                    id_profile_config = {
                        'profile_type': 'id',
                        'insights_collector': False
                    }

                    # Process reels configuration
                    if reels_upload_enabled:
                        reels_config = id_info_dict.get("reels_config", {})
                        reels_result = self.process_content_config("reels", reels_config, id_name, package_name, id_or_page="id")
                        if reels_result and reels_result.get('profile_list'):
                            id_profile_config['reels_upload'] = reels_result
                            id_profile_has_content = True

                    # Process videos configuration
                    if videos_upload_enabled:
                        videos_config = id_info_dict.get("videos_config", {})
                        videos_result = self.process_content_config("videos", videos_config, id_name, package_name, id_or_page="id")
                        if videos_result and videos_result.get('profile_list'):
                            id_profile_config['videos_upload'] = videos_result
                            id_profile_has_content = True

                    # Process images configuration
                    if images_upload_enabled:
                        images_config = id_info_dict.get("image_config", {})
                        images_result = self.process_content_config("images", images_config, id_name, package_name, id_or_page="id")
                        if images_result and images_result.get('profile_list'):
                            id_profile_config['images_upload'] = images_result
                            id_profile_has_content = True

                    # Process story configuration
                    if story_upload_enabled:
                        story_config = id_info_dict.get("story_config", {})
                        story_result = self.process_content_config("story", story_config, id_name, package_name, id_or_page="id")
                        if story_result and story_result.get('profile_list'):
                            id_profile_config['story_upload'] = story_result
                            id_profile_has_content = True

                    # Add ID profile to profiles_config only if it has content
                    if id_profile_has_content:
                        id_profile_config['insights_collector'] = True
                        profiles_config[id_name] = id_profile_config

                    # Process page-level information
                    page_info_dict = id_info.get("pages_information", {})
                    self.logger.debug(f"Processing {len(page_info_dict)} pages for ID {id_key}")

                    for page_key, page_info in page_info_dict.items():
                        page_name = page_info.get("Page_Name", "")
                        self.logger.debug(f"Processing page: {page_name}")

                        # Add current Page into all profile page 
                        all_profiles.append(page_name)

                        # Initialize page profile configuration only if needed
                        page_profile_has_content = False
                        page_profile_config = {
                            'profile_type': 'page',
                            'insights_collector': False
                        }

                        # Get page-level upload type flags
                        page_upload_types = page_info.get("set_upload_types", {})
                        page_reels_upload = page_upload_types.get("reels_upload", False)
                        page_videos_upload = page_upload_types.get("video_upload", False)
                        page_images_upload = page_upload_types.get("image_upload", False)
                        page_story_upload = page_upload_types.get("story_upload", False)

                        self.logger.debug(f"Page {page_name} upload types - Reels: {page_reels_upload}, Video: {page_videos_upload}, "
                                         f"Image: {page_images_upload}, Story: {page_story_upload}")

                        # Process page reels configuration
                        if page_reels_upload:
                            page_reels_config = page_info.get("reels_config", {})
                            page_reels_result = self.process_content_config("reels", page_reels_config, page_name, package_name, id_or_page="page")
                            if page_reels_result and page_reels_result.get('profile_list'):
                                page_profile_config['reels_upload'] = page_reels_result
                                page_profile_has_content = True

                        # Process page videos configuration
                        if page_videos_upload:
                            page_videos_config = page_info.get("videos_config", {})
                            page_videos_result = self.process_content_config("videos", page_videos_config, page_name, package_name, id_or_page="page")
                            if page_videos_result and page_videos_result.get('profile_list'):
                                page_profile_config['videos_upload'] = page_videos_result
                                page_profile_has_content = True

                        # Process page images configuration
                        if page_images_upload:
                            page_images_config = page_info.get("image_config", {})
                            page_images_result = self.process_content_config("images", page_images_config, page_name, package_name, id_or_page="page")
                            if page_images_result and page_images_result.get('profile_list'):
                                page_profile_config['images_upload'] = page_images_result
                                page_profile_has_content = True

                        # Process page story configuration
                        if page_story_upload:
                            page_story_config = page_info.get("story_config", {})
                            page_story_result = self.process_content_config("story", page_story_config, page_name, package_name, id_or_page="page")
                            if page_story_result and page_story_result.get('profile_list'):
                                page_profile_config['story_upload'] = page_story_result
                                page_profile_has_content = True

                        # Add page profile to profiles_config only if it has content
                        if page_profile_has_content:
                            page_profile_config['insights_collector'] = True
                            profiles_config[page_name] = page_profile_config

                # Process ID Active tasks if id_active_enable is enabled
                if self.is_global_id_active_enable and id_active_enabled:
                    self.logger.info(f"Processing ID active tasks for ID {id_key}")

                    # Process ID active configuration
                    id_active_config_dict = self.process_id_active_data(id_active_dict=id_active_dict, profile_name=id_name)

                    # If ID profile doesn't exist in profiles_config, create it
                    if id_name not in profiles_config:
                        profiles_config[id_name] = {
                            'profile_type': 'id',
                            'insights_collector': False
                        }

                    # Add ID active configuration to the existing profile
                    profiles_config[id_name]['id_active_config'] = id_active_config_dict
                    profiles_config[id_name]['insights_collector'] = True

                # Add combined tasks to inner queue only once
                if profiles_config:
                    # Check if there's any content to process
                    has_upload_content = any(
                        any(key in profile_config for key in ['reels_upload', 'videos_upload', 'images_upload', 'story_upload'])
                        for profile_config in profiles_config.values()
                    )

                    has_id_active_content = any(
                        'id_active_config' in profile_config
                        for profile_config in profiles_config.values()
                    )

                    if has_upload_content or has_id_active_content:
                        self.logger.info(f"Adding combined tasks for {len(profiles_config)} profiles")
                        # Add the entire profiles_config as a single task
                        inner_queue.put(profiles_config)
                        tasks_added = True

                # Add insights update task if necessary
                if tasks_added and self.should_update_insight():
                    # Create insights profile list from profiles_config
                    insight_collector_profiles = [
                        (profile_name, profile_config['profile_type']) 
                        for profile_name, profile_config in profiles_config.items() 
                        if profile_config['insights_collector']
                    ]

                    if insight_collector_profiles:
                        self.logger.info(f"Adding insights update task for {len(insight_collector_profiles)} profiles")
                        inner_queue.put({
                            "insights_update_task": "insights_task_collector",
                            "insights_update_task_argument": {
                                "profile_list": insight_collector_profiles,
                                "profiles_config": profiles_config
                            }
                        })

                # Add task dictionary to main queue if there are tasks
                if tasks_added:
                    ids_with_tasks += 1
                    ld_instance_serial = self.ld_inst_adb_serial_by_name(ld_player_instance_name)
                    if not ld_instance_serial:
                        self.logger.error(f"Failed to get ADB serial for LDPlayer: {ld_player_instance_name}")
                        continue
                    
                    if not self.is_global_id_active_enable:
                        id_active_enabled = False

                    task_dict = {
                        "serial": ld_instance_serial,
                        "device_name": ld_player_instance_name,
                        "id_name": id_name,
                        "upload_method": upload_method,
                        "id_information_idx": id_information_idx,
                        "local_output_file_path": main_folder_path,
                        "page_manager_path": self.page_manager_path,
                        "task_queue": inner_queue,
                        "upload_enabled": upload_enabled,
                        "all_profiles": all_profiles,
                        "id_active_enabled": id_active_enabled
                    }
                    self.main_queue.put(task_dict)
                    self.logger.info(f"Added task for ID {id_key} to main queue (Upload: {upload_enabled}, ID Active: {id_active_enabled})")

            self.logger.info(f"Processed {ids_processed} IDs, {ids_with_tasks} with tasks")
            self.check_and_update_insight()

            return self.main_queue
        except FileNotFoundError as e:
            self.logger.error(f"File not found: {e}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON file: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in collect_tasks_from_json: {e}")

        return self.main_queue


    def check_image_available_in_folder(self, profile_name, folder, num_of_image=1):
        """
        Check if a specific number of image files are available in the specified folder.

        Args:
            profile_name (str): Name of the profile for logging purposes
            folder (str): Path to the folder to check for images
            num_of_image (int): Minimum number of images required (default: 1)

        Returns:
            bool: True if at least num_of_image images are found, False otherwise
        """
        self.logger.info(f"Checking for {num_of_image} image(s) in folder: {folder} for profile: {profile_name}")
        
        if not folder:
            self.logger.error(f"No folder path provided for {profile_name}")
            return False
            
        if not os.path.exists(folder):
            self.logger.error(f"Folder not found for {profile_name}, folder path: {folder}")
            return False
            
        try:
            # Image file extensions
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            image_count = 0
            found_files = []

            for filename in os.listdir(folder):
                if filename.lower().endswith(image_extensions):
                    image_count += 1
                    found_files.append(filename)
                    
                    if image_count >= num_of_image:
                        self.logger.info(f"Found sufficient image files ({image_count}) for {profile_name}")
                        return True

            if image_count > 0:
                self.logger.warning(f"Only {image_count} image(s) available for {profile_name}, but {num_of_image} required.")
            else:
                self.logger.warning(f"No images available for {profile_name} in folder: {folder}")

            return False

        except Exception as e:
            self.logger.error(f"Error checking image files in folder: {e}")
            return False
        

if __name__ == "__main__":

    import json
    import queue

    # Assuming the TaskCollector class is defined as provided
    task_collector = TaskCollector()
    main_queue = task_collector.collect_tasks_from_json()

    # Print all tasks in the main queue
    while not main_queue.empty():
        task = main_queue.get()
        # Create a copy of the task dictionary and remove the non-serializable task_queue
        task_copy = task.copy()
        del task_copy["task_queue"]
        print("Task:")
        print(json.dumps(task_copy, indent=4))
        # Process the inner task_queue
        inner_queue = task["task_queue"]
        print("Inner tasks:")
        while not inner_queue.empty():
            inner_task = inner_queue.get()
            print(json.dumps(inner_task, indent=4))
        print("-" * 50)