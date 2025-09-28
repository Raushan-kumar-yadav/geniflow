import ctypes
import sys
import os
import time
import threading
import queue
import logging
import subprocess
from subprocess import CREATE_NO_WINDOW
from multiprocessing import JoinableQueue, Manager

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QDialog,
    QPushButton, QLabel, QScrollArea, QGridLayout, QMessageBox,QListView,QTableView,QHeaderView,QAbstractItemView,QAbstractItemView,QGroupBox)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, Slot,QStringListModel,QPropertyAnimation,Property
from PySide6.QtGui import QPixmap, QFont, QFontDatabase, QIcon,QStandardItemModel,QStandardItem
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QPixmap, QPainter, QIcon, QDesktopServices
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Append parent directory to sys.path so that the custom modules can be imported
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from geni_backend_src.start_activity_main import LDTaskExecutor
from geni_backend_src.task_collector import TaskCollector
from geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten
from geni_backend_src.downloader_task_collector import DownloaderTaskCollector
from geni_backend_src.start_download_activity import VideoDownloaderTaskManager
from geni.geni_backend_src.copy_task_collector import CopyTaskCollector
from geni.geni_backend_src.copy_task_executor import CopyTaskExecutor
from geni_backend_src.profiles_info_fetcher import ProfileInfoFatcher
from geni_ui_src.login_src.login_window import SerialCodeApp


class StyledFrame(QFrame):
    """
    A styled QFrame that mimics the appearance of CTkFrame.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.setStyleSheet("""
            StyledFrame {
                background-color: rgba(128,128,128,.1);
                border: 2px solid gray;
                border-radius: 8px;
            }
        """)


class CurrentActivity(StyledFrame):
    """
    A frame that displays the current activity table with dynamically
    resized columns.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_widgets()
        
    def _create_widgets(self):
        layout = QVBoxLayout(self)
        
        # Header label
        header = QLabel("Activity Info")
        header.setStyleSheet("font-size: 12pt; font-weight: bold; background-color: none;")
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Create table view
        self.current_activity_table_view = QTableView()
        self.current_activity_table_view.setObjectName("current_activity_table_view")
        self.current_activity_table_view.setAlternatingRowColors(True)
        
        # Configure table selection behavior
        self.current_activity_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.current_activity_table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Make table header visible and enable sorting
        self.current_activity_table_view.horizontalHeader().setVisible(True)
        self.current_activity_table_view.setSortingEnabled(True)
        
        # Add the table to layout
        layout.addWidget(self.current_activity_table_view)
        
        # Create and set the model
        headers = ["No", "LDName", "App", "Profile", "Current activity", "Others"]
        self.model = QStandardItemModel(0, len(headers), self)
        self.model.setHorizontalHeaderLabels(headers)
        
        # Set the model to the table view
        self.current_activity_table_view.setModel(self.model)
        
        # Add sample data rows
        self.add_row(["1", "LD1", "MyApp", "Default", "Running", "–"])
        self.add_row(["2", "LD2", "Browser", "Social", "Idle", "Not connected"])
        self.add_row(["3", "LD3", "Game", "Gaming", "Paused", "Waiting for input"])
        
        # Apply column resizing after adding data
        self.adjust_column_sizes()
    
    def add_row(self, data_list):
        """Add a new row to the activity table"""
        row = self.model.rowCount()
        self.model.insertRow(row)
        
        for col, text in enumerate(data_list):
            item = QStandardItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.model.setItem(row, col, item)
    
    def adjust_column_sizes(self):
        """
        Dynamically adjust column sizes based on content and importance
        """
        header = self.current_activity_table_view.horizontalHeader()
        
        # First resize all columns to their contents
        self.current_activity_table_view.resizeColumnsToContents()
        
        # Set specific resize behavior for each column
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # No column
        self.current_activity_table_view.setColumnWidth(0, 40)
        
        # LDName column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.current_activity_table_view.setColumnWidth(1, 80)
        
        # App column
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.current_activity_table_view.setColumnWidth(2, 100)
        
        # Profile column
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.current_activity_table_view.setColumnWidth(3, 100)
        
        # Current activity column (give it more space)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        # Others column
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)
        self.current_activity_table_view.setColumnWidth(5, 120)
        
        # Make sure the table uses all available horizontal space
        header.setStretchLastSection(False)
    
    def clear_table(self):
        """Clear all rows from the table, keeping the headers"""
        self.model.removeRows(0, self.model.rowCount())
    
    def update_table(self, data_list_of_lists):
        """Update the entire table with new data"""
        self.clear_table()
        for row_data in data_list_of_lists:
            self.add_row(row_data)
        self.adjust_column_sizes()

