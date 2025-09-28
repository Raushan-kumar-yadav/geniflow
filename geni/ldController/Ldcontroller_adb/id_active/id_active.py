from pickle import TRUE
import time
import random
from lxml import etree
import xml.etree.ElementTree as ET
from pathlib import Path
import sys
import os
from datetime import datetime
import time 
import shutil


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



#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))

from geni.ldController.Ldcontroller_adb import AdbImageUpload
from ldController.Ldcontroller_adb.LdAdb import *

try:
    
    from ldController.Ldcontroller_adb.geni_config_collector import DeviceSettingsFlatten
    from ldController.Ldcontroller_adb.AdbCheckinUpload import AdbCheackinUpload
    from ldController.Ldcontroller_adb.AdbStoryUpload import AdbStoryUpload
    from ldController.Ldcontroller_adb.AdbImageUpload import AdbimageUpload
except Exception as e :
    print(e)



class IdActive():

    def __init__(self, control_pasue_callback,device_name=None, device_serial = None,local_output_file_path="",download_folder=""):
        self.device = device_name
        self.adb = device_serial
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



    def Photo_upload(self,profile_name,id_or_page="id",is_group_sharing_enable=False,group_list=[],downlaod_folder=""):
        """
        Upload images with optional scheduling functionality.

        Args:
            profile_name: Name of the profile to upload to
        """

        


        self.ld_adb_controller.InstallAndCheckAPK()




        # Default caption if list is too short
        default_caption = "Hi"
        sub_folder = "imagess"



        
 

        



        try:
                # Get caption for this video (or use default if none available)
                image_caption = self.ld_adb_controller.MoveFileWithCaption(media_type="image",sub_folder=sub_folder,download_folder=downlaod_folder)

                if not image_caption:
                    print("image not avlaible in download folder so qiting upload")
                    return 




                # Switch to Gallery to refrace the file that add to folder
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Gallery",app_package_name_to_switch="com.android.gallery3d")
                self.check_for_call_and_pause(id_or_page)




                # Switch to facebook
                self.ld_adb_controller.switch_appliction(app_name_to_switch="Facebook",app_package_name_to_switch="com.facebook.katana")
                self.check_for_call_and_pause(id_or_page)





                # Check for popups and discard buttons
                self.ld_adb_controller.discard_post()
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.discard_story()





                # Check for pop in fb home screen 
                self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,  delay=0)
                self.ld_adb_controller.check_popup_on_home_fb()





                # Click on plus button to create a new post
                plus_btn_x_path = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"







                # Click on Select photos or videos for your post
                select_photo_or_video_btn_xpath = "//node[@content-desc='Select photos or videos for your post']"
                self.check_for_call_and_pause(id_or_page)
                self.ld_adb_controller.click_element(xpath_expr=select_photo_or_video_btn_xpath)







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
                    self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,delay=0)

                    return 
            



                if is_create_post_label_visiable:


                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.click_element_if_visibale(xpath_expr="//node[contains(@text,'Say something about this photo')]")
                        self.ld_adb_controller.click_element_if_visibale(xpath_expr="//node[contains(@text,'Say something about this photo')]")




                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.PullText(str(image_caption))
                        print(f"image caption for profile {profile_name}: {image_caption}")




                        self.random_time(from_time=0.5, to_time=1)
                        self.ld_adb_controller.click_on_cursor()




                        self.random_time(from_time=2, to_time=4)
                        self.pause_event.wait()
                        self.check_for_call()




                        is_next_clicked = self.ld_adb_controller.click_element_if_visibale(
                            xpath_expr=next_btn_xpath
                        )




                        if not is_next_clicked:
                            self.check_for_call_and_pause(id_of_page=id_or_page)
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

                if not is_post_setting_visible:

                    self.check_for_call_and_pause(id_or_page)
                    self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page=id_or_page)
                    self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,delay=0)
                    return 






                if is_post_setting_visible:
                

                            # Immediate sharing (non-scheduled)

                            post_btn_xpath = "//node[@content-desc='POST']"
                            is_clicked_on_post = self.ld_adb_controller.click_element_if_visibale(xpath_expr=post_btn_xpath)
                            if not is_clicked_on_post:
                                self.ld_adb_controller.clickByCoordinate(x=post_btn_x_coord,y=post_btn_y_coord)





                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.check_popup_on_home_fb()





                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.open_notifications_check_uploading(cheack_for_call_and_pause=self.check_for_call_and_pause,  id_or_page=id_or_page)



                            self.check_for_call_and_pause(id_or_page)
                            reels_uploading_delay = self.device_config_dic.flatten_json()["Reels Uploading Delay"]
                            self.check_for_call_and_pause(id_or_page)



                            self.random_time(
                                from_time=int(reels_uploading_delay) * 0.9,
                                to_time=reels_uploading_delay
                            )



                            self.check_for_call_and_pause(id_or_page)
                            print("Phots uploading Done")
                            self.check_for_call()




                            # Remove all the image file from dict
                            self.check_for_call_and_pause(id_or_page)
                            self.ld_adb_controller.empty_folders(subfolder=sub_folder)




                else:



                        print("Error: Post setting window not found ")
                        self.check_for_call_and_pause(id_or_page)
                        self.ld_adb_controller.back_btn_untill_discard_btn(pause_and_cheack_call_back=self.check_for_call_and_pause,    id_or_page=id_or_page)



                        self.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.check_for_call_and_pause,id_or_page=id_or_page,    scroll_down_num=3,delay=0)

                        # Exit current iteration
                        return 
                
        except Exception as e :
            print("Error uploading this imate Restarting the facebook")
            self.ld_adb_controller.stopApp()
            self.check_for_call_and_pause(id_or_page)
            self.ld_adb_controller.startApp()
        
        return 


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

    def like_post(self):
        """
        click on like btn and like 
        """
        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        like_btn_xpath = "//node[contains(@content-desc,'Like')]"

        self.ld_adb_controller.click_element(xpath_expr=like_btn_xpath,max_attempts=1)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

    
    def react_post(self):

        """
        Click on like btn and reaction 
        

        """

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        like_btn_xpath = "//node[contains(@content-desc,'Like')]"

        self.ld_adb_controller.long_press_on_element(xpath_expr=like_btn_xpath,max_attempts=1)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        reactinos_list = ["Love","Haha","Wow","Sad","Angry"]

        reaction = random.choice(reactinos_list)

        reactoin_xpath = f"//node[contains(@content-desc,'{reaction}')]"

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.click_element(xpath_expr=reactoin_xpath,max_attempts=1)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

    def comment_on_post(self,comment_text):
        """
        click on comment btn and post some comments 

        :arrgs: comment text

        :retun: none 
        """

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        comment_btn_xpath = "//node[@content-desc='Comment']"

        self.ld_adb_controller.click_element(comment_btn_xpath,max_attempts=1)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()


        commenet_as_xpath = "//node[contains(@text,'Comment')]"
        write_public_comment_xpath = "//node[contains(@text,'Write a')]"

        is_comment_visible = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=commenet_as_xpath,max_attempts=3)


        if not is_comment_visible:

            self.ld_adb_controller.BackButton()

            return False
        
        
        try:
            self.ld_adb_controller.click_element(commenet_as_xpath,max_attempts=1)

        except:
            
            self.ld_adb_controller.click_element(write_public_comment_xpath,max_attempts=1)

        if is_comment_visible or self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element="//node[contains(@text,'Write a')]",max_attempts=1):

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.PullText(Text=comment_text)

            self.random_time(from_time=1,to_time=3)
            self.check_for_call()
            self.pause_event.wait()

            #press_post_btn

            send_comment_btn = "//node[contains(@content-desc,'Send')]"

            self.ld_adb_controller.click_element(send_comment_btn,max_attempts=1)

            self.random_time(from_time=1,to_time=3)
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.BackButton()

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.BackButton()

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()
        else:

            print("comments sections is not Visible.... Pressed Back btn ")

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.BackButton()
            self.ld_adb_controller.BackButton()




    def share_post_to_group(self,caption,list_of_group=[]):

        """share post to given groups 
            :arrg: caption to put 
            :arrg: list of group to search 

            :return true or false :
        
        """
        if not list_of_group:
            
            print("No group where given to share")
            
            return False

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        share_btn_xpath = "//node[contains(@content-desc,'Share')]"

        try:
            self.ld_adb_controller.click_element(share_btn_xpath,max_attempts=1)
        except:

            return False

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        group_btn_xpath = "//node[contains(@content-desc,'Group')]"


        try:
            self.ld_adb_controller.click_element(group_btn_xpath,max_attempts=1)

        except:
            print("cant find element...Doing Swip")

            self.ld_adb_controller.ScrollByCoordinate(x_start=300,y_start=400,x_end=315,y_end=100)




        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        search_bar_xpath = "//node[@text='Search']"

        self.ld_adb_controller.click_element(search_bar_xpath,max_attempts=1)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()


        for group in list_of_group:

            self.ld_adb_controller.PullText(group)

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            result_element_xpath = "//node[@class='android.widget.CheckBox']"

            is_group_avl = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=result_element_xpath,max_attempts=1)
            self.random_time()
            self.check_for_call()
            self.pause_event.wait()
            
            if is_group_avl:

                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                check_box_xpath = "//node[@class='android.widget.CheckBox']"

                self.ld_adb_controller.click_element(check_box_xpath,max_attempts=1)

                

                self.random_time()
                self.check_for_call()
                self.pause_event.wait()


                done_btn_xpath = "//node[contains(@content-desc,'Done')]"
                self.ld_adb_controller.click_element(done_btn_xpath,max_attempts=1)


                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

            else:

                print(f"Group with name: {group} not found...Trying other groups")

                done_btn_xpath1 = "//node[contains(@content-desc,'Done')]"

                self.ld_adb_controller.click_element(done_btn_xpath1)

                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

            
        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        save_btn_xpath = "//node[contains(@content-desc,'Save')]"

        try:
            self.ld_adb_controller.click_element(save_btn_xpath,max_attempts=1)
        except:

            print("No group where found.....Pressed back btn")
            self.ld_adb_controller.BackButton()

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.BackButton()

            return


        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        write_something_xpath = "//node[contains(@text,'Write something')]"
        self.ld_adb_controller.click_element(write_something_xpath,max_attempts=1)

        self.random_time(from_time=3,to_time=6)
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.PullText(Text=caption)

        self.random_time(from_time=3,to_time=6)
        self.check_for_call()
        self.pause_event.wait()

        post_btn_x_coord = 494
        post_btn_y_coord = 68

        self.ld_adb_controller.clickByCoordinate(x=post_btn_x_coord,y=post_btn_y_coord)



        self.random_time(from_time=3,to_time=6)
        self.check_for_call()
        self.pause_event.wait()

        print("Post shared to groups successfully")
        return True


    def share_to_stroy(self):

        """share post to stroy
            :arrg: none
            :return true or false :
        """
        
        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        share_btn_xpath = "//node[contains(@content-desc,'Share')]"

        self.ld_adb_controller.click_element(share_btn_xpath,max_attempts=1)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        your_stroy_btn_xpath = "//node[contains(@content-desc,'Your story')]"

        self.ld_adb_controller.click_element(your_stroy_btn_xpath,max_attempts=1)


        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        share_btn_xpath = "//node[@text='Share']"

        self.ld_adb_controller.click_element(share_btn_xpath,max_attempts=1)

        self.random_time(from_time=2,to_time=4)
        self.check_for_call()
        self.pause_event.wait()


    def check_notifications(self,minutes=5):

        """Go to notification section and check notification"""

        self.ld_adb_controller.startApp()
        notification_btn_x_coord = 411
        notification_btn_y_coord = 136

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.clickByCoordinate(notification_btn_x_coord,y=notification_btn_y_coord)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        #check notification for given minuts 
        
        current_time = time.time()
        end_time = current_time + minutes * 60

        while current_time < end_time:

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            notificaton_xpath ="//node[contains(@content-desc,'Unread')]" 
            notification_banner =  "//node[@content-desc='Notifications']"  
            is_found_not = self.ld_adb_controller.click_element_if_visibale(xpath_expr=notificaton_xpath)

            if not is_found_not:
                print("No New Notification found!...")
                self.ld_adb_controller.BackButton()
                return


            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            is_element_visible = False
            is_home = False

            max_backBtn_attempt = 0

            while is_element_visible == False:
                
                self.random_time()
                self.check_for_call()
                self.pause_event.wait()
            
                is_element_visible=self.ld_adb_controller.check_element_visiable(element_to_be_visiable=notificaton_xpath,max_attempts=1,delay=0)
                is_home = self.ld_adb_controller.check_loading_screen_gone(delay=0)
                if is_element_visible:
                    break
                if is_home:
                    print("No Unread Notification Found!....")
                    return
                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                self.ld_adb_controller.BackButton()

                max_backBtn_attempt += 1

                if max_backBtn_attempt > 5:
                    
                    print("Max back btn attempts reached...Exiting with check notification")
                    return

            current_time = time.time()
            
            self.ld_adb_controller.random_scroll()

        is_home_screen = self.ld_adb_controller.check_loading_screen_gone(delay=0)
        if not is_home_screen:
            self.ld_adb_controller.BackButton()    

    def confirm_friend_request(self,num_of_friends):
        """go to friend section and confirm friend request
            :arrg: num_of_friends to confirm"""
        self.ld_adb_controller.startApp()
        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        profile_x_coord=503
        profile_y_coord=147


        self.ld_adb_controller.clickByCoordinate(x=profile_x_coord,y=profile_y_coord)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        friend_xpath = "//node[contains(@content-desc,'Friends')]"
        is_clicked_by_xpat = self.ld_adb_controller.click_element_if_visibale(xpath_expr=friend_xpath)

        if not is_clicked_by_xpat:
            is_clicked = self.ld_adb_controller.ClickOnTextByImage("Friends")

            if not is_clicked:
                self.ld_adb_controller.BackButton()
                print("Error going to friend section")
                return

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        confirm_btn_x_coord = 247 
        confirm_btn_y_coord = 369

        for i in range(int(num_of_friends)):

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.click_element(xpath_expr="//node[contains(@content-desc,'Confirm')]",max_attempts=1)

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

        """         self.ld_adb_controller.BackButton()

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.BackButton() """

        self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id",back_btn_num=4)

    def add_friend(self,no_of_friends):

        """go to friend section and add friend
            :arrg: num_of_friends to confirm"""

        self.ld_adb_controller.startApp()

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        profile_x_coord=503
        profile_y_coord=147


        self.ld_adb_controller.clickByCoordinate(x=profile_x_coord,y=profile_y_coord)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        friend_xpath = "//node[contains(@content-desc,'Friends')]"

        is_clicked_by_xpat = self.ld_adb_controller.click_element_if_visibale(xpath_expr=friend_xpath)

        if not is_clicked_by_xpat:
            is_clicked = self.ld_adb_controller.ClickOnTextByImage("Friends")

            if not is_clicked:
                self.ld_adb_controller.BackButton()
                print("Error going to friend section")
                return

        

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        suggeestions_btn_xpath = "//node[@content-desc='Suggestions']"

        self.ld_adb_controller.click_element(suggeestions_btn_xpath,max_attempts=1)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        add_btn_x_coord = 247
        add_btn_y_coord = 273

        for i in range(int(no_of_friends)):

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.click_element(xpath_expr="//node[contains(@content-desc,'Add')]",max_attempts=1)

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

        """         self.ld_adb_controller.BackButton()

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.BackButton()

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.BackButton() """
        
        self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id",back_btn_num=4) 


    def check_msg_and_reply(self,minutes=5,reply_text=["hello","hi"]):

        self.ld_adb_controller.startApp()

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()


        message_btn_x_coord = 500
        message_btn_y_coord = 68


        self.ld_adb_controller.clickByCoordinate(message_btn_x_coord,message_btn_y_coord)

        self.random_time(from_time=4,to_time=7)
        self.check_for_call()
        self.pause_event.wait()


        close_btn_xpath = "//node[(@content-desc='Close')]"


        is_close_element_visiable = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=close_btn_xpath,max_attempts=1)

        if is_close_element_visiable:


            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.click_element(xpath_expr=close_btn_xpath)


        self.random_time()
        self.check_for_call()
        self.pause_event.wait()


        is_close_element_visiable2 = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=close_btn_xpath,max_attempts=1)

        if is_close_element_visiable2:

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.click_element(xpath_expr=close_btn_xpath)
        
        
        self.random_time()
        self.check_for_call()
        self.pause_event.wait()


        self.ld_adb_controller.random_scroll()

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        random_msg_x_coord2 = random.randint(230,245)  
        random_msg_y_coord2 = random.randint(535,545)     

        self.ld_adb_controller.clickByCoordinate(random_msg_x_coord2,random_msg_y_coord2)

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        is_close_element_visiable3 = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=close_btn_xpath,max_attempts=1)

        if is_close_element_visiable3:

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.click_element(xpath_expr=close_btn_xpath)



        is_close_element_visiable4 = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=close_btn_xpath,max_attempts=1)
        if is_close_element_visiable4:

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            self.ld_adb_controller.click_element(xpath_expr=close_btn_xpath)

        
        #pressed back btn
        self.ld_adb_controller.BackButton()


        current_time = time.time()
        end_time = current_time + minutes * 60

        scrolled_num = 1

        if scrolled_num > 4:

            f_scrolled_num = scrolled_num - random.randint(1,4)

            scrolled_num = f_scrolled_num

        

        while current_time < end_time:

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            scroll_num = 0

            while scroll_num < scrolled_num:

                self.ld_adb_controller.random_scroll()

                scroll_num += 1


            scrolled_num += 1


            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            random_msg_x_coord = random.randint(230,245)  
            random_msg_y_coord = random.randint(535,545)     

            self.ld_adb_controller.clickByCoordinate(random_msg_x_coord,random_msg_y_coord)


            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            is_close_element_visiable5 = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=close_btn_xpath,max_attempts=1)

            if is_close_element_visiable5:
            
                self.random_time()
                self.check_for_call()
                self.pause_event.wait()
    
                self.ld_adb_controller.click_element(xpath_expr=close_btn_xpath)


            is_type_a_msg_xpath = "//node[@content-desc='Type a message']"

            is_type_a_msg_visiable = self.ld_adb_controller.check_element_visiable(element_to_be_visiable=is_type_a_msg_xpath,max_attempts=1)

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            if is_type_a_msg_visiable:

                self.ld_adb_controller.click_element(xpath_expr=is_type_a_msg_xpath,max_attempts=1)

                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                random_msg=random.choice(reply_text)

                self.ld_adb_controller.PullText(Text=random_msg)


                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                send_btn_xpath = "//node[(@content-desc='Send')]"

                self.ld_adb_controller.click_element(send_btn_xpath,max_attempts=1)

                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                self.ld_adb_controller.BackButton()

                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                self.ld_adb_controller.BackButton()

                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

            else:
            
                self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id",back_btn_num=4)
            current_time = time.time()
            

        

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id",back_btn_num=2)


    def back_btn_until_home(self, max_attempt):
        """
        Navigate back to home screen by pressing back button or restarting app if needed.

        Logic:
        1. Check if app is loaded (loading screen gone)
        2. If loaded, return (we're done)
        3. If not loaded, try pressing back button up to 5 times
        4. After each back press, check if app is loaded
        5. If still not loaded after 5 back presses, restart the app
        6. Repeat the whole process for max_attempt times
        """

        for attempt in range(max_attempt):
            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            # First check: Is app already loaded?
            if self.ld_adb_controller.check_loading_screen_gone():
                return  # App is loaded, we're done

            # App is not loaded, try pressing back button up to 5 times
            app_loaded = False
            for back_press in range(5):
                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                # Press back button
                self.ld_adb_controller.BackButton()

                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                # Check if app is loaded after pressing back
                if self.ld_adb_controller.check_loading_screen_gone():
                    app_loaded = True
                    return  # App is loaded, we're done

            # If we've tried 5 back presses and app still not loaded, restart the app
            if not app_loaded:
                self.random_time()
                self.check_for_call()
                self.pause_event.wait()

                # Stop the app
                self.ld_adb_controller.stopApp()

                self.random_time(from_time=1, to_time=2)
                self.check_for_call()
                self.pause_event.wait()

                # Start the app
                self.ld_adb_controller.startApp()

                # Give some time for app to start
                self.random_time(from_time=2, to_time=3)
                self.check_for_call()
                self.pause_event.wait()

        # If we've exhausted all attempts and still not at home
        print(f"Failed to reach home screen after {max_attempt} attempts")




    def collect_method_to_run(self,config_dict={
            "like_post": {"enable": False, "weight": 1},
            "react_post": {"enable": False, "weight": 1},
            "comment_on_post": {"enable": False, "weight": 1, "caption": "hello"},
            "share_post_to_group": {"enable": False, "weight": 1, "group_list": ["hi", "helo"]},
            "share_to_stroy": {"enable": False, "weight": 1}
        }):

        enable_weight = config_dict


        methods = []
        weights = []

        # Check each method in the configuration and add to methods/weights if enabled
        if enable_weight.get("like_post", {}).get("enable",False) == True:
            methods.append(lambda: self.like_post())
            weights.append(enable_weight["like_post"]["weight"])

        if enable_weight.get("react_post", {}).get("enable",False) == True:
            methods.append(lambda: self.react_post())
            weights.append(enable_weight["react_post"]["weight"])

        if enable_weight.get("comment_on_post", {}).get("enable",False) == True:
            caption = enable_weight["comment_on_post"].get("caption", "hello")
            methods.append(lambda: self.comment_on_post(caption))
            weights.append(enable_weight["comment_on_post"]["weight"])

        if enable_weight.get("share_post_to_group", {}).get("enable",False) == True:
            group_list = enable_weight["share_post_to_group"].get("group_list", [])
            methods.append(lambda: self.share_post_to_group(list_of_group=group_list))
            weights.append(enable_weight["share_post_to_group"]["weight"])

        if enable_weight.get("share_to_stroy", {}).get("enable",False) == True:
            methods.append(lambda: self.share_to_stroy())
            weights.append(enable_weight["share_to_stroy"]["weight"])

        
        methods.append(None)
        weights.append(20)  

        return (methods, weights)

    

    def scroll_feed_and_activiy(self,minutes,config_dict):

        self.ld_adb_controller.startApp()

        start_time = time.time()
        end_time = start_time + minutes * 60
        print(f"Running randomly selected functions for {minutes} minute(s).")
        methods , weights = self.collect_method_to_run(config_dict)



        while time.time() < end_time:

            self.pause_event.wait()

            self.ld_adb_controller.random_scroll()

            chosen = random.choices(methods, weights=weights, k=1)[0]
            if chosen is not None:
                
                is_like_visiable = self.ld_adb_controller.check_element_visiable(element_to_be_visiable="//node[contains(@content-desc,'Like')]")

                if is_like_visiable:

                    try:
                        chosen() 
                    except:

                        continue
                else:
                    continue
            else:
                print("No function executed this iteration.")
            time.sleep(3)  

        print("Finished executing functions.")

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id",back_btn_num=4)

    def scroll_reels_and_activiy(self,minutes,config_dict):

        self.ld_adb_controller.startApp()

        width = 540
        height = 960

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        profile_x_coord=503
        profile_y_coord=147

        x = random.randint(int(width * 0.2), int(width * 0.8))
        y1 = random.randint(int(height * 0.7), int(height * 0.9))
      
        y2 = random.randint(int(height * 0.1), int(height * 0.3))

        reels_btn_feed = "//node[@content-desc='View reels']"
        is_reel_found = self.ld_adb_controller.scroll_and_click_on_element(scroll_x_coord=x,scroll_y_coordinate=y1,element_xpath=reels_btn_feed,max_no_attempt=100,delay=random.uniform(2,10),offset=250)

        if not is_reel_found:
            self.ld_adb_controller.BackButton()


        self.random_time()
        self.check_for_call()
        self.pause_event.wait()


        start_time = time.time()
        end_time = start_time + minutes * 60
        print(f"Running randomly selected functions for {minutes} minute(s).")
        methods , weights = self.collect_method_to_run(config_dict)



        while time.time() < end_time:

            self.pause_event.wait()

            self.ld_adb_controller.random_scroll()

            chosen = random.choices(methods, weights=weights, k=1)[0]
            if chosen is not None:
                
                is_like_visiable = self.ld_adb_controller.check_element_visiable(element_to_be_visiable="//node[contains(@content-desc,'Like')]")

                if is_like_visiable:

                    try:
                        chosen() 
                    except:

                        continue
                else:
                    continue
            else:
                print("No function executed this iteration.")
            time.sleep(10)  

        print("Finished executing functions.")

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id",back_btn_num=4)


    def scroll_videos_and_activiy(self,minutes,config_dict):

        self.ld_adb_controller.startApp()

        self.random_time()
        self.check_for_call()
        self.pause_event.wait()

        profile_x_coord=503
        profile_y_coord=147

        video_tab_xpath = "//node[contains(@content-desc,'Video, tab')]"

        is_clicked_by_video_tab = self.ld_adb_controller.click_element_if_visibale(xpath_expr=video_tab_xpath)
        if not is_clicked_by_video_tab:
            self.ld_adb_controller.clickByCoordinate(x=profile_x_coord,y=profile_y_coord)

            self.random_time()
            self.check_for_call()
            self.pause_event.wait()

            video_xpath = "//node[contains(@content-desc,'Video')]"
            is_clicked_by_xpat = self.ld_adb_controller.click_element_if_visibale(xpath_expr=video_xpath)

            if not is_clicked_by_xpat:
                is_clicked = self.ld_adb_controller.ClickOnTextByImage("Video")

                if not is_clicked:
                    self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id",back_btn_num=4)
                    print("Error going to friend section")
                    return


        self.random_time()
        self.check_for_call()
        self.pause_event.wait()


        start_time = time.time()
        end_time = start_time + minutes * 60
        print(f"Running randomly selected functions for {minutes} minute(s).")
        methods , weights = self.collect_method_to_run(config_dict)



        while time.time() < end_time:

            self.pause_event.wait()

            self.ld_adb_controller.random_scroll()

            chosen = random.choices(methods, weights=weights, k=1)[0]
            if chosen is not None:
                
                is_like_visiable = self.ld_adb_controller.check_element_visiable(element_to_be_visiable="//node[contains(@content-desc,'Like')]")

                if is_like_visiable:

                    try:
                        chosen() 
                    except:

                        continue
                else:
                    continue
            else:
                print("No function executed this iteration.")
            time.sleep(10)  

        print("Finished executing functions.")

        self.ld_adb_controller.back_btn_untill_home(pause_and_cheack_call_back=self.check_for_call_and_pause,id_or_page="id",back_btn_num=4)
        


