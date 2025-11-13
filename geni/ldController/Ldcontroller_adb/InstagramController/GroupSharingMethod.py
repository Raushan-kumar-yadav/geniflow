from ast import Pass, Return
from asyncio import wait
import time
import random
from typing import Self
from click import Group, group
from lxml import etree
import xml.etree.ElementTree as ET
import sys
from datetime import datetime
import os
import shutil
from pathlib import Path

import uiautomator2

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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..')))

#ldController.Ldcontroller_adb.
from ldController.Ldcontroller_adb.LdAdb import *

try:
    #ldController.Ldcontroller_adb.
    from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten

except Exception as e :
    print(e)

class GroupPosting():
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
        call_decline_xpath ="//node[@content-desc='Decline']"

        self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)


        
    def check_for_call_and_pause(self,id_or_page="id"):

        self.random_time()
        self.pause_event.wait()
        
        if id_or_page == "id":
            call_decline_xpath ="//node[@content-desc='Decline']"
            self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)
    
    



    def UploadPostInGroup(self,ProfileName,is_caption_from_original_file=True,VideoCaptionList=[],Profile_lists=[],id_name=None):
                
                
                self.check_for_call_and_pause()
                # FacebookLogo_xpath ="//node[contains(@content-desc,'Create, Double tap to create a new post, story, or reel')"
                # IsOnHomeTab = self.ld_adb_controller.check_element_visiable(after_loading_screen_element=FacebookLogo_xpath,max_attempts=10,delay=2)
                # if not IsOnHomeTab:
                #     self.ld_adb_controller.back_btn_untill_home()
                # print("notttt")

                self.ld_adb_controller.BackButton()
                self.check_for_call_and_pause()
                self.ld_adb_controller.BackButton()
                self.check_for_call_and_pause()
                self.ld_adb_controller.BackButton()
                home_btn_xpath = "//node[contains(@content-desc,'Create, Double tap to create a new post, story, or reel')]"
                IsEditvideoTabVisible = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=home_btn_xpath,max_attempts=5,delay=2)
                if not IsEditvideoTabVisible:
                    self.ld_adb_controller.BackButton()
                    self.check_for_call_and_pause()
                    self.ld_adb_controller.BackButton()
                print("founddddddddd")
                self.check_for_call_and_pause()
                # #GO TO PROFILE PAGE                
                profile_x_coord=503
                profile_y_coord=147

                menu_btn_xpath = "//node[contains(@content-desc,'Menu, tab')]"

                is_menu_btn_clicked = self.ld_adb_controller.clickByCoordinate(profile_x_coord,profile_y_coord)
                self.check_for_call_and_pause()

                Group_btn_xpath = "//node[contains(@content-desc,'Groups')]"
                Is_Group_btn_clicked = self.ld_adb_controller.click_element_if_visibale(Group_btn_xpath)
                self.check_for_call_and_pause()
                
                Search_Btn_XPath ="//node[@text='Search your groups by name']"
                Is_Group_btn_clicked = self.ld_adb_controller.click_element_if_visibale(Search_Btn_XPath)
                self.check_for_call_and_pause()

                
                
                
                if not VideoCaptionList:
                    print("⚠️ No captions left, skipping.")
                    return
                if not Profile_lists:
                    print("⚠️ No groups left, skipping.")
                    return

                video_caption = VideoCaptionList[0]
                Group_Name = Profile_lists[0]


                # self.ld_adb_controller.clear_text_field(max_length=100)
                self.ld_adb_controller.PullText(str(Group_Name))
                GroupName_xpath = f"//node[contains(@content-desc,'{Group_Name}')]"
                self.check_for_call_and_pause()
                
    
                Is_Group_available = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=GroupName_xpath,max_attempts=10,delay=2)
                if Is_Group_available:  
                    IsInGroup=self.ld_adb_controller.click_element_if_visibale(GroupName_xpath)
                else:
                    pass
   
                self.check_for_call_and_pause()

                CreatePostButton_XPath = "//node[contains(@content-desc,'Write something...')]" # post buttton x path
                self.ld_adb_controller.scroll_and_find_element(scroll_x_coord=20,scroll_y_coordinate=0,element_xpath=CreatePostButton_XPath,max_no_attempt=5)
                self.check_for_call_and_pause()

                self.ld_adb_controller.click_element_if_visibale(CreatePostButton_XPath) # Click on post button
                self.check_for_call_and_pause() 

                self.ld_adb_controller.switch_appliction(app_name_to_switch="Gallery",app_package_name_to_switch="com.android.gallery3d")#Switching to gallery to refresh content loading in fb
                self.check_for_call_and_pause() #wait for random delay and chk for calls decline 
            

                self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")#switching back to Facebook
                self.check_for_call_and_pause() 

                Describe_your_reel_btn_xpath = "//node[contains(@content-desc,'Photo/video')]"
                self.ld_adb_controller.click_element_if_visibale(xpath_expr=Describe_your_reel_btn_xpath)
                self.check_for_call_and_pause() 


                select_gallery_album = "//node[@content-desc='Gallery']"
                is_clicked_on_alb = self.ld_adb_controller.click_element(xpath_expr=select_gallery_album)
                if not is_clicked_on_alb:
                    ...
                
                select_Images_album = "//node[@content-desc='imagess, 1, Media']"
                is_clicked_on_alb = self.ld_adb_controller.click_element(xpath_expr=select_Images_album)
                self.check_for_call_and_pause()

                first_btn_x_coord = 85
                first_btn_y_coord = 418
                self.ld_adb_controller.clickByCoordinate(x=first_btn_x_coord,y=first_btn_y_coord)
                self.check_for_call_and_pause()


                caption_Btn_XPath ="//node[@text='Say something about this photo…']"
                IsCaptionButtonClicked = self.ld_adb_controller.click_element_if_visibale(caption_Btn_XPath)
                self.check_for_call_and_pause()
                
                self.ld_adb_controller.PullText(str(video_caption))
                self.check_for_call_and_pause()

                           
               
                Post_Btn_XPath = "//node[@content-desc='POST']"
                IsPostButtonClicked = self.ld_adb_controller.click_element_if_visibale(Post_Btn_XPath)
                self.check_for_call_and_pause()

                

                # Check if POST was successful
                if IsPostButtonClicked:
                    print("✅ Posted successfully")
                else:
                    print("❌ Failed to post")

