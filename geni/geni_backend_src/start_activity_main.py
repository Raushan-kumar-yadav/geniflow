import multiprocessing
from multiprocessing import Manager
import time
from datetime import datetime
import queue
import os
import logging
import platform
import subprocess
from subprocess import CREATE_NO_WINDOW
from typing import Dict, Any, Optional, List
import sys

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QSpinBox
)
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QPalette

from geni_backend_src.MultiPageUploading import MultiPageUpload

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

        
def process_without_app_switch_methods(task, device_name, serial, main_file_path, pause_control_callback, id_name, task_count, id_information_idx):
    """Process tasks without app switching methods."""
    logger = logging.getLogger("process_task_worker")
    
    if "reels_uploading" in task:
        try:
            reels_uploading_argument = task["reels_uploading_argumanet"]
            profile_lists = reels_uploading_argument["Profile_lists"]
            reel_captions_list = reels_uploading_argument["video_captions"]
            package_name = reels_uploading_argument["app_package"]
            reels_profile_folder = reels_uploading_argument["reels_video_profile_folder"]
            schedule_times_list = reels_uploading_argument["schedule_times_list"]
            is_schedule_enable = reels_uploading_argument["is_schedule_enable"]
            
            
            from ldController.Ldcontroller_adb.AdbReelUpload import AdbReelsUpload
            reels_upload_inst = AdbReelsUpload(
                device_name=device_name,
                device_serial=serial,
                local_output_file_path=main_file_path,
                control_pasue_callback=pause_control_callback
            ) 
            reels_upload_inst.reel_upload_page_list(
                Profile_lists=profile_lists,
                id_name=id_name,
                video_captions_list=reel_captions_list,
                reels_profile_folder=reels_profile_folder,
                app_package=package_name,
                schdule_time_list=schedule_times_list,
                is_schedule_enable_list=is_schedule_enable
            )
            logger.info(f"Reels upload task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing reels_upload task on {device_name}: {str(e)}")
    
    if "video_uploading" in task:
        try:
            video_uploading_argument = task["video_uploading_argumanet"]
            video_profile_lists = video_uploading_argument["Profile_lists"]
            video_captions_list = video_uploading_argument["video_captions"]
            video_package_name = video_uploading_argument["app_package"]
            video_profile_folder = video_uploading_argument["video_profile_folder"]
            video_schedule_times_list = video_uploading_argument["schedule_times_list"]
            video_is_schedule_enable = video_uploading_argument["is_schedule_enable"]
            
            from ldController.Ldcontroller_adb.AdbVideoUpload import AdbVideoUpload
            video_upload_inst = AdbVideoUpload(
                device_name=device_name,
                device_serial=serial,
                local_output_file_path=main_file_path,
                control_pasue_callback=pause_control_callback
            ) 
            video_upload_inst.video_upload_page_list(
                Profile_lists=video_profile_lists,
                id_name=id_name,
                video_captions_list=video_captions_list,
                video_profile_folder=video_profile_folder,
                app_package=video_package_name,
                schdule_time_list=video_schedule_times_list,
                is_schedule_enable_list=video_is_schedule_enable
            )
            logger.info(f"Video upload task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing video_upload task on {device_name}: {str(e)}")
    
    if "image_uploading" in task:
        try:
            image_uploading_argument = task["image_uploading_argumanet"]
            image_profile_lists = image_uploading_argument["Profile_lists"]
            image_captions_list = image_uploading_argument["image_captions"]
            image_package_name = image_uploading_argument["app_package"]
            image_profile_folder = image_uploading_argument["image_profile_folder"]
            image_schedule_times_list = image_uploading_argument["schedule_times_list"]
            image_is_schedule_enable = image_uploading_argument["is_schedule_enable"]
            
            from ldController.Ldcontroller_adb.AdbImageUpload import AdbimageUpload
            image_upload_inst = AdbimageUpload(
                device_name=device_name,
                device_serial=serial,
                local_output_file_path=main_file_path,
                control_pasue_callback=pause_control_callback
            ) 
            image_upload_inst.image_upload_page_list(
                Profile_lists=image_profile_lists,
                id_name=id_name,
                image_captions_list=image_captions_list,
                image_profile_folder=image_profile_folder,
                app_package=image_package_name,
                schdule_time_list=image_schedule_times_list,
                is_schedule_enable_list=image_is_schedule_enable
            )
            logger.info(f"Image upload task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing image_upload task on {device_name}: {str(e)}")
    
    if "story_uploading" in task:
        try:
            story_uploading_argument = task["story_uploading_argumanet"]
            story_profile_lists = story_uploading_argument["Profile_lists"]
            story_captions_list = story_uploading_argument["story_captions"]
            story_package_name = story_uploading_argument["app_package"]
            story_profile_folder = story_uploading_argument["story_profile_folder"]
            # Note: Story uploading may not use schedule times
            
            from ldController.Ldcontroller_adb.AdbStoryUpload import AdbStoryUpload
            story_upload_inst = AdbStoryUpload(
                device_name=device_name,
                device_serial=serial,
                local_output_file_path=main_file_path,
                control_pasue_callback=pause_control_callback
            ) 
            story_upload_inst.story_upload_page_list(
                Profile_lists=story_profile_lists,
                id_name=id_name,
                image_captions=story_captions_list,
                image_profile_folder=story_profile_folder,
                app_package=story_package_name
            )
            logger.info(f"Story upload task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing story_upload task on {device_name}: {str(e)}")
    
    if "id_active_task" in task:
        try:
            id_active_argument = task["id_active_argumanet"]
            config_dict = id_active_argument["config_dict"]
            
            from ldController.Ldcontroller_adb.id_active.id_active import MainIdActive
            id_active_inst = MainIdActive(
                device_serial=serial,
                device_name=device_name,
                local_output_file_path=main_file_path,
                control_pause_callback=pause_control_callback,
                task_dict=config_dict,
                id_name=id_name
            ) 
            
            id_active_inst.execute_shuffled_methods_with_loop()


            logger.info(f"ID active task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing id_active task on {device_name}: {str(e)}")
    
    if "insights_update_task" in task:
        try:
            insights_update_task_arg = task["insights_update_task_argumanet"]
            insight_update_profile_list = insights_update_task_arg["profile_list"]
            package_name = insights_update_task_arg.get("app_package", "com.instagram.android")
            
            from ldController.Ldcontroller_adb.insights_collector import AdbProfileInsightsUpdate
            insight_update_task = AdbProfileInsightsUpdate(
                control_pasue_callback=pause_control_callback,
                page_manager_path=r"User_Data\Page_manager.json",
                device_serial=serial,
                local_output_file_path=main_file_path
            )
            insight_update_task.profile_insight_update_page_list(
                id_information_idx=id_information_idx,
                Profile_lists=insight_update_profile_list,
                app_package=package_name
            )
            logger.info(f"Insights update task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing insights_update task on {device_name}: {str(e)}")


