import ctypes
import multiprocessing
import multiprocessing.managers
import sys
import os
import time
import threading
import queue
from queue import Empty
from datetime import datetime
from typing import Dict, Any
import logging
import subprocess
import sys, time, multiprocessing as mp, random
from subprocess import CREATE_NO_WINDOW
from multiprocessing import JoinableQueue, Manager

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QDialog,
    QPushButton, QLabel, QScrollArea, QGridLayout, QMessageBox,QListView,QTableView,QHeaderView,QAbstractItemView,QAbstractItemView,QGroupBox)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, Slot,QStringListModel,QPropertyAnimation,Property
from PySide6.QtGui import QPixmap, QFont, QFontDatabase, QIcon,QStandardItemModel,QStandardItem
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QPixmap, QPainter, QIcon, QDesktopServices

from PySide6.QtWidgets import (QApplication, QTableView, QVBoxLayout,
                               QLabel, QAbstractItemView, QWidget)
from PySide6.QtCore    import Qt, QTimer
from PySide6.QtGui     import QStandardItemModel, QStandardItem, QColor

from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Append parent directory to sys.path so that the custom modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..',)))
#from geni_backend_src.start_activity_main import LDTaskExecutor

from geni_backend_src.start_activity_main import LDTaskExecutor
from geni_backend_src.task_collector import TaskCollector
from geni_backend_src.utlitis.geni_config_collector import DeviceSettingsFlatten
from geni_backend_src.downloader_task_collector import DownloaderTaskCollector
from geni_backend_src.start_download_activity import VideoDownloaderTaskManager
from geni.geni_backend_src.copy_task_collector import CopyTaskCollector
from geni.geni_backend_src.copy_task_executor import CopyTaskExecutor
from geni_backend_src.profiles_info_fetcher import ProfileInfoFatcher
from geni_ui_src.login_src.login_window import SerialCodeApp
from geni_ui_src.log_viewer import LogAnalyzer

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
    
