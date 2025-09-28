import sys
import os
import queue
import multiprocessing
import time
from multiprocessing import Queue, Pool, Manager, Event, Process
import logging
import threading
from datetime import datetime

import asyncio  

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


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from geni_backend_src.downloader_task_collector import DownloaderTaskCollector
from geni.Downloaders.all_platform_shorts_downloader.UnifiedSocialMediaDownloader import UnifiedSocialMediaDownloader

class VideoDownloaderTaskManager:
    """
    A class to manage concurrent video downloading tasks using multiple Chrome instances.
    """
    
    def __init__(self, max_concurrent_tasks=6, log_file="download_tasks.log", external_queue=None,activity_queue = None):
        """
        Initialize the task manager.
        """
        self.max_concurrent_tasks = max_concurrent_tasks
        self._paused = False   # When True, no new tasks will be spawned.
        self._stopped = False  # When True, the manager will stop processing and cleanup.
        
        self.setup_logging(log_file)
        
        self.logger = logging.getLogger("task_processor")
        self.logger.setLevel(logging.DEBUG)  
        
        self.manager = Manager()
        
        self.activity_queue = activity_queue
        # Set up task queue.
        if external_queue is not None:
            self.task_queue = external_queue
        else:
            self.task_queue = self.manager.Queue()
            
        self.result_queue = self.manager.Queue()

        # Create shared events using the Manager.
        self.control_pause = self.manager.Event()
        self.control_pause.set() 

        self.control_quit = self.manager.Event()
        self.control_quit.clear()
        
        self._start_lock = threading.Lock()
        
        self.active_processes = {}
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.total_tasks = 0
        
        # Store tasks for debugging.
        self.tasks_list = []
    
    def setup_logging(self, log_file):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.DEBUG,  
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def count_tasks(self):
        """Count the number of tasks in the queue and store them for debugging."""
        self.tasks_list = []
        task_count = 0
        temp_queue = self.manager.Queue()
        
        while not self.task_queue.empty():
            try:
                task = self.task_queue.get(block=False)
                self.tasks_list.append(task)
                temp_queue.put(task)
                task_count += 1
                self.logger.debug(f"Found task {task_count} in queue")
            except queue.Empty:
                break
        
        for task in self.tasks_list:
            self.task_queue.put(task)
        
        self.total_tasks = task_count
        self.logger.info(f"Total tasks in queue: {task_count}")
        return task_count
    
    @staticmethod
    def worker_process(control_quit_callback, control_pause_callback, task_data, result_queue, worker_id,activity_queue):
        """
        Static method to be run in a separate process for downloading videos.
        """
        # Configure worker-specific logger.
        logger = logging.getLogger(f"worker_{worker_id}")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        downloader_instance = None
        try:
            logger.info(f"Worker {worker_id} starting task with PID {os.getpid()}")
            download_config_profile_list = task_data
            

            base_user_data_dir, profile_dir, excelpath,proc_identifier = download_config_profile_list[0][0]
            profile_config = download_config_profile_list[1]

            activity_callback(activity_queue, proc_identifier, "Geni", "", "Getting Download Config", "None","ds")
            
            
            
  
            logger.info(f"Worker {worker_id} creating Chrome instance with data dir: {base_user_data_dir}")
            
            # Create and run the downloader instance.
            downloader_instance = UnifiedSocialMediaDownloader(
                control_quit_callback=control_quit_callback,
                control_pause_callback=control_pause_callback,
                base_user_data_dir=base_user_data_dir,
                profile_dir=profile_dir,
                excelpath=excelpath,
                proc_identifier=proc_identifier,
                activity_queue=activity_queue

            )
            
            logger.info(f"Worker {worker_id} initialized downloader, starting download process")
            activity_callback(activity_queue, proc_identifier, "Geni", "", "Opening Browser", "None","ds")
            
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(downloader_instance.__ainit__())  # Await async init
            result = loop.run_until_complete(downloader_instance.process_multiple_profiles(download_config_profile_list=profile_config))
            
            activity_callback(activity_queue, proc_identifier, "Geni", "", "completed Download task successfully", "None","s")
            logger.info(f"Worker {worker_id} completed task successfully")
            result_queue.put((worker_id, result, True))
            
        except Exception as e:
            activity_callback(activity_queue, proc_identifier, "Geni", "", "completed Download task ", f"Error:{e}","s")
            logger.error(f"Worker {worker_id} encountered error: {str(e)}", exc_info=True)
            result_queue.put((worker_id, str(e), False))
        finally:
            if downloader_instance:
                try:
                    # Fixed: Run async close_browser in the event loop
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(downloader_instance.close_browser())
                    delete_callback(activity_queue, proc_identifier)
                except:
                    pass
    
    def force_start_all_processes(self):
        """Force start processes for all tasks at once."""
        self.count_tasks() 
        self.logger.info(f"Force starting {min(self.max_concurrent_tasks, self.total_tasks)} processes")
        
        for i in range(min(self.max_concurrent_tasks, self.total_tasks)):
            if i < len(self.tasks_list):
                worker_id = f"worker_{i}"
                task = self.tasks_list[i]
                try:
                    _ = self.task_queue.get_nowait()
                except queue.Empty:
                    self.logger.warning(f"Queue empty when trying to start process {i}")
                    continue
                
                self.logger.info(f"Starting {worker_id} with task: {task}")
                
                process = Process(
                    target=VideoDownloaderTaskManager.worker_process,
                    args=(self.control_quit, self.control_pause, task, self.result_queue, worker_id,self.activity_queue),
                    daemon=False
                )
                process.start()
                self.active_processes[worker_id] = process
                self.logger.info(f"Started process {worker_id} (PID: {process.pid})")
                time.sleep(1.5)
        
        self.logger.info(f"Started {len(self.active_processes)} processes")
    
    def start_new_process(self):
        """Start a new worker process if tasks are available."""
        with self._start_lock:
            try:
                task = self.task_queue.get(block=True, timeout=0.2)
            except (queue.Empty, Exception) as e:
                self.logger.debug(f"No task available: {e}")
                return False

            worker_id = f"worker_{len(self.active_processes)}"
            self.logger.info(f"Starting {worker_id}")
            process = Process(
                target=VideoDownloaderTaskManager.worker_process,
                args=(self.control_quit, self.control_pause, task, self.result_queue, worker_id,self.activity_queue),
                daemon=False  
            )
            process.start()
            self.active_processes[worker_id] = process
            self.logger.info(f"Started process {worker_id} (PID: {process.pid})")
            time.sleep(1.5)
            return True
    
    def check_completed_processes(self):
        """Check for and handle completed processes."""
        try:
            worker_id, result, success = self.result_queue.get(timeout=0.5)
            if worker_id in self.active_processes:
                process = self.active_processes[worker_id]
                process.join(timeout=5)
                if process.is_alive():
                    self.logger.warning(f"Process {worker_id} not responding, terminating")
                    process.terminate()
                del self.active_processes[worker_id]
                if success:
                    self.completed_tasks += 1
                    self.logger.info(f"Task completed: {worker_id}, {self.completed_tasks}/{self.total_tasks} done")
                else:
                    self.failed_tasks += 1
                    self.logger.error(f"Task failed: {worker_id}, error: {result}")
            return True
        except queue.Empty:
            return False
    
    def check_dead_processes(self):
        """Check for and handle processes that died unexpectedly."""
        for worker_id, process in list(self.active_processes.items()):
            if not process.is_alive():
                self.logger.warning(f"Process {worker_id} died unexpectedly")
                process.join(0)
                del self.active_processes[worker_id]
                self.failed_tasks += 1
    
    def cleanup(self):
        """Clean up all active processes."""
        for worker_id, process in list(self.active_processes.items()):
            self.logger.info(f"Shutting down process {worker_id}")
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
    
    def pause(self):
        """Pause the manager so that no new tasks will be spawned."""
        self._paused = True
        self.control_pause.clear()
        self.logger.info("VideoDownloaderTaskManager paused. No new tasks will be spawned until resumed.")
    
    def resume(self):
        """Resume the manager to allow new tasks to be spawned."""
        self._paused = False
        self.control_pause.set()
        self.logger.info("VideoDownloaderTaskManager resumed. New tasks will be spawned.")
    
    def quit(self):
        """Quit the manager gracefully by setting the stop flag and cleaning up active processes."""
        self.control_quit.set()
        self.control_pause.set() 
        self._stopped = True
        self.logger.info("Quit requested. Terminating all active processes and stopping the manager.")
        time.sleep(10)
    
    def run(self):
        """Run the task manager with forced start of multiple processes."""
        self.count_tasks()
        self.logger.info(f"Initialized task manager with {self.total_tasks} tasks, running {self.max_concurrent_tasks} concurrent tasks")
        
        try:
            
            
            while (self.completed_tasks + self.failed_tasks) < self.total_tasks:
                if self._stopped:
                    self.logger.info("Stop flag set. Exiting run loop.")
                    break
                
                if self._paused:
                    self.logger.info("Manager is paused. Waiting to resume...")
                    time.sleep(1)
                    continue
                
                if len(self.active_processes) < self.max_concurrent_tasks:
                    self.start_new_process()
                
                self.check_completed_processes()
                self.check_dead_processes()
                
                self.logger.info(f"Status: Active={len(self.active_processes)}, Completed={self.completed_tasks}, Failed={self.failed_tasks}, Total={self.total_tasks}")
                time.sleep(5)
            
            self.logger.info(f"Task manager complete. Processed {self.completed_tasks}/{self.total_tasks} tasks. Failed: {self.failed_tasks}")
        
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, shutting down workers")
        
        finally:
            self.cleanup()


