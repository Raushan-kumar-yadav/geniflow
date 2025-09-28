import time
import random
from lxml import etree
import xml.etree.ElementTree as ET
import sys
from pathlib import Path
import os
import shutil


#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ldController.Ldcontroller_adb.LdAdb import *

try:
    
    from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten


except Exception as e :
    print(e)



class AdbImageUploadASW():

    def __init__(self, control_pasue_callback,device_name=None, device_serial = None,local_output_file_path=""):
        self.device = device_name
        self.adb = device_serial
        self.pause_event = control_pasue_callback
        self.ld_adb_controller = LdAdbController(device_serial=device_serial,local_output_file_path=local_output_file_path)

        self.device_config_dic = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")


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

    


    def check_is_paused(self):

        if not self.pause_event.is_set():

            self.pause_event.wait()


    def check_for_call(self):

        call_decline_xpath ="//node[@content-desc='DECLINE']"

        self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)


        
    def check_for_call_and_pause(self,id_of_page ="id"):

        self.random_time()
        self.pause_event.wait()
        
        if id_of_page == "id":
            call_decline_xpath ="//node[@content-desc='DECLINE']"
            self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)



        
    def set_schedule_time(self,day,hour,min,am_pm,id_or_page):
        #click on schedule for later by coordinate 

        scheduling_optons_btn_xpath = "//node[contains(@content-desc,'Scheduling options')]"

        is_scheduling_seted = "//node[contains(@content-desc,'Scheduling options, Post now')]" #if its return true means scheduling not seted if false means set

        schedule_for_later_x_coord = 240
        schedule_for_later_y_coord = 350

        day_picker_element_xpath ="//node[@resource-id='android:id/date_picker_day_picker']"
        ok_btn_xpath = "//node[@text='OK']"
        custom_day_btn_xpath =f"//node[@text='{day}']"



        am_pm_lower = str(am_pm).lower()
        f_am_pm_text = "AM"
        if am_pm_lower == "am":
            f_am_pm_text = "AM"
        else:
            f_am_pm_text ="PM"
        am_pm_xpath = f"//node[@text='{f_am_pm_text}']"




        is_scheduling_optoin_visiable = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=scheduling_optons_btn_xpath)

        

        if is_scheduling_optoin_visiable:
            
            print("started scheduling post")

            self.ld_adb_controller.click_element(xpath_expr=scheduling_optons_btn_xpath)

            self.check_for_call_and_pause(id_or_page)

            self.ld_adb_controller.clickByCoordinate(x=schedule_for_later_x_coord,y=schedule_for_later_y_coord)

            self.check_for_call_and_pause(id_or_page)

            is_day_picker_visiable = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=day_picker_element_xpath)
            
            if not is_day_picker_visiable:
                self.ld_adb_controller.clickByCoordinate(x=260,y=390)
                is_day_picker_visiable = True
            
            if is_day_picker_visiable:
                print("Current day ")
                
                if day == None:
                    print("current day selected")
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.click_element(xpath_expr=ok_btn_xpath)
                else:
                    print("custom day selected")
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.click_element(xpath_expr=custom_day_btn_xpath)
                    self.check_for_call_and_pause(id_or_page)

                    self.ld_adb_controller.click_element(xpath_expr=ok_btn_xpath)


                self.check_for_call_and_pause(id_or_page)
                
                self.ld_adb_controller.click_element(xpath_expr="//node[@content-desc='Switch to text input mode for the time input.']")

                self.check_for_call_and_pause(id_or_page)

                self.ld_adb_controller.click_element(xpath_expr="//node[@resource-id='android:id/input_hour']")

                self.check_for_call_and_pause(id_or_page)

                self.ld_adb_controller.Delete_text_from_back()

                self.check_for_call_and_pause(id_or_page)

                self.ld_adb_controller.PullText(Text=hour)

                self.check_for_call_and_pause(id_or_page)

                self.ld_adb_controller.click_element(xpath_expr="//node[@resource-id='android:id/input_minute']")

                self.check_for_call_and_pause(id_or_page)
                
                self.ld_adb_controller.Delete_text_from_back()
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.PullText(Text=min)

                self.check_for_call_and_pause(id_or_page)

                self.ld_adb_controller.click_element(xpath_expr="//node[@resource-id='android:id/am_pm_spinner']")

                self.check_for_call_and_pause(id_or_page)

                self.ld_adb_controller.click_element(xpath_expr=am_pm_xpath)

                self.check_for_call_and_pause(id_or_page)

                self.ld_adb_controller.click_element(xpath_expr=ok_btn_xpath)

                self.check_for_call_and_pause(id_or_page)

                save_btn_xpath = "//node[@content-desc='Save']"
                is_save_btn_visiable = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=save_btn_xpath,max_attempts=2)

                if is_save_btn_visiable:
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.click_element(xpath_expr=save_btn_xpath)
                else:
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.click_element(xpath_expr="//node[@content-desc='Back']")
            else:
                print("do something else ")


    def test_schedule_time(self, time_lists):
        is_scheduling_seted_xpath = (
            "//node[contains(@content-desc,'Scheduling options, Post now')]"
        )
        queue = list(time_lists)  

        while queue:
            day, hour, minute, am_pm = queue.pop(0)
            print("Trying schedule:", day, hour, minute, am_pm)

            is_scheduled_success = (
                self.ld_adb_controller
                    .check_loading_screen_gone(after_loading_screen_element=is_scheduling_seted_xpath)
            )

            if is_scheduled_success:
                self.set_schedule_time(day=day, hour=hour, min=minute, am_pm=am_pm)
                return True
            else:
                print("Schedule failed, next…")

        return False

            
                

    def Reel_upload(self,profle_name,image_caption_list,id_or_page,caption_from_orgvid=True,schdule_time_list=[],is_schedule_enable=False):

        current_schdule_done = False
        self.pause_event.wait()
        self.check_for_call()

        if image_caption_list is None:
            image_caption_list = []

        if schdule_time_list is None:
            schdule_time_list = []

        # Create a copy of lists to avoid modifying the original ones
        captions = image_caption_list.copy()
        available_schedule_times = schdule_time_list.copy()  # Track remaining available times
        # Default caption if list is too short
        default_caption = "image post"
        # Determine scheduling mode
        if is_schedule_enable and available_schedule_times:
            # We'll use the available scheduling times
            pass
        elif not is_schedule_enable or not available_schedule_times:
            # If scheduling not enabled or no times provided, use immediate posting
            available_schedule_times = [(None, "00", "00", "PM")]
        # Counter for images
        image_num = 1

        

        while available_schedule_times:  # Process at least one image
            # Get caption for this image (or use default if none available)
            image_caption = default_caption
            if captions:
                image_caption = captions.pop()
           

            self.ld_adb_controller.switch_appliction()
            self.check_for_call_and_pause(id_or_page)
                                
            self.ld_adb_controller.ScrollByCoordinate(x_start=200,y_start=500,x_end=200,y_end=800,Duration=500) #swipe down to refrace
            is_cliced_on_profile_album = self.ld_adb_controller.verify_opend_folder_and_select_folder_in_file(profile_name=profle_name,folder_subfix="_img",folder_type="image",cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)

            if is_cliced_on_profile_album:
            
                self.check_for_call_and_pause(id_or_page)
                
                self.ld_adb_controller.ScrollByCoordinate(x_start=200,y_start=500,x_end=200,y_end=800,Duration=500) #swipe down to refrace
                self.check_for_call_and_pause(id_or_page)
                is_image_avl = self.ld_adb_controller.check_content_btn_number_visiable(xpath_expr="//node[@resource-id='android:id/title']",btn_number=image_num)
                if not is_image_avl:
                    print("Image schduling faild due to Image not avlaible on facebook gallery")
                    self.ld_adb_controller.BackButton()
                    available_schedule_times.clear()
                    self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                    return
                else:
                    from_image_caption = self.ld_adb_controller.select_folder_form_file_and_share_and_return_caption(video_num=image_num,share_to="image",profile_name=profle_name,folder_subfix="_img",folder_type="image",check_for_pause_and_call=self.check_for_call_and_pause,id_or_page=id_or_page)
                    if caption_from_orgvid:
                        image_caption = from_image_caption
                self.check_for_call_and_pause(id_or_page)
                #click on next btn

                next_btn_x_coor = 480
                next_btn_y_coor = 66
                next_btn_xpath = "//node[@content-desc='NEXT']"
                is_next_btn_visible = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=next_btn_xpath,max_attempts=10)

                self.ld_adb_controller.long_scroll_down_num(scroll_down_num=2,delay=1,check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                if is_next_btn_visible:
                    
                    self.ld_adb_controller.click_element_if_visibale(xpath_expr="//node[contains(@hint,'Say something about this photo')]")
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.PullText(str(image_caption))
                    print(f"image caption for profile {profle_name}: {image_caption}")
                    self.random_time(from_time=0.5, to_time=1)
                    self.ld_adb_controller.click_on_cursor()
                    self.random_time(from_time=2, to_time=4)
                    self.pause_event.wait()
                    self.check_for_call()
                
                    is_next_btn_clicked = self.ld_adb_controller.click_element_if_visibale(xpath_expr=next_btn_xpath)
                    if not is_next_btn_clicked:
                        self.ld_adb_controller.clickByCoordinate(x=next_btn_x_coor,y=next_btn_y_coor)
                    self.ld_adb_controller.long_scroll_down_num(scroll_down_num=2,delay=1,check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                else:
                    self.check_for_call_and_pause(id_or_page)
                    available_schedule_times.clear()
                    self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.BackButton()

                    return
                

                self.pause_event.wait()
                self.check_for_call()

                is_post_now_btn = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element="//node[@content-desc='POST']",max_attempts=3,delay=2)

                if is_post_now_btn:
                
                    #run schdule method to add schdule time
                    is_scheduling_set_xpath = ("//node[contains(@content-desc,'Scheduling options, Post now')]")
                    
                    if is_schedule_enable and len(available_schedule_times) > 0:
                        # Create a queue of scheduling times to try for this post
                        queue = available_schedule_times.copy()  # Copy the available times
                        scheduling_succeeded = False
                        used_schedule = None  # Track which schedule time worked

                        # Try scheduling times until one works or we run out of options
                        while queue:

                            current_schedule = queue.pop(0)  # Remove and get the next schedule to try
                            used_schedule = current_schedule  # Track the schedule we're trying

                            day, hour, minute, am_pm = current_schedule
                            print(f"Trying schedule: {day} {hour}:{minute} {am_pm}")
                            self.set_schedule_time(day=day, hour=hour, min=minute, am_pm=am_pm,id_or_page=id_or_page)
                            self.check_for_call_and_pause(id_or_page)

                            is_scheduled_success = self.ld_adb_controller.check_loading_screen_gone(
                                after_loading_screen_element=is_scheduling_set_xpath
                            )

                            if not is_scheduled_success:
                                print("Scheduling Done")
                                scheduling_succeeded = True

                                # Remove the successful schedule from available_schedule_times
                                if used_schedule and used_schedule in available_schedule_times:
                                    available_schedule_times.remove(used_schedule)
                                    print(f"Removed used schedule time. Remaining times: {len(available_schedule_times)}")
                                break
                            else:
                                if used_schedule and used_schedule in available_schedule_times:
                                    available_schedule_times.remove(used_schedule)
                                    print(f"Removed used schedule time. Remaining times: {len(available_schedule_times)}")

                        if not scheduling_succeeded:
                            print("Tried all the schedule times but none of them worked...Cancling scheduleing")
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.BackButton()
                            self.check_for_call_and_pause(id_or_page)
                            self.random_time(from_time=3,to_time=5)
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                            self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                            return
                            
                        else:
                            #click on share now btn 
                            post_btn_xpath = "//node[@content-desc='POST']"
                            self.ld_adb_controller.click_element(xpath_expr=post_btn_xpath,max_attempts=2)
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                            self.ld_adb_controller.check_popup_on_home_fb() #we can remove it 
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                            reels_uploding_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                            #image_num += 1
                            self.random_time(from_time=int(reels_uploding_delay)*0.9,
                                             to_time=reels_uploding_delay)
                           
                            self.pause_event.wait()
                            self.check_for_call()
                            self.ld_adb_controller.switch_appliction()
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.select_folder_form_file_and_delete(video_num=image_num,profile_name=profle_name,folder_subfix="_img",folder_type="image",check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                            self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                            print("Reel uploading Done")
                            self.check_for_call()
                    else:

                        available_schedule_times.pop()
                        #click on share now btn 
                        post_btn_xpath = "//node[@content-desc='POST']"
                        self.ld_adb_controller.click_element(xpath_expr=post_btn_xpath,max_attempts=2)
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                        self.ld_adb_controller.check_popup_on_home_fb()
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                        reels_uploding_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                        #image_num += 1
                        self.random_time(from_time=int(reels_uploding_delay)*0.9,
                                         to_time=reels_uploding_delay)
                        
                        self.pause_event.wait()
                        self.check_for_call()
                        self.ld_adb_controller.switch_appliction()
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.select_folder_form_file_and_delete(video_num=image_num,profile_name=profle_name,folder_subfix="_img",folder_type="image",check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                        print("Reel uploading Done")
                        self.check_for_call()
                else:
                    print("Error at Post button")
                    available_schedule_times.clear()
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.BackButton()
                    self.check_for_call_and_pause(id_or_page)
                    self.random_time(from_time=3,to_time=5)
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                    return
                    
            else:
                print("Folder not avlaible to upload from")
                available_schedule_times.clear()
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                return

                    
                    
    

    def reels_upload_after_loading_screen(self, profile_name, image_captions_list , app_package, id_or_page,schdule_time_list=[],is_schdule_enable=False,caption_from_orgvid=True,
                                         after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                                         max_attempts=4, delay=5, max_restart_attempts=5,
                                         switch_profile_attempts=3, switch_profile_delay=5):

        restart_attempts = 0

        while restart_attempts < max_restart_attempts:
            print(f"Checking if app is loaded (attempt {restart_attempts + 1}/{max_restart_attempts})")

            self.pause_event.wait()
            self.check_for_call()

            # Check if the screen has loaded by looking for the specified element
            if self.ld_adb_controller.check_loading_screen_gone(
                after_loading_screen_element=after_loading_screen_element,
                max_attempts=max_attempts,
                delay=delay
            ):
                # Element found, screen has loaded, proceed with upload
                print("App loaded successfully, proceeding with reel upload")
                
                self.Reel_upload(profle_name=profile_name, id_or_page=id_or_page,image_caption_list=image_captions_list,schdule_time_list=schdule_time_list,is_schedule_enable=is_schdule_enable,caption_from_orgvid=caption_from_orgvid) 
                
                return True

            # Element not found, restart the app and try again
            print("App not loaded properly, restarting app...")
            self.ld_adb_controller.stopApp(app_package=app_package)

            self.random_time(from_time=1, to_time=5)

            self.ld_adb_controller.startApp(app_package=app_package)
            self.check_for_call_and_pause(id_or_page)
            time.sleep(random.uniform(2,4))
            self.ld_adb_controller.save_you_login_info()

            # Retry switching profile until successful or attempts exhausted
            switch_attempt = 0
            while switch_attempt < switch_profile_attempts:

                self.pause_event.wait()
                self.check_for_call()

                reels_uploding_delay2 = self.device_config_dic.flatten_json()["Reels Uploading Delay"]

                self.random_time(from_time=int(reels_uploding_delay2)*0.9,
                                 to_time=reels_uploding_delay2)


                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                self.ld_adb_controller.wait_till_list_element_visiable_in_fb(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                switched_profile = self.ld_adb_controller.switch_profle_to(profile_name=profile_name,cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page="id")
                if switched_profile:
                    print("Profile switched successfully.")
                    break
                else:
                    print(f"Profile switch failed, attempt {switch_attempt + 1}/{switch_profile_attempts}. Retrying...")
                    time.sleep(switch_profile_delay)
                    switch_attempt += 1

            if not switched_profile:
                print("Failed to switch profile after multiple attempts.")
                restart_attempts += 1

        # If we've exhausted all restart attempts
        print(f"Failed to load app properly after {max_restart_attempts} restart attempts")
        return False

    def empty_folders(self, folder_input):
        """
        Safely empties each folder in the provided list or single folder path by deleting all files and subdirectories.
        Includes multiple security checks to prevent accidental deletion of system folders or drives.

        Args:
            folder_input (list or str): A list of folder paths or a single folder path string to be emptied.
        """
        # Convert string input to list for uniform processing
        if isinstance(folder_input, str):
            folder_list = [folder_input]
        else:
            folder_list = folder_input

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


    def image_upload_page_list(self,Profile_lists=[],id_name=None,image_captions_list=[],image_profile_folder = [],schdule_time_list=[],is_schedule_enable_list=[],captions_sources=[],app_package="com.facebook.katana"):
        
        #self.ld_adb_controller.cheack_ld_instance_open_or_not_for_20sec(id_frame_idx=1)

        self.pause_event.wait()
        self.check_for_call()

        self.ld_adb_controller.stopApp(app_package=app_package)
        self.check_for_call_and_pause()
        self.ld_adb_controller.startApp(app_package=app_package)
        self.check_for_call_and_pause()
        time.sleep(random.uniform(2,4))
        self.ld_adb_controller.save_you_login_info()
        self.check_for_call_and_pause()
        after_loading_screen_element = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"

        home_screen = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=after_loading_screen_element)

        self.check_for_call_and_pause()


        if home_screen:


            self.random_time(from_time=6,to_time=12)
            self.pause_event.wait()
            self.check_for_call()

            
            while len(Profile_lists) > 0:

                self.pause_event.wait()
                self.check_for_call()

                current_profile,id_or_page = Profile_lists.pop()
                current_profile_image_caption = image_captions_list.pop()
                current_profile_is_schedule_enable = is_schedule_enable_list.pop()
                current_profile_schdule_list = []
                current_profile_folder = ""
                current_profile_captions_sources = "From Original Video"
                is_current_caption_from_org_vid = True
                

                if current_profile_is_schedule_enable:
                    current_profile_schdule_list = schdule_time_list.pop()

                if len(image_profile_folder) > 0 :
                    current_profile_folder = image_profile_folder.pop()

                if len(captions_sources) >0:
                    current_profile_captions_sources = captions_sources.pop()
                
                if current_profile_captions_sources == "From Original Video":
                    is_current_caption_from_org_vid = True
                else:
                    is_current_caption_from_org_vid = False

                self.ld_adb_controller.startApp(app_package)
                self.check_for_call_and_pause()
                time.sleep(random.uniform(2,4))
                self.ld_adb_controller.save_you_login_info()
                self.check_for_call_and_pause()


                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                
                self.pause_event.wait()
                self.check_for_call()
                self.ld_adb_controller.wait_till_list_element_visiable_in_fb(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                check_profile = self.ld_adb_controller.switch_profle_to(profile_name=current_profile,cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page=id_or_page)

                self.pause_event.wait()
                self.check_for_call()

                if check_profile == True:
                    try:
                        Reel_upload = self.reels_upload_after_loading_screen(profile_name=current_profile,id_or_page=id_or_page,image_captions_list=current_profile_image_caption,  schdule_time_list=current_profile_schdule_list,is_schdule_enable=current_profile_is_schedule_enable,app_package=app_package,  after_loading_screen_element=after_loading_screen_element,caption_from_orgvid=is_current_caption_from_org_vid,
                        max_attempts=4,max_restart_attempts=5,delay=3)

                        self.pause_event.wait()
                        self.check_for_call()

                        self.random_time(from_time=1,to_time=3)
                        self.empty_folders(current_profile_folder)
                        self.check_for_call_and_pause(id_or_page)

                        

                    except Exception as e :
                        print(f"Error Uploading Image on profile #{current_profile} ....  Cause: {e}")
                        self.ld_adb_controller.stopApp(app_package=app_package)
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.startApp(app_package=app_package)
                        self.check_for_call_and_pause(id_or_page)
                        time.sleep(random.uniform(2,4))
                        self.ld_adb_controller.save_you_login_info()
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.discard_post_and_story(cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page=id_or_page)

            self.ld_adb_controller.HomeButton()
            self.empty_folders(image_profile_folder)
            print("Image Uploading done on all profiles")
            self.random_time(from_time=8,to_time=14)
            print("Closing LDPlayer instance")








if __name__ == "__main__": 

    from multiprocessing import Manager

    manager = Manager()
    control_pause =manager.Event()
    control_pause.set()


    test_run  = AdbImageUploadASW(device_serial="emulator-5554",local_output_file_path=r"E:\facebook_ld\ld_player0\main_folder",control_pasue_callback=control_pause)

    profile_list = [("Brucelee","page")] #"Kajal Kumari","Vibes videos"
    schdule_list = [False]
    image_captions= [["no","what is up guys","are you serious","oh yes"],["hi","hello","no","most dengrous","no","yes"],["no","what is up guys","are you serious","hi","hello","whatup?"]]
    id_name=profile_list[0]
    folders= [r"E:\facebook_ld_player\ld-2\main\Akshita Kumari_vid",r"E:\facebook_ld_player\ld-2\main\Javad aka Utlending.memes_vid"]
    #test_run.empty_folders(folders)


    times_lists = [[(None,"11","02","AM"),(None,"8","30","PM"),(None,"9","02","PM"),(None,"10","02","PM")],[(None,"12","02","AM"),(None,"12","30","PM"),(None,"12","02","AM"),(None,"3","02","PM"),(None,"7","02","PM"),(None,"8","02","PM")],[(None,"11","02","AM"),(None,"8","30","PM"),(None,"9","02","PM"),(None,"10","02","PM")]]
    test_run.image_upload_page_list(Profile_lists=profile_list,id_name=id_name,image_captions_list=image_captions,schdule_time_list=times_lists,is_schedule_enable_list=schdule_list,app_package="com.facebook.katana")

    #test_run.test_schedule_time(time_lists=times_lists)






        