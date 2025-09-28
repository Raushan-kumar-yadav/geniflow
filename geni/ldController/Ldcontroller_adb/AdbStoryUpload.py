from re import sub
import time
import random
import xml.etree.ElementTree as ET
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



class AdbStoryUpload():

    def __init__(self, control_pasue_callback,device_name=None, device_serial = None,image_or_video="image",local_output_file_path="",download_folder="",activity_queue=None):
        self.device = device_name
        self.adb = device_serial
        self.activity_queue = activity_queue
        self.pause_event = control_pasue_callback
        self.local_output_file_path = local_output_file_path
        self.ld_adb_controller = LdAdbController(device_serial=device_serial,local_output_file_path=local_output_file_path,download_folder=download_folder)
        #self.fb_popup = AdbFbPopUp(device_serial=self.adb,local_output_file_path=local_output_file_path,pause_callback=self.pause_event)

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

        

    def story_upload(self,profile_name,id_or_page,image_or_video="video",story_caption=[],is_caption_from_original=True,download_folder="",num_of_story=1):

        #self.ld_adb_controller.InstallAndCheckAPK()




        # Check if any winodw and discard them 
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Discard Post", "None","ds")
        self.ld_adb_controller.discard_post()
        self.check_for_call_and_pause(id_or_page)
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Story Post", "None","ds")
        self.ld_adb_controller.discard_story()




        content_num = 1

        for story in range(num_of_story):

            try:
                # Subfolder
                subfolder="videoss"
                if image_or_video == "video":
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Uploading Video In Story", "None","ds")
                    subfolder="reels"
                else:
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Uploading Image In Story", "None","ds")
                    subfolder ="imagess"
                
                if image_or_video == "both":
                    random_choice = random.choices( ["reels","imagess"])
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Choosing Random content type for Story", "None","ds")
                    subfolder = random_choice


                # Get caption for this video 
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Moving Content", "None","ds")
                caption = self.ld_adb_controller.MoveFileWithCaption(media_type=image_or_video,sub_folder=subfolder,download_folder=download_folder)
    
                if not caption:
                    print("Video not avlaible in download folder so trying image")
                    subfolder = "imagess"
                    caption = self.ld_adb_controller.MoveFileWithCaption(media_type="image",sub_folder=subfolder,download_folder=download_folder)
                    if not caption:
                        print("Tried Image to image also not avlaible so quiting story upload")
                        return 
                    

                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Getting Captions", "None","ds")
                if not is_caption_from_original:
                    caption = story_caption.pop(0)
    
    
    
                self.check_for_call_and_pause(id_or_page)
    
    
    
    
                # Switch to Gallery to refrace the file that add to folder
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Gallery", profile_name, "Opening Gallery", "None","ds")
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Gallery",app_package_name_to_switch="com.android.gallery3d")
                self.check_for_call_and_pause(id_or_page)
    
    
    
    
                # Switch to facebook
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Swtching to Facebook", "None","ds")
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                self.check_for_call_and_pause(id_or_page)
            
    
    
    
    
    
                #click on plus button 
                pluse_btn_x_coor = 363
                pluse_btn_y_coor = 66
            
    
    



                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,  delay=0)
    
    
    



    
                plus_btn_x_path = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"
                create_strory_btn_xapth = "//node[@content-desc='Create story']"
                create_a_story_btn_xpath = "//node[@content-desc='Create a story']"
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Clicking Create Story", "None","ds")
                self.ld_adb_controller.click_element_if_visibale(xpath_expr=create_strory_btn_xapth)
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.click_element_if_visibale(xpath_expr=create_a_story_btn_xpath)
    
    
    
    
    
    
    
    
    
            
                # Cheack if there is discard button
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Discard Btn", "None","ds")
                is_discard_btn = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element="//node[@text='DISCARD']")
                if is_discard_btn:
                
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.click_element("//node[@text='DISCARD']")
                    self.check_for_call_and_pause(id_or_page)
            
    
    
    
    
    
    
                self.pause_event.wait()
                gallary_btn_x_coor =  66
                gallary_btn_y_coor = 308
    
                gallery_btn_xpat = "//node[@content-desc='Gallery']"
                gallery_btn_x_coor = 77
                gallery_btn_y_coor = 260
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Opening Album", "None","ds")
                is_gallery_btn_clicked = self.ld_adb_controller.click_element_if_visibale(xpath_expr=gallery_btn_xpat)
                if not is_gallery_btn_clicked:
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.clickByCoordinate(gallery_btn_x_coor, gallery_btn_y_coor)
    
    
    
    
    
    
                # Click on profile album if not found then scroll and find
                Select_profile_album= f"//node[@content-desc='Select album, {subfolder}']"
                self.check_for_call_and_pause(id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Album", "None","ds")
                is_cliced_on_profile_album=self.ld_adb_controller.click_element_if_visibale(xpath_expr=Select_profile_album)
    
                if is_cliced_on_profile_album == False:
                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Album Not Found", "None","s")
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Going to home", "None","ds")
                    self.ld_adb_controller.BackButton()
                    return
    
    
    
    
    
    
    
                self.check_for_call_and_pause(id_or_page)
        
    
    
                # Click on frist video or photo
                frist_vid_x_coor= 98
                frist_vid_y_coor = 396
    
                if is_cliced_on_profile_album:
                
                
                    self.check_for_call_and_pause(id_or_page)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Selecting Video", "None","ds")
                    self.ld_adb_controller.clickByCoordinate(x=frist_vid_x_coor,y=frist_vid_y_coor)
                    self.check_for_call_and_pause(id_or_page)
                    #Click on entry wedget to add captions
                    add_caption_x_coor = 315
                    add_caption_y_coor = 275
                    self.random_time(from_time=8,to_time=12)
                    activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Wating For Next Win", "None","ds")
                    is_share_now_btn = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element="//node[@content-desc='Share']")
    
    
    
    
                    if not is_share_now_btn:
                        self.ld_adb_controller.clickByCoordinate(x=share_btn_x_coor,y=share_btn_y_coor)
                        is_home_screen = self.ld_adb_controller.check_loading_screen_gone(delay=0)
                        if not is_home_screen:
                            if not self.ld_adb_controller.click_element_if_visibale(xpath_expr = "//node[@content-desc='Discard story']"):
                            
                                self.check_for_call_and_pause(id_or_page=id_or_page)
                                self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,       id_or_page=id_or_page)
    
                            else:
                                self.ld_adb_controller.BackButton()
                                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,  id_or_page=id_or_page,scroll_down_num=3,delay=0)
                            return
    
    
    
    
    
    
    
                    if is_share_now_btn:
                    
                        # Pull caption text 
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Popups", "None","ds")
                        self.ld_adb_controller.clickByCoordinate(x=200,y=random.uniform(a=26,b=30))
                        self.check_for_call_and_pause(id_or_page)
    
                        text_btn_xpath = "//node[(@content-desc='Text')]"
                        self.random_time(from_time=8,to_time=13)
                        is_text_visible = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=text_btn_xpath)
    
    
    
    
                        if caption != "":
                        
                            if is_text_visible:
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Adding Capions", "None","ds")
                                self.ld_adb_controller.click_element(xpath_expr=text_btn_xpath)
    
                                self.check_for_call_and_pause(id_or_page)

                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Sending Caption", "None","ds")
                                self.ld_adb_controller.PullText(str(caption))
    
    
                                print(f"video captions for profile {profile_name}: ",caption)
    
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Wating For Any Popups", "None","ds")
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

                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Draging Caption", "None","ds")
                                self.ld_adb_controller.ScrollByCoordinate(x_start=drag_st_x_coord,y_start=drag_st_y_coord,x_end=drag_ed_x_coord,        y_end=drag_ed_y_coord,Duration=random.  randint   (3000,4000))
    
                                self.check_for_call_and_pause(id_or_page)
    
    
    
    
    
    
    
    
    
    
    
                        # Click on share now btn 
                        share_btn_x_coor = 435
                        share_btn_y_coor = 905
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Sharing Story..", "None","ds")
                        is_clicked_on_share = self.ld_adb_controller.click_element(xpath_expr="//node[@content-desc='Share']")
                        if not is_clicked_on_share:
                        
                            self.ld_adb_controller.clickByCoordinate(x=share_btn_x_coor,y=share_btn_y_coor)
                            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Home Screen", "None","ds")
                            is_home_screen = self.ld_adb_controller.check_loading_screen_gone()
                            if not is_home_screen:
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Home Screen Not Visible", "None","ds")
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Back Btn", "None","ds")
                                self.ld_adb_controller.BackButton()
                                self.check_for_call_and_pause(id_or_page=id_or_page)
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Back Btn", "None","ds")
                                self.ld_adb_controller.BackButton()
                                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,  id_or_page=id_or_page,scroll_down_num=3,delay=0)
                                return
    
    
    
    
    
    
    
    
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                        self.ld_adb_controller.scroll_down_num(scroll_down_num=2,delay=3,check_for_call_and_pause=self.check_for_call_and_pause,        id_or_page=id_or_page)
                        self.check_for_call_and_pause(id_or_page)
    
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Uploading..", "None","ds")
                        self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.check_for_call_and_pause,      id_or_page=id_or_page)

                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Story Uploaded..", "None","ds")
                        reels_uploding_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
    
    
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Waiting Delay", "None","ds")


                        self.random_time(from_time=int(reels_uploding_delay)*0.9,
                                         to_time=reels_uploding_delay)
                        

                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Scroll Down", "None","ds")
                        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,        scroll_down_num=3,delay=0)
    
                        self.check_for_call_and_pause(id_or_page)
    
                        print("Story uploading Done")
    
                        self.check_for_call_and_pause(id_or_page)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Removing Used Contents", "None","ds")
                        self.ld_adb_controller.empty_folders(folder_input=self.local_output_file_path,subfolder=subfolder)
                        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Story Uploaded successful ", f"Count:{content_num}","s")
                        content_num +=1

            except Exception as e :
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Story Uploadeding Error", f"Count:{content_num}","s")
                print(f"Error uploading story:{e}")

        #check for popups if visiable then close
        #self.fb_popup.IncreaseYourReachOnHomeScreen()

    def story_upload_after_loading_screen(self, profile_name, captions_source, app_package, id_or_page,image_or_video,caption_list=[],download_folder="",stroy_num=1,
                                         after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                                         max_attempts=4, delay=5, max_restart_attempts=5,
                                         switch_profile_attempts=3, switch_profile_delay=5):





        

        self.check_for_call_and_pause()
        activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Starting APP", "None","ds")
        self.ld_adb_controller.startApp()
        self.check_for_call_and_pause()






        is_caption_from_original_file = False
        if captions_source == "From Original Video":
            is_caption_from_original_file = True
        else:
            is_caption_from_original_file = False

        
        restart_attempts = 0







        while restart_attempts < max_restart_attempts:
            print(f"Checking if app is loaded (attempt {restart_attempts + 1}/{max_restart_attempts})")

            self.check_for_call_and_pause(id_or_page)
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Checking Loading Screen", "None","ds")
            # Check if the screen has loaded by looking for the specified element
            if self.ld_adb_controller.check_loading_screen_gone(
                after_loading_screen_element=after_loading_screen_element,
                max_attempts=max_attempts,
                delay=delay
            ):
                activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "App Loaded", "None","ds")
                # Element found, screen has loaded, proceed with upload
                print("App loaded successfully, proceeding with Sotry upload")
                
                self.story_upload(profile_name=profile_name,id_or_page=id_or_page,image_or_video=image_or_video,story_caption=caption_list,is_caption_from_original=is_caption_from_original_file,download_folder=download_folder)
                
                return True




            # Element not found, restart the app and try again
            print("App not loaded properly, restarting app...")
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "App Not loaded", "None","ds")
            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Stoping App", "None","ds")
            self.ld_adb_controller.stopApp(app_package=app_package)




            activity_callback(self.activity_queue, self.device, "Facebook", profile_name, "Starting App", "None","ds")
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
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
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





if __name__ == "__main__":
    
    from multiprocessing import Manager
    Manager_m = Manager()
    pause_enn = Manager_m.Event()
    pause_enn.set()

    test_run  = AdbStoryUpload(control_pasue_callback=pause_enn,device_serial="emulator-5554",local_output_file_path=r"E:\facebook_ld\ld_player0\main_folder",download_folder=r"E:\facebook_ld\ld_player0\Brucelee\Brucelee_download_story")

    profile_list = [("Brucelee","page"),("Kajal Kumari","id")]
    video_captions= [["what is up guys "],["what is up guys"]]
    id_name=profile_list[0]
    folders= [r"E:\facebook_ld_player\LdPlayer0\main_folder\Brucelee_img",r"E:\facebook_ld_player\LdPlayer0\main_folder\Brucelee_img"]


    test_run.story_upload(profile_name="Brucelee",id_or_page="page",image_or_video="image",story_caption="Hi❤️",is_caption_from_original=False)





        