def prepare_task(quit_event, pause_event, result_queue):
    """
    Worker function that runs in a separate process using the VideoDownloaderTaskManager
    """
    try:
        # Configuration structure:
        # [
        #     [(chrome_user_data_dir, profile_dir, excel_path)],
        #     [
        #         (user_id, platform_name, no_of_items, save_path, content_type),
        #         ...
        #     ]
        # ]
        download_config_profile_list = [
            [(r"E:\facebook_ld_player\LDPlayer0\chrome", r"p", r"E:\facebook_ld_player\LDPlayer0\chrome\reels_history.xlsx")],

            [   ('jaysmedia6410', 'pinterest', 5, r'E:\facebook_ld\ld_player0\Kajal Kumari\Kajal Kumari_download_img', 'image')
            ]
        ]

        """                         ("InspiringLion", "youtube", 1, r"E:\downloads\car_shorts", "video"),
                ("HumansNoContext", "twitter", 1, r"E:\downloads\human_videos", "video"),
                ("memes_ka_hutiapa", "instagram", 1, r"E:\downloads\meme_reels", "reel"),
                ("NatGeo", "instagram", 1, r"E:\downloads\natgeo_images", "reel") """
        
        # Create task queue and add our single task
        manager = Manager()
        task_queue = manager.Queue()
        task_queue.put(download_config_profile_list)
        
        # Create task manager with the configured task
        task_manager = VideoDownloaderTaskManager(
            max_concurrent_tasks=1,  # Since we have only one task
            external_queue=task_queue
        )
        
        # Set the control events from the parent process
        task_manager.control_quit = quit_event
        task_manager.control_pause = pause_event
        
        # Run the task manager
        task_manager.run()
        
        # Send result back to main process
        result_queue.put(True)
        print("Download process completed successfully!")
            
    except Exception as e:
        print(f"Error in worker process: {e}")
        result_queue.put(False)


