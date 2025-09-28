import json
import os
from copy import deepcopy
from PySide6.QtCore import QThread

class BulkConfigSettingsEditors:
    
    def __init__(self, json_file_path):
        """
        Initialize the ConfigManager with a JSON file path.
        
        Args:
            json_file_path (str): Path to the JSON configuration file
        """
        self.current_index = 0
        self.total_indices = 0
        self.task_progress = ""
        self.is_task_done = False
        self.json_file_path = json_file_path
        self.config = self._load_json_file()
        
    def _load_json_file(self):
        """
        Load the JSON configuration file.
        
        Returns:
            dict: The loaded configuration or an empty dict if the file doesn't exist
        """
        if os.path.exists(self.json_file_path):
            try:
                with open(self.json_file_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except json.JSONDecodeError:
                print(f"Error decoding JSON file: {self.json_file_path}")
                return {}
            except Exception as e:
                print(f"Error loading JSON file: {e}")
                return {}
        else:
            print(f"JSON file not found: {self.json_file_path}")
            return {}
            
    def save_json_file(self):
        """
        Save the current configuration back to the JSON file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.config, file, indent=4)
            print("Successfully saved changes")
            return True
        except Exception as e:
            print(f"Error saving JSON file: {e}")
            return False
    
    def copy_id_info_config(self, selected_id_info_index, copy_to_id_info_indices, bulk_config_props):
        """
        Copy configuration from one ID information to others, including their pages.
        
        Args:
            selected_id_info_index (int): Source ID information index
            copy_to_id_info_indices (list): List of target ID information indices
            bulk_config_props (dict): Dictionary of configuration properties to copy
            
        Returns:
            dict: Updated configuration
        """
        # Create source key for selected ID information
        source_key = f"Id_information.{selected_id_info_index}"
        
        # Check if source key exists in the configuration
        if source_key not in self.config:
            print(f"Source key {source_key} not found in configuration")
            self.task_progress = f"Error: Source key {source_key} not found"
            self.is_task_done = True
            return self.config
        
        # Get source ID information
        source_id_info = self.config[source_key]
        
        # Calculate total pages for progress tracking
        total_pages = 0
        if "pages_information" in source_id_info:
            total_pages = len(source_id_info["pages_information"]) * len(copy_to_id_info_indices)
        
        # Set total count for progress tracking
        self.total_indices = len(copy_to_id_info_indices) + total_pages
        self.current_index = 0
        self.is_task_done = False
        
        # Process each target ID information index
        for target_index in copy_to_id_info_indices:
            target_key = f"Id_information.{target_index}"
            
            self.task_progress = f"Editing {target_index}.ID"
            self.current_index += 1
            
            # Skip if target key is the same as source key
            if target_key == source_key:
                continue
            
            # Create target key if it doesn't exist
            if target_key not in self.config:
                self.config[target_key] = {}
            
            # Add small delay to make progress visible
            QThread.msleep(300)
            
            # Copy basic properties
            self._copy_basic_properties(source_id_info, self.config[target_key], bulk_config_props)
            
            # Copy ID active properties
            if "id_active" in source_id_info:
                if "id_active" not in self.config[target_key]:
                    self.config[target_key]["id_active"] = {}
                self._copy_id_active_properties(source_id_info["id_active"], 
                                              self.config[target_key]["id_active"], 
                                              bulk_config_props)
            
            # Add small delay to make progress visible
            QThread.msleep(300)
            
            # Copy ID info properties
            if "ID_info" in source_id_info:
                if "ID_info" not in self.config[target_key]:
                    self.config[target_key]["ID_info"] = {}
                self._copy_id_info_properties(source_id_info["ID_info"], 
                                            self.config[target_key]["ID_info"], 
                                            bulk_config_props)
            
            self.task_progress = f"Editing Done On {target_index}.ID"
            
            # Now handle pages if they exist in the source
            if "pages_information" in source_id_info:
                # Create pages_information in target if it doesn't exist
                if "pages_information" not in self.config[target_key]:
                    self.config[target_key]["pages_information"] = {}
                
                # Find source Page.1 to use as template for all target pages
                source_page1_key = None
                source_page1 = None
                for page_key, page_data in source_id_info["pages_information"].items():
                    if page_key == "Page.1":
                        source_page1_key = page_key
                        source_page1 = page_data
                        break
                
                # If Page.1 exists in source, copy it to all pages in target
                if source_page1:
                    self._copy_page1_to_all_pages(
                        source_page1, 
                        self.config[target_key]["pages_information"],
                        bulk_config_props,
                        target_index
                    )
                else:
                    # If no Page.1 exists, copy all pages normally
                    self._copy_pages_information(
                        source_id_info["pages_information"],
                        self.config[target_key]["pages_information"],
                        bulk_config_props,
                        target_index
                    )

        # Mark task as complete
        self.is_task_done = True
        return self.config

    def _copy_page1_to_all_pages(self, source_page1, target_pages, bulk_config_props, target_id_index):
        """
        Copy Page.1 configuration to all pages in the target.
        
        Args:
            source_page1 (dict): Source Page.1 configuration
            target_pages (dict): Target pages configuration
            bulk_config_props (dict): Configuration properties to copy
            target_id_index (int): ID index being processed for progress tracking
        """
        # If target_pages is empty, create a default Page.1
        if not target_pages:
            target_pages["Page.1"] = {}
            self._copy_page_configuration(source_page1, target_pages["Page.1"], "Page.1", bulk_config_props, target_id_index)
            return
        
        # Apply Page.1 configuration to all existing pages
        for target_page_key, target_page in target_pages.items():
            self.current_index += 1
            
            # Get the page name from the target or use a default
            page_name = target_page.get("Page_Name", f"Page {target_page_key.split('.')[-1]}")
            self.task_progress = f"Applying Page.1 template to {page_name} for ID {target_id_index}"
            
            # Copy the configuration while preserving the page name
            self._copy_page_configuration(source_page1, target_page, page_name, bulk_config_props, target_id_index)
            
            # Add small delay to make progress visible
            QThread.msleep(200)
            
            self.task_progress = f"Completed applying template to {page_name} for ID {target_id_index}"

    def _copy_page_configuration(self, source_page, target_page, page_name, bulk_config_props, target_id_index):
        """
        Copy a page configuration from source to target.
        
        Args:
            source_page (dict): Source page configuration
            target_page (dict): Target page configuration
            page_name (str): Page name to preserve
            bulk_config_props (dict): Configuration properties to copy
            target_id_index (int): ID index for progress tracking
        """
        # Preserve the page name
        target_page["Page_Name"] = page_name
        
        # Copy content type configurations
        for content_type, config_key, bulk_prop in [
            ("reels", "reels_config", bulk_config_props["Reels"]),
            ("videos", "videos_config", bulk_config_props["Video"]),
            ("image", "image_config", bulk_config_props["Bonus"]),
            ("story", "story_config", bulk_config_props["Story"])
        ]:
            if config_key in source_page:
                if config_key not in target_page:
                    target_page[config_key] = {}
                self._copy_content_type_config(
                    source_page[config_key],
                    target_page[config_key],
                    config_key,
                    bulk_prop
                )
            
        # Copy download and edit settings
        if bulk_config_props["download_edits"] and "configure_download_bonus_edits_video_edits" in source_page:
            if "configure_download_bonus_edits_video_edits" not in target_page:
                target_page["configure_download_bonus_edits_video_edits"] = {}
            
            # Copy auto download/edit flags
            for key, value in source_page["configure_download_bonus_edits_video_edits"].items():
                if key != "Download Configurations":
                    target_page["configure_download_bonus_edits_video_edits"][key] = deepcopy(value)
            
            # Copy download configurations except path values
            if "Download Configurations" in source_page["configure_download_bonus_edits_video_edits"]:
                if "Download Configurations" not in target_page["configure_download_bonus_edits_video_edits"]:
                    target_page["configure_download_bonus_edits_video_edits"]["Download Configurations"] = {}
                
                for key, value in source_page["configure_download_bonus_edits_video_edits"]["Download Configurations"].items():
                    if "path" not in key.lower() and "folder" not in key.lower() and "history" not in key.lower():
                        target_page["configure_download_bonus_edits_video_edits"]["Download Configurations"][key] = deepcopy(value)
        
        # Copy upload types if needed
        if bulk_config_props["upload_type"] and "set_upload_types" in source_page:
            target_page["set_upload_types"] = deepcopy(source_page["set_upload_types"])
        
        # Copy Auto Video Edits if needed
        if "Auto Video Edits" in source_page and any(bulk_config_props[content_type]["auto_edits"] for content_type in ["Reels", "Video", "Bonus", "Story"]):
            if "Auto Video Edits" not in target_page:
                target_page["Auto Video Edits"] = {}
            
            if "Title" in source_page["Auto Video Edits"]:
                if "Title" not in target_page["Auto Video Edits"]:
                    target_page["Auto Video Edits"]["Title"] = {}
                
                for key, value in source_page["Auto Video Edits"]["Title"].items():
                    if "path" not in key.lower():
                        target_page["Auto Video Edits"]["Title"][key] = deepcopy(value)

    def _copy_pages_information(self, source_pages, target_pages, bulk_config_props, target_id_index):
        """
        Copy all pages from source to target, preserving page names.
        
        Args:
            source_pages (dict): Source pages configuration
            target_pages (dict): Target pages configuration
            bulk_config_props (dict): Configuration properties to copy
            target_id_index (int): ID index being processed for progress tracking
        """
        # Skip if no source pages
        if not source_pages:
            return
            
        # Process each source page
        for source_page_key, source_page in source_pages.items():
            # Create the same page key in the target
            if source_page_key not in target_pages:
                target_pages[source_page_key] = {}
            
            # Preserve page name if it exists in the target
            page_name = target_pages[source_page_key].get("Page_Name", source_page.get("Page_Name", ""))
            
            self.current_index += 1
            self.task_progress = f"Editing page {page_name} for ID {target_id_index}"
            
            # Copy the page configuration
            target_page = target_pages[source_page_key]
            
            # Set Page_Name
            target_page["Page_Name"] = page_name
            
            # Add small delay to make progress visible
            QThread.msleep(200)
            
            # Copy content type configurations
            for content_type, config_key, bulk_prop in [
                ("reels", "reels_config", bulk_config_props["Reels"]),
                ("videos", "videos_config", bulk_config_props["Video"]),
                ("image", "image_config", bulk_config_props["Bonus"]),
                ("story", "story_config", bulk_config_props["Story"])
            ]:
                if config_key in source_page:
                    if config_key not in target_page:
                        target_page[config_key] = {}
                    self._copy_content_type_config(
                        source_page[config_key],
                        target_page[config_key],
                        config_key,
                        bulk_prop
                    )
                
            # Copy download and edit settings
            if bulk_config_props["download_edits"] and "configure_download_bonus_edits_video_edits" in source_page:
                if "configure_download_bonus_edits_video_edits" not in target_page:
                    target_page["configure_download_bonus_edits_video_edits"] = {}
                
                # Copy auto download/edit flags
                for key, value in source_page["configure_download_bonus_edits_video_edits"].items():
                    if key != "Download Configurations":
                        target_page["configure_download_bonus_edits_video_edits"][key] = deepcopy(value)
                
                # Copy download configurations except path values
                if "Download Configurations" in source_page["configure_download_bonus_edits_video_edits"]:
                    if "Download Configurations" not in target_page["configure_download_bonus_edits_video_edits"]:
                        target_page["configure_download_bonus_edits_video_edits"]["Download Configurations"] = {}
                    
                    for key, value in source_page["configure_download_bonus_edits_video_edits"]["Download Configurations"].items():
                        if "path" not in key.lower() and "folder" not in key.lower() and "history" not in key.lower():
                            target_page["configure_download_bonus_edits_video_edits"]["Download Configurations"][key] = deepcopy(value)
            
            # Copy upload types if needed
            if bulk_config_props["upload_type"] and "set_upload_types" in source_page:
                target_page["set_upload_types"] = deepcopy(source_page["set_upload_types"])
            
            # Copy Auto Video Edits if needed
            if "Auto Video Edits" in source_page and any(bulk_config_props[content_type]["auto_edits"] for content_type in ["Reels", "Video", "Bonus", "Story"]):
                if "Auto Video Edits" not in target_page:
                    target_page["Auto Video Edits"] = {}
                
                if "Title" in source_page["Auto Video Edits"]:
                    if "Title" not in target_page["Auto Video Edits"]:
                        target_page["Auto Video Edits"]["Title"] = {}
                    
                    for key, value in source_page["Auto Video Edits"]["Title"].items():
                        if "path" not in key.lower():
                            target_page["Auto Video Edits"]["Title"][key] = deepcopy(value)
            
            self.task_progress = f"Completed editing page {page_name} for ID {target_id_index}"

    def _copy_basic_properties(self, source, target, bulk_config_props):
        """Copy basic properties based on bulk_config_props settings"""
        # Basic properties
        if bulk_config_props["upload_method"] and "upload_method" in source:
            target["upload_method"] = source["upload_method"]
        
        # Don't copy id_name, package_name, and Ld_name
        # Preserve these values or set defaults if they don't exist
        if "id_name" not in target:
            target["id_name"] = ""
        if "package_name" not in target:
            target["package_name"] = "com.facebook.katana"
        if "Ld_name" not in target:
            target["Ld_name"] = ""
        
        # Copy other properties except for path values
        for key, value in source.items():
            if key not in ["id_name", "package_name", "Ld_name", "id_active", "ID_info", "pages_information", "Main_folder_path", "chrome_instance_path"]:
                target[key] = deepcopy(value)

    def _copy_id_active_properties(self, source, target, bulk_config_props):
        """Copy ID active properties based on bulk_config_props settings"""
        # Copy loops configuration
        if bulk_config_props["loops"]:
            if "num_of_loop" in source:
                target["num_of_loop"] = source["num_of_loop"]
            if "loop_delay" in source:
                target["loop_delay"] = source["loop_delay"]
            if "shuffel" in source:
                target["shuffel"] = source["shuffel"]
        
        # Copy scroll reels and videos configuration
        if bulk_config_props["scroll_reels_video"] and "scroll_reels_and_vid" in source:
            if "scroll_reels_and_vid" not in target:
                target["scroll_reels_and_vid"] = {}
            
            for key, value in source["scroll_reels_and_vid"].items():
                if key != "activity":
                    target["scroll_reels_and_vid"][key] = deepcopy(value)
            
            # Copy activity configuration
            if "activity" in source["scroll_reels_and_vid"]:
                if "activity" not in target["scroll_reels_and_vid"]:
                    target["scroll_reels_and_vid"]["activity"] = {}
                
                for act_key, act_value in source["scroll_reels_and_vid"]["activity"].items():
                    target["scroll_reels_and_vid"]["activity"][act_key] = deepcopy(act_value)
        
        # Copy scroll feed configuration
        if bulk_config_props["scroll_feeds"] and "scroll_feed" in source:
            if "scroll_feed" not in target:
                target["scroll_feed"] = {}
            
            for key, value in source["scroll_feed"].items():
                if key != "activity":
                    target["scroll_feed"][key] = deepcopy(value)
            
            # Copy activity configuration
            if "activity" in source["scroll_feed"]:
                if "activity" not in target["scroll_feed"]:
                    target["scroll_feed"]["activity"] = {}
                
                for act_key, act_value in source["scroll_feed"]["activity"].items():
                    target["scroll_feed"]["activity"][act_key] = deepcopy(act_value)
        
        # Copy check message configuration
        if bulk_config_props["check_reply_msg"] and "check_msg" in source:
            target["check_msg"] = deepcopy(source["check_msg"])
        
        # Copy add and confirm friends configuration
        if bulk_config_props["add_confirm_friends"] and "add_and_confirm_friends" in source:
            target["add_and_confirm_friends"] = deepcopy(source["add_and_confirm_friends"])
        
        # Copy post photo configuration without folder paths
        if "post_photo" in source:
            if "post_photo" not in target:
                target["post_photo"] = {}
            
            for key, value in source["post_photo"].items():
                if key != "post_photo_config":
                    target["post_photo"][key] = deepcopy(value)
            
            # Copy post photo config without folder paths
            if "post_photo_config" in source["post_photo"]:
                if "post_photo_config" not in target["post_photo"]:
                    target["post_photo"]["post_photo_config"] = {}
                
                for key, value in source["post_photo"]["post_photo_config"].items():
                    if "folder" not in key.lower():
                        target["post_photo"]["post_photo_config"][key] = deepcopy(value)
        
        # Copy post checkin configuration without folder paths
        if bulk_config_props["post_checkin"] and "post_checkin" in source:
            if "post_checkin" not in target:
                target["post_checkin"] = {}
            
            for key, value in source["post_checkin"].items():
                if key != "post_checkin_config":
                    target["post_checkin"][key] = deepcopy(value)
            
            # Copy post checkin config without folder paths
            if "post_checkin_config" in source["post_checkin"]:
                if "post_checkin_config" not in target["post_checkin"]:
                    target["post_checkin"]["post_checkin_config"] = {}
                
                for key, value in source["post_checkin"]["post_checkin_config"].items():
                    if "folder" not in key.lower():
                        target["post_checkin"]["post_checkin_config"][key] = deepcopy(value)
        
        # Copy create story configuration without folder paths
        if bulk_config_props["create_story"] and "create_story" in source:
            if "create_story" not in target:
                target["create_story"] = {}
            
            for key, value in source["create_story"].items():
                if key != "create_story_config":
                    target["create_story"][key] = deepcopy(value)
            
            # Copy create story config without folder paths
            if "create_story_config" in source["create_story"]:
                if "create_story_config" not in target["create_story"]:
                    target["create_story"]["create_story_config"] = {}
                
                for key, value in source["create_story"]["create_story_config"].items():
                    if "folder" not in key.lower():
                        target["create_story"]["create_story_config"][key] = deepcopy(value)
        
        # Copy check notification configuration
        if bulk_config_props["check_notification"] and "check_notification" in source:
            target["check_notification"] = deepcopy(source["check_notification"])
        
        return target

    def _copy_id_info_properties(self, source, target, bulk_config_props):
        """Copy ID info properties based on bulk_config_props settings"""
        # Copy upload types if needed
        if bulk_config_props["upload_type"] and "set_upload_types" in source:
            target["set_upload_types"] = deepcopy(source["set_upload_types"])
        
        # Copy reels configuration
        self._copy_content_type_config(source, target, "reels_config", bulk_config_props["Reels"])
        
        # Copy videos configuration
        self._copy_content_type_config(source, target, "videos_config", bulk_config_props["Video"])
        
        # Copy image configuration
        self._copy_content_type_config(source, target, "image_config", bulk_config_props["Bonus"])
        
        # Copy story configuration
        self._copy_content_type_config(source, target, "story_config", bulk_config_props["Story"])
        
        # Copy download and edit settings
        if bulk_config_props["download_edits"] and "configure_download_bonus_edits_video_edits" in source:
            if "configure_download_bonus_edits_video_edits" not in target:
                target["configure_download_bonus_edits_video_edits"] = {}
            
            # Copy auto download/edit flags
            for key, value in source["configure_download_bonus_edits_video_edits"].items():
                if key != "Download Configurations":
                    target["configure_download_bonus_edits_video_edits"][key] = deepcopy(value)
            
            # Copy download configurations except path values
            if "Download Configurations" in source["configure_download_bonus_edits_video_edits"]:
                if "Download Configurations" not in target["configure_download_bonus_edits_video_edits"]:
                    target["configure_download_bonus_edits_video_edits"]["Download Configurations"] = {}
                
                for key, value in source["configure_download_bonus_edits_video_edits"]["Download Configurations"].items():
                    if "path" not in key.lower() and "folder" not in key.lower() and "history" not in key.lower():
                        target["configure_download_bonus_edits_video_edits"]["Download Configurations"][key] = deepcopy(value)
        
        # Copy Auto Video Edits
        if "Auto Video Edits" in source and any(bulk_config_props[content_type]["auto_edits"] for content_type in ["Reels", "Video", "Bonus", "Story"]):
            if "Auto Video Edits" not in target:
                target["Auto Video Edits"] = {}
            
            if "Title" in source["Auto Video Edits"]:
                if "Title" not in target["Auto Video Edits"]:
                    target["Auto Video Edits"]["Title"] = {}
                
                for key, value in source["Auto Video Edits"]["Title"].items():
                    if "path" not in key.lower():
                        target["Auto Video Edits"]["Title"][key] = deepcopy(value)
        
        return target

    def _copy_content_type_config(self, source, target, config_key, config_props):
        """Copy content type specific configuration (reels, videos, images, stories)"""
        if config_key in source:
            # Create target config if it doesn't exist
            if config_key not in target:
                target[config_key] = {}
            
            # Skip folder paths
            for key, value in source[config_key].items():
                if key not in ["download_folder", "ld_folder"]:
                    # Copy download configuration
                    if key == "download_configuration" and config_props["download_config"]:
                        if key not in target[config_key]:
                            target[config_key][key] = {}
                        
                        for sub_key, sub_value in value.items():
                            if "history" not in sub_key.lower():
                                target[config_key][key][sub_key] = deepcopy(sub_value)
                    
                    # Copy captions configuration
                    elif key == "captions" and config_props["caption_config"]:
                        if key not in target[config_key]:
                            target[config_key][key] = {}
                        
                        for sub_key, sub_value in value.items():
                            if "path" not in sub_key.lower():
                                target[config_key][key][sub_key] = deepcopy(sub_value)
                    
                    # Copy schedule configuration
                    elif key == "schedule_config" and config_props["schedule_time"]:
                        target[config_key][key] = deepcopy(value)
                    
                    # Copy schedule_enable flag
                    elif key == "schedule_enable" and config_props["schedule_time"]:
                        target[config_key][key] = value
                    
                    # Copy auto edit preset
                    elif key == "auto_edit_preset" and config_props["auto_edits"]:
                        target[config_key][key] = deepcopy(value)
        
        return target


def main():
    """Main function to execute the configuration copying process"""
    
    # Define the JSON file path
    json_file_path = r"User_Data\Page_manager.json"
    
    try:
        # Initialize the ConfigManager
        config_manager = BulkConfigSettingsEditors(json_file_path)
    
        
        # Create bulk configuration dictionary
        bulk_config  = {
            # Common properties for auto upload settings
            "upload_method": True,
            "download_edits": True,
            "upload_type": True,
            # ID Active properties
            "scroll_reels_video": True,
            "scroll_feeds": True,
            "check_reply_msg": True,
            "add_confirm_friends": True,
            "post_checkin": True,
            "create_story": True,
            "check_notification": True,
            "loops": True,
            # Content type specific properties
            "Reels": {
                "download_config": True,
                "caption_config": True,
                "schedule_time": True,
                "auto_edits": True
            },
            "Video": {
                "download_config": True,
                "caption_config": True,
                "schedule_time": True,
                "auto_edits": True
            },
            "Bonus": {
                "download_config": False,
                "caption_config": True,
                "schedule_time": True,
                "auto_edits": True
            },
            "Story": {
                "download_config": True,
                "caption_config": True,
                "schedule_time": True,
                "auto_edits": True
            }
        }
        
        # Execute the configuration copying
        config_manager.copy_id_info_config(1, [2,3,4], bulk_config)
        
        # Save the changes
        config_manager.save_json_file()
        
        print(f"\nSuccessfully copied configurations from ID 1 to IDs 2, 3, 4, including their pages.")
        
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()