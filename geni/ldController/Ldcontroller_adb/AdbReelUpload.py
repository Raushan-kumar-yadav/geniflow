import time
import random
from lxml import etree
import xml.etree.ElementTree as ET
import sys
from datetime import datetime
import os
import shutil
from pathlib import Path

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

#ldController.Ldcontroller_adb.
from ldController.Ldcontroller_adb.LdAdb import *

try:
    #ldController.Ldcontroller_adb.
    from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten

except Exception as e :
    print(e)



    

class AdbReelsUpload():

    def __init__(self, control_pasue_callback,device_name=None, device_serial = None,local_output_file_path="",download_folder="",activity_queue=None):
        self.device = device_name
        self.adb = device_serial
        self.local_output_path = local_output_file_path
        self.download_folder_path = download_folder
        self.activity_queue = activity_queue
        self.pause_event = control_pasue_callback
        self.ld_adb_controller = LdAdbController(device_serial=device_serial,local_output_file_path=local_output_file_path,download_folder=download_folder)
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


        
    def check_for_call_and_pause(self,id_or_page="id"):

        self.random_time()
        self.pause_event.wait()
        
        if id_or_page == "id":
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



        try:
            activity_callback(self.activity_queue, self.device, "Facebook", "", "Loading Scheduling", "None","ds")
            is_scheduling_optoin_visiable = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=scheduling_optons_btn_xpath)



            if is_scheduling_optoin_visiable:

                print("started scheduling post")
                activity_callback(self.activity_queue, self.device, "Facebook", "", "started Scheduling", "None","ds")
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
                        activity_callback(self.activity_queue, self.device, "Facebook", "", "Ignoring Day", "None","ds")
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", "", "Current Day", "None","ds")
                        self.ld_adb_controller.click_element(xpath_expr=ok_btn_xpath)
                    else:
                        print("custom day selected")
                        activity_callback(self.activity_queue, self.device, "Facebook", "", "Custom Day", "None","ds")
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", "", "Putting Day", "None","ds")
                        self.ld_adb_controller.click_element(xpath_expr=custom_day_btn_xpath)
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", "", "Clicking Ok", "None","ds")
                        self.ld_adb_controller.click_element(xpath_expr=ok_btn_xpath)


                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Switch To Text", "None","ds")
                    self.ld_adb_controller.click_element(xpath_expr="//node[@content-desc='Switch to text input mode for the time input.']")

                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Clicked Hour", "None","ds")
                    self.ld_adb_controller.click_element(xpath_expr="//node[@resource-id='android:id/input_hour']")

                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Cleard Hour", "None","ds")
                    self.ld_adb_controller.Delete_text_from_back()

                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Send Hour", "None","ds")
                    self.ld_adb_controller.PullText(Text=hour)

                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Clicked Min", "None","ds")
                    self.ld_adb_controller.click_element(xpath_expr="//node[@resource-id='android:id/input_minute']")

                    self.check_for_call_and_pause(id_or_page)

                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Cleard Min", "None","ds")
                    self.ld_adb_controller.Delete_text_from_back()
                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Sending Min", "None","ds")
                    self.ld_adb_controller.PullText(Text=min)

                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Sending AM/PM", "None","ds")
                    self.ld_adb_controller.click_element(xpath_expr="//node[@resource-id='android:id/am_pm_spinner']")

                    self.check_for_call_and_pause(id_or_page)

                    self.ld_adb_controller.click_element(xpath_expr=am_pm_xpath)

                    self.check_for_call_and_pause(id_or_page)

                    self.ld_adb_controller.click_element(xpath_expr=ok_btn_xpath)

                    self.check_for_call_and_pause(id_or_page)
                    save_btn_xpath = "//node[@content-desc='Save']"
                    activity_callback(self.activity_queue, self.device, "Facebook", "", "Saved Current Scheduling", "None","ds")
                    is_save_btn_visiable = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=save_btn_xpath,max_attempts=2)

                    if is_save_btn_visiable:
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.click_element(xpath_expr=save_btn_xpath)
                    else:
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.click_element(xpath_expr="//node[@content-desc='Back']")
                else:
                    print("do something else ")
        except Exception as e :
            print("Error At Sheduling")
            activity_callback(self.activity_queue, self.device, "Facebook", "", "Reel Upload Sheduling Error", f"Error:{e}","ds")


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

            
                

    def reel_upload(self,profile_name,id_or_page,schedule_time_list=None,is_schedule_enable=False,num_of_video=1,is_caption_from_original_file = True,caption_list=[],is_group_sharing_enable=False,ignore_name = True,num_of_share = 1, group_list="" ,download_folder=""):
        """
        Upload videos with optional scheduling functionality.

        Args:
            profile_name: Name of the profile to upload to
            video_caption_list: List of captions for videos
            schedule_time_list: List of schedule times in format [(day, hour, minute, am_pm), ...]
            is_schedule_enable: Whether to use scheduling
        """

        
        #self.ld_adb_controller.InstallAndCheckAPK()

        if schedule_time_list is None:
            schedule_time_list = []

        self.pause_event.wait()
        self.check_for_call()

        # Create a copy of lists to avoid modifying the original ones
        available_schedule_times = schedule_time_list.copy()  # Track remaining available times

        # Default caption if list is too short
        default_caption = "Video post"

        # Determine scheduling mode
        if is_schedule_enable and available_schedule_times:
            # We'll use the available scheduling times
            pass
        elif not is_schedule_enable or not available_schedule_times:
            # If scheduling not enabled or no times provided, use immediate posting
            available_schedule_times = []
            for schedule in range(num_of_video):
                available_schedule_times.append((None, "00", "00", "PM"))


        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Discard Post", "None","ds")
        # Check for popups and discard buttons
        self.ld_adb_controller.discard_post()
        self.check_for_call_and_pause(id_or_page)
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Story Post", "None","ds")
        self.ld_adb_controller.discard_story()


        # Counter for videos
        video_num = 1

        # Process each video while we have captions or videos to post
        while available_schedule_times: 
            
            try:
                # Get caption for this video (or use default if none available)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Moving Content", "None","ds")
                video_caption = self.ld_adb_controller.MoveFileWithCaption(media_type="video",sub_folder="reels",download_folder=download_folder)

                if not video_caption:
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Content Not Found", "Error","s")
                    print("Video not avlaible in download folder so qiting upload")
                    return available_schedule_times
            




        
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Getting Captions", "None","ds")
                # Replace catption if not from original file
                if not is_caption_from_original_file:
                    video_caption = caption_list.pop(0)
                print(f"Processing video #{video_num} with {len(available_schedule_times)} available schedule times")






                # Switch to Gallery to refrace the file that add to folder
                self.check_for_call_and_pause(id_or_page)
                
                activity_callback(self.activity_queue, self.device, "Gallery", profile_name, "Opening Gallery", "None","ds")
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Gallery",app_package_name_to_switch="com.android.gallery3d")
                






                # Switch to facebook
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Swtching to Facebook", "None","ds")
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")







            


                # Check for pop in fb home screen 
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=2,delay=0)
                #self.ld_adb_controller.check_popup_on_home_fb() #enable this if getting other popups






                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Clicking Create reel", "None","ds")
                # Click on plus button to create a new post
                plus_btn_x_path = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"
                reels_id_btn_xpath = "//node[@content-desc='Reel']"

            
       


            
                
                # Try to click on reels tab if visible
                reels_tab_xpath = "//node[@content-desc='Reels']"
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.click_element_if_visibale(xpath_expr=reels_tab_xpath)






                # Click on create reel
                create_reel_xpath = "//node[@content-desc='Create reel']"
                self.check_for_call_and_pause(id_or_page)
                is_create_reel_wid_visible = self.ld_adb_controller.click_element_if_visibale(xpath_expr=create_reel_xpath)
                # If tab create reel is not visible then click on plus btn and then click on reel and so on.....
                if not is_create_reel_wid_visible:
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.click_element_if_visibale(xpath_expr=plus_btn_x_path)
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.click_element_if_visibale(xpath_expr=reels_id_btn_xpath)







                # Click discard if there is discard button
                Discard_button_xpath = "//node[@text='DISCARD']"
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Discard Btn", "None","ds")
                self.ld_adb_controller.click_element_if_visibale(Discard_button_xpath)
            







                # Click on gallery button
                gallery_btn_xpat = "//node[@content-desc='Gallery']"
                gallery_btn_x_coor = 61
                gallery_btn_y_coor = 262
                self.check_for_call_and_pause(id_or_page)
                self.check_for_call_and_pause(id_or_page)
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Opening Album", "None","ds")
                is_gallery_btn_clicked = self.ld_adb_controller.click_element_if_visibale(xpath_expr=gallery_btn_xpat)
                if not is_gallery_btn_clicked:
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.clickByCoordinate(gallery_btn_x_coor, gallery_btn_y_coor)








                # Navigate to reels folder
                select_reels_album = f"//node[@content-desc='Select album, reels']"
                self.check_for_call_and_pause(id_or_page)
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Album", "None","ds")
                is_clicked_on_alb = self.ld_adb_controller.click_element(xpath_expr=select_reels_album)
                if not is_clicked_on_alb:
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Album", "Error","ds")









                # Click on frist video on facebook gallery
                frist_btn_x_coord = 85
                frist_btn_y_coord = 418
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Video", "None","ds")
                self.ld_adb_controller.clickByCoordinate(x=frist_btn_x_coord,y=frist_btn_y_coord)
                self.check_for_call_and_pause(id_or_page)
            
            
            








                # Check if next button visible 
                next_btn_x_coor = 435
                next_btn_y_coor = 905
                next_btn_xpath = "//node[@content-desc='Next']"
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Clicking Next", "None","ds")
                is_next_btn_visible = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=next_btn_xpath,max_attempts=20,delay=2)

                # If next btn is visible then click on next btn and if not then click on back btn
                if is_next_btn_visible:
                    self.check_for_call_and_pause(id_or_page)
                    is_clicked_on_next_btn = self.ld_adb_controller.click_element(next_btn_xpath,max_attempts=3)
                    if not is_clicked_on_next_btn:
                        self.ld_adb_controller.clickByCoordinate(x=next_btn_x_coor, y=next_btn_y_coor)

                else:
                    print(f"Discarting Reel Uploading on Profile:{profile_name} Due to Next button not found!!")
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Error at Reel Uploading", "Error:Next Button not found..","s")
                    self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    available_schedule_times.pop(0)
                    return







  
            






                # Click on Caption btn 
                add_caption_x_coor = 315
                add_caption_y_coor = 275

                # Push Captioin text 
                Describe_your_reel_btn_xpath = "//node[contains(@hint,'Describe your reel')]"
                Share_now_btn_xpath = "//node[@content-desc='Share now']"
                Share_now_loaidng_sceen_xpaths = ["//node[@content-desc='Share now']","//node[contains(@text,'Scheduling options')]"]
                # Wait for share button to appear
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Wating For Setting Dig", "None","ds")
                is_share_now_btn = self.ld_adb_controller.CheckLoadingScreenGoneListElements(
                    after_loading_screen_elements=Share_now_loaidng_sceen_xpaths,max_attempts=20,delay=2
                )
                self.check_for_call_and_pause(id_or_page=id_or_page)
                if is_share_now_btn:
                    # Add title to video
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Clicking Captions", "None","ds")
                    self.ld_adb_controller.click_element_if_visibale(xpath_expr=Describe_your_reel_btn_xpath)
                    self.ld_adb_controller.clickByCoordinate(x = add_caption_x_coor,y=add_caption_y_coor)
                    self.ld_adb_controller.clickByCoordinate(x = add_caption_x_coor,y=add_caption_y_coor)
                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Sending Captions", "None","ds")
                    self.ld_adb_controller.PullText(str(video_caption))
                    print(f"Video caption for profile {profile_name}: {video_caption}")
                    self.random_time(from_time=0.5, to_time=1)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Clicking On Cursor", "None","ds")
                    self.ld_adb_controller.click_on_cursor()
            










                # Check if shedule enable if enable then process with schedule 
                is_scheduling_set_xpath = "//node[contains(@content-desc,'Scheduling options, Post now')]"
                if is_schedule_enable and len(available_schedule_times) > 0:
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scheduling Post", "None","ds")
                            # Create a queue of scheduling times to try for this post
                            queue = available_schedule_times.copy()  
                            scheduling_succeeded = False
                            used_schedule = None  # Track which schedule time worked

                            # Try scheduling times until one works or we run out of options
                            while queue:

                                current_schedule = queue.pop(0)  
                                used_schedule = current_schedule  

                                day, hour, minute, am_pm = current_schedule
                                print(f"Trying schedule: {day} {hour}:{minute} {am_pm}")
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, f"Trying schedule{day}/{hour}/{minute}/{am_pm}", "None","ds")

                                self.set_schedule_time(day=day, hour=hour, min=minute, am_pm=am_pm,id_or_page=id_or_page)
                                self.check_for_call_and_pause(id_or_page)

                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Scheduling Success", "None","ds")
                                is_scheduled_success = self.ld_adb_controller.check_loading_screen_gone(
                                    after_loading_screen_element=is_scheduling_set_xpath
                                )

                                if not is_scheduled_success:
                                    print("Scheduling Done")
                                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Scheduling successful", "None","ds")
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


                            # Check if any scheduling time worked
                            if not scheduling_succeeded:
                                print("Tried all the schedule times but none of them worked...Canceling post")
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Tried all the schedule None Of Them Worked", "Error","s")
                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Going Home", "None","ds")
                                self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,   id_or_page=id_or_page)
                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,  id_or_page=id_or_page,scroll_down_num=2,delay=0)
                                return available_schedule_times

                            else:
                                # Schedule worked, now share the post
                                share_now_btn_x_coor = 310
                                share_now_btn_y_coor = 910
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scheduling successful", "None","ds")
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Posting Reel", "None","ds")
                                self.ld_adb_controller.clickByCoordinate(x=share_now_btn_x_coor, y=share_now_btn_y_coor)
                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Uploading..", "None","ds")
                                self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Reel Uploaded..", f"Count:{video_num}","ds")
                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Waiting Delay", "None","ds")
                                reels_uploading_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Removing Used Contents", "None","ds")
                                self.ld_adb_controller.empty_folders(subfolder="reels")
                                self.check_for_call_and_pause(id_or_page=id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Reel Uploaded successful With Scheduling ", f"Count:{video_num}","s")
                                video_num +=1


                else:
                    """ Immediate sharing (non-scheduled) """

                    #remove one from available schedule time
                    available_schedule_times.pop()


                    # Share post to group if enabled 
                    if is_group_sharing_enable:
                        try:
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Sharing To Groups", "None","ds")
                            self.ld_adb_controller.SharePostToGroups(num_of_share=num_of_share,ignore_name=ignore_name,groups_name=group_list,check_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page=id_or_page)
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Group Sharing Done", "None","ds")
                        except Exception as e :
                            print(f"Error Sharing post to group:{e} ")
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Error at Groups Sharing in Reel Uploading", f"Error:{e}","s")
                            
                    # Click on share btn
                    share_now_btn_x_coor = 310
                    share_now_btn_y_coor = 910
                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Posting Reel", "None","ds")
                    self.ld_adb_controller.clickByCoordinate(x=share_now_btn_x_coor, y=share_now_btn_y_coor)



                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                    self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=2,delay=0)



                    # Check is uploding done or not 
                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Uploading..", "None","ds")
                    self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.
                    check_for_call_and_pause,id_or_page=id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Reel Uploaded..", f"Count:{video_num}","ds")






                    # Wait for given delay from user
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Waiting Delay", "None","ds")
                    reels_uploading_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                    self.check_for_call_and_pause(id_or_page)
                    self.random_time(
                                from_time=int(reels_uploading_delay) * 0.9,
                                to_time=reels_uploading_delay
                        )




                    # Remove popup form home screen
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                    self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=1,delay=0)
                    self.pause_event.wait()
                    self.check_for_call()



                    # Print that uploading done 
                    print("Reel uploading Done")
                    self.check_for_call_and_pause(id_or_page=id_or_page)




                    # Remove all the files from reels folder 
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Removing Used Contents", "None","ds")
                    self.ld_adb_controller.empty_folders(subfolder="reels")
                    self.check_for_call_and_pause(id_or_page=id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Reel Uploaded successful", f"Count:{video_num}","s")
                    video_num +=1
            except Exception as e :
                print(f"Error in reels upload")
                self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Reel Uploading Error", f"Error:{e},Count:{video_num}","s")
                available_schedule_times.pop()
        return available_schedule_times





    def reel_upload_after_loading_screen(self, profile_name ,id_or_page, app_package, schdule_time_list=[],is_schedule_enable=False,num_of_videos = 1,is_group_sharing_enable=False,group_list="",caption_form="From Original Video",captions_list=[],download_folder="",ignore_name=False,num_of_share =1,
                                         after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                                         max_attempts=4, delay=5, max_restart_attempts=5,
                                         switch_profile_attempts=3, switch_profile_delay=5):
        """
        Attempts to upload a reel after checking if the app has loaded properly.
        If loading screen check fails, it restarts the app and tries again until successful.

        Now includes retry logic for switching profiles.

        Returns:
            bool: True if upload was successful, False otherwise
        """

        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Starting APP", "None","ds")
        self.check_for_call_and_pause()
        self.ld_adb_controller.startApp()
        self.check_for_call_and_pause()



        is_caption_from_original_file = False
        if caption_form == "From Original Video":
            is_caption_from_original_file = True
        else:
            is_caption_from_original_file = False



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
                # Element found, screen has loaded, proceed with upload
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "App Loaded", "None","ds")
                print("App loaded successfully, proceeding with reel upload")
                
                self.reel_upload(profile_name=profile_name,schedule_time_list=schdule_time_list,is_schedule_enable=is_schedule_enable,id_or_page=id_or_page,num_of_video=num_of_videos,is_group_sharing_enable=is_group_sharing_enable,group_list=group_list,is_caption_from_original_file=is_caption_from_original_file,caption_list=captions_list,download_folder=download_folder,ignore_name=ignore_name,num_of_share=num_of_share)
                
                return True

            # Element not found, restart the app and try again
            print("App not loaded properly, restarting app...")
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "App Not loaded", "None","ds")
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Stoping App", "None","ds")
            self.ld_adb_controller.stopApp(app_package=app_package)

            self.random_time(from_time=1, to_time=5)
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Starting App", "None","ds")
            self.ld_adb_controller.startApp(app_package=app_package)
            time.sleep(random.uniform(1,2))
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Popups", "None","ds")
            self.ld_adb_controller.save_you_login_info()
            self.ld_adb_controller.discard_post()
            self.ld_adb_controller.discard_story()
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")

            # Retry switching profile until successful or attempts exhausted
            switch_attempt = 0
            while switch_attempt < switch_profile_attempts:
                
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Cheacking Loading Screen", "None","ds")
                self.ld_adb_controller.wait_till_list_element_visiable_in_fb(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Swtching Profile", "None","ds")
                switched_profile = self.ld_adb_controller.switch_profle_to(profile_name=profile_name,cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page="id")




                if switched_profile:
                    print("Profile switched successfully.")
                    break
                else:
                    print(f"Profile switch failed, attempt {switch_attempt + 1}/{switch_profile_attempts}. Retrying...")
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Retrying Swtching Profile", "None","ds")
                    time.sleep(switch_profile_delay)
                    switch_attempt += 1


            if not switched_profile:
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Failed to switch profile", "Error","s")
                print("Failed to switch profile after multiple attempts.")
                restart_attempts += 1

        # If we've exhausted all restart attempts
        print(f"Failed to load app properly after {max_restart_attempts} restart attempts")
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Failed to Load App", "Error","s")
        return False



    def reel_upload_page_list(self,Profile_lists=[],id_name=None,video_captions_list=[],reels_profile_folder = [],schdule_time_list=[],is_schedule_enable_list=[],app_package="com.facebook.katana"):
        
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

        if not home_screen:
            self.ld_adb_controller.discard_post()
            self.check_for_call_and_pause()
            self.ld_adb_controller.discard_story()
        
        self.check_for_call_and_pause()


        if home_screen:


            self.random_time(from_time=1,to_time=3)
            self.pause_event.wait()
            self.check_for_call()

            


            while len(Profile_lists) > 0:

                self.pause_event.wait()
                self.check_for_call()

                current_profile,id_or_page = Profile_lists.pop()
                current_profile_video_caption = video_captions_list.pop()
                current_profile_is_schedule_enable = is_schedule_enable_list.pop()
                current_profile_folder = ""

                current_profile_schdule_list = []
                if current_profile_is_schedule_enable:
                    current_profile_schdule_list = schdule_time_list.pop()

                if len(reels_profile_folder) > 0:
                    current_profile_folder = reels_profile_folder.pop()

                self.ld_adb_controller.startApp(app_package)
                self.check_for_call_and_pause()
                time.sleep(random.uniform(2,4))
                self.ld_adb_controller.save_you_login_info()
                self.check_for_call_and_pause()

                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=1)
                self.ld_adb_controller.wait_till_list_element_visiable_in_fb(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                check_profile = self.ld_adb_controller.switch_profle_to(profile_name=current_profile,cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page="id")

                self.pause_event.wait()
                self.check_for_call()

                if check_profile == True:

                    try:
                        Reel_upload = self.reel_upload_after_loading_screen(profile_name=current_profile,id_or_page=id_or_page,video_captions_list=current_profile_video_caption,   is_schedule_enable=current_profile_is_schedule_enable,schdule_time_list=current_profile_schdule_list,app_package=app_package,  after_loading_screen_element=after_loading_screen_element,
                        max_attempts=4,max_restart_attempts=5,delay=3)

                        self.pause_event.wait()
                        self.check_for_call()

                        self.random_time(from_time=1,to_time=3)
                        self.empty_folders(current_profile_folder)
                        self.check_for_call_and_pause(id_or_page)
                        

                    except Exception as e :
                        print(f"Error Uploading Reels on #{current_profile} Profile...., Cause: {e}")
                        self.ld_adb_controller.stopApp(app_package=app_package)
                        self.check_for_call_and_pause()
                        self.ld_adb_controller.startApp(app_package=app_package)
                        self.check_for_call_and_pause()
                        time.sleep(random.uniform(2,4))
                        self.ld_adb_controller.save_you_login_info()
                        self.check_for_call_and_pause()
                        self.ld_adb_controller.discard_post_and_story(cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page=id_or_page)
            
            self.ld_adb_controller.HomeButton()
            self.empty_folders(reels_profile_folder)
            print(f"Reels Uploading done on all Profiles")
            self.random_time(from_time=8,to_time=14)
            print("Closing LDPlayer instance")








if __name__ == "__main__": 

    from multiprocessing import Manager

    manager = Manager()
    control_pause =manager.Event()
    control_pause.set()


    test_run  = AdbReelsUpload(device_serial="emulator-5554",local_output_file_path=r"E:\facebook_ld\ld_player0\main_folder",control_pasue_callback=control_pause , download_folder=r"E:\facebook_ld\ld_player0\Kajal Kumari\Kajal Kumari_download_reel")


    folders= [r"E:\facebook_ld_player\ld-2\main\Akshita Kumari_vid",r"E:\facebook_ld_player\ld-2\main\Javad aka Utlending.memes_vid"]
    #test_run.empty_folders(folders)

    profile_list = [("lamzionrainey","page")]
    schdule_list = [True,False,True]
    video_captions= [["no","what is up guys","are you serious","oh yes"],["hi","hello","no","most dengrous","no","yes"],["no","what is up guys","are you serious","hi","hello","whatup?"]]

    id_name=profile_list[0]

    times_lists = [[(None,"11","02","AM"),(None,"8","30","PM"),(None,"9","02","PM"),(None,"10","02","PM")],[(None,"12","02","AM"),(None,"12","30","PM"),(None,"12","02","AM"),(None,"3","02","PM"),(None,"7","02","PM"),(None,"8","02","PM")],[(None,"11","02","AM"),(None,"8","30","PM"),(None,"9","02","PM"),(None,"10","02","PM"),(None,"11","02","PM")]]

    schdule_list = [(None,"00","00","AM"),(None,"00","00","PM"),(None,"00","00","PM"),(None,"00","00","PM")]
    test_run.reel_upload(profile_name="Brucelee",schedule_time_list=schdule_list,is_schedule_enable=False,id_or_page="page",num_of_video=3)

    #test_run.test_schedule_time(time_lists=times_lists)






        