# Example usage
if __name__ == "__main__":
    # Set multiprocessing start method (important for cross-platform compatibility)
    if sys.platform.startswith('win'):
        multiprocessing.set_start_method('spawn', force=True)
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("main_process.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("main")
    
    # Create multiprocessing events and queue
    quit_event = multiprocessing.Event()
    pause_event = multiprocessing.Event()
    pause_event.set()  # Start in non-paused state
    result_queue = multiprocessing.Queue()
    
    # Create the main worker process
    main_process = Process(
        target=prepare_task, 
        args=(quit_event, pause_event, result_queue),
        daemon=True
    )
    
    try:
        logger.info("Starting download process...")
        # Start process
        main_process.start()
        
        # Wait for the main process to complete
        main_process.join()
        
        # Get the result from the worker process
        try:
            result = result_queue.get(timeout=5)  # 5 second timeout
            if result:
                logger.info("Download process completed successfully!")
            else:
                logger.error("Download process encountered an error.")
        except:
            logger.error("Could not retrieve result from worker process.")
        
        logger.info("All tasks have been completed.")
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user. Cleaning up...")
        quit_event.set()
        
        # Terminate process if it's still running
        if main_process.is_alive():
            main_process.terminate()
            main_process.join(timeout=5)
            if main_process.is_alive():
                main_process.kill()
        
        logger.info("Cleanup completed.")
    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        quit_event.set()
        
        # Cleanup on error
        if main_process.is_alive():
            main_process.terminate()
            main_process.join(timeout=5)