class StyledFrame(QFrame):

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
    HEADERS = ["LDName", "App", "Profile",
               "Current activity", "Others", "Last update"]

    def __init__(self, parent=None,log_dir=None):
        super().__init__(parent) 

        # Create log directory
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Log file paths
        self.log_file = self.log_dir / "activity.log"
        self.detail_log_file = self.log_dir / "detailed_activity.log"
        
        self.clear_log_file()
        self.model = QStandardItemModel(0, len(self.HEADERS), self)
        self.model.setHorizontalHeaderLabels(self.HEADERS)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(2, 85)
        self.table.setColumnWidth(3, 250)
        self.table.setColumnWidth(4, 50)
        self.table.setColumnWidth(5, 50)
        self.table.horizontalHeader().setStretchLastSection(True)
        

        self.resume_event = multiprocessing.Event()
        self.manager = Manager()
        """ self.control_pause = self.manager.Event()
        self.control_pause.set() """
        self.resume_event.set()

        lay = QVBoxLayout(self)  
        lay.addWidget(self.table)

        self.row_for_no: Dict[str, int] = {}
        self.process_data: Dict[str, Dict[str, Any]] = {}
        self.queue = mp.Queue()
        self.finished_processes = set()

        # Timer to drain the queue
        self.timer = QTimer()
        self.timer.timeout.connect(self.start_drain_queue_thred)
        self.timer.start(10)

    def start_drain_queue_thred(self):
        threading.Thread(target=self._drain_queue).start()

    def _drain_queue(self):
        processed = 0
        while processed < 10000:  
            try:
                data = self.queue.get_nowait()
                command = data[0]
                
                if command == 'UPDATE':
                    # Check if logging parameter exist
                    if len(data) > 7:  
                        self.resume_event.wait()
                        self._apply_update(*data[1:7])  
                        self._handle_logging(*data[1:])  
                    else:
                        self.resume_event.wait()
                        self._apply_update(*data[1:])
                        
                elif command == 'DELETE':
                    self.resume_event.wait()
                    self._delete_process(data[1])
                    
                elif command == 'FINISHED':
                    # Check if logging parameter exis
                    if len(data) > 7: 
                        self.resume_event.wait()
                        self._mark_finished(*data[1:7])  
                        self._handle_logging(*data[1:])  
                    else:
                        self.resume_event.wait()
                        self._mark_finished(*data[1:])
                        
                elif command == 'LOG':
                    self.resume_event.wait()
                    self._handle_logging(*data[1:])
                    
                processed += 1
            except Empty:
                break
    
    def pause(self):
        #self.control_pause.clear()
        self.resume_event.clear()

    def resume(self):
        #self.control_pause.set()

        self.resume_event.set()

    def _apply_update(self, ldname, app, profile, current, others, ts):
        """Apply an update to a process row."""
        
        self.process_data[ldname] = {
            'ldname': ldname, 'app': app,
            'profile': profile, 'current': current, 
            'others': others, 'timestamp': ts
        }

        # Create new row
        if ldname not in self.row_for_no:
            row = self.model.rowCount()
            self.model.insertRow(row)
            self.row_for_no[ldname] = row
        else:
            row = self.row_for_no[ldname]

        # Update all cells in the row
        for column, text in enumerate((ldname, app, profile, current, others, ts)):
            item = self.model.item(row, column)
            if item is None:
                item = QStandardItem()
                item.setTextAlignment(Qt.AlignCenter)
                self.model.setItem(row, column, item)
            item.setText(str(text))

        # Color coding 
        self._apply_row_colors(row, current, ldname in self.finished_processes)
        #self._resize_table()

    def _handle_logging(self, ldname, app, profile, current, others, timestamp, log_type=None):
        """Handle logging operations independently of UI updates."""
        if log_type == "s":
            self._save_to_log(ldname, app, profile, current, others, timestamp)
            
        self._save_to_detail_log(ldname, app, profile, current, others, timestamp)

    def clear_log_file(self):
        """Clear the log file"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")  
            print(f"Log file cleared: {self.log_file}")
        except Exception as e:
            print(f"Error clearing log file: {e}")

    def _save_to_log(self,ldname, app, profile, current, others, timestamp):
        "Save all the detail to log file "
        try:
            log_entry = f"[{timestamp}] {ldname} | {app} | {profile} | {current} | {others}\n"
            with open(self.log_file,'a',encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error saving activity log: {e}")


    def _save_to_detail_log(self,ldname, app, profile, current, others, timestamp):
        "Save all the detail to log file "
        try:
            log_entry = f"[{timestamp}] {ldname} | {app} | {profile} | {current} | {others}\n"
            with open(self.detail_log_file,'a',encoding='utf-8') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error saving details activity log: {e}")



    def _mark_finished(self, ldname, app, profile, current, others, ts):
        """Mark a process as finished with special styling."""
        self.finished_processes.add(ldname)
        self._apply_update(ldname, app, profile, current, others, ts)

    def _delete_process(self, ldname):
        """Delete a process row and update all mappings."""
        if ldname not in self.row_for_no:
            print(f"Warning: Cannot delete process {ldname} - not found")
            return

        row_to_delete = self.row_for_no[ldname]
        
        self.model.removeRow(row_to_delete)
        
        updated_mappings = {}
        for process_ldname, row_idx in self.row_for_no.items():
            if process_ldname == ldname:
                continue  
            elif row_idx > row_to_delete:
                updated_mappings[process_ldname] = row_idx - 1  
            else:
                updated_mappings[process_ldname] = row_idx  
        
        self.row_for_no = updated_mappings
        
        # Clean up process data
        if ldname in self.process_data:
            del self.process_data[ldname]
        if ldname in self.finished_processes:
            self.finished_processes.remove(ldname)
            
        print(f"Deleted process {ldname}. Remaining processes: {list(self.row_for_no.keys())}")
        #self._resize_table()

    def _apply_row_colors(self, row, status, is_finished):
        """Apply appropriate colors based on process status."""
        if is_finished or status.lower() in ["finished", "completed"]:
            color = QColor(27,86,253,128)
        elif status.lower() in ["error", "failed"]:
            color = QColor(255, 200, 200)  
        elif status.lower() in ["starting", "initializing"]:
            color = QColor(27,86,253,128)
        else:
            color = QColor(27,86,253,128)  
            
        for col in range(self.model.columnCount()):
            item = self.model.item(row, col)
            if item:
                item.setBackground(color)

    def _resize_table(self):
        """Resize table columns and rows to fit content."""
        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()

    def get_activity_callback(self):
        """Get the activity update callback."""
        return lambda *args: activity_callback(self.queue, *args)

    def get_delete_callback(self):
        """Get the delete callback."""
        return lambda ldname: delete_callback(self.queue, ldname)

    def get_finished_callback(self):
        """Get the finished callback."""
        return lambda *args: mark_finished_callback(self.queue, *args)

    def delete_process_by_no(self, ldname):
        """Manually delete a process by its LDName."""
        delete_callback(self.queue, str(ldname))

    def delete_selected_process(self):
        """Delete the currently selected process in the table."""
        selection = self.table.selectionModel().selectedRows()
        if not selection:
            print("No process selected for deletion")
            return
            
        row = selection[0].row()
        ldname_item = self.model.item(row, 0)  
        if ldname_item:
            process_ldname = ldname_item.text()
            self.delete_process_by_no(process_ldname)
            print(f"Deleting selected process: {process_ldname}")

    def get_active_processes(self):
        """Get list of currently active process ldnames."""
        return list(self.row_for_no.keys())

    def clear_finished_processes(self):
        """Clear all finished processes."""
        for ldname in list(self.finished_processes):
            self.delete_process_by_no(ldname)

    # Helper methods for easier usage
    def add_process(self, device_name, app, profile, status, others=""):
        """Add a new process directly"""
        activity_callback(self.queue, device_name, app, profile, status, others)
    
    def update_process(self, device_name, app, profile, status, others=""):
        """Update an existing process"""
        activity_callback(self.queue, device_name, app, profile, status, others)

    def mark_process_finished(self, device_name, app, profile, status, others=""):
        """Mark a process as finished"""
        mark_finished_callback(self.queue, device_name, app, profile, status, others)

    def log_activity(self, device_name, app, profile, status, others="", log_type="s"):
        """Log activity without updating UI"""
        log_callback(self.queue, device_name, app, profile, status, others, log_type)



class ActivityControl(StyledFrame):
    
    pause_signal = Signal()
    show_about_dialog_signal = Signal()

    def __init__(self, parent=None,main_win_ref=None,Current_activity_ref=None):
        super().__init__(parent)
        
        # Activity states: "stopped", "running", "paused"
        self.state = "stopped"
        # Activity types: "main", "fetch"
        self.current_activity_type = "main"
        self.main_queue = queue.Queue()
        self.start_time = 0
        self.main_win_ref = main_win_ref
        self.current_activity_win_ref = Current_activity_ref
        self.Activity_queue = Current_activity_ref.queue
        self.serial_code_verification = SerialCodeApp()
        

        self.elapsed_time = 0
        self.page_manager_path = r"User_Data\Page_manager.json"
        self.is_auto_sleep_enable_in_id_fetch = False
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

        header_frame = QFrame()
        header_frame.setStyleSheet("""background-color: rgb(34, 81, 200);border-radius: 10px;""")
        header_frame.setFixedHeight(35)
        header_frame.setFixedWidth(180)
        bg_layout = QVBoxLayout(header_frame)
        layout.addWidget(header_frame, alignment=Qt.AlignCenter)

        header = QLabel("Activity Controls")
        header.setStyleSheet("font-size: 12pt; font-weight: bold; background-color: none; color: white;")
        bg_layout.addWidget(header, alignment=Qt.AlignCenter)

        controls_layout = QHBoxLayout()
        layout.addLayout(controls_layout)

        play_pause_frame = QGroupBox()
        play_pause_frame.setTitle("Play/Pause Controls")
        play_pause_frame.setObjectName("play_pause_frame")
        play_pause_frame.setStyleSheet("""
            QGroupBox#play_pause_frame {
                border: 2px solid rgba(128,128,128,0.8);
                border-radius: 8px;
                padding-top: 5px;
                margin-top: 10px;
                padding-right: 10px;
                padding-left: 10px;
                padding-bottom: 5px;
                background-color: rgba(128,128,128,0.2);
            }
            QGroupBox#play_pause_frame::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                font-weight: bold;
                border-radius: 5px;
                padding-left: 5px;
                padding-right: 5px;
                padding-top: 1px;
                padding-bottom: 1px;
                background-color: rgba(128,128,128,0.8);
            }
        """)
        play_pause_frame.setFixedWidth(360)
        play_pause_frame.setAlignment(Qt.AlignCenter)

        play_pause_layout = QGridLayout(play_pause_frame)
        play_pause_layout.setAlignment(Qt.AlignCenter)
        play_pause_layout.setHorizontalSpacing(20)
        play_pause_layout.setVerticalSpacing(10)

        play_btn_widget = QWidget()
        play_btn_widget.setObjectName("play_btn_widget")
        play_btn_widget.setStyleSheet("QWidget#play_btn_widget { background-color: transparent; }")
        play_btn_layout = QVBoxLayout(play_btn_widget)
        play_btn_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        play_btn_layout.setSpacing(2)

        self.activity_type_label = QLabel("Main Activity")
        self.activity_type_label.setStyleSheet("background-color: none; font-weight: bold; color: white; text-align: center; font-size: 12px;")
        self.activity_type_label.setFixedWidth(100)
        self.activity_type_label.setAlignment(Qt.AlignHCenter)
        play_btn_layout.addWidget(self.activity_type_label)

        self.play_pause_button = AnimatedHoverButton("")
        self.play_pause_button.setIcon(QIcon(self.play_icon))
        self.play_pause_button.setToolTip("Start/stop Activity")
        self.play_pause_button.setIconSize(QSize(90,90))
        self.play_pause_button.setFixedSize(100, 100)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        play_btn_layout.addWidget(self.play_pause_button)

        quit_Widget = QWidget()
        quit_Widget.setObjectName("quit_Widget")
        quit_Widget.setStyleSheet("QWidget#quit_Widget { background-color: transparent; }")
        quit_layout = QVBoxLayout(quit_Widget)
        quit_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        quit_layout.setSpacing(2)

        quit_btn_label = QLabel("Quit All")
        quit_btn_label.setStyleSheet("background-color: transparent; font-weight: bold; color: white; text-align: center; font-size: 12px;")
        quit_btn_label.setFixedWidth(100)
        quit_btn_label.setAlignment(Qt.AlignHCenter)
        quit_layout.addWidget(quit_btn_label)

        quit_button = AnimatedHoverButton(self)
        quit_button.setIcon(QIcon(r"geni\geni_ui_src\ui_assets\Icons\sign-out.png"))
        quit_button.setToolTip("Quit All Processes and Stop the Tool")
        quit_button.setIconSize(QSize(90,90))
        quit_button.setFixedSize(100, 100)
        quit_button.setToolTip("Quit All Processes and Stop the Tool")
        quit_button.clicked.connect(self.handle_quit)
        quit_layout.addWidget(quit_button)

        ################################TIMERRRRRRRRRRRR###################
        timer_frame = QGroupBox()
        timer_frame.setTitle("Elapsed Time")
        timer_frame.setObjectName("timer_frame")
        timer_frame.setStyleSheet("""
            QGroupBox#timer_frame {
                border: 2px solid rgba(128,128,128,0.8);
                border-radius: 8px;
                padding-top: 5px;
                margin-top: 10px;
                padding-right: 10px;
                padding-left: 10px;
                padding-bottom: 5px;
                background-color: rgba(128,128,128,0.2);
            }
            QGroupBox#timer_frame::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                border-radius: 5px;
                padding-left: 5px;
                padding-right: 5px;
                padding-top: 1px;
                padding-bottom: 1px;
                background-color: rgba(128,128,128,0.8);
            }
        """)
        timer_frame.setFixedWidth(360)
        timer_widget = QWidget()
        timer_widget.setStyleSheet("background-color: none")
        timer_widget.setObjectName("timer_widget")
        timer_layout = QVBoxLayout(timer_frame)
        timer_layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        font_id = QFontDatabase.addApplicationFont("geni/geni_ui_src/ui_assets/Icons/fonts/Digital Dismay.otf") if Path("geni/geni_ui_src/ui_assets/Icons/fonts/Digital Dismay.otf").exists() else -1
        digital_font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"

        self.timer_display = QLabel("00:00:00")
        self.timer_display.setAttribute(Qt.WA_TranslucentBackground)
        self.timer_display.setStyleSheet("background-color: transparent; font-weight: bold; color: white; text-align: center; font-size: 12px;")
        timer_font = QFont(digital_font_family, 55)
        self.timer_display.setFont(timer_font)
        self.timer_display.setStyleSheet("color: red;")
        timer_layout.addWidget(self.timer_display)

        play_pause_layout.addWidget(play_btn_widget, 0, 0)
        play_pause_layout.addWidget(quit_Widget, 0, 1)

        controls_layout.addWidget(play_pause_frame)
        controls_layout.addWidget(timer_frame)


        View_logs_details = QGroupBox()
        View_logs_details.setObjectName("Log_Frame")
        View_logs_details.setTitle("Log Frame")
        View_logs_details.setAlignment(Qt.AlignVCenter)
        View_logs_details.setStyleSheet("""
            QGroupBox#Log_Frame {
                border: 2px solid rgba(128,128,128,0.8);
                border-radius: 8px;
                padding-top: 5px;
                margin-top: 10px;
                padding-right: 10px;
                padding-left: 10px;
                padding-bottom: 5px;
                background-color: rgba(128,128,128,0.2);
            }
            QGroupBox#Log_Frame::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                border-radius: 5px;
                padding-left: 5px;
                padding-right: 5px;
                padding-top: 1px;
                padding-bottom: 1px;
                background-color: rgba(128,128,128,0.8);
            }
        """)

        view_log_label = QLabel("Activity Log")
        view_log_label.setStyleSheet("background-color: transparent; font-weight: bold; color: white; text-align: center; font-size: 12px;")
        view_log_btn = AnimatedHoverButton(self)
        view_log_btn.setFixedSize(100, 100)
        view_log_btn.setIcon(QIcon(r"geni\geni_ui_src\ui_assets\Icons\log.png"))
        view_log_btn.setIconSize(QSize(80,80))
        view_log_btn.setToolTip("view Current Activity Log")
        view_log_btn.clicked.connect(self.open_activities_log)
        view_log_label.setAlignment(Qt.AlignHCenter)

        detail_log_label = QLabel("Detail Activity Log")
        detail_log_label.setAlignment(Qt.AlignHCenter)
        detail_log_label.setStyleSheet("background-color: transparent; font-weight: bold; color: white; text-align: center; font-size: 12px;")
        detail_log_btn = AnimatedHoverButton(self)
        detail_log_btn.setIcon(QIcon(r"geni\geni_ui_src\ui_assets\Icons\detaillog.png"))
        detail_log_btn.setIconSize(QSize(80,80))
        detail_log_btn.setToolTip("view overall Detail Activity Log")
        detail_log_btn.setFixedSize(100, 100)
        detail_log_btn.clicked.connect(self.open_detail_activities_log)

        log_layout = QVBoxLayout()
        log_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        log_layout.addWidget(view_log_label)
        log_layout.addWidget(view_log_btn)

        detail_log_layout = QVBoxLayout()
        detail_log_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        detail_log_layout.addWidget(detail_log_label)
        detail_log_layout.addWidget(detail_log_btn)

        log_frame_layout = QHBoxLayout(View_logs_details)
        log_frame_layout.addLayout(log_layout)
        log_frame_layout.addSpacing(20)
        log_frame_layout.addLayout(detail_log_layout)
        log_frame_layout.setAlignment(Qt.AlignCenter)
        log_frame_layout.setContentsMargins(0,10,0,10)

        View_logs_details.setFixedWidth(360)
        layout.addWidget(View_logs_details, alignment=Qt.AlignHCenter)




#########################INSTAGRAMMMM####################################

        instagram_activity_type_frame = QGroupBox()
        instagram_activity_type_frame.setTitle("Instagram Activity (Pro Version)")
        instagram_activity_type_frame.setObjectName("instagram_activity_type_frame")
        instagram_activity_type_frame.setStyleSheet("""
            QGroupBox#instagram_activity_type_frame {
                border: 2px solid rgba(128,128,128,0.8);
                border-radius: 8px;
                padding-top: 5px;
                margin-top: 10px;
                padding-right: 10px;
                padding-left: 10px;
                padding-bottom: 5px;
                background-color: rgba(128,128,128,0.2);
            }
            QGroupBox#instagram_activity_type_frame::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                border-radius: 5px;
                padding-left: 5px;
                padding-right: 5px;
                padding-top: 1px;
                padding-bottom: 1px;
                background-color: rgba(128,128,128,0.8);
            }
        """)
        instagram_activity_type_frame.setFixedWidth(780)
        instagram_activity_type_frame.setFixedHeight(300)
        Comingsoon_label = QLabel("Only Available in Pro Version")
        instagram_activity_layout = QHBoxLayout(instagram_activity_type_frame)
        instagram_activity_layout.setAlignment(Qt.AlignCenter)
        # self.main_activity_button = QPushButton("Main Activity")
        # self.main_activity_button.setToolTip("Set Activity Type to Main Activity")
        # self.main_activity_button.setFixedWidth(150)
        # self.main
        # # self.main_activity_button.clicked.connect(lambda: self.set_activity_type("main"))
        # activity_type_layout.addWidget(self.main_activity_button)
        # self.fetch_activity_button = QPushButton("Fetch Activity")
        # self.fetch_activity_button.setToolTip("Set Activity Type to Fetch Activity")
        # self.fetch_activity_button.setFixedWidth(150)
        # self.fetch_activity_button.clicked.connect(lambda: self.set_activity_type("fetch"))
        instagram_activity_layout.addWidget(Comingsoon_label)
        layout.addWidget(instagram_activity_type_frame, alignment=Qt.AlignHCenter)

        layout.addStretch()  

    def open_activities_log(self):
        
        self.activities_log_window = LogAnalyzer(log_dir=r"logs")
        self.activities_log_window.show() #.show to display the window

    def open_detail_activities_log(self):
        
        self.detail_activities_log_window = LogAnalyzer(log_dir=r"logs", log_type="Detail_log")
        self.detail_activities_log_window.show()


    def verify_serial_and_start_activity(self):

        self.serial_code_verification.show_success_message = False
        self.serial_code_verification.run_complete_verification(self.start_activity,timer_callback=self.start_timer,show_err_callback=self.show_about_dialog_signal)
    


    def show_about_box(self):

        About = AboutDialog()
        About.exec()

    def handle_pause_from_thread(self):
        """ handle pause commands from worker threads"""
        if self.state == "running":
            logging.info("Auto-pause handled in main thread")
            self.pause_timer()
            self.state = "paused"
            logging.info("All tasks completed; timer paused.")
        else:
            logging.info("Auto-pause called but current state is: %s", self.state)

    def set_activity_type(self, activity_type):
        """
        Sets the current activity type and updates the UI .
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
        else:  
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
        """
        if self.state == "stopped":
            # Clear  stop flag
            self.stop_event.clear()
    
            # Launch the appropriate activity based on the current activity type. if main activity then it will start the uploading task and all else it will start the profile info fetch task
            if self.current_activity_type == "main":
                threading.Thread(target=self.verify_serial_and_start_activity, daemon=True).start()
                logging.info("Starting Main Activity...")
                
            else:  
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
            # Run the quit_all_task in new thread to avoid stucking the  UI
            threading.Thread(target=self._quit_all_task_async, daemon=True).start()
            self.reset_ui()
        else:
            logging.info("Quit cancelled by user.")

    def _quit_all_task_async(self):
        self.quit_all_task()
        QTimer.singleShot(0, self.reset_ui)

    def reset_ui(self):
        self.state = "stopped"
        self.elapsed_time = 0
        self.timer_display.setText("00:00:00")
        self.play_pause_button.setIcon(QIcon(self.play_icon))
        self.stop_event.clear()

    def auto_pause(self):
        """
        handle auto pause after all task got completed
        """
        # Use emit signel to avoid cross-thread UI updates and blocking it we use signal when we have to update something in different thread
        logging.info("Auto-pause triggered. Current state: %s", self.state)
        self.pause_signal.emit()


    def get_ld_list(self, ld_console_folder_path):

        ld_list = []
        try:
            cmd = [os.path.join(ld_console_folder_path, "ldconsole.exe"), "list2"]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT,creationflags=CREATE_NO_WINDOW,shell=True)
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
            device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json").flatten_json() # Make soure to change this path before using it in your pc bitch 
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
            
            self.profile_info_fetcher_task_manager = ProfileInfoFatcher(main_queue=tasks_queue,max_instances=device_settings["Number of instance at a time"],ld_player_path=device_settings["LD Location"],is_arrange_ld=device_settings["Auto arrange ld player"],instance_delay=device_settings["LD Opening Delay"],main_win_ref=self.main_win_ref,is_sleep_on=self.is_auto_sleep_enable_in_id_fetch,activity_queue=self.Activity_queue,)


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
                external_queue=mp_task_queue,activity_queue=self.Activity_queue
            )
            self.video_downloader_task_manager.run()
            logging.info("Downloaded %d tasks.", task_count)
        except Exception as e:
            logging.error("Error in download_task: %s", e)

    def reels_upload_task(self):
        """Collects tasks and starts the reels_upload executor."""
        
        

        try:
            device_settings = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json").flatten_json()
            collector = TaskCollector()
            raw_tasks_queue = collector.collect_tasks_from_json()

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

            self.reels_upload_task_executor = LDTaskExecutor(
                tasks_queue,
                max_instances=device_settings["Number of instance at a time"],
                ld_player_path=collector.ld_player_path,
                instance_delay=device_settings["LD Opening Delay"],
                is_arrange_ld=device_settings["Auto arrange ld player"],
                activity_queue=self.Activity_queue,
                current_activity_ref=self.current_activity_win_ref
            )
            self.reels_upload_task_executor.run()
        except Exception as e:
            logging.error("Error in Task: %s", e)


    def bulk_reels_copy_task(self):
        """
        Collects tasks and starts the reels copy executor.
        Now this function is not in used because this copy thing handle in runtime now so igone this function
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

            # All tasks completed
            self.pause_signal.emit()

        except Exception as e:
            logging.error(f"Error in main activity: {e}")
            # Emit the pause signal rather than calling auto_pause directly
            self.pause_signal.emit()

    def pause_tasks(self):
        """
        Pauses all active executors by calling their respective pause methods. In all other method like reels_upload_task we have method called pause so if user pause in activity tab its going to activate all pause method in all the tasks if running
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

        when user click on quit all button this method will call all the quit/stop method in all the tasks if running. samjha randbe
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

        # Wait for all stop threads to finish
        for t in threads:
            t.join()
        logging.info("All tasks have been successfully stopped.")

    def _stop_executor(self, stop_func, name):
        """
        Helper function to call an executor's .
        """
        try:
            stop_func()
            logging.info("%s stopped successfully", name)
        except Exception as e:
            logging.error("Error while stopping %s: %s", name, e)

class AnimatedHoverButton(QPushButton):
    def __init__(self, text="", btn_padding=6, parent=None):
        super().__init__(text, parent)
        self._hoverLevel = 0.0
        self._pressLevel = 0.0
        self.btn_padding = btn_padding
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)
        
        self.setStyleSheet("""
            QPushButton:focus {
                outline: none;
            }
        """)

        # Animation for hover
        self._hoverAnim = QPropertyAnimation(self, b"hoverLevel", self)
        self._hoverAnim.setDuration(250)
        
        # Animation for press/release
        self._pressAnim = QPropertyAnimation(self, b"pressLevel", self)
        self._pressAnim.setDuration(100)
        
        self.update_style()
        self.setDefault(False)
        self.setAutoDefault(False)
        self.setMinimumSize(100, 40)

    @Property(float)
    def hoverLevel(self):
        return self._hoverLevel

    @hoverLevel.setter
    def hoverLevel(self, value):
        self._hoverLevel = value
        self.update_style()

    @Property(float)
    def pressLevel(self):
        return self._pressLevel

    @pressLevel.setter
    def pressLevel(self, value):
        self._pressLevel = value
        self.update_style()

    def enterEvent(self, event):
        self._hoverAnim.setStartValue(self._hoverLevel)
        self._hoverAnim.setEndValue(1.0)
        self._hoverAnim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hoverAnim.setStartValue(self._hoverLevel)
        self._hoverAnim.setEndValue(0.0)
        self._hoverAnim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self._pressAnim.setStartValue(self._pressLevel)
        self._pressAnim.setEndValue(1.0)
        self._pressAnim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressAnim.setStartValue(self._pressLevel)
        self._pressAnim.setEndValue(0.0)
        self._pressAnim.start()
        super().mouseReleaseEvent(event)

    def update_style(self):
        hover_alpha = 0.7 + 0.2 * self._hoverLevel
        press_alpha = 0.9 + 0.1 * self._pressLevel
        bg_alpha = press_alpha if self._pressLevel > 0 else hover_alpha
        color = f"rgba(30, 100, 255, {bg_alpha:.2f})"
        base_font_size = 14
        font_size = base_font_size + 1 * self._hoverLevel
        font_size = base_font_size - 1 if self._pressLevel > 0 else font_size
        padding = f"padding: {self.btn_padding}px"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 10px;
                {padding};
                font-weight: 600;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: {font_size}px;
            }}
        """)
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
        
        
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        
        facebook_btn = SocialButton("Facebook", "https://facebook.com/geniflow", "📘")
        twitter_btn = SocialButton("Twitter", "https://twitter.com/geniflow", "🐦")
        
        row1.addWidget(facebook_btn)
        row1.addWidget(twitter_btn)
        
        
        row2 = QHBoxLayout()
        row2.setSpacing(15)
        
        instagram_btn = SocialButton("Instagram", "https://instagram.com/geniflow", "📷")
        linkedin_btn = SocialButton("LinkedIn", "https://linkedin.com/company/geniflow", "💼")
        
        row2.addWidget(instagram_btn)
        row2.addWidget(linkedin_btn)
        
        
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
        
        
        contact_row1 = QHBoxLayout()
        contact_row1.setSpacing(15)
        
        whatsapp_btn = SocialButton("WhatsApp", "https://wa.me/919113161106", "💬")
        telegram_btn = SocialButton("Telegram", "https://t.me/geniflow", "✈️")
        
        contact_row1.addWidget(whatsapp_btn)
        contact_row1.addWidget(telegram_btn)
        
        
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
        
        # Center the button
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
        
        # Create widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Create and add frames
        current_activity_frame = CurrentActivity()
        activity_control_frame = ActivityControl()
        
        main_layout.addWidget(current_activity_frame)
        main_layout.addWidget(activity_control_frame)
        
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    # Init the main application 
    app = QApplication(sys.argv) # Pass the requred args to the QApplication bohi bsdke jo ek din btaya tha 
    window = MainWindow()
    window.show()
    sys.exit(app.exec())