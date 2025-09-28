import multiprocessing
from multiprocessing import Manager, Pool, Process, Queue, Event, Lock
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
import queue
import os
import logging
import subprocess
from typing import Dict, Any, Optional, List, Tuple
import sys
import threading
from functools import partial
import asyncio
import concurrent.futures

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
            
            id_active_inst.execute_shuffled_methods()


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
            
            id_active_inst.execute_shuffled_methods()


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


class ADBConnectionPool:
    """Connection pool for ADB operations to reduce overhead."""
    
    def __init__(self, adb_path: str, pool_size: int = 10):
        self.adb_path = adb_path
        self.pool_size = pool_size
        self._lock = threading.Lock()
        self._cache = {}
        self._last_check = {}
    
    def check_device_status_batch(self, serials: List[str]) -> Dict[str, bool]:
        """Check multiple device statuses in parallel."""
        with ThreadPoolExecutor(max_workers=min(len(serials), 5)) as executor:
            future_to_serial = {
                executor.submit(self._check_single_device, serial): serial 
                for serial in serials
            }
            
            results = {}
            for future in as_completed(future_to_serial):
                serial = future_to_serial[future]
                try:
                    results[serial] = future.result()
                except Exception as e:
                    logging.error(f"Error checking device {serial}: {e}")
                    results[serial] = False
            
            return results
    
    def _check_single_device(self, serial: str) -> bool:
        """Check single device with caching."""
        current_time = time.time()
        
        # Use cached result if recent (within 5 seconds)
        if (serial in self._cache and 
            serial in self._last_check and 
            current_time - self._last_check[serial] < 5):
            return self._cache[serial]
        
        try:
            result = subprocess.run(
                [str(self.adb_path), "-s", serial, "get-state"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True, 
                timeout=5
            )
            
            is_ready = result.returncode == 0 and "device" in result.stdout.strip()
            
            with self._lock:
                self._cache[serial] = is_ready
                self._last_check[serial] = current_time
            
            return is_ready
            
        except (subprocess.TimeoutExpired, Exception) as e:
            logging.warning(f"ADB check failed for {serial}: {e}")
            with self._lock:
                self._cache[serial] = False
                self._last_check[serial] = current_time
            return False

class LDPlayerManager:
    """Optimized LD Player management with parallel operations."""
    
    def __init__(self, ld_player_path: str, is_arrange_ld: bool = False):
        self.ld_player_path = ld_player_path
        self.is_arrange_ld = is_arrange_ld
        self.ldconsole_path = os.path.join(ld_player_path, "ldconsole.exe")
        self._executor = ThreadPoolExecutor(max_workers=8)
        
    def batch_launch_instances(self, device_configs: List[Dict]) -> Dict[str, bool]:
        """Launch multiple LD Player instances in parallel."""
        futures = {}
        
        for config in device_configs:
            device_name = config['device_name']
            future = self._executor.submit(self._launch_single_instance, device_name)
            futures[device_name] = future
        
        results = {}
        for device_name, future in futures.items():
            try:
                results[device_name] = future.result(timeout=120)  # 2 minute timeout per instance
            except Exception as e:
                logging.error(f"Failed to launch {device_name}: {e}")
                results[device_name] = False
        
        return results
    
    def _launch_single_instance(self, device_name: str) -> bool:
        """Launch a single LD Player instance."""
        try:
            # Check if already running
            check_cmd = [self.ldconsole_path, "isrunning", "--name", device_name]
            result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            
            if "running" in result.stdout.lower():
                logging.info(f"LD Player instance {device_name} is already running")
                if self.is_arrange_ld:
                    subprocess.run([self.ldconsole_path, "sortWnd"], timeout=30)
                return True

            # Launch the instance
            launch_cmd = [self.ldconsole_path, "launch", "--name", device_name]
            logging.info(f"Launching LD Player instance: {device_name}")
            subprocess.run(launch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

            # Wait for initialization with exponential backoff
            backoff_times = [2, 3, 5, 8, 10]  # Progressive wait times
            max_retries = 15
            
            for i in range(max_retries):
                wait_time = backoff_times[min(i, len(backoff_times)-1)]
                time.sleep(wait_time)
                
                result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
                if "running" in result.stdout.lower():
                    logging.info(f"LD Player instance {device_name} successfully started after {i+1} attempts")
                    if self.is_arrange_ld:
                        subprocess.run([self.ldconsole_path, "sortWnd"], timeout=30)
                    return True
                    
            logging.error(f"Failed to start LD Player instance {device_name} after {max_retries} attempts")
            return False
            
        except Exception as e:
            logging.error(f"Error launching LD Player instance {device_name}: {str(e)}")
            return False
    
    def batch_close_instances(self, device_names: List[str]) -> Dict[str, bool]:
        """Close multiple LD Player instances in parallel."""
        futures = {}
        
        for device_name in device_names:
            future = self._executor.submit(self._close_single_instance, device_name)
            futures[device_name] = future
        
        results = {}
        for device_name, future in futures.items():
            try:
                results[device_name] = future.result(timeout=60)
            except Exception as e:
                logging.error(f"Failed to close {device_name}: {e}")
                results[device_name] = False
        
        return results
    
    def _close_single_instance(self, device_name: str) -> bool:
        """Close a single LD Player instance."""
        try:
            logging.info(f"Closing LD Player instance: {device_name}")
            
            # Graceful quit
            quit_cmd = [self.ldconsole_path, "quit", "--name", device_name]
            subprocess.run(quit_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            time.sleep(3)
            
            # Verify closure
            check_cmd = [self.ldconsole_path, "isrunning", "--name", device_name]
            result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            
            if "not running" in result.stdout.lower() or "running" not in result.stdout.lower():
                logging.info(f"LD Player instance {device_name} successfully closed")
                return True
            else:
                logging.warning(f"Graceful quit failed for {device_name}, attempting force quit")
                force_cmd = [self.ldconsole_path, "quit", "--name", device_name, "--force"]
                subprocess.run(force_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                return True
                
        except Exception as e:
            logging.error(f"Error closing LD Player instance {device_name}: {str(e)}")
            return False

def optimized_process_task_worker(pause_control_callback, task_dict, ld_player_path, adb_path, resume_event, is_arrange_ld=False):
    """Optimized worker process function with better resource management."""
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
    logger = logging.getLogger("optimized_process_task_worker")

    # Extract task information
    device_name = task_dict["device_name"]
    id_name = task_dict["id_name"]
    id_information_idx = task_dict["id_information_idx"]
    main_file_path = task_dict["local_output_file_path"]
    upload_method = task_dict["upload_method"]
    serial = task_dict["serial"]
    inner_task_list = task_dict.get("task_list", [])

    logger.info(f"Processing task for device: {device_name}, ID: {id_name}, Serial: {serial}, Method: {upload_method}")

    # Initialize managers
    adb_pool = ADBConnectionPool(adb_path)
    ld_manager = LDPlayerManager(ld_player_path, is_arrange_ld)

    try:
        # Launch LD Player instance
        success = ld_manager._launch_single_instance(device_name)
        if not success:
            logger.error(f"Failed to open LD Player instance {device_name}. Skipping tasks.")
            return

        # Wait for ADB connection with optimized checking
        if not _wait_for_adb_connection(adb_pool, serial, timeout=180):
            logger.error(f"Failed to establish ADB connection for {serial}")
            return

        # Process tasks with parallel preparation
        for task_count, task in enumerate(inner_task_list, 1):
            # Wait for resume signal before processing each task
            logger.info(f"Waiting for resume signal before task #{task_count}")
            resume_event.wait()
            
            logger.info(f"Executing task #{task_count}/{len(inner_task_list)} on {device_name}")
            
            # Process based on upload method
            if upload_method == "Without Apps Switch":
                process_without_app_switch_methods(
                    task=task, device_name=device_name, serial=serial, 
                    main_file_path=main_file_path, pause_control_callback=pause_control_callback, 
                    id_name=id_name, task_count=task_count, id_information_idx=id_information_idx
                )
            else:
                process_with_app_switch_methods(
                    task=task, device_name=device_name, serial=serial, 
                    main_file_path=main_file_path, pause_control_callback=pause_control_callback, 
                    id_name=id_name, task_count=task_count, id_information_idx=id_information_idx
                )

            # Inter-task delay with optimization
            delay_time = _get_optimized_delay()
            logger.info(f"Waiting {delay_time} seconds before next task")
            time.sleep(delay_time)

        logger.info(f"All tasks ({len(inner_task_list)}) completed for {device_name}")

    except Exception as e:
        logger.error(f"Critical error in task processing for {device_name}: {str(e)}")
    finally:
        # Close LD Player instance
        if not ld_manager._close_single_instance(device_name):
            logger.warning(f"Failed to close LD Player instance {device_name} properly")

def _wait_for_adb_connection(adb_pool: ADBConnectionPool, serial: str, timeout: int = 180) -> bool:
    """Wait for ADB connection with optimized checking."""
    start_time = time.time()
    check_interval = 2
    
    while time.time() - start_time < timeout:
        if adb_pool._check_single_device(serial):
            return True
        time.sleep(check_interval)
        # Increase check interval progressively to reduce CPU usage
        check_interval = min(check_interval * 1.1, 10)
    
    return False

def _get_optimized_delay() -> int:
    """Get optimized delay time with fallback."""
    try:
        from geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten
        device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")
        return device_settings.flatten_json().get("reels_uploading Delay", 20)  # Reduced default
    except Exception:
        return 20  # Reduced default delay

class LDTaskExecutor:
    """Highly optimized LD Task Executor with advanced parallel processing."""
    
    def __init__(self, main_queue, max_instances=4, ld_player_path=None, instance_delay=2, is_arrange_ld=False):
        """Initialize the OptimizedLDTaskExecutor."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("optimized_ld_executor.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("OptimizedLDTaskExecutor")  

        self.main_queue = main_queue
        self.adb_path = r"platform-tools\adb.exe"
        self.max_instances = max_instances
        self.instance_delay = max(1, instance_delay)  # Minimum delay of 1 second
        self.is_arrange_ld = is_arrange_ld 
        self.stop_event = multiprocessing.Event() 
        self.active_instances = {}  
        self.lock = multiprocessing.Lock()
        self.resume_event = multiprocessing.Event()
        self.manager = Manager()
        self.control_pause = self.manager.Event()
        self.control_pause.set()
        self.resume_event.set()

        # Initialize connection pool and LD manager
        self.adb_pool = ADBConnectionPool(self.adb_path)
        
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

        if self.ld_player_path:
            self.ld_manager = LDPlayerManager(self.ld_player_path, self.is_arrange_ld)
        
        # Process pool for better resource management
        self.process_pool = None
        self.task_futures = {}

    def pause(self):
        """Pause the executor."""
        self.resume_event.clear()
        self.control_pause.clear()
        self.logger.info("Executor paused.")

    def resume(self):
        """Resume the executor."""
        self.resume_event.set()
        self.control_pause.set()
        self.logger.info("Executor resumed.")

    def quit_all(self):
        """Quit all processing immediately."""
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
        if self.process_pool:
            self.process_pool.terminate()
            self.process_pool.join()
        
        for device_name in list(self.active_instances.keys()):
            proc = self.active_instances[device_name]["process"]
            self.logger.info(f"Force terminating process for device: {device_name}")
            proc.terminate()
            proc.join()
            del self.active_instances[device_name]
        
        # Force quit LD Player instances
        self._force_quit_ld_instances()
        self.logger.info("All processes force terminated.")

    def _force_quit_ld_instances(self):
        """Force quit all LD Player instances."""
        try:
            cmd = "taskkill /F /IM dnplayer.exe"
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            self.logger.info("Force quit LD Player instances")
        except Exception as e:
            self.logger.error(f"Error stopping LD instances: {e}")

    def _batch_start_processes(self, task_batch: List[Dict]) -> Dict[str, multiprocessing.Process]:
        """Start multiple processes in batch with staggered launch."""
        processes = {}
        
        for i, task_dict in enumerate(task_batch):
            device_name = task_dict["device_name"]
            
            if device_name in self.active_instances:
                self.logger.warning(f"Device {device_name} is already active. Skipping.")
                continue

            proc = multiprocessing.Process(
                target=optimized_process_task_worker,
                args=(self.control_pause, task_dict, self.ld_player_path, self.adb_path, self.resume_event, self.is_arrange_ld),
                name=f"OptimizedProcess-{device_name}"
            )
            
            processes[device_name] = proc
            
            # Staggered start to avoid resource contention
            if i > 0 and self.instance_delay > 0:
                time.sleep(self.instance_delay)

        # Start all processes
        for device_name, proc in processes.items():
            proc.start()
            self.logger.info(f"Started optimized process for device: {device_name}")
        
        return processes

    def run(self):
        """Run the optimized executor with advanced parallel processing."""
        self.logger.info(f"Starting OptimizedLDTaskExecutor with max {self.max_instances} simultaneous instances")
        self.logger.info(f"Main queue size: {self.main_queue.qsize()}")
        self.logger.info(f"LD Player path: {self.ld_player_path}")

        while not self.stop_event.is_set() and not (self.main_queue.empty() and len(self.active_instances) == 0):
            with self.lock:
                # Collect batch of tasks to start
                task_batch = []
                while len(self.active_instances) + len(task_batch) < self.max_instances and not self.main_queue.empty():
                    try:
                        task_dict = self.main_queue.get(block=False)
                        task_batch.append(task_dict)
                    except queue.Empty:
                        break
                
                # Start processes in batch
                if task_batch:
                    new_processes = self._batch_start_processes(task_batch)
                    
                    for device_name, proc in new_processes.items():
                        task_dict = next(t for t in task_batch if t["device_name"] == device_name)
                        self.active_instances[device_name] = {
                            "process": proc,
                            "start_time": time.time(),
                            "id_name": task_dict["id_name"]
                        }

            # Monitor and cleanup active instances
            completed_devices = []
            for device_name, proc_info in self.active_instances.items():
                proc = proc_info["process"]
                if not proc.is_alive():
                    proc.join()
                    completed_devices.append(device_name)
                    self.main_queue.task_done()
                elif time.time() - proc_info["start_time"] > 3600:  # 1 hour timeout
                    self.logger.warning(f"Process for {device_name} exceeded timeout. Terminating.")
                    proc.terminate()
                    proc.join()
                    completed_devices.append(device_name)
                    self.main_queue.task_done()
            
            # Remove completed processes
            for device_name in completed_devices:
                del self.active_instances[device_name]
                self.logger.info(f"Process for {device_name} completed and removed from active instances.")

            self.logger.info(f"Status: {len(self.active_instances)}/{self.max_instances} active instances, {self.main_queue.qsize()} tasks remaining")
            time.sleep(5)  # Reduced monitoring interval

        self.logger.info("Exiting optimized run loop.")

    def stop(self):
        """Stop all running processes gracefully."""
        self.logger.info("Stopping OptimizedLDTaskExecutor gracefully...")
        self.stop_event.set()
        
        # Clear pending tasks
        while not self.main_queue.empty():
            try:
                self.main_queue.get_nowait()
                self.main_queue.task_done()
            except queue.Empty:
                break
        
        # Stop active processes
        if hasattr(self, 'ld_manager') and self.ld_manager:
            device_names = list(self.active_instances.keys())
            if device_names:
                self.ld_manager.batch_close_instances(device_names)
        
        for device_name in list(self.active_instances.keys()):
            proc = self.active_instances[device_name]["process"]
            proc.terminate()
            proc.join()
            self.logger.info(f"Stopped process for device: {device_name}")
        
        self._force_quit_ld_instances()
        self.logger.info("All processes stopped gracefully.")


# Example usage with performance monitoring
if __name__ == "__main__":
    from task_collector import TaskCollector
    from multiprocessing import JoinableQueue
    import threading
    import time

    # Performance monitoring
    start_time = time.time()
    
    # Get tasks from TaskCollector
    collector = TaskCollector()
    raw_tasks_queue = collector.collect_tasks_from_json()

    # Convert tasks
    tasks_list = []
    while not raw_tasks_queue.empty():
        tasks_list.append(raw_tasks_queue.get())

    tasks_queue = JoinableQueue()
    for task in tasks_list:
        if "task_queue" in task:
            inner_list = []
            while not task["task_queue"].empty():
                inner_list.append(task["task_queue"].get())
            task["task_list"] = inner_list
            del task["task_queue"]
        tasks_queue.put(task)

    print(f"Task preparation completed in {time.time() - start_time:.2f} seconds")

    # Create optimized executor with higher concurrency
    executor = LDTaskExecutor(
        tasks_queue, 
        max_instances=min(4, multiprocessing.cpu_count()),  # Scale with CPU cores
        ld_player_path=collector.ld_player_path,
        instance_delay=1  # Reduced delay for faster startup
    )

    # Control function
    def control_actions():
        time.sleep(60)
        print("Pausing executor...")
        executor.pause()
        time.sleep(30)  # Reduced pause time
        print("Resuming executor...")
        executor.resume()

    # Start control thread
    control_thread = threading.Thread(target=control_actions, daemon=True)
    control_thread.start()

    # Run executor
    executor_start_time = time.time()
    executor.run()

    total_time = time.time() - start_time
    execution_time = time.time() - executor_start_time
    
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Task processing time: {execution_time:.2f} seconds")
    
    control_thread.join(timeout=1)