class MainIdActive():
    def __init__(self, control_pause_callback, device_name=None, device_serial=None, local_output_file_path="", task_dict=None,id_name=None,activity_queue=None):
        self.device = device_name
        self.adb = device_serial
        self.activity_queue = activity_queue
        self.pause_event = control_pause_callback
        self.local_output_file_path = local_output_file_path
        self.id_name = id_name
        self.num_of_loops = 0
        # Default task dictionary if none is provided
        if task_dict is None:
            self.task_dict = {
                "loops":{"num_of_loop":2,"loops_delay":3},
                "Photo_upload": {"enable": False, "profile_name": "", "photo_caption": "","ld_folder":[],"download_folder":""},
                "check_notifications": {"enable": False, "duration": 5},
                "confirm_friend_request": {"enable": False, "num_of_friends": 5},
                "add_friend": {"enable": False, "num_of_friends": 5},
                "check_msg_and_reply": {"enable": False, "duration": 5},
                "scroll_feed_and_activiy": {
                    "enable": False, 
                    "duration": 5, 
                    "config_dict": {
                        "like_post": {"enable": False, "weight": 1},
                        "react_post": {"enable": False, "weight": 1},
                        "comment_on_post": {"enable": False, "weight": 1, "caption": "hello"},
                        "share_post_to_group": {"enable": False, "weight": 1, "group_list": ["hi", "helo"]},
                        "share_to_stroy": {"enable": False, "weight": 1}
                    }
                },
                "scroll_reels_and_activiy": {
                    "enable": False, 
                    "duration": 5, 
                    "config_dict": {
                        "like_post": {"enable": False, "weight": 1},
                        "react_post": {"enable": False, "weight": 1},
                        "comment_on_post": {"enable": False, "weight": 1, "caption": "hello"},
                        "share_post_to_group": {"enable": False, "weight": 1, "group_list": ["hi", "helo"]},
                        "share_to_stroy": {"enable": False, "weight": 1}
                    }
                },
                "scroll_videos_and_activiy": {
                    "enable": False, 
                    "duration": 5, 
                    "config_dict": {
                        "like_post": {"enable": False, "weight": 1},
                        "react_post": {"enable": False, "weight": 1},
                        "comment_on_post": {"enable": False, "weight": 1, "caption": "hello"},
                        "share_post_to_group": {"enable": False, "weight": 1, "group_list": ["hi", "helo"]},
                        "share_to_stroy": {"enable": False, "weight": 1}
                    }
                },
                "post_checkin": {"enable": False, "profile_list": "", "image_captions": "", "checkin_location": "", "folders": "","add_photo":False,"package_name":"com.facebook.katana"},

                "post_story":{"enable":False,"num_of_story":1,"profile_list":[],"video_captions":[],"folder":[]}
            }
        else:
            self.task_dict = task_dict
            
        # Create the IdActive instance
        self.id_active = IdActive(
            control_pasue_callback=control_pause_callback,
            device_name=device_name,
            device_serial=device_serial,
            local_output_file_path=local_output_file_path
        )
        """ "Photo_upload",
            "check_notifications",
            "confirm_friend_request",
            "add_friend",
            "check_msg_and_reply",
            "scroll_feed_and_activiy",
            "scroll_reels_and_activiy", 
            "scroll_videos_and_activiy",
            "post_checkin",
            "post_story" """
        # List of all available methods
        self.all_method_list = [

            "Photo_upload",
            "check_notifications",
            "confirm_friend_request",
            "add_friend",
            "check_msg_and_reply",
            "scroll_feed_and_activiy",
            "scroll_reels_and_activiy", 
            "scroll_videos_and_activiy",
            "post_checkin",
            "post_story"
            ]
        self.all_method_list_after_one_loop = [

            "check_notifications",
            "confirm_friend_request",
            "add_friend",
            "check_msg_and_reply",
            "scroll_feed_and_activiy",
            "scroll_reels_and_activiy", 
            "scroll_videos_and_activiy"
        
            ]
    
    def execute_shuffled_methods(self):
        """
        Shuffles all methods and executes them if they are enabled in task_dict
        """
        
        print("Switching Profile")

        if not self.id_name:
            print("ID Name not found skipping ID Active Task.........")
            return
        if self.num_of_loops == 0:
            self.id_active.ld_adb_controller.switch_profle_to(profile_name=self.id_name,cheack_for_call_and_pause_callback=self.id_active.check_for_call_and_pause,id_or_page="id")
            
        self.id_active.ld_adb_controller.discard_post()
        
        # Shuffle the methods list
        if self.num_of_loops == 0:
            methods_to_execute = self.all_method_list.copy()
            random.shuffle(methods_to_execute)
        else:
            methods_to_execute = self.all_method_list_after_one_loop.copy()
            random.shuffle(methods_to_execute)

        print(f"Methods will be executed in this order: {methods_to_execute}")
        
        
        for method_name in methods_to_execute:
            method_config = self.task_dict.get(method_name)
            
           
            if method_config and method_config.get("enable"):
                print(f"Executing method: {method_name}")
                
                # Check if method should be executed based on config validation
                if self.validate_method_config(method_name, method_config):

                    try:
                        self.execute_method(method_name, method_config)
                    except Exception as e :
                        print("Something Went Worng In current ID Active Task Skipping This.....")
                    time.sleep(3)
                    
                    self.id_active.back_btn_until_home(max_attempt=5)
                    time.sleep(3)
                else:
                    print(f"Skipping method: {method_name} - required configuration values are missing or None")
            else:
                print(f"Skipping method: {method_name} - disabled or not found in config")
        
        self.id_active.ld_adb_controller.stopApp()
        
    def validate_method_config(self, method_name, method_config):
        """
        Validate if the method configuration has all required non-None values
        Returns True if valid, False if any required values are None or missing
        """
        if method_name == "Photo_upload":
            profile_name = method_config.get("profile_name")
            photo_caption = method_config.get("photo_caption")
            folder = method_config.get("folder")
            
            
            # Check if critical values are None or empty
            if profile_name is None or photo_caption is None or folder is None :
                print(f"Photo_upload: Missing required values - profile_name: {profile_name}, photo_caption: {photo_caption}")
                return False
                
        elif method_name == "post_checkin":
            profile_list = method_config.get("profile_list")
            image_captions = method_config.get("image_captions")
            checkin_location = method_config.get("checkin_location")
            folders = method_config.get("folders")
            
            # Check if critical values are None or empty lists
            if (profile_list is None or len(profile_list) == 0 or
                checkin_location is None or 
                folders is None or len(folders) == 0):
                print(f"post_checkin: Missing required values - profile_list: {profile_list}, checkin_location: {checkin_location}, folders: {folders}")
                return False
                
        elif method_name == "post_story":
            profile_list = method_config.get("profile_list")
            video_captions = method_config.get("video_captions"," ")
            folder = method_config.get("folder")
            
            # Check if critical values are None or empty lists
            if (profile_list is None or len(profile_list) == 0 or
                folder is None or len(folder) == 0):
                print(f"post_story: Missing required values - profile_list: {profile_list}, video_captions: {video_captions}, folder: {folder}")
                return False
        
        return True
        
    def execute_method(self, method_name, method_config):
        """
        Execute a specific method with its configuration
        """
        if method_name == "Photo_upload":
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Uploading IDACT Image", "None","ds")

            try:
                image_upload = AdbimageUpload(control_pasue_callback=self.pause_event,device_name=self.device,device_serial=self.adb,local_output_file_path=self.   local_output_file_path,activity_queue=self.activity_queue)
                image_upload.image_upload_after_loading_screen(
                                        profile_name=method_config.get("profile_name", ""),
                                        id_or_page="id",
                                        app_package="com.facebook.katana",
                                        schedule_time_list=None,
                                        is_schedule_enable=False,
                                        is_group_sharing_enable=method_config.get("is_group_sharing_enable",False),
                                        group_list=method_config.get("group_list",[]),
                                        caption_form=method_config.get("caption_souce",[]),
                                        caption_list=method_config.get("photo_caption",""),
                                        download_folder=method_config.get("folder","") ,
                                        num_of_image=method_config.get("media_count",1) ,
                                        num_of_share=0,ignore_name=True
                                    )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "IDACT Image Uploaded", f"None","s")
            except Exception as e :
                print("Error in Photo Upload in id active")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Uploading IDACT Image", f"Error:{e}","s")

        elif method_name == "check_notifications":
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, " Checking Notifications", "None","ds")
            try:
                self.id_active.check_notifications(
                minutes=method_config.get("duration", 5)
            )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, " Checking Notifications Done", "None","s")

            except Exception as e:
                print("error at cheacking notification")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, " Checking Notifications", f"Error:{e}","s")
                
            
        elif method_name == "confirm_friend_request":
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Confirming Friends Request", "None","ds")

            try:
                self.id_active.confirm_friend_request(
                num_of_friends=method_config.get("num_of_friends", 5)
                )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Confirming Friends Request Done", "None","s")
            except Exception as e:
                print("error at Confriming friend request")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Confirming Friends Request", f"Error:{e}","s")
            
        elif method_name == "add_friend":

            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Adding Friends ", "None","ds")

            try:
                self.id_active.add_friend(
                    no_of_friends=method_config.get("num_of_friends", 5)
                )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Adding Friends Done", "None","s")

            except Exception as e:
                print("error at Adding Friends")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Adding Friends", f"Error:{e}","s")

        elif method_name == "check_msg_and_reply":
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Replying Msg", "None","ds")

            try:
                self.id_active.check_msg_and_reply(
                    minutes=method_config.get("duration", 5),
                    reply_text=method_config.get("reply_text", ["hello", "hi"])
                )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Replying Msg Done", "None","s")

            except Exception as e:
                print("error at Replying Msg")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Replying Msg", f"Error:{e}","s")
            
        elif method_name == "scroll_feed_and_activiy":
            
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scrolling Feed", "None","ds")

            try:
                self.id_active.scroll_feed_and_activiy(
                    minutes=method_config.get("duration", 5),
                    config_dict=method_config.get("config_dict", {})
                )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scrolling Feed Done", "None","s")
            except Exception as e:
                print("error at Scrolling Feed")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scrolling Feed", f"Error:{e}","s")
            
        elif method_name == "scroll_reels_and_activiy":

            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scrolling Reels", "None","ds")

            try:
                self.id_active.scroll_reels_and_activiy(
                    minutes=method_config.get("duration", 5),
                    config_dict=method_config.get("config_dict", {})
                )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scrolling Reels Done", "None","s")
            except Exception as e:
                print("error at scrolling Reels")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "scrolling Reels", f"Error:{e}","s")
            
        elif method_name == "scroll_videos_and_activiy":

            try:
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scrolling Videos", "None","ds")
                self.id_active.scroll_videos_and_activiy(
                    minutes=method_config.get("duration", 5),
                    config_dict=method_config.get("config_dict", {})
                )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scrolling Videos Done", "None","s")
            
            except Exception as e:
                print("error at Scrolling Videos")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scrolling Videos", f"Error:{e}","s")
            
        elif method_name == "post_checkin" :
            
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Uploading CheckIN", "None","ds")

            try:
                post_cheackin = AdbCheackinUpload(control_pasue_callback=self.pause_event,device_name=self.device,device_serial=self.adb,local_output_file_path=self.   local_output_file_path)

                post_cheackin.checkin_upload_after_loading_screen(profile_name=method_config.get("profile_list"),captions=method_config.get("video_captions"),  checkin_location=method_config.get("checkin_location"),add_photo=method_config.get("add_photo"),app_package="com.facebook.katana",download_folder=method_config.get   ("folders"),is_caption_from_original_file=method_config.get("caption_source"))
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Uploading CheckIN Done", "None","s")

            except Exception as e:
                print("error at Confriming friend request")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Uploading CheckIN", f"Error:{e}","s")

        elif method_name == "post_story":
            
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Uploading IDACT Story", "None","ds")

            try:
                profile_list = method_config.get("profile_list")
                f_profile_list = [(profile_list,"id")]
                story_upload = AdbStoryUpload(control_pasue_callback=self.pause_event,device_name=self.device,device_serial=self.adb,local_output_file_path=self.   local_output_file_path,activity_queue=self.activity_queue)
                story_upload.story_upload_after_loading_screen(
                                        profile_name=profile_list,
                                        captions_source=method_config.get("caption_souce"),
                                        id_or_page="id",
                                        image_or_video="video",
                                        caption_list=[method_config.get("video_captions")],
                                        download_folder=method_config.get("folder"),
                                        app_package="com.facebook.katana",
                                        stroy_num=method_config.get("num_of_story",1)
                                    )
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Uploading IDACT Story Done", "None","s")
            except Exception as e:
                print("error at Uploading IDACT Story")
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Uploading IDACT Story", f"Error:{e}","s")

    def execute_shuffled_methods_with_loop(self):
        
        print("stating app..")
        
        activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Getting ID Active Config", "None","ds")

    
        loops = self.task_dict.get("loops",{})
        num_of_loops = loops.get("num_of_loop",1)
        loop_delay = loops.get("loops_delay",3)

        for loop in range(0,num_of_loops):
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, " Shuffling activities ", "None","ds")
            self.execute_shuffled_methods()
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, " Starting ID Active ", "None","ds")
            self.num_of_loops = 1
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, f" Current IDACT Loop:{self.num_of_loops}", "None","s")
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, f"Waiting Before Starting Next Loop if any left", "None","ds")
            time.sleep(int(loop_delay))


    def id_active_after_loading_screen(self,after_loading_screen_element="//node[@content-desc='Create, Double tap to create a new post, story, or reel']",
                                         max_attempts=4, delay=5, max_restart_attempts=5,
                                         switch_profile_attempts=3,switch_profile_delay=5):
        """
        Attempts to upload a reel after checking if the app has loaded properly.
        If loading screen check fails, it restarts the app and tries again until successful.

        Now includes retry logic for switching profiles.

        Returns:
            bool: True if upload was successful, False otherwise
        """

        activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Starting APP", "None","ds")
        self.id_active.check_for_call_and_pause()
        self.id_active.ld_adb_controller.startApp()
        self.id_active.check_for_call_and_pause()

        id_or_page = "id"
        app_package = "com.facebook.katana"
    

        restart_attempts = 0

        while restart_attempts < max_restart_attempts:
            print(f"Checking if app is loaded (attempt {restart_attempts + 1}/{max_restart_attempts})")

            self.id_active.check_for_call_and_pause()
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Checking Loading Screen", "None","ds")
            # Check if the screen has loaded by looking for the specified element
            if self.id_active.ld_adb_controller.check_loading_screen_gone(
                after_loading_screen_element=after_loading_screen_element,
                max_attempts=max_attempts,
                delay=delay
            ):
                # Element found, screen has loaded, proceed with upload
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "App Loaded", "None","ds")
                print("App loaded successfully, proceeding with Id Active")
                
                self.execute_shuffled_methods_with_loop()
                
                return True

            # Element not found, restart the app and try again
            print("App not loaded properly, restarting app...")
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "App Not loaded", "None","ds")
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Stoping App", "None","ds")
            self.id_active.ld_adb_controller.stopApp(app_package=app_package)

            time.sleep(random.uniform(2,4))
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Starting App", "None","ds")
            self.id_active.ld_adb_controller.startApp(app_package=app_package)
            time.sleep(random.uniform(1,2))
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Checking Popups", "None","ds")
            self.id_active.ld_adb_controller.save_you_login_info()
            self.id_active.ld_adb_controller.discard_post()
            self.id_active.ld_adb_controller.discard_story()
            activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Scroll Down", "None","ds")

            # Retry switching profile until successful or attempts exhausted
            switch_attempt = 0
            while switch_attempt < switch_profile_attempts:
                
                self.id_active.ld_adb_controller.scroll_down_num(check_for_call_and_pause=self.id_active.check_for_call_and_pause,id_or_page=id_or_page,scroll_down_num=3,delay=0)
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Cheacking Loading Screen", "None","ds")
                self.id_active.ld_adb_controller.wait_till_list_element_visiable_in_fb(cheack_for_call_and_pause=self.id_active.check_for_call_and_pause,id_or_page=id_or_page)
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Swtching Profile", "None","ds")
                switched_profile = self.id_active.ld_adb_controller.switch_profle_to(profile_name=self.id_name,cheack_for_call_and_pause_callback=self.id_active.check_for_call_and_pause,id_or_page="id")




                if switched_profile:
                    print("Profile switched successfully.")
                    break
                else:
                    print(f"Profile switch failed, attempt {switch_attempt + 1}/{switch_profile_attempts}. Retrying...")
                    activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Retrying Swtching Profile in ID Active", "None","ds")
                    time.sleep(switch_profile_delay)
                    switch_attempt += 1


            if not switched_profile:
                activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Failed to switch profile in ID Active", "Error","s")
                print("Failed to switch profile after multiple attempts.")
                restart_attempts += 1

        # If we've exhausted all restart attempts
        print(f"Failed to load app properly after {max_restart_attempts} restart attempts")
        activity_callback(self.activity_queue, self.device, "Facebook", self.id_name, "Failed to Load App in ID Active", "Error","s")
        return False
    
            