def process_with_app_switch_methods(task, device_name, serial, main_file_path, pause_control_callback, id_name, task_count, id_information_idx):
    """Process tasks with app switching methods."""
    logger = logging.getLogger("process_task_worker")
    
    if "reels_uploading" in task:
        try:
            reels_uploading_argument = task["reels_uploading_argumanet"]
            profile_lists = reels_uploading_argument["Profile_lists"]
            reel_captions_list = reels_uploading_argument["video_captions"]
            reel_captions_source = reels_uploading_argument["captions_sources"]
            package_name = reels_uploading_argument["app_package"]
            reels_profile_folder = reels_uploading_argument["reels_video_profile_folder"]
            schedule_times_list = reels_uploading_argument["schedule_times_list"]
            is_schedule_enable = reels_uploading_argument["is_schedule_enable"]
            
            from ldController.Ldcontroller_adb.AdbReelUpload_ASW import AdbReelUploadASW
            reels_upload_inst = AdbReelUploadASW(
                device_name=device_name,
                device_serial=serial,
                local_output_file_path=main_file_path,
                control_pasue_callback=pause_control_callback
            ) 
            reels_upload_inst.reels_upload_page_list(
                Profile_lists=profile_lists,
                id_name=id_name,
                captions_sources=reel_captions_source,
                video_captions_list=reel_captions_list,
                reels_profile_folder=reels_profile_folder,
                app_package=package_name,
                schdule_time_list=schedule_times_list,
                is_schedule_enable_list=is_schedule_enable
            )
            logger.info(f"Reels upload task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing reels_upload task on {device_name}: {str(e)}")
    
    if "video_uploading" in task:
        try:
            video_uploading_argument = task["video_uploading_argumanet"]
            video_profile_lists = video_uploading_argument["Profile_lists"]
            video_captions_list = video_uploading_argument["video_captions"]
            video_captions_sources = video_uploading_argument["captions_sources"]
            video_package_name = video_uploading_argument["app_package"]
            video_profile_folder = video_uploading_argument["video_profile_folder"]
            video_schedule_times_list = video_uploading_argument["schedule_times_list"]
            video_is_schedule_enable = video_uploading_argument["is_schedule_enable"]
            
            from ldController.Ldcontroller_adb.AdbVideoUpload_ASW import AdbVideoUploadASW
            video_upload_inst = AdbVideoUploadASW(
                device_name=device_name,
                device_serial=serial,
                local_output_file_path=main_file_path,
                control_pasue_callback=pause_control_callback
            ) 
            video_upload_inst.video_upload_page_list(
                Profile_lists=video_profile_lists,
                id_name=id_name,
                video_captions_list=video_captions_list,
                video_profile_folder=video_profile_folder,
                app_package=video_package_name,
                captions_sources=video_captions_sources,
                schdule_time_list=video_schedule_times_list,
                is_schedule_enable_list=video_is_schedule_enable
            )
            logger.info(f"Video upload task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing video_upload task on {device_name}: {str(e)}")
    
    if "image_uploading" in task:
        try:
            image_uploading_argument = task["image_uploading_argumanet"]
            image_profile_lists = image_uploading_argument["Profile_lists"]
            image_captions_list = image_uploading_argument["image_captions"]
            image_captions_sources = image_uploading_argument["captions_sources"]
            image_package_name = image_uploading_argument["app_package"]
            image_profile_folder = image_uploading_argument["image_profile_folder"]
            image_schedule_times_list = image_uploading_argument["schedule_times_list"]
            image_is_schedule_enable = image_uploading_argument["is_schedule_enable"]
            
            from ldController.Ldcontroller_adb.AdbImageUpload_ASW import AdbImageUploadASW
            image_upload_inst = AdbImageUploadASW(
                device_name=device_name,
                device_serial=serial,
                local_output_file_path=main_file_path,
                control_pasue_callback=pause_control_callback
            ) 
            image_upload_inst.image_upload_page_list(
                Profile_lists=image_profile_lists,
                id_name=id_name,
                image_captions_list=image_captions_list,
                captions_sources=image_captions_sources,
                image_profile_folder=image_profile_folder,
                app_package=image_package_name,
                schdule_time_list=image_schedule_times_list,
                is_schedule_enable_list=image_is_schedule_enable
            )
            logger.info(f"Image upload task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing image_upload task on {device_name}: {str(e)}")
    
    if "story_uploading" in task:
        try:
            story_uploading_argument = task["story_uploading_argumanet"]
            story_profile_lists = story_uploading_argument["Profile_lists"]
            story_captions_list = story_uploading_argument["story_captions"]
            story_package_name = story_uploading_argument["app_package"]
            story_profile_folder = story_uploading_argument["story_profile_folder"]
            # Note: Story uploading may not use schedule times
            
            from ldController.Ldcontroller_adb.AdbStoryUpload import AdbStoryUpload
            story_upload_inst = AdbStoryUpload(
                device_name=device_name,
                device_serial=serial,
                local_output_file_path=main_file_path,
                control_pasue_callback=pause_control_callback
            ) 
            story_upload_inst.story_upload_page_list(
                Profile_lists=story_profile_lists,
                id_name=id_name,
                image_captions=story_captions_list,
                image_profile_folder=story_profile_folder,
                app_package=story_package_name
            )
            logger.info(f"Story upload task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing story_upload task on {device_name}: {str(e)}")
    
    if "id_active_task" in task:
        try:
            id_active_argument = task["id_active_argumanet"]
            config_dict = id_active_argument["config_dict"]
            
            from ldController.Ldcontroller_adb.id_active.id_active import MainIdActive
            id_active_inst = MainIdActive(
                device_serial=serial,
                device_name=device_name,
                local_output_file_path=main_file_path,
                control_pause_callback=pause_control_callback,
                task_dict=config_dict,
                id_name=id_name
            ) 
            
            id_active_inst.execute_shuffled_methods_with_loop()


            logger.info(f"ID active task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing id_active task on {device_name}: {str(e)}")
    
    if "insights_update_task" in task:
        try:
            insights_update_task_arg = task["insights_update_task_argumanet"]
            insight_update_profile_list = insights_update_task_arg["profile_list"]
            package_name = insights_update_task_arg.get("app_package", "com.instagram.android")
            
            from ldController.Ldcontroller_adb.insights_collector import AdbProfileInsightsUpdate
            insight_update_task = AdbProfileInsightsUpdate(
                control_pasue_callback=pause_control_callback,
                page_manager_path=r"User_Data\Page_manager.json",
                device_serial=serial,
                local_output_file_path=main_file_path
            )
            insight_update_task.profile_insight_update_page_list(
                id_information_idx=id_information_idx,
                Profile_lists=insight_update_profile_list,
                app_package=package_name
            )
            logger.info(f"Insights update task #{task_count} completed on {device_name}")
        except Exception as e:
            logger.error(f"Error executing insights_update task on {device_name}: {str(e)}")




