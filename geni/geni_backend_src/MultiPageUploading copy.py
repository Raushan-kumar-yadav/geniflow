import logging
import time
import random
from datetime import datetime
from geni.ldController.Ldcontroller_adb.LdAdb import *
from geni.geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten
from ldController.Ldcontroller_adb.id_active.id_active import MainIdActive


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
    

class MultiPageUpload():
    def __init__(self, task, device_name, serial, main_folder_path, pause_control_callback, id_name, task_count, id_information_idx, all_profiles=[], package_name="com.facebook.katana",is_id_active_enable=False,activity_queue=None):
        self.task = task
        self.device_name = device_name
        self.serial = serial
        self.activity_queue=activity_queue
        self.main_folder_path = main_folder_path  
        self.is_id_active_enabled = is_id_active_enable
        self.pause_control_callback = pause_control_callback
        self.id_name = id_name
        self.task_count = task_count
        self.package_name = package_name
        self.id_information_idx = id_information_idx  
        self.all_profiles = all_profiles
        
        # Fix: Use the callback directly as the pause_event
        self.pause_event = pause_control_callback
        self.ld_adb_controller = LdAdbController(device_serial=serial, local_output_file_path=main_folder_path)
        self.device_config_dic = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")

    def has_any_task(self, task_dict, key_list):
        return any(key in task_dict for key in key_list)
    
    def check_is_paused(self):
        if not self.pause_event.is_set():
            self.pause_event.wait()

    def check_for_call(self):
        call_decline_xpath ="//node[@content-desc='DECLINE']"
        self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)
    
    def check_for_call_and_pause(self, id_or_page="id"):
        self.random_time()
        self.pause_event.wait()

        if id_or_page == "id":
            call_decline_xpath ="//node[@content-desc='DECLINE']"
            self.ld_adb_controller.check_for_call(xpath=call_decline_xpath)
    
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

    def extract_profile_info(self, profile_list, current_profile, profile_type):
        """
        Helper method to safely extract profile name and type from profile_list
        """
        try:
            if not profile_list:
                return current_profile, profile_type
            
            # Handle different profile_list structures
            if isinstance(profile_list, list) and len(profile_list) > 0:
                first_item = profile_list[0]
                
                # Case 1: [["profile_name", "profile_type"]] - nested list
                if isinstance(first_item, list) and len(first_item) >= 2:
                    return first_item[0], first_item[1]
                
                # Case 2: ["profile_name", "profile_type"] - flat list with 2 elements
                elif isinstance(first_item, str) and len(profile_list) >= 2:
                    return profile_list[0], profile_list[1]
                
                # Case 3: ["profile_name"] - single profile name
                elif isinstance(first_item, str):
                    return first_item, profile_type
            
            # Fallback to current profile info
            return current_profile, profile_type
            
        except Exception as e:
            print(f"Error extracting profile info: {e}")
            return current_profile, profile_type

    def process_without_app_switch_methods(self):
        """Process tasks without app switching methods."""
        logger = logging.getLogger("process_task_worker")
    
        # Check if pause_event is properly initialized
        if self.pause_event:
            self.pause_event.wait()
        
        self.ld_adb_controller.InstallAndCheckAPK()
        
        self.check_for_call()
        app_package = "com.facebook.katana"
    
        # Task to be executed in this loop
        all_uploading_task = ["reels_upload", "videos_upload", "images_upload", "story_upload"]
    
        self.ld_adb_controller.stopApp(app_package=app_package)
        self.check_for_call_and_pause()
        activity_callback(self.activity_queue, self.device_name, "Geni", self.id_name, "Starting Facebook", "None","ds")
        self.ld_adb_controller.startApp(app_package=app_package)
        self.check_for_call_and_pause()
        time.sleep(random.uniform(1,2))
        self.ld_adb_controller.save_you_login_info()
        self.check_for_call_and_pause()

        # Send log callback
        activity_callback(self.activity_queue, self.device_name, "Geni", self.id_name, "Checking Loading screen", "None","ds")


        after_loading_screen_element = "//node[@content-desc='Create, Double tap to create a new post, story, or reel']"
        home_screen = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=after_loading_screen_element)
        
        if not home_screen:
            self.ld_adb_controller.discard_post()
            self.check_for_call_and_pause()
            self.ld_adb_controller.discard_story()
    
        self.check_for_call_and_pause()
    
        if home_screen:
            activity_callback(self.activity_queue, self.device_name, "Geni", self.id_name, "App Loaded", "None","ds")

            self.random_time(from_time=1, to_time=3)

            # Create a copy of the list to avoid modification during iteration
            profiles_to_process = self.all_profiles.copy()
            for current_profile in profiles_to_process:
                try:

                    # Start the app
                    activity_callback(self.activity_queue, self.device_name, "Geni", self.id_name, "Starting Facebook", "None","ds")
                    
                    self.ld_adb_controller.startApp(app_package=app_package)
                    
                    # Clean up profile name 
                    current_profile = current_profile.strip()
                    print(f"Processing profile: {current_profile}")

                    

                    # Check if this profile has tasks defined
                    if current_profile not in self.task:
                        print(f"No tasks found for profile: {current_profile}")
                        continue
                    

                    
                    current_profile_task = self.task.get(current_profile, {})
                    

                    # Get profile metadata from the task configuration
                    profile_type = current_profile_task.get("profile_type", "id")
                    is_insight_update = current_profile_task.get("insights_collector", False)
                    
                    
                    # Check if there are any uploading tasks available
                    is_task_avl = self.has_any_task(task_dict=current_profile_task, key_list=all_uploading_task)
                    if not is_task_avl and not is_insight_update :
                        print(f"No uploading tasks or insights update available for profile: {current_profile}")
                        continue 
                    
                    
                    
                    activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Switching Profile", "None","ds")
                    

                    is_profile_switched = self.ld_adb_controller.switch_profle_to(
                        profile_name=current_profile,
                        cheack_for_call_and_pause_callback=self.check_for_call_and_pause,  
                        id_or_page=profile_type
                    )
                    
                    if not is_profile_switched:
                        self.ld_adb_controller.stopApp()
                        time.sleep(random.uniform(1,2))
                        self.ld_adb_controller.startApp()
                        time.sleep(random.uniform(1,2))

                        home_screen2 = self.ld_adb_controller.check_loading_screen_gone(after_loading_screen_element=after_loading_screen_element)

                        if home_screen2:
                            is_profile_switched2 = self.ld_adb_controller.switch_profle_to(
                            profile_name=current_profile,
                            cheack_for_call_and_pause_callback=self.check_for_call_and_pause,  
                            id_or_page=profile_type
                            )
                            if not is_profile_switched2:
                                print(f"Error at profile switching for: {current_profile}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Switching Profile Faild", "None","s")
                                continue  
                    

                    activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Profile Switched ", "None","ds")
                    if is_profile_switched:
                        # Reels upload task
                        if "reels_upload" in current_profile_task:
                            activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Processing Reels Uploading", "None","ds")
                            try:
                                reels_uploading_argument = current_profile_task.get("reels_upload", {})
                                profile_list = reels_uploading_argument.get("profile_list", [])
                                
                                # Use the helper method to extract profile info
                                profile_name, profile_type2 = self.extract_profile_info(
                                    profile_list, current_profile, profile_type
                                )
                                
                                captions_sources = reels_uploading_argument.get("captions_sources", "From Original Video")
                                reel_captions_list = reels_uploading_argument.get("captions_list", [])
                                number_of_videos = reels_uploading_argument.get("num_of_content", 1) 
                                reels_download_folder = reels_uploading_argument.get("download_folder_path", "")  
                                schedule_time_list = reels_uploading_argument.get("schedule_time_list", [])
                                reels_ld_folder = reels_uploading_argument.get("ld_folder_path", "")
                                is_group_sharing_enable = reels_uploading_argument.get("is_group_sharing_enable", False)
                                group_list = reels_uploading_argument.get("group_list", "")
                                is_schedule_enable = reels_uploading_argument.get("is_schedule_enable", False)
                                ignore_name = reels_uploading_argument.get("ignore_name",False)
                                num_of_sharing = reels_uploading_argument.get("num_of_group_to_share",1)
        
                                from ldController.Ldcontroller_adb.AdbReelUpload import AdbReelsUpload
                                reels_upload_inst = AdbReelsUpload(
                                    device_name=self.device_name,
                                    device_serial=self.serial,
                                    local_output_file_path=self.main_folder_path,
                                    download_folder=reels_download_folder,  
                                    control_pasue_callback=self.pause_control_callback,
                                    activity_queue=self.activity_queue
                                )

                                reels_upload_inst.reel_upload_after_loading_screen(
                                    profile_name=profile_name,
                                    id_or_page=profile_type2,
                                    app_package=self.package_name,
                                    schdule_time_list=schedule_time_list,
                                    num_of_videos=number_of_videos,
                                    is_group_sharing_enable=is_group_sharing_enable,
                                    group_list=group_list,
                                    caption_form=captions_sources,
                                    captions_list=reel_captions_list,
                                    is_schedule_enable=is_schedule_enable,
                                    num_of_share = num_of_sharing,
                                    ignore_name = ignore_name
                                )
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "All Reels Uploading Done", "None","s")
                                logger.info(f"Reels upload task #{self.task_count} completed on {self.device_name}")
                                self.ld_adb_controller.stopApp()
                            except Exception as e:
                                logger.error(f"Error executing reels_upload task on {self.device_name}: {str(e)}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "All Reels Uploading ", "Error","s")
                                self.ld_adb_controller.stopApp()

                        # Videos upload task
                        if "videos_upload" in current_profile_task:
                            activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Processing Videos Uploading", "None","ds")
                            try:
                                videos_uploading_argument = current_profile_task.get("videos_upload", {})  
                                profile_list = videos_uploading_argument.get("profile_list", [])
                                
                                # Use the helper method to extract profile info
                                profile_name, profile_type2 = self.extract_profile_info(
                                    profile_list, current_profile, profile_type
                                )
                                
                                captions_sources = videos_uploading_argument.get("captions_sources", "From Original Video")
                                reel_captions_list = videos_uploading_argument.get("captions_list", [])
                                number_of_videos = videos_uploading_argument.get("num_of_content", 1)
                                download_folder = videos_uploading_argument.get("download_folder_path", "") 
                                schedule_time_list = videos_uploading_argument.get("schedule_time_list", [])
                                reels_ld_folder = videos_uploading_argument.get("ld_folder_path", "")
                                is_group_sharing_enable = videos_uploading_argument.get("is_group_sharing_enable", False)
                                group_list = videos_uploading_argument.get("group_list", [])
                                is_schedule_enable = videos_uploading_argument.get("is_schedule_enable", False)
                                ignore_name = videos_uploading_argument.get("ignore_name",False)
                                num_of_sharing = videos_uploading_argument.get("num_of_group_to_share",1)
        
                                from ldController.Ldcontroller_adb.AdbVideoUpload import AdbVideosUpload
        
                                video_upload_inst = AdbVideosUpload(
                                    device_name=self.device_name,
                                    device_serial=self.serial,
                                    local_output_file_path=self.main_folder_path,
                                    control_pasue_callback=self.pause_control_callback,
                                    activity_queue=self.activity_queue

                                )
                                video_upload_inst.vides_upload_after_loading_screen(
                                    profile_name=profile_name,
                                    id_or_page=profile_type2,
                                    schdule_time_list=schedule_time_list,
                                    num_of_videos=number_of_videos,
                                    is_group_sharing_enable=is_group_sharing_enable,
                                    group_list=group_list,
                                    caption_form=captions_sources,
                                    captions_list=reel_captions_list,
                                    is_schedule_enable=is_schedule_enable,
                                    download_folder=download_folder,
                                    app_package=app_package,
                                    ignore_names=ignore_name,
                                    num_of_share=num_of_sharing
                                )
                                logger.info(f"Video upload task #{self.task_count} completed on {self.device_name}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "All Videos Uploading Done", "None","s")
                                self.ld_adb_controller.stopApp()
                            except Exception as e:
                                logger.error(f"Error executing video_upload task on {self.device_name}: {str(e)}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "All Reels Uploading ", f"Error:{e}","s")
                                self.ld_adb_controller.stopApp()
        
                        # Image upload task
                        if "images_upload" in current_profile_task: 
                            activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Processing Images Uploading", "None","ds")
                            try:
                                image_uploading_argument = current_profile_task.get("images_upload", {})  
                                profile_list = image_uploading_argument.get("profile_list", [])
                                
                                # Use the helper method to extract profile info
                                profile_name, profile_type2 = self.extract_profile_info(
                                    profile_list, current_profile, profile_type
                                )
                                
                                captions_sources = image_uploading_argument.get("captions_sources", "From Original Video")
                                captions_list = image_uploading_argument.get("captions_list", [])
                                number_of_images = image_uploading_argument.get("num_of_content", 1)
                                download_folder = image_uploading_argument.get("download_folder_path", "") 
                                schedule_time_list = image_uploading_argument.get("schedule_time_list", [])
                                reels_ld_folder = image_uploading_argument.get("ld_folder_path", "")
                                is_group_sharing_enable = image_uploading_argument.get("is_group_sharing_enable", False)
                                group_list = image_uploading_argument.get("group_list", [])
                                is_schedule_enable = image_uploading_argument.get("is_schedule_enable", False)
                                ignore_name = image_uploading_argument.get("ignore_name",False)
                                num_of_sharing = image_uploading_argument.get("num_of_group_to_share",1)
        
                                from ldController.Ldcontroller_adb.AdbImageUpload import AdbimageUpload
                                image_upload_inst = AdbimageUpload(
                                    device_name=self.device_name,
                                    device_serial=self.serial,
                                    local_output_file_path=self.main_folder_path, 
                                    control_pasue_callback=self.pause_control_callback ,
                                    activity_queue=self.activity_queue
                                )
                                image_upload_inst.image_upload_after_loading_screen(
                                    profile_name=profile_name,
                                    id_or_page=profile_type2,
                                    app_package=app_package,
                                    schedule_time_list=schedule_time_list,
                                    is_schedule_enable=is_schedule_enable,
                                    is_group_sharing_enable=is_group_sharing_enable,
                                    group_list=group_list,
                                    caption_form=captions_sources,
                                    caption_list=captions_list,
                                    download_folder=download_folder ,
                                    num_of_image=number_of_images,
                                    num_of_share=num_of_sharing,ignore_name=ignore_name
                                )
        
                                logger.info(f"Image upload task #{self.task_count} completed on {self.device_name}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "All Image Uploading Done", "None","s")
                                self.ld_adb_controller.stopApp()
                            except Exception as e:
                                logger.error(f"Error executing image_upload task on {self.device_name}: {str(e)}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "All Reels Uploading ", f"Error:{e}","s")
                                self.ld_adb_controller.stopApp()
        
                        # Story upload task
                        if "story_upload" in current_profile_task:  
                            activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Processing Story Uploading", "None","ds")
                            try:
                                story_uploading_argument = current_profile_task.get("story_upload", {})  
                                profile_list = story_uploading_argument.get("profile_list", [])
                                
                                # Use the helper method to extract profile info
                                profile_name, profile_type2 = self.extract_profile_info(
                                    profile_list, current_profile, profile_type
                                )
                                
                                captions_sources = story_uploading_argument.get("captions_sources", "From Original Video")
                                captions_list = story_uploading_argument.get("captions_list", [])
                                number_of_videos = story_uploading_argument.get("num_of_content", 1)
                                download_folder = story_uploading_argument.get("download_folder_path", "")  
                                schedule_time_list = story_uploading_argument.get("schedule_time_list", [])
                                reels_ld_folder = story_uploading_argument.get("ld_folder_path", "")
                                is_group_sharing_enable = story_uploading_argument.get("is_group_sharing_enable", False)
                                group_list = story_uploading_argument.get("group_list", [])
                                story_type = story_uploading_argument.get("story_type","video")
                                is_schedule_enable = story_uploading_argument.get("is_schedule_enable", False)
        
                                from ldController.Ldcontroller_adb.AdbStoryUpload import AdbStoryUpload
                                story_upload_inst = AdbStoryUpload(
                                    device_name=self.device_name,
                                    device_serial=self.serial,
                                    local_output_file_path=self.main_folder_path, 
                                    control_pasue_callback=self.pause_control_callback,
                                    activity_queue=self.activity_queue
                                )
                                story_upload_inst.story_upload_after_loading_screen(
                                    profile_name=profile_name,
                                    captions_source=captions_sources,
                                    id_or_page=profile_type2,
                                    image_or_video=story_type,
                                    caption_list=captions_list,
                                    download_folder=download_folder,
                                    stroy_num=number_of_videos,
                                    app_package=app_package
                                )
                                
                                logger.info(f"Story upload task #{self.task_count} completed on {self.device_name}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "All Story Uploading Done", "None","s")
                                self.ld_adb_controller.stopApp()
                            except Exception as e:
                                logger.error(f"Error executing story_upload task on {self.device_name}: {str(e)}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "All Story Uploading ", f"Error:{e}","s")
                                self.ld_adb_controller.stopApp()
        
                        # Insights update task
                        if is_insight_update:
                            try:
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Processing Insight Update", "None","ds")
                                from ldController.Ldcontroller_adb.insights_collector import AdbProfileInsightsUpdate
                                insight_update_task = AdbProfileInsightsUpdate(
                                    control_pasue_callback=self.pause_control_callback, 
                                    page_manager_path=r"User_Data\Page_manager.json",
                                    device_serial=self.serial,
                                    local_output_file_path=self.main_folder_path  
                                )
                                insight_update_task.profile_insight_update_after_loading_screen(
                                    profile_name=current_profile,
                                    id_information_idx=self.id_information_idx,
                                    id_or_page=profile_type,
                                    app_package="com.facebook.katana"
                                )
        
                                logger.info(f"Insights update task #{self.task_count} completed on {self.device_name}")
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Insight Updating Done", "None","s")
                            except Exception as e:
                                logger.error(f"Error executing insights_update task on {self.device_name}: {str(e)}") 
                                activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Insight Updating ", f"Error:{str(e)}","s")
                
                except Exception as e:
                    logger.error(f"Critical error in task processing for {current_profile}: {str(e)}")
                    activity_callback(self.activity_queue, self.device_name, "Facebook", current_profile, "Critical Errors", f"Error:{str(e)}","s")
                    print(f"Critical error in task processing for {current_profile}: {str(e)}")
                    continue  


            id_name = self.all_profiles.pop(0)
            id_active_config_dict = self.task.get("id_active_config",{})
            if self.is_id_active_enabled:
                try:
                    activity_callback(self.activity_queue, self.device_name, "Facebook", id_name, "Processing Id Active", "None","s")
                    IdActive = MainIdActive(control_pause_callback=self.pause_control_callback,device_name=self.device_name,device_serial=self.serial,local_output_file_path=self.  main_folder_path ,task_dict=id_active_config_dict,id_name=id_name,activity_queue=self.activity_queue)
                    IdActive.id_active_after_loading_screen()
                except Exception as e :
                    print(f"Error In Id Active{e}")
                    activity_callback(self.activity_queue, self.device_name, "Facebook", id_name, "Id Active", f"Error:{str(e)}","s")
            # Clear the processed profiles
            self.all_profiles.clear()
            logger.info(f"All profiles processed successfully on {self.device_name}")
            activity_callback(self.activity_queue, self.device_name, "Facebook", id_name, "ALL Task Done", "None","s")
            delete_callback(self.activity_queue,self.device_name)
            return
