import time
import threading
import os
import json
import logging
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QAction
import sys
from openpyxl import Workbook  

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from geni.Downloaders.all_platform_shorts_downloader.UnifiedSocialMediaDownloader import UnifiedSocialMediaDownloader
from geni.ldController.Ldcontroller_adb.LdAdb import LdAdbController
# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler and set level to info
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

# Try to create a file handler as well
try:
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = logging.FileHandler('logs/folder_manager.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
except Exception as e:
    logger.warning(f"Could not set up file logging: {e}")


class create_folder_and_config(QObject):
    # Define signals for thread-safe UI updates
    log_signal = Signal(str, str)  # (level, message)
    
    def __init__(self, current_id_index,all_ld_folder_path,create_folder_config_ld_prop):
        super().__init__()

        self.id_frame_idx = current_id_index  
        self.id_name = ""
        self.page_manager_path = r"User_Data\Page_manager.json"
        self.main_folder = ""
        self.all_ld_folder_path = all_ld_folder_path
        # Regular content folders
        self.download_image_folder = ""
        self.reel_download_folder = ""
        self.video_download_folder = ""
        self.story_download_folder = ""
        self.image_ld_folder = ""
        self.reel_ld_folder = ""
        self.video_ld_folder = ""
        self.story_video_ld_folder = ""
        self.reels_history_xlsx_path =""
        # ID active folders
        self.download_id_act_checkin_photo = ""
        self.download_id_act_story_video = ""
        self.download_id_act_photo = ""
        self.ld_id_act_checkin_photo = ""
        self.ld_id_act_story_video = ""
        self.ld_id_act_photo = ""

        self.chrome_instance_path = ""
        
        # Configuration flags
        self.create_id_active_folder = True 

        self.pages_list = []
        self.savecallback = None
        self.restart_this_ld_instance = None  
        self.create_folder_config_ld_prop=create_folder_config_ld_prop
        
        self.all_pages_folders_props = {}

        # Connect signals to slots for thread-safe logging
        self.log_signal.connect(self._log_message)

    def _log_message(self, level, message):
        """Log message safely from any thread"""
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)

    def create_ld_folder_and_main_folder(self, current_id_index, all_ld_folder_path):
        """
        Create folders with LD name and then inside that create another folder with Ld-name + "Main_folder"
        and set folder path to self.main_folder
        """
        try:
            # Get ID information from the JSON (assuming we have access to it)
            id_key = f"Id_information.{current_id_index}"

            with open(self.page_manager_path, 'r') as f:
                config_data = json.load(f)
                    
                if id_key in config_data:
                    ld_name = config_data[id_key].get("Ld_name", "default_ld")
   
                    # Create main LD folder
                    ld_folder_path = os.path.join(all_ld_folder_path, ld_name)
                    if not os.path.exists(ld_folder_path):
                        os.makedirs(ld_folder_path, exist_ok=True)
                    
                    # Create Main_folder inside LD folder
                    main_folder_path = os.path.join(ld_folder_path, "main_folder")
                    if not os.path.exists(main_folder_path):
                        os.makedirs(main_folder_path, exist_ok=True)
                    
                    # Set the main_folder path
                    self.main_folder = main_folder_path
                    
                    logger.info(f"Successfully created LD folders for {ld_name}")
                    return True, f"Successfully created LD folders for {ld_name}"
            
            logger.error("Failed to find configuration for the specified ID index")
            return False, "Failed to find configuration for the specified ID index"
        
        except Exception as e:
            logger.error(f"Error creating LD folders: {str(e)}")
            return False, f"Error creating LD folders: {str(e)}"

    def create_pages_folders(self, current_id_index):
        """
        Create page folders as needed and loop through all the pages available in page_information 
        of that id index and save into self.all_pages_folders_props and then take all the path 
        and save into page_manage.json
        """
        try:
            # Get ID information and pages information
            id_key = f"Id_information.{current_id_index}"
                
            with open(self.page_manager_path, 'r') as f:
                config_data = json.load(f)
                
            if id_key not in config_data:
                logger.error(f"ID information for index {current_id_index} not found")
                return False, f"ID information for index {current_id_index} not found"
                
            id_info = config_data[id_key]
            pages_info = id_info.get("pages_information", {})
            
            if not pages_info:
                logger.error("No pages information found")
                return False, "No pages information found"
            
            # Loop through all pages and create folders
            for page_key, page_data in pages_info.items():

                raw_page_name = page_data.get("Page_Name", "Default_Page")
                page_name = self.clean_name(raw_page_name)
                
                self.pages_list.append(raw_page_name)
                
                # Create a dictionary to store the page configuration
                page_folders = {}
                
                # Create folder structure for each content type
                main_folder_for_download = os.path.dirname(self.main_folder)
                
                # Ensure the page directory exists
                page_dir = os.path.join(main_folder_for_download, page_name)
                if not os.path.exists(page_dir):
                    os.makedirs(page_dir, exist_ok=True)
                
                # Map content types to their config keys
                content_type_mapping = {
                    "_reel": "reels_config",
                    "_vid": "videos_config",
                    "_img": "image_config",
                    "_story": "story_config"
                }
                
                # Create folders for each content type
                for content_type, config_key in content_type_mapping.items():
                    # Create download folder
                    download_folder_name = f"{page_name}_download{content_type}"
                    download_path = os.path.join(page_dir, download_folder_name)
                    if not os.path.exists(download_path):
                        os.makedirs(download_path, exist_ok=True)
                    
                    # Create LD folder
                    """ ld_folder_name = f"{page_name}{content_type}"
                    ld_path = os.path.join(self.main_folder, ld_folder_name)
                    if not os.path.exists(ld_path):
                        os.makedirs(ld_path, exist_ok=True) """
                    
                    # Initialize config key if needed
                    if config_key not in page_folders:
                        page_folders[config_key] = {
                            "download_folder": "",
                            "ld_folder": ""
                        }
                    
                    # Store paths in dictionary
                    page_folders[config_key]["download_folder"] = os.path.abspath(download_path)
                    
                
                # Store page folders configuration
                self.all_pages_folders_props[page_key] = page_folders
            
            # Save paths 
            logger.info("Successfully created page folders")
            return True, "Successfully created page folders"
            
        except Exception as e:
            logger.error(f"Error creating page folders: {str(e)}")
            return False, f"Error creating page folders: {str(e)}"

    def restart_ld_inst(self):
        """Restart LD instance and emit log signals instead of showing messages directly."""
        try:
            restart = LdAdbController()
            restart.local_output_file_path = self.main_folder
            restart.device_serial = restart.ld_inst_adb_serial__of_selected_frame(id_frame_idx=self.id_frame_idx)
            restart.close_ld_inst(id_info_idx=self.id_frame_idx)
            is_done, message = restart.set_pc_shared_folder(id_frame_idx=self.id_frame_idx)
            if not is_done:
                self.log_signal.emit("error", message)
                return

            local_is_done, local_message = restart.set_open_loacl_adb(self.id_frame_idx)
            if not local_is_done:
                self.log_signal.emit("error", local_message)
                return
            time.sleep(4)

            ld_name, _ = restart.get_id_info(self.id_frame_idx)
            restart.set_ld_instance_prop(ld_name)
            restart.start_ld_inst(self.id_frame_idx)

            restart.cheack_ld_instance_open_or_not_for_20sec(id_frame_idx=self.id_frame_idx)

            is_inst, inst_message = restart.check_and_install_list_of_apps(self.id_frame_idx)

            time.sleep(2)
            
            try:
                restart.set_dnd_mode()
            except Exception as e:
                print(f"Error settting dnd mode{e}")
            time.sleep(1)

            

            try:
                restart.allow_all_permission()
            except Exception as e :
                print(f"Error while allowing all permissoin : {e}")
            

            
            if not is_inst:
                msg = f"Main folder path set but default apps not installed to LD: '{ld_name}'\n{inst_message}"
                self.log_signal.emit("error", msg)
                return
            
            time.sleep(4)
            msg = f"Main folder path set and default apps installed to LD: '{ld_name}'"
            self.log_signal.emit("info", msg)
            restart.close_ld_inst(id_info_idx=self.id_frame_idx)
        except Exception as e:
            self.log_signal.emit("error", f"Failed to restart LD: {e}")

    def on_restart_button_click(self):
        """Start the restart process in a separate thread."""
        if self.restart_this_ld_instance:
            self.restart_this_ld_instance.setEnabled(False)
            thread = threading.Thread(target=self.async_restart, daemon=True)
            thread.start()

    def async_restart(self):
        """Run restart in a worker thread."""
        self.restart_ld_inst()
        # Use signal to safely enable button from worker thread
        if self.restart_this_ld_instance:
            self.restart_this_ld_instance.setEnabled(True)


    def create_chrome_instance(self):

        import undetected_chromedriver as uc
        options = uc.ChromeOptions()
        
        main_folder = self.main_folder
        chrome_instance = self.chrome_instance_path
        
        if not main_folder:
            self.show_message_signal.emit("Error", "Please select a main folder first")  
            return

        chrome_path = []
        
        try:
            if main_folder and chrome_instance:
                chrome_path = ["chrome_path_given", chrome_instance, "Profile 1"]
            elif main_folder and not chrome_instance:
                chrome_path = ["chrome_path_not_given", main_folder, "chrome", "Profile 1"]
            else:
                print("Error while fetching chrome folder paths")
                return
        except Exception as e:
            print(f"Error: {e}")
            return

        if chrome_path[0] == "chrome_path_given":
            chrome_instance_base_path = chrome_path[1]
            chrome_instance_profile_path = chrome_path[2]
            
            downloader_instance = UnifiedSocialMediaDownloader(
                control_pause_callback=None,
                control_quit_callback=None,
                base_user_data_dir=chrome_instance_base_path,
                profile_dir=chrome_instance_profile_path,
                uc_refrance=options
            )
            downloader_instance.web_link = "https://www.google.com/"
            downloader_instance.start_browser()
            self.chrome_instance_path = chrome_instance_base_path
            self.create_history_xlsx()
            self.save_all()
            time.sleep(2)
            downloader_instance.close_browser()

        elif chrome_path[0] == "chrome_path_not_given":
            main_folder_path = chrome_path[1]
            parent_path = os.path.dirname(main_folder_path)
            chrome_instance_base_path = os.path.join(parent_path, chrome_path[2])
            chrome_instance_profile_path = chrome_path[3]

            downloader_instance = UnifiedSocialMediaDownloader(
                control_pause_callback=None,
                control_quit_callback=None,
                base_user_data_dir=chrome_instance_base_path,
                profile_dir=chrome_instance_profile_path,
                uc_refrance=options
            )
            downloader_instance.web_link = "https://www.google.com/"
            downloader_instance.start_browser()
            self.chrome_instance_path = chrome_instance_base_path
            self.create_history_xlsx()
            self.save_all()
            downloader_instance.close_browser()

    def create_history_xlsx(self):

        path = self.chrome_instance_path
        os.makedirs(path, exist_ok=True)
        pc_xlsx_path = os.path.join(path, "reels_history.xlsx")

        if os.path.exists(pc_xlsx_path):
            self.reels_history_xlsx_path = pc_xlsx_path
            print("reels_history XLSX file already exists")
        else:
            wb = Workbook()
            wb.save(pc_xlsx_path)
            self.reels_history_xlsx_path = pc_xlsx_path
            print("reels_history XLSX file created")
           
    def new_thread_chrome_instance_run(self):
        if getattr(self, "chrome_thread_running", False):
            return
        self.chrome_thread_running = True
        thread = threading.Thread(target=self.create_chrome_instance, daemon=True)
        thread.start()

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
    
    def create_id_folders(self, id_index):
        """
        Create all folders for ID profile (determined by id_name) and save paths to configuration
        """
        try:
            # Get ID information
            id_key = f"Id_information.{id_index}"

            with open(self.page_manager_path, 'r') as f:
                config_data = json.load(f)

            if id_key not in config_data:
                logger.error(f"ID information for index {id_index} not found")
                return False, f"ID information for index {id_index} not found"

            id_info = config_data[id_key]
            raw_id_name = id_info.get("id_name", "")
            id_name = self.clean_name(raw_id_name)
            ld_name = id_info.get("Ld_name", "")


            if not id_name:
                logger.error("ID name not found in configuration")
                return False, "ID name not found in configuration"

            if not self.main_folder:
                logger.error("Main folder path not set. Please create LD folders first.")
                return False, "Main folder path not set. Please create LD folders first."

            # Create folders for the ID profile
            main_folder_for_download = os.path.dirname(self.main_folder)

            # Create ID directory if it doesn't exist
            id_profile_dir = os.path.join(main_folder_for_download, id_name)
            if not os.path.exists(id_profile_dir):
                os.makedirs(id_profile_dir, exist_ok=True)

            # Create download folders for different content types
            content_types = [
                ("_download_img", "download_image_folder"),
                ("_download_reel", "reel_download_folder"),
                ("_download_vid", "video_download_folder"),
                ("_download_story", "story_download_folder")
            ]

            # Always create content folders
            for suffix, attr_name in content_types:
                folder_name = f"{id_name}{suffix}"
                folder_path = os.path.join(id_profile_dir, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path, exist_ok=True)
                    logger.info(f"Created download folder: {folder_path}")

                
                setattr(self, attr_name, os.path.abspath(folder_path))

            # Create LD folders for different content types
            ld_content_types = [
                ("_img", "image_ld_folder"),
                ("_reel", "reel_ld_folder"),
                ("_vid", "video_ld_folder"),
                ("_story", "story_video_ld_folder")
            ]

            # Create standard LD content folders
            for suffix, attr_name in ld_content_types:
                folder_name = f"{id_name}{suffix}"
                folder_path = os.path.join(self.main_folder, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path, exist_ok=True)
                    logger.info(f"Created LD folder: {folder_path}")

                
                setattr(self, attr_name, os.path.abspath(folder_path))

     
            if self.create_id_active_folder:
                # ID active download folders
                id_active_download_types = []

                checkin_download = ("_download_id_act_checkin_photo", "download_id_act_checkin_photo")
                photo_download = ("_download_id_act_photo", "download_id_act_photo")
                story_download = ("_download_id_act_story_video", "download_id_act_story_video")

                if self.create_folder_config_ld_prop["create_id_act_post_cheackin_folder"]:
                    id_active_download_types.append(checkin_download)

                if self.create_folder_config_ld_prop["create_id_act_post_video_folder"]:
                    id_active_download_types.append(story_download)

                if self.create_folder_config_ld_prop["create_id_act_post_photo_folder"]:
                    id_active_download_types.append(photo_download)    

                # Create ID active download folders
                for suffix, attr_name in id_active_download_types:
                    folder_name = f"{id_name}{suffix}"
                    folder_path = os.path.join(id_profile_dir, folder_name)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path, exist_ok=True)
                        logger.info(f"Created ID active download folder: {folder_path}")

      
                    setattr(self, attr_name, os.path.abspath(folder_path))

                # ID active LD folders
                id_active_ld_types = []

                ld_checkin = ("_id_act_checkin_photo", "ld_id_act_checkin_photo")
                ld_photo = ("_id_act_photo", "ld_id_act_photo")
                ld_story_vid = ("_id_act_story_video", "ld_id_act_story_video")

                if self.create_folder_config_ld_prop["create_id_act_post_cheackin_folder"]:
                    id_active_ld_types.append(ld_checkin)

                if self.create_folder_config_ld_prop["create_id_act_post_video_folder"]:
                    id_active_ld_types.append(ld_photo)

                if self.create_folder_config_ld_prop["create_id_act_post_photo_folder"]:
                    id_active_ld_types.append(ld_story_vid) 


                # Create ID active LD folders
                for suffix, attr_name in id_active_ld_types:
                    folder_name = f"{id_name}{suffix}"
                    folder_path = os.path.join(self.main_folder, folder_name)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path, exist_ok=True)
                        logger.info(f"Created ID active LD folder: {folder_path}")

   
                    setattr(self, attr_name, os.path.abspath(folder_path))

                # Add debug logs to confirm ID active folders created
                logger.info(f"ID active folders created for {id_name}:")
                logger.info(f"download_id_act_checkin_photo: {self.download_id_act_checkin_photo}")
                logger.info(f"download_id_act_photo: {self.download_id_act_photo}")
                logger.info(f"download_id_act_story_video: {self.download_id_act_story_video}")
                logger.info(f"ld_id_act_checkin_photo: {self.ld_id_act_checkin_photo}")
                logger.info(f"ld_id_act_photo: {self.ld_id_act_photo}")
                logger.info(f"ld_id_act_story_video: {self.ld_id_act_story_video}")
            else:
                logger.info(f"ID active folders creation skipped as it is disabled")

            # Save the ID name
            self.id_name = raw_id_name

            
            if self.savecallback:
                self.savecallback()
            else:
                self.save_all()  

            return True, f"Successfully created all folders for ID profile: {id_name}"

        except Exception as e:
            logger.error(f"Error creating ID folders: {str(e)}")
            return False, f"Error creating ID folders: {str(e)}"



    def save_all(self):
        """Save all configuration changes to the JSON file"""
        try:
            with open(self.page_manager_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            id_key = f"Id_information.{self.id_frame_idx}"

            if id_key in data:
                # Update the configuration with the main folder path
                data[id_key]["Main_folder_path"] = self.main_folder
                
                if self.chrome_instance_path:
                    data[id_key]["chrome_instance_path"] = self.chrome_instance_path

                # If we have an ID name, update the ID-specific configurations
                if hasattr(self, 'id_name') and self.id_name:
                    id_info = data[id_key].get("ID_info", {})

                    # Update reels configuration
                    if hasattr(self, 'reel_download_folder') and hasattr(self, 'reel_ld_folder'):
                        reels_config = id_info.get("reels_config", {})
                        reels_config["download_folder"] = self.reel_download_folder
                        reels_config["ld_folder"] = self.reel_ld_folder
                        id_info["reels_config"] = reels_config

                    # Update videos configuration
                    if hasattr(self, 'video_download_folder') and hasattr(self, 'video_ld_folder'):
                        videos_config = id_info.get("videos_config", {})
                        videos_config["download_folder"] = self.video_download_folder
                        videos_config["ld_folder"] = self.video_ld_folder
                        id_info["videos_config"] = videos_config

                    # Update images configuration
                    if hasattr(self, 'download_image_folder') and hasattr(self, 'image_ld_folder'):
                        image_config = id_info.get("image_config", {})
                        image_config["download_folder"] = self.download_image_folder
                        image_config["ld_folder"] = self.image_ld_folder
                        id_info["image_config"] = image_config

                    # Update story configuration
                    if hasattr(self, 'story_download_folder') and hasattr(self, 'story_video_ld_folder'):
                        story_config = id_info.get("story_config", {})
                        story_config["download_folder"] = self.story_download_folder
                        story_config["ld_folder"] = self.story_video_ld_folder
                        id_info["story_config"] = story_config

                    # Also update the download_folder_config section for backward compatibility
                    download_folder_config = id_info.get("download_folder_config", {})
                    if hasattr(self, 'video_download_folder'):
                        download_folder_config["download_video_folder"] = self.video_download_folder
                    if hasattr(self, 'download_image_folder'):
                        download_folder_config["download_image_folder"] = self.download_image_folder
                    id_info["download_folder_config"] = download_folder_config

                    # Also update the Folder config section for backward compatibility
                    folder_config = id_info.get("Folder config", {})
                    if hasattr(self, 'video_ld_folder'):
                        folder_config["Video Folder"] = self.video_ld_folder
                    if hasattr(self, 'image_ld_folder'):
                        folder_config["Image Folder"] = self.image_ld_folder
                    id_info["Folder config"] = folder_config

                    configure_download_bonus_edits_video_edits = id_info.get("configure_download_bonus_edits_video_edits", {})
                    if hasattr(self,"reels_history_xlsx_path"):
                        configure_download_bonus_edits_video_edits["Download Configurations"]["Save downloaded video history"] = self.reels_history_xlsx_path
                    
                    id_info["configure_download_bonus_edits_video_edits"] = configure_download_bonus_edits_video_edits

                    # Update the ID_info in the data
                    data[id_key]["ID_info"] = id_info

                # Save ID active folder paths - this is where we need to fix things
                if self.create_id_active_folder:
                    # Initialize the id_active section if it doesn't exist
                    if "id_active" not in data[id_key]:
                        data[id_key]["id_active"] = {}

                    id_active = data[id_key]["id_active"]

                    # Make sure all necessary sections exist
                    # For post_photo
                    if "post_photo" not in id_active:
                        id_active["post_photo"] = {}
                    if "post_photo_config" not in id_active["post_photo"]:
                        id_active["post_photo"]["post_photo_config"] = {}

                    # For post_checkin
                    if "post_checkin" not in id_active:
                        id_active["post_checkin"] = {}
                    if "post_checkin_config" not in id_active["post_checkin"]:
                        id_active["post_checkin"]["post_checkin_config"] = {}

                    # For create_story
                    if "create_story" not in id_active:
                        id_active["create_story"] = {}
                    if "create_story_config" not in id_active["create_story"]:
                        id_active["create_story"]["create_story_config"] = {}

                    # Update post_photo configuration
                    if hasattr(self, 'download_id_act_photo') and hasattr(self, 'ld_id_act_photo'):
                        post_photo_config = id_active["post_photo"]["post_photo_config"]
                        post_photo_config["post_photo_download_folder"] = self.download_id_act_photo
                        post_photo_config["post_photo_ld_folder"] = self.ld_id_act_photo
                        # Log the path being saved
                        logger.info(f"Saving post_photo paths: {self.download_id_act_photo}, {self.ld_id_act_photo}")

                    # Update post_checkin configuration
                    if hasattr(self, 'download_id_act_checkin_photo') and hasattr(self, 'ld_id_act_checkin_photo'):
                        post_checkin_config = id_active["post_checkin"]["post_checkin_config"]
                        post_checkin_config["post_checkin_photo_download_folder"] = self.download_id_act_checkin_photo
                        post_checkin_config["post_checkin_ld_photo_folder"] = self.ld_id_act_checkin_photo
                        # Log the path being saved
                        logger.info(f"Saving post_checkin paths: {self.download_id_act_checkin_photo}, {self.ld_id_act_checkin_photo}")

                    # Update create_story configuration
                    if hasattr(self, 'download_id_act_story_video') and hasattr(self, 'ld_id_act_story_video'):
                        create_story_config = id_active["create_story"]["create_story_config"]
                        create_story_config["create_story_video_download_folder"] = self.download_id_act_story_video
                        create_story_config["create_story_video_folder"] = self.ld_id_act_story_video
                        # Log the path being saved
                        logger.info(f"Saving create_story paths: {self.download_id_act_story_video}, {self.ld_id_act_story_video}")
                else:
                    logger.info("Skipping saving ID active folder paths as ID active is disabled")

                # If we have page folders, save those configurations too
                if hasattr(self, 'all_pages_folders_props') and self.all_pages_folders_props:
                    pages_info = data[id_key].get("pages_information", {})

                    for page_key, page_folders in self.all_pages_folders_props.items():
                        if page_key in pages_info:
                            # Update each config directly from our page_folders structure
                            for config_key, config_values in page_folders.items():
                                if config_key in pages_info[page_key]:
                                    # Update download_folder and ld_folder for each content type
                                    if "download_folder" in config_values:
                                        pages_info[page_key][config_key]["download_folder"] = config_values["download_folder"]
                                    if "ld_folder" in config_values:
                                        pages_info[page_key][config_key]["ld_folder"] = config_values["ld_folder"]

                    # Update the pages_information in the data
                    data[id_key]["pages_information"] = pages_info

            # Write the updated data back to the JSON file
            with open(self.page_manager_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            logger.info("Successfully saved all configurations to JSON file")
            return True

        except Exception as e:
            logger.error(f"Error saving configurations: {str(e)}")
            return False

    

    
    def extract_main_folder(self):
        """Extract main folder path from configuration"""
        try:
            with open(self.page_manager_path, 'r') as f:
                config_data = json.load(f)

            id_key = f"Id_information.{self.id_frame_idx}"
            if id_key in config_data:
                return config_data[id_key].get("Main_folder_path", "")
            return ""
        except Exception as e:
            logger.error(f"Error extracting main folder: {str(e)}")
            return ""
     
    def set_save_callback(self, callback):
        """Set the callback function to be called after saving"""
        self.savecallback = callback
        
    def set_restart_button(self, button):
        """Set the reference to the restart button for UI operations"""
        self.restart_this_ld_instance = button

    def main_create_folder_and_ld_config(self):
        """
        Run the complete folder setup sequence for both ID and page profiles

        Args:
            id_index: The ID index in the configuration
            all_ld_folder_path: Path to the LD folders directory
            page_manager_path: Path to the page_manager.json file

        Returns:
            bool: True if setup was successful, False otherwise
        """
        try:


            # Step 1: Create LD folders and main folder
            success, message = self.create_ld_folder_and_main_folder(self.id_frame_idx, self.all_ld_folder_path)
            if not success:
                logger.error(f"Failed to create LD folders: {message}")
                return False
            logger.info(f"LD folders created: {message}")

            # Step 2: Create ID folders 
            success, message = self.create_id_folders(self.id_frame_idx)
            if not success:
                logger.error(f"Failed to create ID folders: {message}")
                return False
            logger.info(f"ID folders created: {message}")

            # Step 3: Create page folders
            success, message = self.create_pages_folders(self.id_frame_idx)
            if not success:
                logger.error(f"Failed to create page folders: {message}")
                return False
            logger.info(f"Page folders created: {message}")

            #run chrome in seprate thread
            if self.create_folder_config_ld_prop["setup_chrome"]:
                self.new_thread_chrome_instance_run()

            # Step 4: Save all configurations
            if not self.save_all():
                logger.error("Failed to save configurations")
                return False
            logger.info("All configurations saved successfully")

            # Step 5: Restart LD instance
            if self.create_folder_config_ld_prop["config_ld"]:
                try:
                    self.restart_ld_inst()
                    logger.info("LD instance restarted successfully")
                except Exception as e:
                    logger.error(f"Error restarting LD instance: {e}")
                    

            return True

        except Exception as e:
            logger.error(f"Error in folder setup sequence: {e}")
            return False
    

def run_folder_setup_sequence(id_index, all_ld_folder_path, page_manager_path):
    """
    Run the complete folder setup sequence for both ID and page profiles
    
    Args:
        id_index: The ID index in the configuration
        all_ld_folder_path: Path to the LD folders directory
        page_manager_path: Path to the page_manager.json file
        
    Returns:
        bool: True if setup was successful, False otherwise
    """
    try:
        # Initialize the folder manager
        folder_manager = create_folder_and_config(id_index)
        folder_manager.page_manager_path = page_manager_path
        
        # Load id_active_enable setting from configuration - fix reading the parameter
        try:
            with open(page_manager_path, 'r') as f:
                config_data = json.load(f)
                id_key = f"Id_information.{id_index}"
                if id_key in config_data:
                    # Set default to True to ensure ID active folders are created if not specified
                    folder_manager.create_id_active_folder = config_data[id_key].get("id_active_enable", True)
                    logger.info(f"ID active folder creation is {'enabled' if folder_manager.create_id_active_folder else 'disabled'}")
                else:
                    # If ID key not found, default to True
                    folder_manager.create_id_active_folder = True
                    logger.info("ID key not found, defaulting to enabled ID active folder creation")
        except Exception as e:
            logger.warning(f"Could not load id_active_enable setting: {e}")
            # Default to True if we can't load the setting
            folder_manager.create_id_active_folder = True
            logger.info("Exception occurred, defaulting to enabled ID active folder creation")
        
        # Step 1: Create LD folders and main folder
        success, message = folder_manager.create_ld_folder_and_main_folder(id_index, all_ld_folder_path)
        if not success:
            logger.error(f"Failed to create LD folders: {message}")
            return False
        logger.info(f"LD folders created: {message}")
        
        # Step 2: Create ID folders - this is the step that needs fixing
        success, message = folder_manager.create_id_folders(id_index)
        if not success:
            logger.error(f"Failed to create ID folders: {message}")
            return False
        logger.info(f"ID folders created: {message}")
        
        # Step 3: Create page folders
        success, message = folder_manager.create_pages_folders(id_index)
        if not success:
            logger.error(f"Failed to create page folders: {message}")
            return False
        logger.info(f"Page folders created: {message}")
        
        #run chrome in seprate thread

        
        folder_manager.new_thread_chrome_instance_run()
        
        # Step 4: Save all configurations
        if not folder_manager.save_all():
            logger.error("Failed to save configurations")
            return False
        logger.info("All configurations saved successfully")
        
        # Step 5: Restart LD instance
        
        try:
            folder_manager.restart_ld_inst()
            logger.info("LD instance restarted successfully")
        except Exception as e:
            logger.error(f"Error restarting LD instance: {e}")
            # Continue anyway since this is not critical
        
        return True
        
    except Exception as e:
        logger.error(f"Error in folder setup sequence: {e}")
        return False

if __name__ == "__main__":
    # Usage example
    id_index = 3
    all_ld_folder_path = r"E:\facebook_ld_player"  # Path to LD folders
    page_manager_path = r"User_Data\Page_manager.json"  # Path to JSON config
    
    success = run_folder_setup_sequence(id_index, all_ld_folder_path, page_manager_path)
    if success:
        print("Complete folder setup sequence executed successfully")
    else:
        print("Folder setup sequence encountered errors")
