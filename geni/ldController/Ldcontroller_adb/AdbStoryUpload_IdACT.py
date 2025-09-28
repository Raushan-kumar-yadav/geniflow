import time
import random
from lxml import etree
import xml.etree.ElementTree as ET
import sys
import os
import shutil
from pathlib import Path


#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ldController.Ldcontroller_adb.LdAdb import *

try:
    
    from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten

except Exception as e :
    print(e)



class AdbStoryUpload():

    def __init__(self, control_pasue_callback,device_name=None, device_serial = None,local_output_file_path=""):
        self.device = device_name
        self.adb = device_serial
        self.pause_event = control_pasue_callback
        self.ld_adb_controller = LdAdbController(device_serial=device_serial,local_output_file_path=local_output_file_path)
        self.fb_popup = AdbFbPopUp(device_serial=self.adb,local_output_file_path=local_output_file_path,pause_callback=self.pause_event)

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

        
    def story_upload(self,profle_name,video_caption,id_or_page):

        
        self.check_for_call_and_pause(id_or_page)

        self.random_time(from_time=4,to_time=6)

        #click on plus button 

        pluse_btn_x_coor = 363
        pluse_btn_y_coor = 66

        self.ld_adb_controller.discard_post()
        self.check_for_call_and_pause(id_or_page)
        self.ld_adb_controller.discard_story()

        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
        plus_btn_x_path = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"

        self.ld_adb_controller.click_element(xpath_expr=plus_btn_x_path)

        self.ld_adb_controller.discard_post()
        self.check_for_call_and_pause(id_or_page)
        self.ld_adb_controller.discard_story()

        self.check_for_call_and_pause(id_or_page)

        #click on reels btn

        story_btn_x_coor = 337
        story_btn_y_coor = 210
        self.ld_adb_controller.clickByCoordinate(story_btn_x_coor,story_btn_y_coor)

        self.check_for_call_and_pause(id_or_page)

        
        #cheack if there is discard button
        is_discard_btn = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element="//node[@text='DISCARD']")

        self.check_for_call_and_pause(id_or_page)

        if is_discard_btn:

            self.check_for_call_and_pause(id_or_page)

            self.ld_adb_controller.click_element("//node[@text='DISCARD']")


            self.check_for_call_and_pause(id_or_page)
        
        self.pause_event.wait()

        gallary_btn_x_coor =  66
        gallary_btn_y_coor = 308

        self.ld_adb_controller.clickByCoordinate(gallary_btn_x_coor,gallary_btn_y_coor)


        self.check_for_call_and_pause(id_or_page)


        self.ld_adb_controller.clickByCoordinate(gallary_btn_x_coor,gallary_btn_y_coor)



        self.check_for_call_and_pause(id_or_page)



        self.ld_adb_controller.clickByCoordinate(gallary_btn_x_coor,gallary_btn_y_coor)



        self.check_for_call_and_pause(id_or_page)

        #click on profile album if not found then scroll and find
        profle_name_with_suffix = self.LdAdbController.clean_name(profle_name) + "_id_act_ story_video"
        Select_profile_album= f"//node[@content-desc='Select album, {profle_name_with_suffix}']"


        self.check_for_call_and_pause(id_or_page)

        is_cliced_on_profile_album=self.ld_adb_controller.scroll_and_click_on_element(scroll_x_coord=133,scroll_y_coordinate=645,element_xpath=Select_profile_album,max_no_attempt=10)


        if is_cliced_on_profile_album == False:
            self.check_for_call_and_pause(id_or_page)
            self.ld_adb_controller.BackButton()
            return


        self.check_for_call_and_pause(id_or_page)

        #click on frist video or photo

        frist_vid_x_coor= 98
        frist_vid_y_coor = 396

        if is_cliced_on_profile_album:


            self.check_for_call_and_pause(id_or_page)

            self.ld_adb_controller.clickByCoordinate(x=frist_vid_x_coor,y=frist_vid_y_coor)


            self.check_for_call_and_pause(id_or_page)


            #click on entry wedget to add captions
            add_caption_x_coor = 315
            add_caption_y_coor = 275

            self.random_time(from_time=8,to_time=12)
            
            is_share_now_btn = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element="//node[@content-desc='Share']")
            
            if not is_share_now_btn:
                self.ld_adb_controller.clickByCoordinate(x=200,y=random.uniform(a=26,b=30))
                self.check_for_call_and_pause(id_or_page)
                if not self.ld_adb_controller.check_element_visiable(element_to_be_visiable="//node[@content-desc='Share']"):
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id")
                    return

            if is_share_now_btn:
                
                
                #pull caption text 
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.clickByCoordinate(x=200,y=random.uniform(a=26,b=30))
                self.check_for_call_and_pause(id_or_page)

                text_btn_xpath = "//node[(@content-desc='Text')]"
                is_text_visible = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=text_btn_xpath)

                if video_caption != "":

                    if is_text_visible:
                        
                        self.ld_adb_controller.click_element(xpath_expr=text_btn_xpath)

                        self.check_for_call_and_pause(id_or_page)

                        self.ld_adb_controller.PullText(str(video_caption))


                        print(f"video captions for profile {profle_name}: ",video_caption)


                        self.random_time(from_time=2,to_time=4)

                        self.check_for_call_and_pause(id_or_page)

                        done_x_coord = 479
                        done_y_coord = 55

                        self.ld_adb_controller.clickByCoordinate(done_x_coord,done_y_coord)


                        self.check_for_call_and_pause(id_or_page)

                        drag_st_x_coord = 260
                        drag_st_y_coord = 481

                        drag_ed_x_coord=236
                        drag_ed_y_coord=800

                        self.ld_adb_controller.ScrollByCoordinate(x_start=drag_st_x_coord,y_start=drag_st_y_coord,x_end=drag_ed_x_coord,y_end=drag_ed_y_coord,Duration=random.  randint   (3000,4000))

                        self.check_for_call_and_pause(id_or_page)


                #click on share now btn 
                share_btn_x_coor = 435
                share_btn_y_coor = 905

                is_clicked_on_share = self.ld_adb_controller.click_element(xpath_expr="//node[@content-desc='Share']")

                if not is_clicked_on_share:
                    
                    self.ld_adb_controller.clickByCoordinate(x=share_btn_x_coor,y=share_btn_y_coor)
                    is_home_screen = self.ld_adb_controller.check_loading_screen_gone()
                    if not is_home_screen:
                        if not self.ld_adb_controller.click_element_if_visibale(xpath_expr = "//node[@content-desc='Discard story']"):
                            self.ld_adb_controller.BackButton()
                            self.check_for_call_and_pause(id_or_page=id_or_page)
                            self.ld_adb_controller.BackButton()
                            self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                        else:
                            self.ld_adb_controller.BackButton()
                            self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                        return
                    
                self.check_for_call_and_pause(id_or_page)
       
                self.ld_adb_controller.long_scroll_down_num(scroll_down_num=2,delay=3,check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)

                self.check_for_call_and_pause(id_or_page)

                self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page)
                reels_uploding_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]

                self.check_for_call_and_pause(id_or_page)


                self.random_time(from_time=int(reels_uploding_delay)*0.9,
                                 to_time=reels_uploding_delay)
                
                
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                self.check_for_call_and_pause(id_or_page)

                print("Story uploading Done")

                self.check_for_call_and_pause(id_or_page)

        #check for popups if visiable then close
        self.fb_popup.IncreaseYourReachOnHomeScreen()

    def video_upload_after_loading_screen(self, profile_name, video_captions, app_package, id_or_page,
                                         after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                                         max_attempts=4, delay=5, max_restart_attempts=5,
                                         switch_profile_attempts=3, switch_profile_delay=5):
        """
        Attempts to upload a reel after checking if the app has loaded properly.
        If loading screen check fails, it restarts the app and tries again until successful.

        Now includes retry logic for switching profiles.

        Parameters:
            profile_name (str): Profile name for the upload
            video_captions (str): Captions for the video
            app_package (str): Package name of the app
            after_loading_screen_element (str): XPath for element indicating app is loaded
            max_attempts (int): Number of attempts to check for loading completion
            delay (int): Seconds to wait between loading check attempts
            max_restart_attempts (int): Maximum number of app restart attempts
            switch_profile_attempts (int): Maximum number of attempts to switch profile
            switch_profile_delay (int): Delay in seconds between switch profile attempts

        Returns:
            bool: True if upload was successful, False otherwise
        """
        restart_attempts = 0

        while restart_attempts < max_restart_attempts:
            print(f"Checking if app is loaded (attempt {restart_attempts + 1}/{max_restart_attempts})")

            self.check_for_call_and_pause(id_or_page)

            # Check if the screen has loaded by looking for the specified element
            if self.ld_adb_controller.check_loading_screen_gone(
                after_loading_screen_element=after_loading_screen_element,
                max_attempts=max_attempts,
                delay=delay
            ):
                # Element found, screen has loaded, proceed with upload
                print("App loaded successfully, proceeding with Sotry upload")
                
                self.story_upload(profle_name=profile_name,id_or_page=id_or_page, video_caption=video_captions)
                
                return True

            # Element not found, restart the app and try again
            print("App not loaded properly, restarting app...")
            self.ld_adb_controller.stopApp(app_package=app_package)

            self.random_time(from_time=1, to_time=4)

            self.ld_adb_controller.startApp(app_package=app_package)
            self.check_for_call_and_pause(id_or_page)
            time.sleep(random.uniform(2,4))
            self.ld_adb_controller.save_you_login_info()
            self.check_for_call_and_pause(id_or_page)
            self.ld_adb_controller.discard_post()
            self.check_for_call_and_pause(id_or_page)
            self.ld_adb_controller.discard_story()

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

    def story_upload_page_list(self,Profile_lists=[],id_name=None,image_captions=[],image_profile_folder = [],app_package="com.facebook.katana"):
        
        #self.ld_adb_controller.cheack_ld_instance_open_or_not_for_20sec(id_frame_idx=1)

        self.pause_event.wait()
        self.check_for_call()

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

                current_profile = Profile_lists.pop()
                current_profile_video_caption = image_captions.pop()

                self.pause_event.wait()
                self.check_for_call()

                check_profile = True #self.switch_profle_to(profile_name=current_profile)

                self.pause_event.wait()
                self.check_for_call()
                
                self.ld_adb_controller.startApp(app_package)
                self.check_for_call_and_pause()
                time.sleep(random.uniform(2,4))
                self.ld_adb_controller.save_you_login_info()
                self.check_for_call_and_pause()
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page="id",scroll_down_num=3,delay=1)


                if check_profile == True:

                    try:
                        Reel_upload = self.video_upload_after_loading_screen(profile_name=current_profile,id_or_page="id",video_captions=current_profile_video_caption,     app_package=app_package,after_loading_screen_element=after_loading_screen_element,
                        max_attempts=4,max_restart_attempts=5,delay=3)

                        self.pause_event.wait()
                        self.check_for_call()
                    except Exception as e:
                        print(f"Error Uploading Story on #{current_profile} Profile")
                        self.ld_adb_controller.stopApp(app_package=app_package)
                        self.check_for_call_and_pause("id")
                        self.ld_adb_controller.startApp(app_package=app_package)
                        self.check_for_call_and_pause()
                        time.sleep(random.uniform(2,4))
                        self.ld_adb_controller.save_you_login_info()
                        self.check_for_call_and_pause()
                        self.ld_adb_controller.discard_post_and_story(cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page="id")

            self.random_time(from_time=1,to_time=3)

            self.empty_folders(image_profile_folder) #if we want to add multiple story upload features then we have to change this to current_folders

        
            print(f"Uploding done on all page of {id_name}")








if __name__ == "__main__":
    
    from multiprocessing import Manager
    Manager_m = Manager()
    pause_enn = Manager_m.Event()
    pause_enn.set()

    test_run  = AdbStoryUpload(control_pasue_callback=pause_enn,device_serial="emulator-5554",local_output_file_path=r"E:\facebook_ld_player\LdPlayer0\main_folder")

    profile_list = [("Brucelee","page"),("Kajal Kumari","id")]
    video_captions= ["what is up guys ","what is up guys"]
    id_name=profile_list[0]
    folders= [r"E:\facebook_ld_player\LdPlayer0\main_folder\Brucelee_img",r"E:\facebook_ld_player\LdPlayer0\main_folder\Brucelee_img"]

    test_run.story_upload_page_list(Profile_lists=profile_list,id_name=id_name,image_captions=video_captions,app_package="com.facebook.katana",image_profile_folder=folders)







        