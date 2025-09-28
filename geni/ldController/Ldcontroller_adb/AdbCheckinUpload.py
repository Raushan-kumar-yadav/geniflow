import time
import random
from lxml import etree
import xml.etree.ElementTree as ET
import sys
import os
from pathlib import Path
import shutil


#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#ldController.Ldcontroller_adb.
from ldController.Ldcontroller_adb.LdAdb import *

try:
    #ldController.Ldcontroller_adb.
    from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten

except Exception as e :
    print(e)



class AdbCheackinUpload():

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
        
        call_decline_xpath ="//node[@content-desc='DECLINE']"
        self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)


    def checkin_upload(self,profle_name,image_caption,checkin_location,add_photo,is_caption_from_original_file,download_folder):


        id_or_page = "id"
        sub_folder = "imagess"
        current_image_caption = image_caption


        self.pause_event.wait()
        self.check_for_call()

        
        #click on plus button 
        pluse_btn_x_coor = 363
        pluse_btn_y_coor = 66


        if not checkin_location:
            print("CheckIN location not givin so skipping....")
            return


        if add_photo:

            # Get caption for this video (or use default if none available)
            Is_img_avl = self.ld_adb_controller.MoveFileWithCaption(media_type="image",sub_folder=sub_folder,download_folder=download_folder)

            if not Is_img_avl:
                print("Image not avl in folder skipping...")
                return
            else:
                current_image_caption = Is_img_avl



            # Replace the caption if not from original file 
            if not is_caption_from_original_file:
                current_image_caption = image_caption


            # Switch to Gallery to refrace the file that add to folder
            self.check_for_call_and_pause(id_or_page)
            self.ld_adb_controller.switch_appliction(app_name_to_switch="Gallery",app_package_name_to_switch="com.android.gallery3d")
            self.check_for_call_and_pause(id_or_page)




            # Switch to facebook
            self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
            self.check_for_call_and_pause(id_or_page)






        # Click on plus btn 
        plus_btn_x_path = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"
        self.check_for_call_and_pause()
        self.ld_adb_controller.click_element(xpath_expr=plus_btn_x_path)







        #click on image or post btn
        post_btn_x_coor = 359
        post_btn_y_coor = 149
        self.check_for_call_and_pause()
        self.ld_adb_controller.clickByCoordinate(post_btn_x_coor,post_btn_y_coor)







        
        #cheack if there is discard button
        self.check_for_call_and_pause()
        is_discard_btn = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element="//node[@text='DISCARD']")
        if is_discard_btn:
            self.check_for_call()
            self.ld_adb_controller.click_element("//node[@text='DISCARD']")
            self.random_time()
            self.check_for_call()
        






        # Click on checnIN btn
        photo_checkon_button_xpath = "//node[(@content-desc='Check in')]"
        self.check_for_call_and_pause()
        self.ld_adb_controller.click_element(xpath_expr=photo_checkon_button_xpath)


        
        is_search_avl = True

        location_not_found_xpath =["//node[(@content-desc='Refresh')]","//node[contains(@text,'Please refresh or type to search for a specific place')]"]
        search_xpath = "//node[contains(@text,'Search')]"
        
        self.check_for_call_and_pause()
        is_search_visible = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=search_xpath,max_attempts=6,delay=2)
        if is_search_visible:
            self.ld_adb_controller.click_element(xpath_expr=search_xpath)
            self.check_for_call_and_pause()
            self.ld_adb_controller.PullText(str(checkin_location))
            self.check_for_call_and_pause()
            is_search_avl = self.ld_adb_controller.CheckLoadingScreenGoneListElements(after_loading_screen_elements=location_not_found_xpath)

            if is_search_avl:
                self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                return
            
        else:
            self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
            return










        if not is_search_avl:

            frist_search_result_x_coord = 245
            frist_search_result_y_coord = 348
            time.sleep(random.uniform(a=4,b=7))
            self.ld_adb_controller.clickByCoordinate(x=frist_search_result_x_coord,y=frist_search_result_y_coord)
            self.check_for_call_and_pause()




            if add_photo:
                self.check_for_call_and_pause()
                self.ld_adb_controller.click_element(xpath_expr="//node[(@content-desc='Photo/video')]")







                # Check again and if found then click on discard btn
                self.ld_adb_controller.discard_post()
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.discard_story()
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.click_element_if_visibale("//node[@text='DISCARD']")
                self.pause_event.wait()







                # Click on gallery button
                gallery_btn_x_coor = 50
                gallery_btn_y_coor = 164
                gallery_btn_xpat = "//node[@content-desc='Gallery']"
                self.check_for_call_and_pause(id_or_page)
                is_gallery_btn_clicked = self.ld_adb_controller.click_element_if_visibale(xpath_expr=gallery_btn_xpat)
                if not is_gallery_btn_clicked:
                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.clickByCoordinate(gallery_btn_x_coor, gallery_btn_y_coor)



                # Select imagess folder
                select_imagess_album_btn_xpath = f"//node[contains(@content-desc,'{sub_folder}')]"
                self.check_for_call_and_pause(id_or_page)
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.click_element(xpath_expr=select_imagess_album_btn_xpath)






                # Click on frist video in facebook gallery
                frist_image_x_coord = 77
                frist_image_y_coord = 290
                self.check_for_call_and_pause(id_or_page)
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
                is_create_post_label_visiable = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=create_post_label_xpath,  max_attempts=20,delay=2)


                if not is_create_post_label_visiable:

                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,delay=0)
            
            



                if is_create_post_label_visiable:


                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.click_element_if_visibale(xpath_expr="//node[contains(@text,'Say something about this photo')]")
                        self.ld_adb_controller.click_element_if_visibale(xpath_expr="//node[contains(@text,'Say something about this photo')]")




                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.PullText(str(current_image_caption))
                        print(f"image caption : {current_image_caption}")




                        self.random_time(from_time=0.5, to_time=1)
                        self.ld_adb_controller.click_on_cursor()




                        self.random_time(from_time=2, to_time=4)
                        self.pause_event.wait()
                        self.check_for_call()




                        is_next_clicked = self.ld_adb_controller.click_element_if_visibale(
                            xpath_expr=next_btn_xpath
                        )




                        if not is_next_clicked:
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.clickByCoordinate(x=next_btn_x_coor, y=next_btn_y_coor)

                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.long_scroll_down_num(scroll_down_num=2,delay=1,check_for_call_and_pause=self.check_for_call_and_pause,   id_or_page=id_or_page)
                        self.check_for_call_and_pause(id_or_page)



                        is_clicked_on_next2 = self.ld_adb_controller.click_element_if_visibale(xpath_expr=next_btn_xpath)





                self.check_for_call_and_pause(id_or_page)





                # Wait for Post setting label to appear
                post_btn_xpath = "//node[@content-desc='POST']"
                post_btn_x_coord = 480
                post_btn_y_coord = 70

                self.check_for_call_and_pause(id_or_page)
                is_post_setting_visible = self.ld_adb_controller.CheckLoadingScreenGoneListElements (after_loading_screen_elements=share_now_screen_xpaths,max_attempts=20,delay=2)

                # now share the post
                is_clicked_post_btn = self.ld_adb_controller.click_element(xpath_expr=post_btn_xpath,max_attempts=2)
                if not is_clicked_post_btn:
                    self.ld_adb_controller.clickByCoordinate(x=post_btn_x_coord,y=post_btn_y_coord)

               

                if not is_post_setting_visible:

                    self.check_for_call_and_pause()
                    self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,delay=0)
                    
                    self.pause_event.wait()
                    self.check_for_call()
                    reels_uploding_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                    self.random_time(from_time=int(reels_uploding_delay)*0.9,
                                     to_time=reels_uploding_delay)
                    print("Checkin with image uploading Done")
                    self.check_for_call()
                    self.ld_adb_controller.empty_folders(subfolder=sub_folder)




            else:
                    


                    self.ld_adb_controller.click_element(xpath_expr="//node[contains(@text,'on your mind?')]")
                    self.check_for_call_and_pause()
                    self.ld_adb_controller.PullText(str(current_image_caption))
                    self.check_for_call_and_pause()
                    self.ld_adb_controller.click_element(xpath_expr="//node[@content-desc='NEXT']")
                    self.check_for_call_and_pause()
                    self.ld_adb_controller.click_element(xpath_expr="//node[@content-desc='POST']")

                    reels_uploding_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                    self.random_time(from_time=int(reels_uploding_delay)*0.9,
                                         to_time=reels_uploding_delay)
                    self.ld_adb_controller.empty_folders(subfolder=sub_folder)
   






        
        





    def checkin_upload_after_loading_screen(self, profile_name, captions,checkin_location,add_photo,is_caption_from_original_file,download_folder,
                                         after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                                         max_attempts=4, delay=5, max_restart_attempts=5,
                                         switch_profile_attempts=3, switch_profile_delay=5,app_package="com.facebook.katana"):



        caption_from_original_file = False
        if is_caption_from_original_file == "From Original Video":
            caption_from_original_file = True



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
                print("App loaded successfully, proceeding with image upload")
                
                self.checkin_upload(profle_name=profile_name, image_caption=captions,checkin_location=checkin_location,add_photo=add_photo,is_caption_from_original_file=caption_from_original_file,download_folder=download_folder)
                
                return True

            # Element not found, restart the app and try again
            print("App not loaded properly, restarting app...")
            self.ld_adb_controller.stopApp(app_package=app_package)

            self.random_time(from_time=2, to_time=5)

            self.ld_adb_controller.startApp(app_package=app_package)
            self.check_for_call_and_pause()
            time.sleep(random.uniform(2,4))
            self.ld_adb_controller.save_you_login_info()


            # Retry switching profile until successful or attempts exhausted
            switch_attempt = 0
            while switch_attempt < switch_profile_attempts:

                self.pause_event.wait()
                self.check_for_call()


                switched_profile =self.ld_adb_controller.switch_profle_to(profile_name=profile_name,cheack_for_call_and_pause_callback=self.check_for_call_and_pause,id_or_page="id")
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



    def image_upload_page_list(self,Profile_lists=[],id_name=None,image_captions=[],image_profile_folder = [],checkin_loactions = [],app_package="com.facebook.katana",add_photo=False,):
        
        #self.ld_adb_controller.cheack_ld_instance_open_or_not_for_20sec(id_frame_idx=1)

        self.pause_event.wait()
        self.check_for_call()

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

                current_profile = Profile_lists.pop()
                current_profile_video_caption = " "
                current_image_profile_folder = ""
                if len(image_captions) > 0:
                    current_profile_video_caption = image_captions.pop()
                
                if len(checkin_loactions) > 0 :
                    current_checkin_location= checkin_loactions.pop()

                if len(image_profile_folder) >0:
                    current_image_profile_folder = image_profile_folder.pop()

                self.pause_event.wait()
                self.check_for_call()

                check_profile = True #self.switch_profle_to(profile_name=current_profile)

                self.pause_event.wait()
                self.check_for_call()

                if check_profile == True:

                    try:
                        checkin_upload = self.checkin_upload_after_loading_screen(profile_name=current_profile,video_captions=current_profile_video_caption,    checkin_location=current_checkin_location,add_photo=add_photo,app_package=app_package,after_loading_screen_element=after_loading_screen_element,
                        max_attempts=4,max_restart_attempts=5,delay=3)

                        self.pause_event.wait()
                        self.check_for_call()

                        self.random_time(from_time=1,to_time=3)
                        self.empty_folders(current_image_profile_folder)

                        self.pause_event.wait()
                        self.check_for_call()
                    except Exception as e :
                        print(f"Error Uploading CheackIN Post #{current_profile} Profile" )



            self.random_time(from_time=8,to_time=14)
            print(f"Uploding done on all page of {id_name}")
           








if __name__ == "__main__":
    
    from multiprocessing import Manager
    Manager_m = Manager()
    pause_enn = Manager_m.Event()
    pause_enn.set()

    test_run  = AdbCheackinUpload(control_pasue_callback=pause_enn,device_serial="emulator-5558",local_output_file_path=r"E:\facebook_ld\raushan\main_folder")

    profile_list = "Rekha Kumari"
    video_captions= "what is up guys "
    checkin_loaciton = "Las Vegas"
    id_name="Rekha Kumari"
    folders= r"E:\facebook_ld\raushan\Rekha Kumari\Rekha Kumari_download_img"

    test_run.checkin_upload_after_loading_screen(profile_name=profile_list,captions=video_captions,checkin_location=checkin_loaciton,add_photo=False,app_package="com.facebook.katana",download_folder=folders,is_caption_from_original_file=True)







        