import multiprocessing
from multiprocessing import Manager
import time
import queue
import os
import logging
from datetime import datetime
import subprocess
from subprocess import CREATE_NO_WINDOW
import sys
import tempfile
import platform
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox, QSpinBox
)
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QPalette


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

from ldController.Ldcontroller_adb.LdAdb import LdAdbController

# Top-level worker function (must be picklable on Windows)
def process_task_worker(pause_control_callback, task_dict, ld_player_path, adb_path, resume_event, is_arrange_ld=False,activity_queue=None):
    # Specify your folder path
    log_folder = "log_folder"  # Use a valid path on your system
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, "ld_executor_worker.log")
    


    
    # Setup logger for the worker process
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("process_task_worker")

    device_name = task_dict.get("device_name", "")
    # Set default value for id_name if not present
    id_name = task_dict.get("id_name", "")
    id_information_idx = task_dict.get("id_information_idx", "")
    main_file_path = task_dict.get("local_output_file_path", "")
    page_manager_path = task_dict.get("page_manager_path", "")
    serial = task_dict.get("serial", "")
    inner_task_list = task_dict.get("task_list", [])


    activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Processing Task", "None","ds")
    

    logger.info(f"Processing task for device: {device_name}, ID: {id_name}, Serial: {serial}")

    def cheack_ld_instance_open_or_not(timeout=1000, target_serial=""):
        start_time = time.time()
        while True:
            result = subprocess.run([str(adb_path), "devices"], stdout=subprocess.PIPE, text=True,shell=True)
            output = result.stdout
            for line in output.splitlines():
                if target_serial in line:
                    if "device" in line and "offline" not in line:
                        print("emulator found")
                        return True
            if time.time() - start_time >= timeout:
                print("unable to find emulator")
                return False
            time.sleep(1)

    def open_ld_player(device_name):
        if not ld_player_path:
            logger.error("LD Player path is not set. Cannot open instance.")
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Opening LD", "Error","s")
            return False
        
        try:
            # Debug: Check if ld_player_path exists
            logger.info(f"LD Player path: {ld_player_path}")
            if not os.path.exists(ld_player_path):
                logger.error(f"LD Player directory does not exist: {ld_player_path}")
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Directory Does Not Exist", "Error","s")
                return False
            
            ldconsole_path = os.path.join(ld_player_path, "ldconsole.exe")
            logger.info(f"Using ldconsole.exe at: {ldconsole_path}")
            
            if not os.path.exists(ldconsole_path):
                logger.error(f"ldconsole.exe not found at {ldconsole_path}")
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "ldconsole not found", "Error","s")
                return False
    
            # Debug: Check if the device exists
            list_cmd = f'"{ldconsole_path}" list2'
            logger.info(f"Checking if device exists: {list_cmd}")
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Checking LD", "None","ds")
            list_result = subprocess.run(list_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            logger.info(f"Device list output: {list_result.stdout}")
            logger.info(f"Device list errors: {list_result.stderr}")
            
            if device_name not in list_result.stdout:
                logger.error(f"Device '{device_name}' not found in LD Player instances")
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Ld Instance Not Found", "Error","s")
                return False
    
            check_cmd = f'"{ldconsole_path}" isrunning --name "{device_name}"'
            
         
            temp_main_folder = tempfile.mkdtemp(prefix="geni_flow_window_ui_dump__")

            try:
             
                if not serial:
                    logger.error(f"Could not get serial for device: {device_name}")
                    activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "LD Error Getting LD serial", "Error","s")
                    return False
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Setting LD Config", "None","ds")
                ld_adb = LdAdbController(device_serial=serial, local_output_file_path=temp_main_folder)
                ld_adb.set_ld_prop_in_info_fetcher(ld_name=device_name)
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "LD Config Done", "None","ds")
                
            except Exception as e:
                logger.error(f"Error setting up LdAdbController: {str(e)}")
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Error setting up LD config", "Error","ds")
                # Continue without it if not critical
            
            launch_cmd = f'"{ldconsole_path}" launch --name "{device_name}"'
            logger.info(f"Executing launch command: {launch_cmd}")
            
            # Debug: Test the command first
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Starting LD", "None","ds")
            test_result = subprocess.run(launch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            logger.info(f"Launch command stdout: {test_result.stdout}")
            logger.info(f"Launch command stderr: {test_result.stderr}")
            logger.info(f"Launch command return code: {test_result.returncode}")
            
            if test_result.returncode != 0:
                logger.error(f"Launch command failed with return code: {test_result.returncode}")
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Error Opening LD", "Error","ds")
                return False
            
            # Use subprocess.run instead of Popen for better error handling
            process = subprocess.Popen(launch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Waiting to initialize LD", "None","ds")
            max_retries = 20
            for i in range(max_retries):
                logger.info(f"Waiting for {device_name} to initialize... ({i+1}/{max_retries})")
                time.sleep(5)
                
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    logger.warning(f"LD Player process for {device_name} terminated with code {process.returncode}")
                

                check_result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
                output = check_result.stdout.strip().lower()
                logger.info(f"Check output after launch attempt: {output}")
                
                if check_result.returncode != 0:
                    logger.warning(f"Check command failed: {check_result.stderr}")
                
                if "running" in output:
                    logger.info(f"LD Player instance {device_name} successfully started")
                    activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "LD Successfully Started", "None","ds")
                    if is_arrange_ld:
                        try:
                            subprocess.run([ldconsole_path, "sortWnd"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
                        except subprocess.CalledProcessError as e:
                            logger.warning(f"Failed to arrange windows: {e}")
                    time.sleep(1)
                    return True
                    
            logger.error(f"Failed to start LD Player instance {device_name} after {max_retries} attempts")
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Failed to start LD ", "Error","ds")
            return False
            
        except FileNotFoundError as e:
            logger.error(f"File not found error: {str(e)}")
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Ld File not found", "Error","ds")
            logger.error("This usually means ldconsole.exe path is incorrect or the executable doesn't exist")
            delete_callback(activity_queue,device_name)
            return False
        except Exception as e:
            logger.error(f"Error opening LD Player instance {device_name}: {str(e)}")
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Error opening LD", "Error","ds")
            delete_callback(activity_queue,device_name)
            logger.error(f"Exception type: {type(e).__name__}")
            return False
        

    def close_ld_player(device_name):
        if not ld_player_path:
            logger.error("LD Player path is not set. Cannot close instance.")
            return False
        try:
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Closing LD", "None","ds")
            delete_callback(activity_queue,device_name)
            ldconsole_path = os.path.join(ld_player_path, "ldconsole.exe")
            logger.info(f"Closing LD Player instance: {device_name}")
            quit_cmd = f'"{ldconsole_path}" quit --name "{device_name}"'
            logger.info(f"Executing quit command: {quit_cmd}")
            subprocess.run(quit_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30, shell=True)
            time.sleep(5)
            check_cmd = f'"{ldconsole_path}" isrunning --name "{device_name}"'
            result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
            logger.info(f"Post-quit check output: {result.stdout.strip()}")
            if "not running" in result.stdout.lower() or "running" not in result.stdout.lower():
                logger.info(f"LD Player instance {device_name} successfully closed")
                return True
            else:
                logger.warning(f"Normal quit failed for {device_name}, forcing quit.")
                force_cmd = f'"{ldconsole_path}" killall'
                subprocess.run(force_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                return True
        except Exception as e:
            logger.error(f"Error closing LD Player instance {device_name}: {str(e)}")
            return False

    try:
        success = False
        for attempt in range(3):
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Opening LD", "None","ds")
            logger.info(f"Attempt {attempt+1}/3 to open LD Player instance {device_name}")
            success = open_ld_player(device_name) and cheack_ld_instance_open_or_not(target_serial=serial)
            if success:
                break
            time.sleep(5)
        if not success:
            logger.error(f"Failed to open LD Player instance {device_name} after multiple attempts. Skipping tasks.")
            return

        task_count = 0
        temp_main_folder = tempfile.mkdtemp(prefix="geni_flow_window_ui_dump_")


        from geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten
        device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")
        time_to_wait = device_settings.flatten_json().get("before_any_task_delay", 30)
        is_vpn_check_enable=device_settings.flatten_json().get("check_vpn_connnection", False)

        if is_vpn_check_enable:
            activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Checking VPN Connection ", "None","ds")
            from ldController.Ldcontroller_adb.LdAdb import VPNMonitor
            vpn_monitor = VPNMonitor(device_id=serial,timeout=time_to_wait,local_output_file_path=temp_main_folder,pause_callback=pause_control_callback)
            is_vpn_connected = vpn_monitor.main()
            if not is_vpn_connected:
                if close_ld_player(device_name):
                    activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Closing LD due to VPN issue", "Error","ds")
                    logger.warning(f"closing LD Player instance due to VPN issue on  #{device_name}")
                else:
                    logger.warning(f"Failed to close LD Player instance {device_name} properly")
                return False
        else:
            time.sleep(time_to_wait)


        for task in inner_task_list:
            # Before executing a task, wait until resume_event is set.
            resume_event.wait()
            task_count += 1
            logger.info(f"Executing task #{task_count} on {device_name}")
            
         
            if "profile_fetch_task" in task:
                try:
           
                    profile_fetch_args = task.get("profile_fetch_task_argumanet", {})

                    package_name = profile_fetch_args.get("app_package", "")
                    
                    if not package_name:
                        logger.warning(f"No app_package specified for task on {device_name}")
                        continue

                   
                    try:
                        activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Processing Info Fetcher", "None","ds")
                        from ldController.Ldcontroller_adb.info_fetcher.info_fetcher import IdAndPageInfoFetcher

                        info_fetcher = IdAndPageInfoFetcher(
                            control_pasue_callback=pause_control_callback,
                            device_name=device_name,
                            device_serial=serial,
                            local_output_file_path=temp_main_folder,
                            activity_queue=activity_queue)

                        info_fetcher.save_profile_info(package_name=package_name, ld_name=device_name)
                        activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Fetchin Done", "None","ds")
                        logger.info(f"Task #{task_count} completed on {device_name}")
                        delete_callback(activity_queue,device_name)
                    except ImportError as ie:
                        logger.error(f"Import error: {str(ie)}. Check if the ldController module is in the Python path.")
                        activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Fetchin Error", "Error","s")
                        delete_callback(activity_queue,device_name)
                except Exception as e:
                    logger.error(f"Error executing profile fetch task on {device_name}: {str(e)}")
                    activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Fetchin Error", f"Error{e}","s")
            else:
                logger.warning(f"Unrecognized task type on {device_name}: {task}")
                activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Unrecognized Task Error", f"Error","s")
                

        time_to_quit = 0.5
        time.sleep(time_to_quit)

        logger.info(f"All tasks ({task_count}) completed for {device_name}")

        if not close_ld_player(device_name):
            logger.warning(f"Failed to close LD Player instance {device_name} properly")
            delete_callback(activity_queue,device_name)
    except Exception as e:
        logger.error(f"Error in task processing for {device_name}: {str(e)}")
        activity_callback(activity_queue, device_name, "Geni", 
                         id_name, "Fetchin Error", f"Error{e}","s")
        delete_callback(activity_queue,device_name)


class ProfileInfoFatcher:
    def __init__(self, main_queue, max_instances=1, ld_player_path=None, instance_delay=0.5, is_arrange_ld=False,main_win_ref=None,is_sleep_on = False ,activity_queue=None):
        """
        Initialize the ProfileInfoFatcher.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("ld_executor.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("ProfileInfoFatcher")  
        self.main_win_ref = main_win_ref
        self.main_queue = main_queue
        self.is_sleep_on = is_sleep_on
        self.activity_queue = activity_queue
        self.adb_path = r"platform-tools\adb.exe"
        self.max_instances = max_instances
        self.instance_delay = instance_delay 
        self.is_arrange_ld = is_arrange_ld 
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
        #self.main_win_ref.add_page_manager_page_row()
        #self.main_win_ref.add_auto_upload_page_row()
        #self.main_win_ref.add_id_active_page_row()
        for device_name in list(self.active_instances.keys()):
            proc = self.active_instances[device_name]["process"]
            d_name = self.active_instances[device_name]["device_name"]

            activity_callback(self.activity_queue, d_name, "Geni", 
                         "", "paused", "None","ds")
        self.logger.info("Executor paused.")

    def resume(self):
        """Resume the executor."""
        self.resume_event.set()
        self.control_pause.set()
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
        self.logger.info(f"Starting ProfileInfoFatcher with max {self.max_instances} simultaneous instances")
        self.logger.info(f"Main queue size: {self.main_queue.qsize()}")
        self.logger.info(f"LD Player path: {self.ld_player_path}")

        while not self.stop_event.is_set() and not (self.main_queue.empty() and len(self.active_instances) == 0):
            with self.lock:
                while len(self.active_instances) < self.max_instances and not self.main_queue.empty():
                    try:
                        task_dict = self.main_queue.get(block=False)
                        device_name = task_dict["device_name"]

                        if device_name in self.active_instances:
                            self.logger.warning(f"Device {device_name} is already active. Skipping duplicate task.")
                            self.main_queue.task_done()
                            continue

                        # Fixed: Ensure id_name exists to prevent KeyError
                        if "id_name" not in task_dict:
                            task_dict["id_name"] = ""  # Set default value
                        
                        proc = multiprocessing.Process(
                            target=process_task_worker,
                            args=(self.control_pause, task_dict, self.ld_player_path, self.adb_path, 
                                  self.resume_event, self.is_arrange_ld,self.activity_queue),
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
                        activity_callback(self.activity_queue, device_name, "Geni", 
                         "", "Fetchin Error", f"Error{e}","s")
                        delete_callback(self.activity_queue, device_name)
                        import traceback
                        self.logger.error(traceback.format_exc())

            # Monitoring and cleanup of active instances...
            for device_name in list(self.active_instances.keys()):
                proc_info = self.active_instances[device_name]
                proc = proc_info["process"]
                if not proc.is_alive():
                    proc.join()
                    self.logger.info(f"Process for {device_name} has completed. Removing from active instances.")
                    del self.active_instances[device_name]
                    self.main_queue.task_done()
                elif time.time() - proc_info["start_time"] > 3600:
                    self.logger.warning(f"Process for {device_name} has been running for over an hour. Forcing close.")
                    proc.terminate()
                    proc.join()
                    del self.active_instances[device_name]
                    self.main_queue.task_done()

            self.logger.info(f"Status: {len(self.active_instances)}/{self.max_instances} active instances, {self.main_queue.qsize()} tasks remaining")
            time.sleep(10)


        if self.is_sleep_on:
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
    executor = ProfileInfoFatcher(tasks_queue, max_instances=2, ld_player_path=collector.ld_player_path)

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