import time
import random
from lxml import etree
import xml.etree.ElementTree as ET
import sys
import os
import shutil
import subprocess
import sys
import json
import re
from datetime import datetime


def activity_callback(queue, ldname, app, profile, current, others, log_type=None):
    """Callback to update process activity with optional logging"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if log_type:
        queue.put(('UPDATE', ldname, app, profile, current, others, timestamp, log_type))
    else:
        queue.put(('UPDATE', ldname, app, profile, current, others, timestamp))

def delete_callback(queue, ldname):
    """Callback to delete a process"""
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


#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..')))

from ldController.Ldcontroller_adb.LdAdb import LdAdbController

from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten
from geni_ui_src.Page_manager_reader import DevicesJson



class IdAndPageInfoFetcher():

    def __init__(self, control_pasue_callback, device_name=None, device_serial=None, local_output_file_path="",activity_queue=None):
        self.device = device_name
        self.adb = device_serial
        self.activity_queue = activity_queue
        self.pause_event = control_pasue_callback
        self.page_manager_path = r"User_Data\Page_manager.json"
        self.ld_adb_controller = LdAdbController(device_serial=device_serial, local_output_file_path=local_output_file_path)
        self.device_config_dic = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")
        self.page_manager_writer = DevicesJson()

    


    def random_time(self, from_time=None, to_time=None):
        max_random_delay = self.device_config_dic.flatten_json()["Anythings Delay"]
        min_random_delay = max_random_delay/2

        if from_time is None:
            min_random_delay = min_random_delay
        else:
            min_random_delay = from_time

        if to_time is None:
            max_random_delay = max_random_delay
        else:
            max_random_delay = to_time

        time.sleep(random.uniform(float(min_random_delay), float(max_random_delay)))

    def check_is_paused(self):
        if not self.pause_event.is_set():
            self.pause_event.wait()

    def get_unique_to_list(self, list1, list2):
        return [item for item in list1 if item not in list2]
   
    def check_for_call_and_pause(self):
        self.random_time()
        self.pause_event.wait()
        
        call_decline_xpath = "//node[@content-desc='DECLINE']"
        self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)


    def check_for_call(self):
        call_decline_xpath = "//node[@content-desc='DECLINE']"
        self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)


    def get_profile_info(self,package_name="com.facebook.katana"):
        # Variables
        id_name = ""
        pages_list = []
        remove_list = ["Create Facebook profile","Go to Accounts Center","NavigationBar Search Icon","Close"]

        

        is_facebook_avlaible = self.ld_adb_controller.check_is_package_installed(package_name=package_name)
        if not is_facebook_avlaible:
            print("facebook not installed")
            activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Facebook not installed", f"Error:Facebook not installed","s")
            delete_callback(self.activity_queue,self.device)
            return (None, [None])
        

        self.check_for_call_and_pause()
        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Setting DND MODE Enable", f"None","ds")
        self.ld_adb_controller.set_dnd_mode()
        self.check_for_call_and_pause()
        
        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Setting DND MODE Enable Done", f"None","ds")
        
        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Starting APP", f"None","ds")
        self.ld_adb_controller.startApp(app_package=package_name)

        # Click on profile menu button 
        self.pause_event.wait()
        self.check_for_call()

        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Wating Loading Screen", f"None","ds")
        is_app_loaded = self.ld_adb_controller.check_loading_screen_gone(max_attempts=5,delay=2)
        if not is_app_loaded:
            activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Error At Fetching APP Not Loaded", f"Error:May be Accound Not logged In!!","s")
            print("Error at loading app")
            return (None, [None])
        
        profile_x_coord = 503
        profile_y_coord = 147

        menu_btn_xpath = "//node[contains(@content-desc,'Menu, tab')]"

        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Going To Menu", f"None","ds")
        is_menu_btn_clicked = self.ld_adb_controller.click_element_if_visibale(xpath_expr=menu_btn_xpath)

        if not is_menu_btn_clicked:
            self.pause_event.wait()
            self.check_for_call()
            self.ld_adb_controller.clickByCoordinate(x=profile_x_coord,y=profile_y_coord)

        self.pause_event.wait()
        self.check_for_call()


        #click on profile_downarrow button

        profile_down_arrow_x = 470
        profile_down_arrow_y = 241

        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Opening Prfile Switching ", f"None","ds")
        
        long_pressed_on_elment = self.ld_adb_controller.long_press_on_element_if_visible(xpath_expr=menu_btn_xpath)

        if not long_pressed_on_elment:
            self.ld_adb_controller.clickByCoordinate(x=profile_down_arrow_x,y=profile_down_arrow_y)



        self.pause_event.wait()
        self.check_for_call()

        # Dump UI to get current profile name 
        max_account_switching_delay = self.device_config_dic.flatten_json()["Account Switching Delay"]
        min_account_switching_delay = int(max_account_switching_delay) * 0.9

        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Switching Waiting", f"None","ds")
        self.random_time(from_time=min_account_switching_delay, to_time=max_account_switching_delay)

        self.pause_event.wait()
        self.check_for_call()
        time.sleep(random.uniform(5,8))

        crate_facebook_profile_xpath = "//node[@content-desc='Go to Accounts Center']"


        try:
                
                activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Getting All Profiles Name", f"None","ds")
                profile_nested_list = self.get_all_profile_names()
                profile_cleaned_list = []
                
                # Flatten the nested lists
                for sublist in profile_nested_list:
                    if isinstance(sublist, list):
                        profile_cleaned_list.extend(sublist)
                    else:
                        profile_cleaned_list.append(sublist)
                
                activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Cleaning Profiles Name", f"None","ds")
                # Remove None values and empty strings
                profile_cleaned_list = [item for item in profile_cleaned_list if item is not None and item != ""]
                
                activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Filtring Profiles Name", f"None","ds")
                         
                unique_profiles_names = list(dict.fromkeys(profile_cleaned_list))
                # Filter out items in remove_list
                pages_list = [item for item in unique_profiles_names if item not in remove_list]
                
                if pages_list:
                    id_name = pages_list.pop(0)
                else:
                    id_name = None
                    pages_list = []

                return (id_name, pages_list)
                
        except Exception as e:
                print(f"Error parsing XML: {e}")
                activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Error Parsing XML", f"Error:{e}","ds")
                         
                return (None, [None])
       

    def get_profile_names(self):
                    
            dumped_xml_path = self.ld_adb_controller.activity_dump_ui()
            
            if not dumped_xml_path:
                print("Failed to dump UI")
                return [None]
                
            try:
                tree = etree.parse(dumped_xml_path)
            
                # Get all profile nodes with content-desc
                all_profile_xpath = "//node[@content-desc and @content-desc!='']"
                profile_list = tree.xpath(all_profile_xpath)

                # Extract content-desc values
                profile_cleaned_list = []
                for item in profile_list:
                    content_desc = item.get("content-desc")
                    if content_desc:
                        # Split by comma if needed
                        cleaned_item = content_desc.split(',')[0]
                        profile_cleaned_list.append(cleaned_item)
                
                return profile_cleaned_list
            except Exception as e :
                print(f"Faild to get profile info due to :{e}")
                return [None]
            
    def get_all_profile_names(self):

        profiles_names=[]
        is_see_all_btn_found = False

        for l in range(7):
            profiles_name= self.get_profile_names()
            profiles_names.append(profiles_name)
            self.check_for_call_and_pause()
            self.ld_adb_controller.ScrollByCoordinate(x_start=random.uniform(300,400),y_start=random.uniform(700,800),x_end=random.uniform(300,400),y_end=random.uniform(600,650))
            self.check_for_call_and_pause()
            is_see_all_btn_found = self.ld_adb_controller.click_element_if_visibale(xpath_expr="//node[contains(@content-desc,'See all')]")
            if is_see_all_btn_found:
                break

        if is_see_all_btn_found:
            for l in range(7):
                self.check_for_call_and_pause()
                profiles_name= self.get_profile_names()
                profiles_names.append(profiles_name)
                self.check_for_call_and_pause()
                self.ld_adb_controller.ScrollByCoordinate(x_start=random.uniform(300,400),y_start=random.uniform(700,800),x_end=random.uniform(300,400),y_end=random.uniform(600,650))
        
        return profiles_names

    def count_id_information_entries(self):
        """
        Count the total number of Id_information entries in the JSON file.

        Returns:
            int: Count of Id_information entries
        """
        try:
            # Read the file content
            with open(self.page_manager_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Check if any entries exist
            if not data:
                return 0

            # Pattern to match "Id_information.{n}" format
            id_info_pattern = re.compile(r'Id_information\.(\d+)')

            # Count entries
            count = 0
            for key in data.keys():
                if id_info_pattern.match(key) or key == "Id_information.1":
                    count += 1

            return count

        except Exception:
            
            return None


    def Remove_matchin_ld_frame_and_reindex(self, ld_name_to_remove):
        """
        Read the JSON file, remove entries with matching Ld_name, and reindex the remaining entries.
        Specifically designed for JSON with 'Id_information.1' format keys.

        Args:
            ld_name_to_remove (str): The Ld_name to match for removal

        Returns:
            tuple: (bool success, str message)
        """
        try:
            # Read the file content
            with open(self.page_manager_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Check if any entries exist
            if not data:
                return False, "JSON file is empty"

            # Simple pattern for "Id_information.1" format
            id_info_pattern = re.compile(r'Id_information\.(\d+)')
            id_entries = {}
            other_entries = {}

            # Sort entries into id_entries and other_entries
            for key, value in data.items():
                match = id_info_pattern.match(key)
                if match:
                    # This is an Id_information entry
                    index = int(match.group(1))
                    id_entries[index] = (key, value)
                else:
                    # This is some other entry
                    other_entries[key] = value

            # Track removed entries
            removed_entries = []
            # Track entries to keep
            kept_entries = []

            # Filter out entries with matching Ld_name
            for index, (key, value) in sorted(id_entries.items()):
                if isinstance(value, dict) and "Ld_name" in value:
                    if value["Ld_name"] == ld_name_to_remove:
                        removed_entries.append(f"{key} (ID: {value.get('id_name', 'unknown')})")
                    else:
                        kept_entries.append((index, value))

            # If no entries were removed, return with message
            if not removed_entries:
                return False, f"No entries with Ld_name '{ld_name_to_remove}' found"

            # Create new data structure with reindexed Id_information entries
            new_data = {}

            # Add non-Id_information entries first
            for key, value in other_entries.items():
                new_data[key] = value

            # Add reindexed Id_information entries
            for new_index, (_, value) in enumerate(kept_entries, 1):
                new_key = f"Id_information.{new_index}"
                new_data[new_key] = value

 

            # Save the updated data back to the file
            with open(self.page_manager_path, 'w', encoding='utf-8') as file:
                json.dump(new_data, file, indent=4)

            return True, f"Removed {len(removed_entries)} entries: {', '.join(removed_entries)}\nReindexed remaining {len(kept_entries)} entries"

        except json.JSONDecodeError:
            return False, "Invalid JSON format in the file"
        except Exception as e:
            return False, f"Error processing file: {str(e)}"
    
    def create_id_with_pages(self, idx, id_name, package_name, ld_name, upload=False, page_names=None):
        """
        Create an ID dictionary and add multiple pages to its pages_information dictionary.

        Args:
            idx: Index for the ID
            id_name: Name of the ID
            package_name: Package name
            ld_name: LD name
            upload: Upload flag (default: False)
            page_names: List of page names to add (default: None)

        Returns:
            Dictionary with ID frame and pages information
        """
        # Create the base ID frame
        id_dict = self.page_manager_writer.create_id_frame(idx, id_name, package_name, ld_name, upload)

        # Get the ID key (e.g., "Id_information.1")
        id_key = f"Id_information.{str(idx)}"

        # Update the id_name, package_name, and ld_name
        id_dict[id_key]["id_name"] = id_name
        id_dict[id_key]["package_name"] = package_name
        id_dict[id_key]["Ld_name"] = ld_name
        id_dict[id_key]["Upload"] = upload

        
        if page_names and isinstance(page_names, list):
           
            pages_information = {}

            for i, page_name in enumerate(page_names, start=1):
                
                page_data = self.page_manager_writer.add_page_data(i, self.ld_adb_controller.clean_name(page_name)) 

                
                pages_information.update(page_data)

            id_dict[id_key]["pages_information"] = pages_information

        return id_dict

    def save_profile_info(self,package_name="com.facebook.katana",ld_name=""):


        #get id name and page names from ld player 
        id_name,pages_list = self.get_profile_info(package_name=package_name)

        if id_name == None:
            activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Error at fatcing", f"Error","ds")
            delete_callback(self.activity_queue, self.device)
            print("Error at fatcing")
            return
        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Creating Backup File", f"None","ds")
        # Create a backup of the original file
        backup_path = self.page_manager_path + ".bak"
        shutil.copy2(self.page_manager_path, backup_path)

        #remove any same ld id frame 
        success, message = self.Remove_matchin_ld_frame_and_reindex(ld_name_to_remove=ld_name)

        if success:
            activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Removed Matcing Ld", f"None","ds")
        print(f"{'Removed Matcing Ld-Player...' if success else 'No Matching Ld-Player Found.... '}")
        print(f"Logs: {message}")

        #get total number of id entries
        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Counting Current LD ", f"None","ds")
        total_ids = self.count_id_information_entries()
        new_id_idx = total_ids + 1

        
        activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Saving Confg To Page Manager", f"None","ds")
        existing_data = {}
        #save id name and page to page manager 
        if id_name != None and len(pages_list) !=0:

            if os.path.exists(self.page_manager_path) and os.path.getsize(self.page_manager_path) > 0:
                try:
                    with open(self.page_manager_path, 'r', encoding='utf-8') as file:
                        existing_data = json.load(file)
                except json.JSONDecodeError:
                    print(f"Warning: {self.page_manager_path} contains invalid JSON. Starting with empty data.")
                    delete_callback(self.activity_queue, self.device)

            new_id_data = self.create_id_with_pages(idx=new_id_idx,id_name=id_name, package_name=package_name,ld_name=ld_name,page_names=pages_list)

            #merge new data with existing data
            merged_data = {**existing_data, **new_id_data}

            with open(self.page_manager_path, 'w', encoding='utf-8') as file:
                json.dump(merged_data, file, indent=4)

            print(f"Successfully saved ID '{id_name}' with {len(pages_list) if pages_list else 0} pages to {self.page_manager_path}")
            activity_callback(self.activity_queue, self.device, "Geni", 
                         id_name, "Fatched Successfully and  saved ", f"None","s")
            delete_callback(self.activity_queue, self.device)

            return merged_data

    

    





if __name__ == "__main__":
    from multiprocessing import Manager

    manager = Manager()
    control_pause = manager.Event()
    control_pause.set()

    test_run = IdAndPageInfoFetcher(
        device_serial="emulator-5554",
        local_output_file_path=r"E:\facebook_ld\raushan\main_folder",
        control_pasue_callback=control_pause
    )
    
    message = test_run.save_profile_info(ld_name="LDPlayer0")