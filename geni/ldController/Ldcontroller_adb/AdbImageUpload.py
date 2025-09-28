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



class AdbimageUpload():

    def __init__(self, control_pasue_callback,device_name=None, device_serial = None,local_output_file_path="",download_folder="",activity_queue=None):
        self.device = device_name
        self.adb = device_serial
        self.activity_queue = activity_queue
        self.local_output_file_path = local_output_file_path
        self.download_folder = download_folder
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

            
                

    def image_upload(self,profile_name,id_or_page,schedule_time_list=None,is_schedule_enable=False,num_of_images=1,is_caption_from_original_file = True,caption_list=[],download_folder="",is_group_sharing_enable=False,ignore_name = True,num_of_share = 1, group_list="" ):
        """
        Upload images with optional scheduling functionality.

        Args:
            profile_name: Name of the profile to upload to
            image_caption_list: List of captions for images
            schedule_time_list: List of schedule times in format [(day, hour, minute, am_pm), ...]
            is_schedule_enable: Whether to use scheduling
        """

        


        


        if schedule_time_list is None:
            schedule_time_list = []



        self.pause_event.wait()
        self.check_for_call()



        # Create a copy of lists to avoid modifying the original ones
        available_schedule_times = schedule_time_list.copy()  # Track remaining available times




        # Default caption if list is too short
        default_caption = "Hi"
        sub_folder = "imagess"


        # Determine scheduling mode
        if is_schedule_enable and available_schedule_times:
            # We'll use the available scheduling times
            pass
        elif not is_schedule_enable or not available_schedule_times:
            # If scheduling not enabled or no times provided, use immediate posting
            available_schedule_times = []
            for schedule in range(num_of_images):
                available_schedule_times.append((None, "00", "00", "PM"))




        
 
        # Check for popups and discard buttons
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Discard Post", "None","ds")
        self.ld_adb_controller.discard_post()
        self.check_for_call_and_pause(id_or_page)
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Story Post", "None","ds")
        self.ld_adb_controller.discard_story()


        image_num = 1

        
        # Process each image while we have captions or images to post
        while available_schedule_times:  # Process at least one image


            try:
                # Get caption for this video (or use default if none available)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Moving Content", "None","ds")
                image_caption = self.ld_adb_controller.MoveFileWithCaption(media_type="image",sub_folder=sub_folder,download_folder=download_folder)

                if not image_caption:
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Content Not Found", "Error","s")
                    print("image not avlaible in download folder so qiting upload")
                    available_schedule_times.clear()
                    return available_schedule_times


                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Getting Captions", "None","ds")
                # Replace the caption if not from original file 
                if not is_caption_from_original_file:
                    image_caption = caption_list.pop(0)


                # Switch to Gallery to refrace the file that add to folder
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Gallery", profile_name, "Opening Gallery", "None","ds")
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Gallery",app_package_name_to_switch="com.android.gallery3d")
                self.check_for_call_and_pause(id_or_page)




                # Switch to facebook
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Swtching to Facebook", "None","ds")
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                self.check_for_call_and_pause(id_or_page)










                # Check for pop in fb home screen 
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,  delay=0)
                self.ld_adb_controller.check_popup_on_home_fb()





                # Click on plus button to create a new post
                plus_btn_x_path = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"







                # Click on Select photos or videos for your post
                select_photo_or_video_btn_xpath = "//node[@content-desc='Select photos or videos for your post']"
                select_photo_or_video_btn_x_coord = 496
                select_photo_or_video_btn_y_coord = 219
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Clicking Create Post", "None","ds")
                is_clicked_on_select_photo = self.ld_adb_controller.click_element_if_visibale(xpath_expr=select_photo_or_video_btn_xpath)
                if not is_clicked_on_select_photo:
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.clickByCoordinate(x=select_photo_or_video_btn_x_coord,y=select_photo_or_video_btn_y_coord)







                # Check again and if found then click on discard btn
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Discard Btn", "None","ds")
                self.ld_adb_controller.click_element_if_visibale("//node[@text='DISCARD']")
                self.pause_event.wait()







                # Click on gallery button
                gallery_btn_x_coor = 50
                gallery_btn_y_coor = 164
                gallery_btn_xpat = "//node[@content-desc='Gallery']"
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Opening Album", "None","ds")
                is_gallery_btn_clicked = self.ld_adb_controller.click_element_if_visibale(xpath_expr=gallery_btn_xpat)
                if not is_gallery_btn_clicked:
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.clickByCoordinate(gallery_btn_x_coor, gallery_btn_y_coor)



                # Select imagess folder
                select_imagess_album_btn_xpath = f"//node[contains(@content-desc,'{sub_folder}')]"
                self.check_for_call_and_pause(id_or_page)
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Album", "None","ds")
                is_clicked_on_alb = self.ld_adb_controller.click_element(xpath_expr=select_imagess_album_btn_xpath)
                if not is_clicked_on_alb:
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Album", "Error","ds")





                # Click on frist video in facebook gallery
                frist_image_x_coord = 77
                frist_image_y_coord = 290
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Video", "None","ds")
                self.ld_adb_controller.clickByCoordinate(x=frist_image_x_coord,y=frist_image_y_coord)
                self.check_for_call_and_pause(id_or_page)
                self.check_for_call_and_pause(id_or_page)






                # Check if create post label visible if yes then pull text and click on next btn
                next_btn_x_coor = 435
                next_btn_y_coor = 66
                next_btn_xpath = "//node[@text='NEXT']"
                create_post_label_xpath = "//node[@text='Create post']"
                post_settings_label_xpat = "//node[@text='Post settings']"
                share_now_screen_xpaths = ["//node[@text='Post settings']","//node[contains(@text,'Scheduling options')]"]

                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Wating For Next Win", "None","ds")
                is_create_post_label_visiable = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=create_post_label_xpath,  max_attempts=20,delay=2)


                if not is_create_post_label_visiable:

                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Next Win Not Found", "None","ds")
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Going To Home", "None","ds")
                    self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                    self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                    available_schedule_times.pop(0)
                    return available_schedule_times
            



                if is_create_post_label_visiable:


                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Caption", "None","ds")
                        self.ld_adb_controller.click_element_if_visibale(xpath_expr="//node[contains(@text,'Say something about this photo')]")
                        self.ld_adb_controller.click_element_if_visibale(xpath_expr="//node[contains(@text,'Say something about this photo')]")




                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Sending Caption", "None","ds")
                        self.ld_adb_controller.PullText(str(image_caption))
                        print(f"image caption for profile {profile_name}: {image_caption}")




                        self.random_time(from_time=0.5, to_time=1)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Clicking On Cursor", "None","ds")
                        self.ld_adb_controller.click_on_cursor()




                        self.random_time(from_time=2, to_time=4)
                        self.pause_event.wait()
                        self.check_for_call()



                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Clicking Next Btn", "None","ds")
                        is_next_clicked = self.ld_adb_controller.click_element_if_visibale(
                            xpath_expr=next_btn_xpath
                        )




                        if not is_next_clicked:
                            self.check_for_call_and_pause(id_of_page=id_or_page)
                            self.ld_adb_controller.clickByCoordinate(x=next_btn_x_coor, y=next_btn_y_coor)

                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                        self.ld_adb_controller.long_scroll_down_num(scroll_down_num=2,delay=1,check_for_call_and_pause=self.check_for_call_and_pause,   id_or_page=id_or_page)
                        self.check_for_call_and_pause(id_or_page)



                        is_clicked_on_next2 = self.ld_adb_controller.click_element_if_visibale(xpath_expr=next_btn_xpath)





                self.check_for_call_and_pause(id_or_page)





                # Wait for Post setting label to appear
                post_btn_xpath = "//node[@content-desc='POST']"
                post_btn_x_coord = 480
                post_btn_y_coord = 70

                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Wating For Next Win", "None","ds")
                is_post_setting_visible = self.ld_adb_controller.CheckLoadingScreenGoneListElements (after_loading_screen_elements=share_now_screen_xpaths,max_attempts=20,delay=2)

                if not is_post_setting_visible:

                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Next Win Not Found", "None","ds")
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Going To Home", "None","ds")
                    self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                    self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,delay=0)
                    available_schedule_times.pop(0)
                    return available_schedule_times






                if is_post_setting_visible:
                
                        # Scheduling element check
                        is_scheduling_set_xpath = "//node[contains(@content-desc,'Scheduling options, Post now')]"

                        if is_schedule_enable and len(available_schedule_times) > 0:

                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scheduling Post", "None","ds")

                            # Create a queue of scheduling times to try for this post
                            queue = available_schedule_times.copy()  
                            scheduling_succeeded = False
                            used_schedule = None  


                            # Try scheduling times until one works or we run out of options
                            while queue:


                                current_schedule = queue.pop(0)  # Remove and get the next schedule to try
                                used_schedule = current_schedule  # Track the schedule we're trying



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
                                self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,    id_or_page=id_or_page)

                                self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)

                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,delay=0)

                    
                                return  available_schedule_times



                            else:


                                # Schedule worked, now share the post
                                post_btn_xpath = "//node[@content-desc='POST']"
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scheduling successful", "None","ds")

                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Posting Image ", "None","ds")
                                is_clicked_post_btn = self.ld_adb_controller.click_element(xpath_expr=post_btn_xpath,max_attempts=2)
                                if not is_clicked_post_btn:
                                    self.ld_adb_controller.clickByCoordinate(x=post_btn_x_coord,y=post_btn_y_coord)



                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=2,delay=0)





                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Uploading..", "None","ds")
                                self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.check_for_call_and_pause,  id_or_page=id_or_page)
                                self.check_for_call_and_pause(id_or_page)

                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Image Uploaded..", "None","ds")


                                
                                reels_uploading_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                                self.check_for_call_and_pause(id_or_page)


                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Waiting Delay", "None","ds")



                                self.random_time(
                                    from_time=int(reels_uploading_delay) * 0.9,
                                    to_time=reels_uploading_delay
                                )




                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=1,delay=0)
                                print("Image scheduling and uploading Done")
                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Removing Used Contents", "None","ds")
                                self.ld_adb_controller.empty_folders(subfolder=sub_folder)
                                self.check_for_call_and_pause(id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Image Uploaded successful With Scheduling ", f"Count:{image_num}","s")
                                image_num +=1

                        else:

                            # Immediate sharing (non-scheduled)
                            available_schedule_times.pop()


                            # Share post to group if enabled 
                            if is_group_sharing_enable:
                                try:
                                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Sharing To Groups", "None","ds")

                                    self.ld_adb_controller.SharePostToGroups(num_of_share=num_of_share,ignore_name=ignore_name,groups_name=group_list,check_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page=id_or_page,
                                                                             is_image=True)
                                    

                                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Group Sharing Done", "None","ds")
                                except Exception as e :
                                    print(f"Error Sharing post to group:{e} ")
                                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Groups Sharing", f"Error:{e}","ds")


                            post_btn_xpath = "//node[@content-desc='POST']"
                            self.check_for_call_and_pause(id_or_page)
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Posting Image", "None","ds")
                            is_clicked_on_post = self.ld_adb_controller.click_element_if_visibale(xpath_expr=post_btn_xpath)
                            if not is_clicked_on_post:
                                self.check_for_call_and_pause(id_or_page)
                                self.ld_adb_controller.clickByCoordinate(x=post_btn_x_coord,y=post_btn_y_coord)




                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=2,delay=0)





                            self.check_for_call_and_pause(id_or_page)
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Uploading..", "None","ds")
                            self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.check_for_call_and_pause,  id_or_page=id_or_page)
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Image Uploaded..", f"Count:{image_num}","ds")



                            self.check_for_call_and_pause(id_or_page)
                            reels_uploading_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                            self.check_for_call_and_pause(id_or_page)

                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Waiting Delay", "None","ds")

                            self.random_time(
                                from_time=int(reels_uploading_delay) * 0.9,
                                to_time=reels_uploading_delay
                            )



                            self.check_for_call_and_pause(id_or_page)
                            print("Image uploading Done")
                            self.check_for_call()




                            # Remove all the image file from dict
                            self.check_for_call_and_pause(id_or_page)
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Removing Used Contents", "None","ds")
                            self.ld_adb_controller.empty_folders(subfolder=sub_folder)
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Image Uploaded successful", f"Count:{image_num}","s")
                            image_num +=1




                else:



                        print("Error: Post setting window not found ")
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Post setting window not found", "Error","s")
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Going To Home", "Noen","s")
                        self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,    id_or_page=id_or_page)

                        self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)

                        available_schedule_times.clear()


                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","s")


                        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,delay=0)



                        # Exit current iteration
                        return available_schedule_times
            except Exception as e :
                print(f"Error uploading this image Restarting the facebook:{e}")
                available_schedule_times.pop()
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Uploading Image", f"Error:{e},Count:{image_num}","s")
                self.ld_adb_controller.stopApp()

        
        return available_schedule_times







    def image_upload_after_loading_screen(self, profile_name ,id_or_page, app_package, schedule_time_list=[],is_schedule_enable=False,is_group_sharing_enable=False,group_list="",caption_form="From Original Video",caption_list=[],download_folder="",num_of_image = 1,ignore_name=False,num_of_share=1,
                                         after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                                         max_attempts=4, delay=5, max_restart_attempts=5,
                                         switch_profile_attempts=3, switch_profile_delay=5):


        self.check_for_call_and_pause()
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Starting APP", "None","ds")
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
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "App Loaded", "None","ds")
                # Element found, screen has loaded, proceed with upload
                print("App loaded successfully, proceeding with image upload")
                
                self.image_upload(profile_name=profile_name,id_or_page=id_or_page,schedule_time_list=schedule_time_list,is_group_sharing_enable=is_group_sharing_enable,group_list=group_list,is_caption_from_original_file=is_caption_from_original_file,caption_list=caption_list,download_folder=download_folder,is_schedule_enable=is_schedule_enable,num_of_images=num_of_image,ignore_name=ignore_name,num_of_share=num_of_share)

                return True

            # Element not found, restart the app and try again
            print("App not loaded properly, restarting app...")
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "App Not loaded", "None","ds")
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Stoping App", "None","ds")

            self.ld_adb_controller.stopApp(app_package=app_package)




            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Starting App", "None","ds")
            self.ld_adb_controller.startApp(app_package=app_package)
            self.ld_adb_controller.startApp(app_package=app_package)
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Popups", "None","ds")
            self.ld_adb_controller.save_you_login_info()
            self.ld_adb_controller.discard_post()
            self.ld_adb_controller.discard_story()




            # Retry switching profile until successful or attempts exhausted
            switch_attempt = 0
            while switch_attempt < switch_profile_attempts:


                self.pause_event.wait()
                self.check_for_call()


                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Cheacking Loading Screen", "None","ds")

                self.ld_adb_controller.wait_till_list_element_visiable_in_fb(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Swtching Profile", "None","ds")

                switched_profile = self.ld_adb_controller.switch_profle_to(profile_name=profile_name,cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page="id")



                if switched_profile:
                    print("Profile switched successfully.")
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Profile switched successfully", "None","ds")
                    break
                else:
                    print(f"Profile switch failed, attempt {switch_attempt + 1}/{switch_profile_attempts}. Retrying...")
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Retrying Swtching Profile", "None","ds")
                    time.sleep(switch_profile_delay)
                    switch_attempt += 1


            if not switched_profile:
                print("Failed to switch profile after multiple attempts.")
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Failed to switch profile", "Error","s")
                restart_attempts += 1

        # If we've exhausted all restart attempts
        print(f"Failed to load app properly after {max_restart_attempts} restart attempts")
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Failed to Load App", "Error","s")
        return False

 
                
















    def image_upload_page_list(self,Profile_lists=[],id_name=None,image_captions_list=[],image_profile_folder = [],schdule_time_list=[],is_schedule_enable_list=[],app_package="com.facebook.katana"):
        
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

        home_screen = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=after_loading_screen_element)

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
                current_profile_folder = ""
                current_profile_schdule_list = []
                
                if current_profile_is_schedule_enable:
                    current_profile_schdule_list = schdule_time_list.pop()

                if len(image_profile_folder) > 0:
                    current_profile_folder = image_profile_folder.pop()



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
                        Reel_upload = self.image_upload_after_loading_screen(profile_name=current_profile,id_or_page=id_or_page,image_captions_list=current_profile_image_caption,  is_schedule_enable=current_profile_is_schedule_enable,schdule_time_list=current_profile_schdule_list,app_package=app_package, after_loading_screen_element=after_loading_screen_element,
                        max_attempts=4,max_restart_attempts=5,delay=3)

                        self.pause_event.wait()
                        self.check_for_call()
                        self.random_time(from_time=1,to_time=4)
                        self.empty_folders(current_profile_folder)
                        self.check_for_call_and_pause(id_or_page)
                        
                    except Exception as e :
                        print(f"Error Uploading Image on #{current_profile} Profile... Cause: {e}")
                        self.ld_adb_controller.stopApp(app_package=app_package)
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.startApp(app_package=app_package)
                        self.check_for_call_and_pause(id_or_page)
                        time.sleep(random.uniform(2,4))
                        self.ld_adb_controller.save_you_login_info()
                        self.check_for_call_and_pause(id_or_page)

                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.discard_post_and_story(cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page=id_or_page)

            self.ld_adb_controller.HomeButton()
            self.empty_folders(image_profile_folder)
            print("Image Uploading done on all profles")
            self.random_time(from_time=8,to_time=14)
            print("Closing LDPlayer instance")








