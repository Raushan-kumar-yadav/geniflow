import shutil
import logging
import queue
from concurrent.futures import ThreadPoolExecutor

import ctypes
import sys
import os
import threading
import time
import random
from lxml import etree
import xml.etree.ElementTree as ET

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from geni.geni_backend_src.copy_task_collector import CopyTaskCollector



class CopyTaskExecutor:
    def __init__(self, task_queue, max_workers=10):
        """
        Initialize the task executor with a task queue and a maximum number of concurrent workers.
        """
        self.task_queue = task_queue
        self.max_workers = max_workers
        self._setup_logger()
        
        # These events control pausing and quitting:
        self.pause_event = threading.Event()
        self.pause_event.set()  
        self.quit_event = threading.Event()

    def _setup_logger(self):
        """
        Set up logging for the executor.
        """
        self.logger = logging.getLogger("ReelsCopyTaskExecutor")
        self.logger.setLevel(logging.DEBUG)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def get_video_files(self, folder_path):
        """
        Returns a list of all video files found in the folder.
        """
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.webm', '.m4v')
        video_files = []
        try:
            for entry in sorted(os.listdir(folder_path)):
                full_path = os.path.join(folder_path, entry)
                if os.path.isfile(full_path) and entry.lower().endswith(video_extensions):
                    video_files.append(full_path)
        except Exception as e:
            self.logger.error(f"Error scanning folder '{folder_path}': {e}")
        return video_files

    def get_image_files(self, folder_path):
        """
        Returns a list of all image files found in the folder.
        """
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico')
        image_files = []
        try:
            for entry in sorted(os.listdir(folder_path)):
                full_path = os.path.join(folder_path, entry)
                if os.path.isfile(full_path) and entry.lower().endswith(image_extensions):
                    image_files.append(full_path)
        except Exception as e:
            self.logger.error(f"Error scanning folder '{folder_path}': {e}")
        return image_files

    def get_media_files(self, folder_path, content_type=None):
        """
        Returns a list of media files based on content type.
        If content_type is None or 'all', returns both images and videos.
        """
        if content_type is None or content_type.lower() == 'all':
            # Return both images and videos
            video_files = self.get_video_files(folder_path)
            image_files = self.get_image_files(folder_path)
            return sorted(video_files + image_files)
        elif content_type.lower() == 'video':
            return self.get_video_files(folder_path)
        elif content_type.lower() == 'image':
            return self.get_image_files(folder_path)
        else:
            self.logger.warning(f"Unknown content type '{content_type}'. Defaulting to videos only.")
            return self.get_video_files(folder_path)

    def prepared_task(self, tasks):
        """
        Process a file copy task.
        Each task consists of [source_path, destination_path, num_of_files, content_type].
        If num_of_files is provided, copy that many files; otherwise, copy only the first one.
        Content type specifies the type of media being processed ('video', 'image', or 'all').
        """
        for task in tasks: 
           
            if len(task) >= 4:
                source_path, destination_path, num_to_copy, content_type = task
            elif len(task) == 3:
                source_path, destination_path, num_to_copy = task
                content_type = None
            else:
                source_path, destination_path = task[:2]
                num_to_copy = 1
                content_type = None

            
            if not isinstance(num_to_copy, int) or num_to_copy <= 0:
                num_to_copy = 1

            # Get media files based on content type
            media_files = self.get_media_files(source_path, content_type)

            if not media_files:
                content_desc = content_type if content_type else "media"
                self.logger.warning(f"No {content_desc} files found in {source_path}")
                continue
            
            # Limit to requested number of files
            media_files = media_files[:num_to_copy]

            # Create destination directory if it doesn't exist
            os.makedirs(destination_path, exist_ok=True)

            # Copy each media file
            copied_count = 0
            for media_file in media_files:
                try:
                    dest_file = os.path.join(destination_path, os.path.basename(media_file))
                    
                    # Check if destination file already exists
                    if os.path.exists(dest_file):
                        # Generate unique filename if file exists
                        base_name, ext = os.path.splitext(os.path.basename(media_file))
                        counter = 1
                        while os.path.exists(dest_file):
                            dest_file = os.path.join(destination_path, f"{base_name}_{counter}{ext}")
                            counter += 1
                    
                    shutil.move(media_file, dest_file)
                    copied_count += 1
                    
                    # Determine file type for logging
                    file_type = self._get_file_type(media_file)
                    content_desc = content_type if content_type else file_type
                    
                    self.logger.info(f"{content_desc.capitalize()} copied successfully: {media_file} to {dest_file}")
                    
                except Exception as e:
                    self.logger.error(f"Error copying {media_file} to {destination_path}: {e}")

            # Log summary
            content_desc = content_type if content_type else "media files"
            self.logger.info(f"Copied {copied_count} of {num_to_copy} requested {content_desc} from {source_path} to {destination_path}")

    def _get_file_type(self, file_path):
        """
        Determine if a file is an image or video based on its extension.
        """
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.mpeg', '.webm', '.m4v')
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico')
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext in video_extensions:
            return "video"
        elif file_ext in image_extensions:
            return "image"
        else:
            return "media"

    def execute_tasks(self):
        """
        Execute tasks concurrently using ThreadPoolExecutor.
        New tasks are submitted only if not paused or quitting.
        """
        futures = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while not self.task_queue.empty():
                if self.quit_event.is_set():
                    self.logger.info("Quit signal received. No new tasks will be submitted.")
                    break
               
                self.pause_event.wait()
                try:
                    task = self.task_queue.get(block=False)
                except queue.Empty:
                    break
                futures.append(executor.submit(self.prepared_task, task))
            
            # Wait for all submitted tasks to complete
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Error in a task: {e}")


    def is_admin(self):
        """Check if the current program has admin permissions."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
        
    def run_as_admin(self):
        """Re-launch the program with admin privileges if not already running as admin."""
        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
        else:
            self.execute_tasks()

    # Pause/resume/quit methods:
    def pause(self):
        """Pause submitting new tasks."""
        self.pause_event.clear()
        self.logger.info("Executor paused.")

    def resume(self):
        """Resume submitting new tasks."""
        self.pause_event.set()
        self.logger.info("Executor resumed.")

    def quit(self):
        """
        Signal the executor to quit (stop submitting new tasks) while letting already submitted tasks complete.
        """
        self.quit_event.set()
        self.logger.info("Quit signal issued. No new tasks will be submitted.")

    def run(self):
        """
        Main run loop that executes tasks concurrently.
        Checks the quit event to stop submitting new tasks.
        """
        self.logger.info(f"Starting ReelsCopyTaskExecutor with max {self.max_workers} workers")
        self.logger.info(f"Task queue size: {self.task_queue.qsize()}")
        
        
        self.execute_tasks()
        self.logger.info("All tasks have been processed.")

    def stop(self):
        """
        Gracefully stop the executor by signaling quit and waiting for tasks to finish.
        """
        self.logger.info("Stopping executor gracefully...")
        self.quit() 
        
       
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
                self.task_queue.task_done()
            except queue.Empty:
                break
        
        self.logger.info("Executor stopped gracefully.")


if __name__ == "__main__":
    from geni.geni_backend_src.copy_task_collector import ReelsCopyTaskCollector
    from queue import Queue

    # Collect tasks using ReelsCopyTaskCollector
    collector = CopyTaskCollector()
    tasks = collector.collect_tasks_from_json_for_copy()  # this returns a Queue

    if tasks.empty():
        print("No task to copy")
        sys.exit(0)

    # Convert tasks into a standard Queue 
    if not isinstance(tasks, Queue):
        task_queue = Queue()
        for task in tasks:
            task_queue.put(task)
    else:
        task_queue = tasks

    executor = CopyTaskExecutor(task_queue, max_workers=10)

   
    def control_actions():
        time.sleep(2)
        print(">>> Pausing executor...")
        executor.pause()
        time.sleep(5)
        print(">>> Resuming executor...")
        executor.resume()
        time.sleep(10)
        print(">>> Issuing quit signal...")
        executor.quit()

    control_thread = threading.Thread(target=control_actions, daemon=True)
    control_thread.start()

    # Start the executor run loop (this call is blocking)
    executor.run()

    # Finally, perform a graceful stop
    executor.stop()