class ActivityControl(StyledFrame):
    # Signal to safely pause the UI from any thread
    pause_signal = Signal()
    show_about_dialog_signal = Signal()

    def __init__(self, parent=None,main_win_ref=None):
        super().__init__(parent)
        
        # Activity states: "stopped", "running", "paused"
        self.state = "stopped"
        # Activity types: "main", "fetch"
        self.current_activity_type = "main"
        self.main_queue = queue.Queue()
        self.start_time = 0
        self.main_win_ref = main_win_ref
        self.serial_code_verification = SerialCodeApp()
        
        self.elapsed_time = 0
        self.page_manager_path = r"User_Data\Page_manager.json"
        self.package_name = "com.facebook.katana"
        self.selected_ld_list = []

        # Load icons for play and pause buttons
        self.play_icon = QPixmap(r"geni\geni_ui_src\ui_assets\Icons\play.png").scaled(
            80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.pause_icon = QPixmap(r"geni\geni_ui_src\ui_assets\Icons\stop.png").scaled(
            80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        # Timer for updating elapsed time display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)  # Update every second
        
        # Event to signal stop/cancel of upcoming tasks
        self.stop_event = threading.Event()
        
        # Executors for the tasks
        self.video_downloader_task_manager = None
        self.reels_upload_task_executor = None
        self.reels_copy_task_executor = None
        self.profile_info_fetcher_task_manager = None
        # Connect our pause signal to the pause handler method
        self.pause_signal.connect(self.handle_pause_from_thread)
        self.show_about_dialog_signal.connect(self.show_about_box)
        
        self._create_widgets()

    def _create_widgets(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Activity Controls")
        header.setStyleSheet("font-size: 12pt; font-weight: bold;background-color:none;")
        layout.addWidget(header, alignment=Qt.AlignLeft)
        
        
        # Play/Pause Control 
        play_pause_frame = QGroupBox()
        play_pause_frame.setTitle("Play/Pause Controls")
        play_pause_frame.setObjectName("play_pause_frame")
        play_pause_frame.setStyleSheet("""QGroupBox#play_pause_frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#play_pause_frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        play_pause_layout = QHBoxLayout(play_pause_frame)
        
        # Play/Pause button section
        play_btn_widget = QWidget()
        play_btn_widget.setObjectName("play_btn_widget")
        play_btn_widget.setStyleSheet("""QWidget#play_btn_widget{background-color:transparent;}""")
        play_btn_layout = QHBoxLayout(play_btn_widget)
        
        # Current activity indicator label
        self.activity_type_label = QLabel("Main Activity")
        self.activity_type_label.setStyleSheet("background-color:none; font-weight:bold;")
        self.activity_type_label.setFixedWidth(100)
        play_btn_layout.addWidget(self.activity_type_label)
        
        self.play_pause_button = AnimatedHoverButton(text="")
        self.play_pause_button.setIcon(QIcon(self.play_icon))
        self.play_pause_button.setIconSize(QSize(80, 80))
        self.play_pause_button.setFixedSize(100, 100)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        play_btn_layout.addWidget(self.play_pause_button)
        
        play_pause_layout.addWidget(play_btn_widget)
        
        # Timer 
        timer_widget = QWidget()
        timer_widget.setStyleSheet("background-color:none")
        timer_widget.setObjectName("timer_widget")
        timer_layout = QHBoxLayout(timer_widget)
        
        timer_label = QLabel("Elapsed Time:")
        timer_label.setFixedWidth(100)
        timer_layout.addWidget(timer_label)
        
        # Load digital font if available
        font_id = QFontDatabase.addApplicationFont(r"geni\geni_ui_src\ui_assets\Icons\fonts\Digital Dismay.otf") 
        digital_font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"
        
        self.timer_display = QLabel("00:00:00")
        timer_font = QFont(digital_font_family, 50)
        self.timer_display.setFont(timer_font)
        self.timer_display.setStyleSheet("color: red;")
        timer_layout.addWidget(self.timer_display)
        
        play_pause_layout.addWidget(timer_widget)
        layout.addWidget(play_pause_frame)
        
        layout.setSpacing(15)

        # Quit All section
        quit_frame = QGroupBox()
        quit_frame.setObjectName("quit_frame")
        quit_frame.setTitle("Quit All")
        quit_frame.setStyleSheet("""QGroupBox#quit_frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#quit_frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        quit_layout = QHBoxLayout(quit_frame)
        
        quit_btn_layout = QHBoxLayout()
        
        quit_btn_label = QLabel("Quit All:")
        quit_btn_label.setStyleSheet("background-color:none")
        quit_btn_label.setFixedWidth(80)
        quit_btn_layout.addWidget(quit_btn_label)
        
        quit_button = AnimatedHoverButton(text="Quit All")
        quit_button.setFixedSize(100, 100)
        quit_button.clicked.connect(self.handle_quit)
        quit_btn_layout.addWidget(quit_button)
        
        quit_layout.addLayout(quit_btn_layout)
        quit_layout.addStretch()  # Add stretch to keep the button on the left
        
        layout.addWidget(quit_frame)
        layout.addStretch()  # Add stretch to keep the UI compact

    def verify_serial_and_start_activity(self):

        self.serial_code_verification.show_success_message = False
        self.serial_code_verification.run_complete_verification(self.start_activity,timer_callback=self.start_timer,show_err_callback=self.show_about_dialog_signal)
    


    def show_about_box(self):

        About = AboutDialog()
        About.exec()

    def handle_pause_from_thread(self):
        """Safely handle pause commands from worker threads"""
        if self.state == "running":
            logging.info("Auto-pause handled in main thread")
            self.pause_timer()
            self.state = "paused"
            logging.info("All tasks completed; timer paused.")
        else:
            logging.info("Auto-pause called but current state is: %s", self.state)

    def set_activity_type(self, activity_type):
        """
        Sets the current activity type and updates the UI accordingly.
        Only allows changing activity type when stopped.
        """
        if self.state != "stopped":
            QMessageBox.warning(
                self,
                "Warning!",
                f"Cannot change activity type while {self.state}. Please stop current activity first.",
                QMessageBox.Ok
            )
            return
        
        self.current_activity_type = activity_type
        if activity_type == "main":
            self.activity_type_label.setText("Main Activity")
            self.main_activity_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 128, 0, 0.5);
                    border: none;
                    border-radius: 8px;
                    padding: 3px;
                }
            """)
            self.fetch_activity_button.setStyleSheet("")
        else:  # fetch
            self.activity_type_label.setText("Fetch Activity")
            self.fetch_activity_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(0, 128, 0, 0.5);
                    border: none;
                    border-radius: 8px;
                    padding: 3px;
                }
            """)
            self.main_activity_button.setStyleSheet("")
        
        logging.info(f"Activity type set to: {activity_type}")

    def toggle_play_pause(self):
        """
        Handles the play/pause toggle button.
        Uses a state machine and launches appropriate activity based on current_activity_type.
        """
        if self.state == "stopped":
            # Clear any previous stop flag
            self.stop_event.clear()
    
            # Launch the appropriate activity based on the current activity type
            if self.current_activity_type == "main":
                threading.Thread(target=self.verify_serial_and_start_activity, daemon=True).start()
                logging.info("Starting Main Activity...")
                
            else:  # fetch
                threading.Thread(target=self.profile_info_fetch_task, daemon=True).start()
                logging.info("Starting Fetch Activity...")
                self.start_timer()
                self.state = "running"
                
        elif self.state == "running":
            self.pause_timer()
            self.pause_tasks()
            self.state = "paused"
        elif self.state == "paused":
            self.resume_tasks()
            self.state = "running"
            self.start_timer(resume=True)
        else:
            logging.warning("Unknown state encountered: %s", self.state)
            


        


    # The following methods remain the same as in the original class
    def start_timer(self, resume=False):
        if not resume:
            self.start_time = time.time()
            self.elapsed_time = 0
        else:
            self.start_time = time.time() - self.elapsed_time
        
        self.play_pause_button.setIcon(QIcon(self.pause_icon))
        self.timer.start()

    def pause_timer(self):
        self.timer.stop()
        self.elapsed_time = time.time() - self.start_time
        self.play_pause_button.setIcon(QIcon(self.play_icon))

    @Slot()
    def update_timer(self):
        if self.state == "running":
            self.elapsed_time = time.time() - self.start_time
            formatted_time = time.strftime("%H:%M:%S", time.gmtime(self.elapsed_time))
            self.timer_display.setText(formatted_time)

    def handle_quit(self):
        if self.state == "stopped":
            QMessageBox.warning(
                self,
                "Warning!",
                "No active tasks. Please start the tool first.",
                QMessageBox.Ok
            )
            return

        reply = QMessageBox.warning(
            self,
            "Confirm Quit",
            "Are you sure you want to quit all processes?",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Ok:
            # Signal stop so that upcoming tasks are cancelled
            self.stop_event.set()
            # Run the quit_all_task asynchronously
            threading.Thread(target=self._quit_all_task_async, daemon=True).start()
            self.reset_ui()
        else:
            logging.info("Quit cancelled by user.")

    def _quit_all_task_async(self):
        self.quit_all_task()
        # Use QTimer to call reset_ui from the main thread
        QTimer.singleShot(0, self.reset_ui)

    def reset_ui(self):
        self.state = "stopped"
        self.elapsed_time = 0
        self.timer_display.setText("00:00:00")
        self.play_pause_button.setIcon(QIcon(self.play_icon))
        self.stop_event.clear()

    def auto_pause(self):
        """
        Properly handles automatic pausing when tasks complete.
        Emits a signal to safely update UI from any thread.
        """
        # Emit signal to be handled in the main thread
        logging.info("Auto-pause triggered. Current state: %s", self.state)
        self.pause_signal.emit()


    def get_ld_list(self, ld_console_folder_path):

        ld_list = []
        try:
            cmd = [os.path.join(ld_console_folder_path, "ldconsole.exe"), "list2"]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT,creationflags=CREATE_NO_WINDOW)
            decoded_output = output.decode("utf-8")
        except subprocess.CalledProcessError as e:
            print("Error while getting the list of LDPlayer:", e)
            print("Error output:", e.output.decode())
            return None

        for line in decoded_output.splitlines():
            if ',' in line:
                parts = line.strip().split(',')
                if len(parts) >= 2:
                    ld_list.append([parts[0], parts[1]])
        return ld_list
    
    def ld_inst_adb_serial_by_name(self, ld_player_name):
        if not ld_player_name:
            print("No LD found")
            return None
        
        device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json").flatten_json()

        ld_instance_list = self.get_ld_list(device_settings["LD Location"]) 
        if not ld_instance_list:
            return None

        ld_instance_idx = None
        for ld in ld_instance_list:
            ld_idx, ld_name = ld
            if ld_player_name == ld_name:
                ld_instance_idx = int(ld_idx)
                break
        if ld_instance_idx is None:
            return None

        base_port = 5554  # Base port for emulator instances
        adb_serial = f"emulator-{base_port + ld_instance_idx * 2}"
        return adb_serial
    
    def build_queue_for_profile_fatch_task(self):

        logging.info(f"Building queue with {len(self.selected_ld_list)} selected LDs")
        for ld in self.selected_ld_list:
            inner_queue = queue.Queue()
            current_ld_serial = self.ld_inst_adb_serial_by_name(ld_player_name=ld)
            inner_queue.put({
                "profile_fetch_task": "profile_fetch_task",
                "profile_fetch_task_argumanet": {"app_package": self.package_name}
            })
            task_dict = {
                "serial": current_ld_serial,
                "device_name": ld,
                "page_manager_path": self.page_manager_path,
                "task_queue": inner_queue
            }
            self.main_queue.put(task_dict)
        logging.info(f"Main queue size after building: {self.main_queue.qsize()}")
        return self.main_queue
    

    def profile_info_fetch_task(self):

        try:
            device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json").flatten_json()
            raw_tasks_queue = self.build_queue_for_profile_fatch_task()

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
                    logging.info("Processed task: %s", task)
                tasks_queue.put(task)

            self.profile_info_fetcher_task_manager = ProfileInfoFatcher(main_queue=tasks_queue,max_instances=device_settings["Number of instance at a time"],ld_player_path=device_settings["LD Location"],is_arrange_ld=device_settings["Auto arrange ld player"],instance_delay=0.5,main_win_ref=self.main_win_ref)


            self.profile_info_fetcher_task_manager.run()
            logging.info("Profile Info Fatcher finished...")
            self.pause_signal.emit()
        except Exception as e: 
            logging.ERROR("Error in profile info fatcher",e)
            self.pause_signal.emit()

    def download_task(self):
        """
        Collects tasks and starts the video downloader manager.
        """
        try:
            device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json").flatten_json()
            task_queue_object = DownloaderTaskCollector()
            task_queue = task_queue_object.collect_tasks_from_json_for_download()

            manager = Manager()
            mp_task_queue = manager.Queue()
            task_count = 0

            while not task_queue.empty():
                try:
                    task = task_queue.get()
                    task_count += 1
                    mp_task_queue.put(task)
                except queue.Empty:
                    break

            self.video_downloader_task_manager = VideoDownloaderTaskManager(
                max_concurrent_tasks=device_settings["Number of chrome instance at a time"],
                external_queue=mp_task_queue
            )
            self.video_downloader_task_manager.run()
            logging.info("Downloaded %d tasks.", task_count)
        except Exception as e:
            logging.error("Error in download_task: %s", e)

    def reels_upload_task(self):
        """
        Collects tasks and starts the reels_upload executor.
        """
        try:
            device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json").flatten_json()
            collector = TaskCollector()
            raw_tasks_queue = collector.collect_tasks_from_json()  # returns a Queue

            tasks_list = []
            while not raw_tasks_queue.empty():
                tasks_list.append(raw_tasks_queue.get())
                print("tasks_list")
            tasks_queue = JoinableQueue()
            for task in tasks_list:
                if "task_queue" in task:
                    inner_list = []
                    while not task["task_queue"].empty():
                        inner_list.append(task["task_queue"].get())
                    task["task_list"] = inner_list
                    del task["task_queue"]
                    logging.info("Processed task: %s", task)
                tasks_queue.put(task)

            self.reels_upload_task_executor = LDTaskExecutor(
                tasks_queue,
                max_instances=device_settings["Number of instance at a time"],
                ld_player_path=collector.ld_player_path,
                instance_delay=device_settings["LD Opening Delay"],
                is_arrange_ld=device_settings["Auto arrange ld player"]
            )
            self.reels_upload_task_executor.run()
        except Exception as e:
            logging.error("Error in Task: %s", e)

    def bulk_reels_copy_task(self):
        """
        Collects tasks and starts the reels copy executor.
        """
        try:
            task_queue_obj = CopyTaskCollector()
            tasks = task_queue_obj.collect_tasks_from_json_for_copy()

            if tasks.empty():
                logging.warning("No task to copy")
                return

            # Ensure tasks are in a queue format.
            task_queue = tasks if isinstance(tasks, queue.Queue) else queue.Queue()
            if not isinstance(tasks, queue.Queue):
                for task in tasks:
                    task_queue.put(task)

            self.reels_copy_task_executor = CopyTaskExecutor(task_queue, max_workers=10)
            self.reels_copy_task_executor.run_as_admin()
        except Exception as e:
            logging.error("Error in bulk_reels_copy_task: %s", e)

    def start_activity(self):
        """
        Starts the main activity.
        Implementation depends on which type of task needs to be run.
        """
        logging.info("Starting main activity...")
        
        self.state = "running"
        try:
            self.download_task()

            if self.stop_event.is_set():
                logging.info("Main activity cancelled after download task.")
                return
            
            #self.bulk_reels_copy_task()
            if self.stop_event.is_set():
                logging.info("Main activity cancelled after bulk reels copy task.")
                return
            
            self.reels_upload_task()

            if self.stop_event.is_set():
                logging.info("Main activity cancelled.")
                return

            logging.info("All main activity tasks completed successfully!")

            # All tasks completed: emit the pause signal rather than calling auto_pause directly
            self.pause_signal.emit()

        except Exception as e:
            logging.error(f"Error in main activity: {e}")
            # Emit the pause signal rather than calling auto_pause directly
            self.pause_signal.emit()

    def pause_tasks(self):
        """
        Pauses all active executors by calling their respective pause methods.
        """
        logging.info("Pausing tasks...")
        if self.reels_upload_task_executor is not None:
            threading.Thread(target=self.reels_upload_task_executor.pause, daemon=True).start()
        else:
            logging.warning("No active reels_upload executor to pause.")

        if self.video_downloader_task_manager is not None:
            threading.Thread(target=self.video_downloader_task_manager.pause, daemon=True).start()
        else:
            logging.warning("No active video downloader executor to pause.")

        if self.reels_copy_task_executor is not None:
            threading.Thread(target=self.reels_copy_task_executor.pause, daemon=True).start()

        if self.profile_info_fetcher_task_manager is not None:
            threading.Thread(target=self.profile_info_fetcher_task_manager.pause, daemon=True).start()

        
        else:
            logging.warning("No active reels copy executor to pause.")

    def resume_tasks(self):
        """
        Resumes all paused executors by calling their respective resume methods.
        """
        logging.info("Resuming tasks...")
        if self.reels_upload_task_executor is not None:
            threading.Thread(target=self.reels_upload_task_executor.resume, daemon=True).start()
        else:
            logging.warning("No active reels_upload executor to resume.")

        if self.video_downloader_task_manager is not None:
            threading.Thread(target=self.video_downloader_task_manager.resume, daemon=True).start()
        else:
            logging.warning("No active video downloader executor to resume.")

        if self.reels_copy_task_executor is not None:
            threading.Thread(target=self.reels_copy_task_executor.resume, daemon=True).start()

        if self.profile_info_fetcher_task_manager is not None:
            threading.Thread(target=self.profile_info_fetcher_task_manager.resume, daemon=True).start()

        else:
            logging.warning("No active reels copy executor to resume.")


    def quit_all_task(self):
        """
        Stops all active executors and waits for them to finish.
        Also ensures that any upcoming tasks are cancelled via the stop_event.
        """
        threads = []
        
        if self.reels_upload_task_executor is not None:
            t = threading.Thread(
                target=self._stop_executor, 
                args=(self.reels_upload_task_executor.stop, "reels_upload executor")
            )
            threads.append(t)
            t.start()
        else:
            logging.warning("No active reels_upload executor to stop.")

        if self.video_downloader_task_manager is not None:
            t = threading.Thread(
                target=self._stop_executor, 
                args=(self.video_downloader_task_manager.quit, "Video downloader task manager")
            )
            threads.append(t)
            t.start()
        else:
            logging.warning("No active video downloader executor to stop.")

        if self.reels_copy_task_executor is not None:
            t = threading.Thread(
                target=self._stop_executor, 
                args=(self.reels_copy_task_executor.stop, "Reels copy executor")
            )
            threads.append(t)
            t.start()

        if self.profile_info_fetcher_task_manager is not None: 
            t = threading.Thread(
                target=self._stop_executor, 
                args=(self.profile_info_fetcher_task_manager.stop, "Reels copy executor")
            )
            threads.append(t)
            t.start()

        else:
            logging.warning("No active reels copy executor to stop.")

        # Wait for all stop threads to finish before returning.
        for t in threads:
            t.join()
        logging.info("All tasks have been successfully stopped.")

    def _stop_executor(self, stop_func, name):
        """
        Helper function to call an executor's stop/quit function.
        """
        try:
            stop_func()
            logging.info("%s stopped successfully", name)
        except Exception as e:
            logging.error("Error while stopping %s: %s", name, e)

class AnimatedHoverButton(QPushButton):
    """QPushButton subclass with smooth color transition on hover."""
    def __init__(self, text, btn_padding=3, parent=None):
        super().__init__(text, parent)
        # hoverLevel: 0.0 (normal) to 1.0 (hovered)
        self._hoverLevel = 0.0
        self.btn_padding = btn_padding
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)
        # Animation setup
        self._anim = QPropertyAnimation(self, b"hoverLevel", self)
        self._anim.setDuration(200)  # 200 ms transition
        # Initial style
        self.update_style()
        
        # Fix to prevent opening new windows
        self.setDefault(False)
        self.setAutoDefault(False)

    def update_style(self):
        # interpolate alpha between 0.5 and 0.8 based on hoverLevel
        alpha = 0.5 + 0.3 * self._hoverLevel
        color = f"rgba(27,86,253,{alpha:.2f})"
        pressed_style = "rgba(27,86,253,1.0)"
        padding = f"padding: {self.btn_padding}px"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 8px;
                {padding};
            }}
            QPushButton:pressed {{
                background-color: {pressed_style};
            }}
        """)

    def enterEvent(self, event):
        # animate to hover state
        self._anim.stop()
        self._anim.setStartValue(self._hoverLevel)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        # animate back to normal
        self._anim.stop()
        self._anim.setStartValue(self._hoverLevel)
        self._anim.setEndValue(0.0)
        self._anim.start()
        super().leaveEvent(event)

    def getHoverLevel(self):
        return self._hoverLevel

    def setHoverLevel(self, value):
        self._hoverLevel = value
        self.update_style()

    hoverLevel = Property(float, getHoverLevel, setHoverLevel)
class SocialButton(QPushButton):
    def __init__(self, text, url, icon_text="", parent=None):
        super().__init__(text, parent)
        self.url = url
        self.setMinimumHeight(50)
        self.setMinimumWidth(200)
        self.setCursor(Qt.PointingHandCursor)
        
        # Dark mode button styling
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3A5998, stop:1 #2D4373);
                color: #FFFFFF;
                border: 1px solid #404040;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                padding: 12px 20px;
                text-align: left;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4A6BB8, stop:1 #3D5393);
                border: 2px solid #5A9FD4;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #2A4988, stop:1 #1D3363);
                border: 2px solid #4A8BC2;
                color: #E0E0E0;
            }
        """)
        
        if icon_text:
            self.setText(f"{icon_text}  {text}")
        
        self.clicked.connect(self.open_link)
    
    def open_link(self):
        QDesktopServices.openUrl(QUrl(self.url))

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeniFlow - About")
        self.setModal(True)
        self.resize(650, 800)
        
        # Set dark mode dialog styling
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2C2C2C, stop:1 #1E1E1E);
                color: #FFFFFF;
            }
        """)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #3C3C3C;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #5A9FD4;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4A8BC2;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                border: none;
                height: 0px;
            }
        """)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(40, 40, 40, 40)
        
        # Header Section
        self.create_header_section(content_layout)
        

        # Contact Section
        self.create_contact_section(content_layout)

        # Social Media Section
        self.create_social_section(content_layout)
        
        
        # Footer
        self.create_footer(content_layout)
        

        
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
    
    def create_header_section(self, layout):
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #404040, stop:1 #353535);
                border-radius: 15px;
                border: 1px solid #555555;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 30, 30, 30)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # App name
        app_name = QLabel("GeniFlow")
        app_name.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 36px;
                font-weight: bold;
                margin-bottom: 10px;
                background: transparent;
            }
        """)
        app_name.setAlignment(Qt.AlignCenter)
        
        # App description
        app_desc = QLabel("Your Ultimate Productivity Companion")
        app_desc.setStyleSheet("""
            QLabel {
                color: #B0B0B0;
                font-size: 18px;
                margin-bottom: 20px;
                background: transparent;
            }
        """)
        app_desc.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(app_name)
        header_layout.addWidget(app_desc)
        
        layout.addWidget(header_frame)
    
    def create_social_section(self, layout):
        social_frame = QFrame()
        social_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #404040, stop:1 #353535);
                border-radius: 15px;
                border: 1px solid #555555;
            }
        """)
        
        social_layout = QVBoxLayout(social_frame)
        social_layout.setContentsMargins(30, 30, 30, 30)
        
        social_title = QLabel("Connect With Us")
        social_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                background: transparent;
            }
        """)
        
        # Social media buttons grid
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        
        facebook_btn = SocialButton("Facebook", "https://facebook.com/geniflow", "📘")
        twitter_btn = SocialButton("Twitter", "https://twitter.com/geniflow", "🐦")
        
        row1.addWidget(facebook_btn)
        row1.addWidget(twitter_btn)
        
        # Row 2
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        instagram_btn = SocialButton("Instagram", "https://instagram.com/geniflow", "📷")
        linkedin_btn = SocialButton("LinkedIn", "https://linkedin.com/company/geniflow", "💼")
        
        row2.addWidget(instagram_btn)
        row2.addWidget(linkedin_btn)
        
        # Row 3
        row3 = QHBoxLayout()
        row3.setSpacing(15)
        
        youtube_btn = SocialButton("YouTube", "https://youtube.com/@geniflow", "📺")
        github_btn = SocialButton("GitHub", "https://github.com/geniflow", "⚡")
        
        row3.addWidget(youtube_btn)
        row3.addWidget(github_btn)
        
        buttons_layout.addLayout(row1)
        buttons_layout.addLayout(row2)
        buttons_layout.addLayout(row3)
        
        social_layout.addWidget(social_title)
        social_layout.addLayout(buttons_layout)
        
        layout.addWidget(social_frame)
    
    def create_contact_section(self, layout):
        contact_frame = QFrame()
        contact_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #404040, stop:1 #353535);
                border-radius: 15px;
                border: 1px solid #555555;
            }
        """)
        
        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setContentsMargins(30, 30, 30, 30)
        
        contact_title = QLabel("Get In Touch")
        contact_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                background: transparent;
            }
        """)
        
        # Contact buttons
        contact_buttons_layout = QVBoxLayout()
        contact_buttons_layout.setSpacing(15)
        
        # Row 1
        contact_row1 = QHBoxLayout()
        contact_row1.setSpacing(15)
        
        whatsapp_btn = SocialButton("WhatsApp", "https://wa.me/919113161106", "💬")
        telegram_btn = SocialButton("Telegram", "https://t.me/geniflow", "✈️")
        
        contact_row1.addWidget(whatsapp_btn)
        contact_row1.addWidget(telegram_btn)
        
        # Row 2
        contact_row2 = QHBoxLayout()
        contact_row2.setSpacing(15)
        
        website_btn = SocialButton("Visit Website", "https://geniflow.com", "🌐")
        email_btn = SocialButton("Email Us", "mailto:hello@geniflow.com", "📧")
        
        contact_row2.addWidget(website_btn)
        contact_row2.addWidget(email_btn)
        
        contact_buttons_layout.addLayout(contact_row1)
        contact_buttons_layout.addLayout(contact_row2)
        
        contact_layout.addWidget(contact_title)
        contact_layout.addLayout(contact_buttons_layout)
        
        layout.addWidget(contact_frame)
    
    def create_footer(self, layout):
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1A1A1A, stop:1 #2D2D2D);
                border-radius: 15px;
                padding: 20px;
                border: 1px solid #444444;
            }
        """)
        
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setAlignment(Qt.AlignCenter)
        
        footer_text = QLabel("© 2024 GeniFlow. All rights reserved.")
        footer_text.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
                background: transparent;
            }
        """)
        footer_text.setAlignment(Qt.AlignCenter)
        
        version_text = QLabel("Version 1.0.0")
        version_text.setStyleSheet("""
            QLabel {
                color: #B0B0B0;
                font-size: 12px;
                background: transparent;
                margin-top: 5px;
            }
        """)
        version_text.setAlignment(Qt.AlignCenter)
        
        footer_layout.addWidget(footer_text)
        footer_layout.addWidget(version_text)
        
        layout.addWidget(footer_frame)
    
    def create_close_button(self, layout):
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        close_btn.setMaximumWidth(120)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #C53030, stop:1 #9B2C2C);
                color: #FFFFFF;
                border: 1px solid #B91C1C;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #DC2626, stop:1 #B91C1C);
                border: 2px solid #DC2626;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #991B1B, stop:1 #7F1D1D);
                border: 2px solid #991B1B;
                color: #E0E0E0;
            }
        """)
        
        close_btn.clicked.connect(self.accept)
        
        # Center the close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        close_layout.addStretch()
        
        layout.addLayout(close_layout)

class MainWindow(QMainWindow):
    """
    Main application window.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Activity Control Application")
        self.resize(900, 600)
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #222222;
                color: white;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QLabel {
                color: white;
            }
            QScrollArea {
                border: none;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Create and add frames
        current_activity_frame = CurrentActivity()
        activity_control_frame = ActivityControl()
        
        main_layout.addWidget(current_activity_frame)
        main_layout.addWidget(activity_control_frame)
        
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    # Initialize the main application window
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())