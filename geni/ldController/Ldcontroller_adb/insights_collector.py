import time
import random
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import os
from datetime import datetime
import shutil
import json  # Make sure to import json if not already imported

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




#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ldController.Ldcontroller_adb.LdAdb import *

try:
    from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten
except Exception as e:
    print(e)


class AdbProfileInsightsUpdate():
    def __init__(self, control_pasue_callback, page_manager_path, device_name=None, device_serial=None, local_output_file_path="",activity_queue=None):
        self.device = device_name
        self.adb = device_serial
        self.activity_queue = activity_queue
        self.pause_event = control_pasue_callback
        self.ld_adb_controller = LdAdbController(device_serial=device_serial, local_output_file_path=local_output_file_path)
        self.page_manager_path = page_manager_path

        self.device_config_dic = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")

    def random_time(self, from_time=None, to_time=None):
        max_random_delay = self.device_config_dic.flatten_json()["Anythings Delay"]
        min_random_delay = max_random_delay / 2

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
        if self.pause_event is not None:
            if not self.pause_event.is_set():
                self.pause_event.wait()


    def check_for_call(self):

        call_decline_xpath ="//node[@content-desc='DECLINE']"

        self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)

    def check_for_call_and_pause(self,id_or_page="id"):

        self.random_time()
        self.pause_event.wait()
        
        if id_or_page == "id":
            call_decline_xpath ="//node[@content-desc='DECLINE']"
            self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)
            

    def clean_string(self,value, substrings_to_remove=None):
        if substrings_to_remove is None:
            substrings_to_remove = []
        for sub in substrings_to_remove:
            value = value.replace(sub, "")
        
        return value.replace("\u00a0", "").strip()


    def profile_insight_update(self, id_information_idx, profle_name,id_or_page):
        Followers = 0
        Views = 0
        Engagement = 0
        view_insight_image_path = ""
        engagement_insight_image_path = ""
        audience_insight_image_path = ""
        setup_avlaible = False

        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
        self.check_for_call_and_pause(id_or_page=id_or_page)


        # click on plus buttn 
        profile_x_coord = 503
        profile_y_coord = 147
        go_to_profile_from_menu_x_coord = 220
        go_to_profile_from_menu_y_coord = 240

        #self.ld_adb_controller.clickByCoordinate(x=profile_x_coord, y=profile_y_coord)
        
        go_to_profile_tab_btn_xpath="//node[@content-desc='Go to profile']"
        menu_btn_xpath = "//node[contains(@content-desc,'Menu, tab')]"



        self.check_for_call_and_pause(id_or_page=id_or_page)
        activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Going to profile", "None","ds")
        click_on_profile_tab = self.ld_adb_controller.click_element_if_visibale(xpath_expr=go_to_profile_tab_btn_xpath)
        if not click_on_profile_tab:
            self.check_for_call_and_pause(id_or_page=id_or_page)
            is_menu_btn_clicked = self.ld_adb_controller.click_element_if_visibale(xpath_expr=menu_btn_xpath)
            if not is_menu_btn_clicked:
                self.check_for_call_and_pause(id_or_page=id_or_page)
                self.ld_adb_controller.clickByCoordinate(x=profile_x_coord,y=profile_y_coord)
            self.check_for_call_and_pause(id_or_page=id_or_page)
            self.ld_adb_controller.clickByCoordinate(x=go_to_profile_from_menu_x_coord,y=go_to_profile_from_menu_y_coord)





        # click on reels btn
        pro_dashboard_xpath = "//node[@content-desc='Professional dashboard']"
        self.check_for_call_and_pause(id_or_page=id_or_page)
        activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Going to Professional Dashboard", "None","ds")
        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=2,delay=0)
        is_clicked = self.ld_adb_controller.click_element_if_visibale(xpath_expr=pro_dashboard_xpath)

        if not is_clicked:
            print("Cant find Dashbord Btn")
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Professional Dashboard btn not found", "Error","s")
            self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
            return

        self.check_for_call_and_pause(id_or_page=id_or_page)
        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=1,delay=0)
        # triple click on gallery btn to avoid error 
        # check if there is discard button
        home_btn_xpath_expr = "//node[@text='Home']"
        insight_btn_xpath = "//node[@text='Insights']"
        see_all_btn_xpath = "//node[@text='See all']"
        is_home = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=insight_btn_xpath)

        if is_home:

            self.check_for_call_and_pause(id_or_page=id_or_page)
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Collecting Profile Stats", "None","ds")
            self.random_time(from_time=3,to_time=4)
            #self.ld_adb_controller.click_element_btn_number(see_all_btn_xpath, btn_number=1)
            self.ld_adb_controller.clickByCoordinate(x=184,y=140)

            self.check_for_call_and_pause(id_or_page=id_or_page)

            see_all_btn_xpath_expr = "//node[@text='See all']"
            self.ld_adb_controller.click_element(see_all_btn_xpath_expr)

            self.check_for_call_and_pause(id_or_page=id_or_page)

            # swipe down to refresh 
            self.ld_adb_controller.ScrollByCoordinate(x_start=random.uniform(225, 230),
                                                        y_start=random.uniform(420, 427),
                                                        x_end=random.uniform(260, 271),
                                                        y_end=random.uniform(580, 595))
            
            self.check_for_call_and_pause(id_or_page=id_or_page)

            views_xpath = "//node[contains(@text,' Views')]"
            Engagement_xpath = "//node[contains(@text,' Engagement')]"
            Follower_xpath = "//node[contains(@text,' Total followers')]"

            views_value = self.ld_adb_controller.find_and_get_element_value(views_xpath, value_key="text")
            Views = self.clean_string(value=views_value,substrings_to_remove="Views")
            
            self.check_for_call_and_pause(id_or_page=id_or_page)
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Taking Views ScreenShot", "None","ds")
            view_insight_image_path = self.ld_adb_controller.TakeScreenCap(Image_name="views.png", folder_name="insigths", sub_folder_name=profle_name)

            self.check_for_call_and_pause(id_or_page=id_or_page)

            self.ld_adb_controller.click_element(xpath_expr="//node[@text='Engagement']")

            self.check_for_call_and_pause(id_or_page=id_or_page)

            # swipe down to refresh 
            self.ld_adb_controller.ScrollByCoordinate(x_start=random.uniform(225, 230),
                                                        y_start=random.uniform(420, 427),
                                                        x_end=random.uniform(260, 271),
                                                        y_end=random.uniform(580, 595))
            
            self.check_for_call_and_pause(id_or_page=id_or_page)

            Engagement_value = self.ld_adb_controller.find_and_get_element_value(Engagement_xpath, value_key="text")
            Engagement = self.clean_string(value=Engagement_value,substrings_to_remove="Engagement")

            self.check_for_call_and_pause(id_or_page=id_or_page)
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Taking Engagement ScreenShot", "None","ds")
            engagement_insight_image_path = self.ld_adb_controller.TakeScreenCap(Image_name="Engagement.png", folder_name="insigths", sub_folder_name=profle_name)

            self.check_for_call_and_pause(id_or_page=id_or_page)

            self.ld_adb_controller.click_element("//node[@text='Audience']")

            self.check_for_call_and_pause(id_or_page=id_or_page)

            # swipe down to refresh 
            self.ld_adb_controller.ScrollByCoordinate(x_start=random.uniform(225, 230),
                                                        y_start=random.uniform(420, 427),
                                                        x_end=random.uniform(260, 271),
                                                        y_end=random.uniform(580, 595))
            
            self.check_for_call_and_pause(id_or_page=id_or_page)

            Followers_value = self.ld_adb_controller.find_and_get_element_value(Follower_xpath, value_key="text")

            Followers =self.clean_string(value=Followers_value,substrings_to_remove="Total followers")
            

            self.check_for_call_and_pause(id_or_page=id_or_page)
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Taking Audience ScreenShot", "None","ds")
            audience_insight_image_path = self.ld_adb_controller.TakeScreenCap(Image_name="audience.png", folder_name="insigths", sub_folder_name=profle_name)

            self.check_for_call_and_pause(id_or_page=id_or_page)
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Checking Setup Avl", "None","ds")
            self.ld_adb_controller.BackButton()

            self.check_for_call_and_pause(id_or_page=id_or_page)

            self.ld_adb_controller.clickByCoordinate(x=531, y=138)

            self.check_for_call_and_pause(id_or_page=id_or_page)

            # this will check that any setup available for setup 
            avlaible_to_setup = "//node[@text='Available to set up']"
            is_setup_avlaible = self.ld_adb_controller.check_loading_screen_gone(avlaible_to_setup)
            if is_setup_avlaible:
                setup_avlaible = True

            self.check_for_call_and_pause(id_or_page=id_or_page)
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Saving Profile Stats to geni", "None","ds")
            new_insights = (Followers, Views, Engagement, setup_avlaible)
            screen_cap_path_list = [view_insight_image_path, engagement_insight_image_path, audience_insight_image_path]

            # collect insight data and insert into json
            self.insert_insight_by_profile(frame_idx=id_information_idx, profile_name=profle_name,
                                           screen_cap_path_list=screen_cap_path_list, new_insights=new_insights)
            
            self.check_for_call_and_pause(id_or_page=id_or_page)

            self.ld_adb_controller.BackButton()

            self.check_for_call_and_pause(id_or_page=id_or_page)

            self.ld_adb_controller.BackButton()

            self.check_for_call_and_pause(id_or_page=id_or_page)
            
            self.random_time(from_time=int(3) / 2, to_time=3)

            self.check_for_call_and_pause(id_or_page=id_or_page)

            self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Insight updating Done", "None","s")
            print("Insight updating Done")


        else:

            print("failed to update insights")
            activity_callback(self.activity_queue, self.device, "Facebook", profle_name, "Insight updating ", "Error","s")

    def insert_insight_by_profile(self, frame_idx, profile_name, screen_cap_path_list=[], new_insights=(0, 0, 0, False)):
        """
        Update insights for a given profile (either by top-level ID Name or a page's Page Name).

        :param frame_idx: The key to locate the record in the JSON.
        :param profile_name: The profile name to update insights.
        :param screen_cap_path_list: A list of screenshot paths.
        :param new_insights: A tuple containing (Followers, Views, Engagement, is_setup_available).
        :return: True if update was successful, otherwise False.
        """
        Followers, Views, Engagement, is_setup_available = new_insights

        # Read existing data from file.
        with open(self.page_manager_path, mode="r", encoding="utf-8") as file:
            page_manager_data = json.load(file)

        record = page_manager_data.get(frame_idx)
        if not record:
            print("No record found with the given frame index.")
            return False

        updated = False

        # Check top-level ID Name.
        if record.get("id_name") == profile_name:
            if "ID_info" in record:
                record["ID_info"]["Insights"]["Followers"] = Followers
                record["ID_info"]["Insights"]["Views"] = Views
                record["ID_info"]["Insights"]["Engagement"] = Engagement
                record["ID_info"]["Insights"]["is_setup_available"] = is_setup_available
                record["ID_info"]["Insights"]["Screenshot Images"] = screen_cap_path_list
                print(f"Updated insights for ID Name: {profile_name}")
                updated = True
        else:
            # Otherwise check each page in "pages_information".
            pages = record.get("pages_information", {})
            for page_key, page in pages.items():
                if page.get("Page_Name") == profile_name:
                    page["Insights"]["Followers"] = Followers
                    page["Insights"]["Views"] = Views
                    page["Insights"]["Engagement"] = Engagement
                    page["Insights"]["is_setup_available"] = is_setup_available
                    page["Insights"]["Screenshot Images"] = screen_cap_path_list
                    print(f"Updated insights for Page Name: {profile_name}")
                    updated = True
                    break

        if not updated:
            print(f"No matching ID Name or Page Name found for: {profile_name}")
            return False

        with open(self.page_manager_path, mode="w", encoding="utf-8") as file:
            json.dump(page_manager_data, file, indent=4)
            print("File updated successfully.")

        return True

    def profile_insight_update_after_loading_screen(self, profile_name, id_information_idx, app_package,id_or_page,
                                                     after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                                                     max_attempts=4, delay=5, max_restart_attempts=5,
                                                     switch_profile_attempts=3, switch_profile_delay=5):
        """
        Attempts to upload a reel after checking if the app has loaded properly.
        If loading screen check fails, it restarts the app and tries again until successful.

        Now includes retry logic for switching profiles.
        """
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Starting App", "None","ds")
        self.ld_adb_controller.startApp()
        restart_attempts = 0

        while restart_attempts < max_restart_attempts:
            print(f"Checking if app is loaded (attempt {restart_attempts + 1}/{max_restart_attempts})")

            self.pause_event.wait()
            self.check_for_call()
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Loading Screen", "None","ds")
            # Check if the screen has loaded by looking for the specified element
            if self.ld_adb_controller.check_loading_screen_gone(
                after_loading_screen_element=after_loading_screen_element,
                max_attempts=max_attempts,
                delay=delay
            ):
                print("App loaded successfully, Updating insights")
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "App loaded", "None","ds")
                self.profile_insight_update(id_information_idx=id_information_idx, profle_name=profile_name,id_or_page=id_or_page)
                return True

            print("App not loaded properly, restarting app...")
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "App not loaded", "None","ds")
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Restarting", "None","ds")
            self.ld_adb_controller.stopApp(app_package=app_package)
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Waiting", "None","ds")
            self.random_time(from_time=2, to_time=5)
            self.check_for_call()
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Starting APP", "None","ds")
            self.ld_adb_controller.startApp(app_package=app_package)

            switch_attempt = 0
            while switch_attempt < switch_profile_attempts:

                self.pause_event.wait()
                self.check_for_call()
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Swtching Profile", "None","ds")
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                switched_profile = self.ld_adb_controller.switch_profle_to(profile_name=profile_name,cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page="id")
                if switched_profile:
                    print("Profile switched successfully.")
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Profile switched", "None","ds")
                    break
                else:
                    print(f"Profile switch failed, attempt {switch_attempt + 1}/{switch_profile_attempts}. Retrying...")
                    time.sleep(switch_profile_delay)
                    switch_attempt += 1

            if not switched_profile:
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Profile switched failed ", "Error","s")
                print("Failed to switch profile after multiple attempts.")
                restart_attempts += 1

        print(f"Failed to load app properly after {max_restart_attempts} restart attempts")
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Insight Upsate ", "Error:App not loaded","s")
        return False



    def profile_insight_update_page_list(self, id_information_idx, Profile_lists=[], app_package="com.facebook.katana"):
        self.pause_event.wait()

        self.ld_adb_controller.startApp(app_package="com.facebook.katana")
        after_loading_screen_element = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"
        home_screen = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=after_loading_screen_element)

        self.check_for_call_and_pause()

        if home_screen:

            self.check_for_call_and_pause()

            while len(Profile_lists) > 0:

                self.check_for_call()
                self.pause_event.wait()

                current_profile,id_or_page = Profile_lists.pop()

                self.ld_adb_controller.startApp(app_package)

                self.check_for_call()
                self.pause_event.wait()
                
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                check_profile = self.ld_adb_controller.switch_profle_to(profile_name=current_profile,cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page="id")

                self.check_for_call()
                self.pause_event.wait()
                
                if check_profile:

                    try:
                        self.profile_insight_update_after_loading_screen(
                            profile_name=current_profile,
                            id_information_idx=id_information_idx,
                            id_or_page=id_or_page,
                            app_package=app_package,
                            after_loading_screen_element=after_loading_screen_element,
                            max_attempts=4,
                            max_restart_attempts=5,
                            delay=2
                        )
                        self.pause_event.wait()
                        self.check_for_call()
                    except Exception as e:
                        print(f"Error Updating Insight On #{current_profile} Profile")
                        self.ld_adb_controller.stopApp(app_package=app_package)
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.startApp(app_package=app_package)
                        self.check_for_call_and_pause(id_or_page)
                        

            self.random_time(from_time=8, to_time=14)

            self.pause_event.wait()
            self.check_for_call()
            
            self.ld_adb_controller.HomeButton()


if __name__ == "__main__":
    import threading
    c = threading.Event()
    c.set()

    test_run = AdbProfileInsightsUpdate(
        device_serial="emulator-5554",
        control_pasue_callback=c,
        local_output_file_path=r"E:\facebook_ld\ld_player0\main_folder",
        page_manager_path=r"User_Data\Page_manager.json"
    ) 

    profile_list = [("Only Gaming","page"),("Brucelee","page"),("Kajal Kumari","id")] #, 
    id_information = "Id_information.1"

    test_run.profile_insight_update_page_list(Profile_lists=profile_list, id_information_idx=id_information, app_package="com.facebook.katana")