def process_task_worker(pause_control_callback, task_dict, ld_player_path, adb_path, resume_event, is_arrange_ld=False,activity_queue=None):
    """Worker process function to handle tasks for a single device."""
    # Setup logging
    log_folder = "log_folder"  
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, f"ld_executor_worker_{task_dict['device_name']}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("process_task_worker")


    # Extract task information
    device_name = task_dict["device_name"]
    id_name = task_dict["id_name"]
    id_information_idx = task_dict["id_information_idx"]
    main_file_path = task_dict["local_output_file_path"]
    upload_method = task_dict["upload_method"]
    serial = task_dict["serial"]
    all_profiles = task_dict["all_profiles"]
    is_id_active_enable = task_dict["id_active_enabled"]
    inner_task_list = task_dict.get("task_list", [])
    # Extract task information
    device_name = task_dict["device_name"]
    id_name = task_dict["id_name"]
    worker_id = f"{device_name}"  
    
    # Send initial activity update
    if activity_queue:
        activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Initializing", "None","ds")



    logger.info(f"Processing task for device: {device_name}, ID: {id_name}, Serial: {serial}, Method: {upload_method}")

    def check_ld_instance_open(timeout=300, target_serial=""):
        """Check if LD instance is open and accessible via ADB."""
        start_time = time.time()
        while True:
            try:
                result = subprocess.run([str(adb_path), "devices"], stdout=subprocess.PIPE, text=True, timeout=10,shell=True)
                output = result.stdout
                for line in output.splitlines():
                    if target_serial in line and "device" in line and "offline" not in line:
                        logger.info(f"Emulator {target_serial} found and ready")
                        return True
                
                if time.time() - start_time >= timeout:
                    logger.error(f"Timeout waiting for emulator {target_serial}")
                    return False
                    
                time.sleep(2)
            except subprocess.TimeoutExpired:
                logger.warning("ADB devices command timed out")
                if time.time() - start_time >= timeout:
                    return False
            except Exception as e:
                logger.error(f"Error checking ADB devices: {str(e)}")
                if time.time() - start_time >= timeout:
                    return False

    def open_ld_player(device_name):
        """Open LD Player instance."""
        if not ld_player_path or not os.path.exists(ld_player_path):
            logger.error(f"Invalid LD Player path: {ld_player_path}")
            return False
            
        try:
            ldconsole_path = os.path.join(ld_player_path, "ldconsole.exe")
            if not os.path.exists(ldconsole_path):
                logger.error(f"ldconsole.exe not found at {ldconsole_path}")
                return False

            # Check if already running
            check_cmd = [ldconsole_path, "isrunning", "--name", device_name]
            result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,shell=True ,timeout=30)
            
            if "running" in result.stdout.lower():
                logger.info(f"LD Player instance {device_name} is already running")
                if is_arrange_ld:
                    subprocess.run([ldconsole_path, "sortWnd"], timeout=30,shell=True)
                return True

            # Launch the instance
            launch_cmd = [ldconsole_path, "launch", "--name", device_name]
            logger.info(f"Launching LD Player instance: {device_name}")
            subprocess.run(launch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,shell=True)

            # Wait for initialization
            max_retries = 24  # 2 minutes with 5-second intervals
            for i in range(max_retries):
                logger.info(f"Waiting for {device_name} to initialize... ({i+1}/{max_retries})")
                time.sleep(5)
                
                result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,shell=True)
                if "running" in result.stdout.lower():
                    logger.info(f"LD Player instance {device_name} successfully started")
                    if is_arrange_ld:
                        subprocess.run([ldconsole_path, "sortWnd"], timeout=30,shell=True)
                    time.sleep(5)  # Additional wait for full initialization
                    return True
                    
            logger.error(f"Failed to start LD Player instance {device_name} after {max_retries} attempts")
            return False
            
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while starting LD Player instance {device_name}")
            return False
        except Exception as e:
            logger.error(f"Error opening LD Player instance {device_name}: {str(e)}")
            return False

    def close_ld_player(device_name):
        """Close LD Player instance."""
        if not ld_player_path or not os.path.exists(ld_player_path):
            logger.error(f"Invalid LD Player path: {ld_player_path}")
            return False
            
        try:
            ldconsole_path = os.path.join(ld_player_path, "ldconsole.exe")
            logger.info(f"Closing LD Player instance: {device_name}")
            
            # Graceful quit
            quit_cmd = [ldconsole_path, "quit", "--name", device_name]
            subprocess.run(quit_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,shell=True)
            time.sleep(5)
            
            # Verify closure
            check_cmd = [ldconsole_path, "isrunning", "--name", device_name]
            result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30,shell=True)
            
            if "not running" in result.stdout.lower() or "running" not in result.stdout.lower():
                logger.info(f"LD Player instance {device_name} successfully closed")
                return True
            else:
                logger.warning(f"Graceful quit failed for {device_name}, attempting force quit")
                force_cmd = [ldconsole_path, "quit", "--name", device_name, "--force"]
                subprocess.run(force_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,shell=True)
                return True
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while closing LD Player instance {device_name}")
            return False
        except Exception as e:
            logger.error(f"Error closing LD Player instance {device_name}: {str(e)}")
            return False

    # Main worker logic
    try:
        # Attempt to open LD Player
        success = False
        for attempt in range(3):
            logger.info(f"Attempt {attempt+1}/3 to open LD Player instance {device_name}")
            if activity_queue:
                    activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Opening LD", "Starting","ds")
            resume_event.wait()
            if open_ld_player(device_name) and check_ld_instance_open(target_serial=serial):
                success = True
                break
            time.sleep(10)
            
        if not success:
            if activity_queue:
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Opening LD", "Errors","ds")
            logger.error(f"Failed to open LD Player instance {device_name} after multiple attempts. Skipping tasks.")
            return
        
        activity_callback(activity_queue, device_name, "Geni", id_name, "LD Ready", "Starting","ds")

        from geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten
        device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")
        time_to_wait = device_settings.flatten_json().get("before_any_task_delay", 30)
        is_vpn_check_enable=device_settings.flatten_json().get("check_vpn_connnection", False)
        
        if is_vpn_check_enable:
            from ldController.Ldcontroller_adb.LdAdb import VPNMonitor
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Starting VPN", "None","ds")
            vpn_monitor = VPNMonitor(device_id=serial,timeout=time_to_wait,local_output_file_path=main_file_path,pause_callback=pause_control_callback)
            is_vpn_connected = vpn_monitor.main()
            if not is_vpn_connected:
                resume_event.wait()
                if close_ld_player(device_name):
                    logger.warning(f"closing LD Player instance due to VPN issue on  #{device_name}")
                    activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Closing LD", " Error VPN not connected","s") 
                    delete_callback(activity_queue,device_name)
                else:
                    logger.warning(f"Failed to close LD Player instance {device_name} properly")
                    activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Closing LD due to VPN Issue", " Error At Closing LD","s")
                    delete_callback(activity_queue,device_name)
                return False
        else:
            time.sleep(time_to_wait)
            
        # Process tasks
        for task_count, task in enumerate(inner_task_list, 1):
            # Wait for resume signal before processing each task
            logger.info(f"Waiting for resume signal before task #{task_count}")
            resume_event.wait()
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Starting task", "Starting worker process","ds")
            logger.info(f"Executing task  on {device_name}")
            multi_upload = MultiPageUpload(task=task,device_name=device_name,serial=serial,main_folder_path=main_file_path,pause_control_callback=pause_control_callback,id_name=id_name,task_count=task_count,id_information_idx=id_information_idx,all_profiles=all_profiles,is_id_active_enable=is_id_active_enable,activity_queue=activity_queue) 
            multi_upload.process_without_app_switch_methods()

            return

        logger.info(f"All tasks ({len(inner_task_list)}) completed for {device_name}")
        activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "All Task Completed", "None","ds")
        
        mark_finished_callback(activity_queue,device_name,"Geni")
        delete_callback(activity_queue,device_name)

    except Exception as e:
        logger.error(f"Critical error in task processing for {device_name}: {str(e)}")
        activity_callback(activity_queue, device_name, "Geni", id_name, f"Error in task {str(e)}", "None","ds")
        delete_callback(activity_queue,device_name)
    finally:
        # Always attempt to close LD Player
        resume_event.wait()
        if not close_ld_player(device_name):
            logger.warning(f"Failed to close LD Player instance {device_name} properly")
            delete_callback(activity_queue,device_name)