# Example usage
if __name__ == "__main__":
    from multiprocessing import Manager
    
    # Setup the control pause event
    manager = Manager()
    control_pause = manager.Event()
    control_pause.set()
    
    
    custom_task_dict = {
        "loops":{"num_of_loop":2,"loops_delay":3},
        "Photo_upload": {"enable": False, "profile_name": "Kajal Kumari", "photo_caption": "Hello friends!","ld_folder":[]},
        "check_notifications": {"enable": False, "duration": 3},

        "confirm_friend_request": {"enable": False, "num_of_friends": 3},
        "add_friend": {"enable": False, "num_of_friends": 2},

        "check_msg_and_reply": {"enable": False, "duration": 2, "reply_text": ["Hello!", "How are you?", "Nice to meet you"]},

        "scroll_feed_and_activiy": {"enable": False, "duration": 2, "config_dict": {
            "like_post": {"enable": "true", "weight": 2},
            "react_post": {"enable": "true", "weight": 1},
            "comment_on_post": {"enable": "true", "weight": 1, "caption": "Great post!"},
            "share_post_to_group": {"enable": False, "weight": 1, "group_list": []},
            "share_to_stroy": {"enable": "false", "weight": 1}
        }},
        "scroll_reels_and_activiy": {"enable": False, "duration": 3, "config_dict": {
            "like_post": {"enable": "true", "weight": 3},
            "comment_on_post": {"enable": "true", "weight": 1, "caption": "Nice video!"},
            "react_post": {"enable": "false", "weight": 0},
            "share_post_to_group": {"enable": False, "weight": 0},
            "share_to_stroy": {"enable": "false", "weight": 0}}},

        "scroll_videos_and_activiy": {"enable": False, "duration": 2, "config_dict": {
            "like_post": {"enable": "true", "weight": 3},
            "comment_on_post": {"enable": "true", "weight": 1, "caption": "Nice video!"},
            "react_post": {"enable": "false", "weight": 0},
            "share_post_to_group": {"enable": False, "weight": 0},
            "share_to_stroy": {"enable": "false", "weight": 0}
        }},
        "post_checkin": {"enable": False, "profile_list": ["Kajal Kumari"], "video_captions": ["im here"], "checkin_location": ["usa"], "folders": [r"E:\facebook_ld_player\LdPlayer0\Kajal Kumari\Kajal Kumari_download_img"],"add_photo":False},
        "post_story":{"enable":False,"num_of_story":1,"profile_list":["Kajal Kumari"],"video_captions":["HI"],"folder":[r"E:\facebook_ld_player\LdPlayer0\Kajal Kumari\Kajal Kumari_download_img"]}
    }
    
    # Create MainIdActive instance
    main_id_active = MainIdActive(
        control_pause_callback=control_pause,
        device_serial="emulator-5558",
        local_output_file_path=r"E:\facebook_ld_player\LdPlayer0\main_folder",
        task_dict=custom_task_dict,
        id_name="Rekha Kumari"
    )
    
    # Execute shuffled methods
    main_id_active.id_active_after_loading_screen()