class GroupSharing():

    def __init__(self,device_name,device_serial,download_folder,activity_queue,control_pasue_callback,local_output_file_path):
        self.device = device_name
        self.adb = device_serial
        self.download_folder_path = download_folder
        self.activity_queue = activity_queue
        self.pause_event = control_pasue_callback
        self.ld_adb_controller = LdAdbController(device_serial=device_serial,local_output_file_path=local_output_file_path,download_folder=download_folder)
        self.device_config_dic = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")

    def SharePostToGroups(self,ProfileName,is_caption_from_original_file=True,MainGroupList=[],ShareToGroupList=[],isIgnoreNameTrue=False,maxShare=1,):
        ...
        
    
    def SelectGroup(self):
        ...












if __name__ == "__main__": 
    from multiprocessing import Manager

    # Initialize multiprocessing manager and control flag
    manager = Manager()
    control_pause = manager.Event()
    control_pause.set()

    # Initialize your GroupSharing instance
    test_run = GroupSharing(
        device_serial="emulator-5554",
        local_output_file_path=r"D:\GENIDATA\LD-1\MAIN",
        control_pasue_callback=control_pause,
        download_folder=r"D:\GENIDATA\LD-1\MAIN\reels"
    )

    # Group names where you want to upload
    GroupNameList = ['Xavier Memes II','fcked up Memes']

    # Same caption for all groups
    VideoCaption = "what is up guys"

    print("🚀 Starting upload process...\n")

    # Upload to each group one by one
    for group_name in GroupNameList:
        print(f"📤 Uploading to group: {group_name}")
        try:
            test_run.UploadPostInGroup(
                ProfileName="Maxxy Here",
                VideoCaptionList=[VideoCaption],   # same caption
                Profile_lists=[group_name]         # one group at a time
            )
            
            print(f"✅ Successfully uploaded to {group_name}\n")
        except Exception as e:
            print(f"❌ Failed to upload in {group_name}: {e}\n")

    print("🎉 All uploads complete!")