if __name__ == "__main__": 

    from multiprocessing import Manager

    manager = Manager()
    control_pause =manager.Event()
    control_pause.set()


    test_run  = AdbimageUpload(device_serial="emulator-5554",local_output_file_path=r"E:\facebook_ld\ld_player0\main_folder",control_pasue_callback=control_pause,download_folder=r"E:\facebook_ld\ld_player0\Only Gaming\Only Gaming_download_img")


    folders= [r"E:\facebook_ld_player\LdPlayer0\main_folder\Brucelee_img",r"E:\facebook_ld_player\LdPlayer0\main_folder\Brucelee_img"]
    #test_run.empty_folders(folders)

    profile_list = [("Only Gaming","page"),("Kajal Kumari","id"),("Steki\r\n","page")]
    schdule_list = [True,False,True]
    image_captions= [["no","what is up guys","are you serious","oh yes"],["hi","hello","no","most dengrous","no","yes"],["no","what is up guys","are you serious","hi","hello","whatup?"]]




    id_name=profile_list[0]



    times_lists = [[(None,"12","02","AM"),(None,"12","30","PM"),(None,"12","02","AM"),(None,"3","02","PM"),(None,"7","02","PM"),(None,"8","02","PM")],[(None,"11","02","AM"),(None,"8","30","PM"),(None,"9","02","PM"),(None,"10","02","PM"),(None,"11","02","PM")]]



    """ test_run.image_upload_page_list(Profile_lists=profile_list,id_name=id_name,image_captions_list=image_captions,schdule_time_list=times_lists,is_schedule_enable_list=schdule_list,app_package="com.facebook.katana") """



    
    schdule_list_s = [(None,"11","02","AM"),(None,"11","02","PM"),(None,"11","02","PM"),(None,"11","05","PM")]


    test_run.image_upload(profile_name="Only Gaming",id_or_page="page",schedule_time_list=schdule_list_s,is_schedule_enable=False,num_of_images=3,is_group_sharing_enable=False)
    #test_run.test_schedule_time(time_lists=times_lists)






        