class LDTaskExecutor:
    def __init__(self, main_queue,max_instances=4, ld_player_path=None, instance_delay=5, is_arrange_ld=False,activity_queue=None,current_activity_ref=None):
        """
        Initialize the LDTaskExecutor.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("ld_executor.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("LDTaskExecutor")  

        self.main_queue = main_queue
        self.adb_path = r"platform-tools\adb.exe"
        self.max_instances = max_instances
        self.instance_delay = instance_delay 
        self.is_arrange_ld = is_arrange_ld 
        self.activity_queue = activity_queue
        self.current_activity_ref = current_activity_ref
        self.stop_event = multiprocessing.Event() 
        self.active_instances = {}  
        self.lock = multiprocessing.Lock()
        self.resume_event = multiprocessing.Event()
        self.manager = Manager()
        self.control_pause = self.manager.Event()
        self.control_pause.set()
        self.resume_event.set()

        # Set LD Player path
        if ld_player_path:
            self.ld_player_path = ld_player_path
        else:
            try:
                from task_collector import TaskCollector
                collector = TaskCollector()
                self.ld_player_path = collector.ld_player_path
                self.logger.info(f"Got LD Player path from TaskCollector: {self.ld_player_path}")
            except Exception as e:
                self.ld_player_path = ""
                self.logger.error(f"Failed to get LD Player path: {str(e)}")

        if self.ld_player_path and not os.path.exists(self.ld_player_path):
            self.logger.warning(f"LD Player path does not exist: {self.ld_player_path}")
        elif not self.ld_player_path:
            self.logger.warning("LD Player path is not set")

    def pause(self):
        """Pause the executor (worker processes will block before processing next task)."""
        self.resume_event.clear()
        self.control_pause.clear()
        for device_name in list(self.active_instances.keys()):
            proc = self.active_instances[device_name]["process"]
            d_name = self.active_instances[device_name]["device_name"]

            activity_callback(self.activity_queue, d_name, "Geni", 
                         "", "paused", "None","ds")
        
        self.current_activity_ref.pause()
        self.logger.info("Executor paused.")

    def resume(self):
        """Resume the executor."""
        self.resume_event.set()
        self.control_pause.set()
        self.current_activity_ref.resume()
        for device_name in list(self.active_instances.keys()):
            proc = self.active_instances[device_name]["process"]
            d_name = self.active_instances[device_name]["device_name"]

            activity_callback(self.activity_queue, d_name, "Geni", 
                         "", "resumed", "None","ds")
        
        self.logger.info("Executor resumed.")

    def quit_all(self):
        """Quit all processing immediately (force termination)"""
        self.logger.info("Quitting all processes immediately...")
        self.stop_event.set()
        # Clear remaining tasks
        while not self.main_queue.empty():
            try:
                self.main_queue.get_nowait()
                self.main_queue.task_done()
            except queue.Empty:
                break
        # Terminate active processes
        for device_name in list(self.active_instances.keys()):
            proc = self.active_instances[device_name]["process"]
            d_name = self.active_instances[device_name]["device_name"]

            delete_callback(self.activity_queue,d_name)
            
            self.logger.info(f"Force terminating process for device: {device_name}")
            proc.terminate()
            proc.join()
            del self.active_instances[device_name]
        # Optionally force quit external LD Player instances
        try:
            
            cmd = "taskkill /F /IM dnplayer.exe"
            self.logger.info(f"Executing force quit command: {cmd}")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except Exception as e:
            self.logger.error("Error stopping ld instances: " + str(e))
        self.logger.info("All processes force terminated.")


    def run(self):
        """
        Process all tasks in the main queue using multiprocessing.
        The loop now also checks if stop_event is set.
        """
        self.logger.info(f"Starting LDTaskExecutor with max {self.max_instances} simultaneous instances")
        self.logger.info(f"Main queue size: {self.main_queue.qsize()}")
        self.logger.info(f"LD Player path: {self.ld_player_path}")
    
        while not self.stop_event.is_set() and not (self.main_queue.empty() and len(self.active_instances) == 0):
            with self.lock:
                while len(self.active_instances) < self.max_instances and not self.main_queue.empty():
                    try:
                        task_dict = self.main_queue.get(block=False)
                        device_name = task_dict["device_name"]
                        self.logger.info(f"here be 1")
                        if device_name in self.active_instances:
                            self.logger.warning(f"Device {device_name} is already active. Skipping duplicate task.")
                            self.main_queue.task_done()
                            continue
                        self.logger.info(f"here be 2")
                        proc = multiprocessing.Process(
                            target=process_task_worker,
                            args=(self.control_pause,task_dict, self.ld_player_path, self.adb_path, self.resume_event, self.is_arrange_ld,self.activity_queue),
                            name=f"Process-{device_name}"
                        )
                        proc.start()
                        self.active_instances[device_name] = {
                            "process": proc,
                            "start_time": time.time(),
                            "id_name": task_dict["id_name"],
                            "device_name":device_name
                        }
                        self.logger.info(f"Started process for device: {device_name} ({len(self.active_instances)}/{self.max_instances} active)")
                        if self.instance_delay > 0:
                            self.logger.info(f"Waiting for {self.instance_delay} seconds before launching the next instance.")
                            time.sleep(self.instance_delay)
                    except queue.Empty:
                        break
                    except Exception as e:
                        self.logger.error(f"Error starting new process: {str(e)}")
    
            # Monitoring and cleanup of active instances...
            for device_name in list(self.active_instances.keys()):
                proc_info = self.active_instances[device_name]
                proc = proc_info["process"]
                if not proc.is_alive():
                    proc.join()
                    self.logger.info(f"Process for {device_name} has completed. Removing from active instances.")
                    del self.active_instances[device_name]
                    self.main_queue.task_done()
    
            self.logger.info(f"Status: {len(self.active_instances)}/{self.max_instances} active instances, {self.main_queue.qsize()} tasks remaining")
            time.sleep(10)

        
        from geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten
        device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")
        is_auto_sleep_enable = device_settings.flatten_json().get("Auto shutdown after task completion", False)
        if is_auto_sleep_enable:
            time.sleep(10)
            self.execute_sleep()

        self.logger.info("Exiting run loop.")
    

    

    def execute_sleep(self):
        """Execute sleep command based on OS"""
        system = platform.system().lower()
        
        try:
            if system == "windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            elif system == "darwin":  
                subprocess.run(["pmset", "sleepnow"], check=True)
            elif system == "linux":
                subprocess.run(["systemctl", "suspend"], check=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to sleep computer: {e}")


    def stop(self):
        """Stop all running processes and clean up gracefully."""
        self.logger.info("Stopping LDTaskExecutor gracefully...")
        self.stop_event.set()
        # Optionally clear pending tasks
        while not self.main_queue.empty():
            try:
                self.main_queue.get_nowait()
                self.main_queue.task_done()
            except queue.Empty:
                break
        try:
            cmd = "taskkill /F /IM dnplayer.exe"
            self.logger.info(f"Executing force quit command: {cmd}")
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except Exception as e:
            self.logger.error("Error stopping ld instances: " + str(e))
        for device_name in list(self.active_instances.keys()):
            proc = self.active_instances[device_name]["process"]
            d_name = self.active_instances[device_name]["device_name"]

            delete_callback(self.activity_queue,d_name)
            proc.terminate()
            proc.join()
            self.logger.info(f"Stopped process for device: {device_name}")
        self.logger.info("All processes stopped gracefully.")


# Example usage
if __name__ == "__main__":
    from task_collector import TaskCollector
    from multiprocessing import JoinableQueue
    import threading
    import time

    # Get tasks from TaskCollector
    collector = TaskCollector()
    raw_tasks_queue = collector.collect_tasks_from_json()  # Returns a Queue

    # Extract tasks into a list
    tasks_list = []
    while not raw_tasks_queue.empty():
        tasks_list.append(raw_tasks_queue.get())

    # Convert tasks_list back into a multiprocessing-safe JoinableQueue.
    tasks_queue = JoinableQueue()
    for task in tasks_list:
        if "task_queue" in task:
            inner_list = []
            while not task["task_queue"].empty():
                inner_list.append(task["task_queue"].get())
            task["task_list"] = inner_list
            del task["task_queue"]
        tasks_queue.put(task)

    # Create the executor instance.
    executor = LDTaskExecutor(tasks_queue, max_instances=2, ld_player_path=collector.ld_player_path)

    # Define a control function to pause, resume, then force-quit the executor.
    def control_actions():
        time.sleep(60)
        print("Pausing executor...")
        executor.pause()
        time.sleep(50)
        print("Resuming executor...")
        executor.resume()


    # Start the control thread (as daemon so it won't block program exit)
    control_thread = threading.Thread(target=control_actions, daemon=True)
    control_thread.start()

    # Run the executor's main loop (this call blocks until there are no more tasks or stop_event is set)
    executor.run()

    control_thread.join(timeout=1)
