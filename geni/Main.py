import sys
import os
import threading
import queue
import time
import ctypes
import logging
import subprocess
from subprocess import CREATE_NO_WINDOW
import json
import webbrowser



os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '0'
os.environ['QT_SCALE_FACTOR'] = '1'
os.environ['QT_SCREEN_SCALE_FACTORS'] = '1'
os.environ['QT_DPI_AWARENESS'] = '0'
os.environ['QT_ENABLE_HIGHDPI_SCALING'] = '0'




""" if sys.platform.startswith('win'):
    try:
        # Hide console window completely
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 1)
        
        # Set DPI awareness to system DPI aware (no per-monitor scaling)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        try:
            # Fallback for older Windows versions
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass """




from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QLabel, 
                              QPushButton, QComboBox, QFrame, QVBoxLayout, QHBoxLayout, 
                              QGridLayout, QScrollArea, QCheckBox,QSplashScreen)
from PySide6.QtCore import Qt, QSize, Signal, QTimer, QPropertyAnimation, Property,QEasingCurve
from PySide6.QtGui import QIcon, QFont,QPixmap,QColor


def setup_application():
    """Setup console hiding and DPI scaling before creating QApplication"""
    
   
    if sys.platform.startswith('win'):
        try:
            # Hide the console 
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32
            
            # Get console window handle
            console_window = kernel32.GetConsoleWindow()
            if console_window != 0:
                
                user32.ShowWindow(console_window, 1)
                
            
            try:
                # Redirect stdout/stderr to null
                sys.stdout = open(os.devnull, 'w')
                sys.stderr = open(os.devnull, 'w')
            except:
                pass
                
            # Set process creation flags to prevent console
            CREATE_NO_WINDOW = 0x08000000
            kernel32.SetConsoleCtrlHandler(None, True)
            
        except Exception as e:
            pass
    
  
    QApplication.setAttribute(Qt.AA_DisableHighDpiScaling, True)
    
  
    QApplication.setAttribute(Qt.AA_Use96Dpi, True)
   
    try:
        QApplication.setAttribute(Qt.AA_DisableWindowContextHelpButton, True)
    except:
        pass

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QTabWidget, QLabel, 
                              QPushButton, QComboBox, QFrame, QVBoxLayout, QHBoxLayout, 
                              QGridLayout, QScrollArea,QCheckBox)
from PySide6.QtCore import Qt, QSize, Signal, QTimer,QPropertyAnimation,Property
from PySide6.QtGui import QIcon, QFont

# Import your other modules here
from geni_ui_src.tab_PageManager import PageRow, allPagesInsight
from geni_ui_src.tab_activity import CurrentActivity, ActivityControl
from geni_ui_src.tab_devices import DevicesInfoLdTable, DevicesSettings
from geni_ui_src.tab_autouploade import MakeProfileFrame,ProfileConfig
from geni_ui_src.user_setting_json_reader import user_settings_json
from geni_ui_src.tab_id_active import make_id_active_frame
from geni_ui_src.login_src.login_window import SerialCodeApp
from geni_ui_src.about_window import AboutDialog

# Dummy import for nuitka 

from ldController.Ldcontroller_adb.AdbCheckinUpload import *
from ldController.Ldcontroller_adb.AdbImageUpload import *
from ldController.Ldcontroller_adb.TimePicker_try import *
from ldController.Ldcontroller_adb.AdbImageUpload_ASW import *
from ldController.Ldcontroller_adb.AdbReelUpload import *
from ldController.Ldcontroller_adb.AdbReelUpload_ASW import *
from ldController.Ldcontroller_adb.AdbStoryUpload_IdACT import *
from ldController.Ldcontroller_adb.AdbStoryUpload import *
from ldController.Ldcontroller_adb.AdbVideoUpload_ASW import *
from ldController.Ldcontroller_adb.AdbVideoUpload import *
from ldController.Ldcontroller_adb.geni_config_collector import *
from ldController.Ldcontroller_adb.insights_collector import *
from ldController.Ldcontroller_adb.LdAdb import *
from ldController.Ldcontroller_adb.TimePicker_try import *

from ldController.Ldcontroller_adb.id_active.id_active import *
from ldController.Ldcontroller_adb.info_fetcher import *

from geni_backend_src.bulk_config_settings_editor import *
from geni_backend_src.copy_task_collector import *
from geni_backend_src.copy_task_executor import *
from geni_backend_src.downloader_task_collector import *
from geni_backend_src.start_download_activity import *
from geni_backend_src.profiles_info_fetcher import *
from geni_backend_src.start_activity_main import *
from geni_backend_src.start_download_activity import *
from geni_backend_src.task_collector import *
from geni_backend_src.utlitis.geni_config_collector import *

from geni.Downloaders.all_platform_shorts_downloader.UnifiedSocialMediaDownloader import * 




""" def is_admin():
    try: 
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        logging.error("Admin check failed: %s", e)
        return False


if not is_admin():
    script = os.path.abspath(sys.argv[0])
    params = " ".join(sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit()   """


# Load user settings from JSON
user = user_settings_json()
user_setting = user.load_or_create_json("User_Data")

def update_single_package(package_name):
    """
    Update a single package in the current virtual environment.
    """
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
        )
        #print(f"Package '{package_name}' updated successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to update package '{package_name}':", e)

# Global queue for thread communication
task_queue = queue.Queue()

def background_task():
    """Simulate a long-running task."""
    for i in range(5):
        time.sleep(1)
        task_queue.put(f"Background task progress: step {i+1}/5")

class ThemedFrame(QFrame):
    """Base frame with transparent background"""
    def __init__(self, parent=None):
        super().__init__(parent)



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.dataHandler = None 
        self.addPageWindow = None
        
        # Variables for debouncing and remembering last settings
        self.user_name = user_setting.get("user_name", "User Name")
        
        self.WindowSetup()
        self.create_widgets()
        

        self.start_background_task()
        self.load_device_settings()

    def WindowSetup(self):
        
        self.setWindowTitle("GeniFlow")
        
        
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        # Use availableGeometry() for better multi-monitor support
        available_geometry = screen.availableGeometry()
        
        screen_width = available_geometry.width()
        screen_height = available_geometry.height()
        


        width = 1500
        height = 650


        x = (screen_width - width) // 2 
        y = (screen_height - height) // 2
        self.setGeometry(x, y, width, height)


        # Set fixed size with proper scaling consideration
        self.setFixedSize(1550, 820)
        

        # Method 5: Explicitly set size policy
        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        


        # Set application icon
        icon_path = "geni/geni_ui_src/ui_assets/Icons/geni_logo.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    

    def create_widgets(self):
        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create the user preferences bar
        user_bar = self.user_preferences_bar()
        main_layout.addWidget(user_bar)
        

        # Create Tabview and its tabs
        self.tabview = QTabWidget()
        main_layout.addWidget(self.tabview)
        

        # Create tabs
        tab_activities = QWidget()
        tab_devices = QWidget()
        tab_auto_upload = QWidget()
        tab_id_active = QWidget()
        tab_page_manager = QWidget()
        

        # Add tabs to tabview
        self.tabview.addTab(tab_activities, "Activities")
        self.tabview.setTabToolTip(0, "To control Current Activity, Start New Activity, View Logs.")
        self.tabview.addTab(tab_devices, "Devices")
        self.tabview.setTabToolTip(1, "To view connected devices/Emulators, Id Fetching, Emulator settings & more!.")
        self.tabview.addTab(tab_auto_upload, "Auto Upload")
        self.tabview.setTabToolTip(2, "To manage Auto Upload on Ids/Pages & Settings Related to Uploading.")
        self.tabview.addTab(tab_id_active, "Id Active")
        self.tabview.setTabToolTip(3, "To manage ID Activity on Ids & Settings Related to ID Active.")
        self.tabview.addTab(tab_page_manager, "Page Manager")
        self.tabview.setTabToolTip(4, "To manage Pages/Profiles, Add/Edit/Delete/view insights of Pages/Ids & more!.")
        
        # Set up Activities tab
        activities_layout = QHBoxLayout(tab_activities)
        current_activity_widget = self.create_activity_tab_layout(tab_activities)
        activities_layout.addWidget(current_activity_widget)
        
        # Set up Devices tab
        devices_layout = QHBoxLayout(tab_devices)
        device_widget = self.create_devices_tab_layout(tab_devices)
        devices_layout.addWidget(device_widget)
        
        # Set up Page Manager tab
        page_manager_layout = QGridLayout(tab_page_manager)
        page_manager_widget = self.create_page_manager_tab_layout(tab_page_manager)
        page_manager_layout.addWidget(page_manager_widget, 0, 0)
        
        # Set up Auto Upload tab
        auto_upload_layout = QGridLayout(tab_auto_upload)
        auto_upload_widget = self.create_auto_upload_tab_layout(tab_auto_upload)
        auto_upload_layout.addWidget(auto_upload_widget, 0, 0)
        
        # Set up Id Active tab
        id_active_layout = QGridLayout(tab_id_active)
        id_active_widget = self.create_id_active_tab_layout(tab_id_active)
        id_active_layout.addWidget(id_active_widget, 0, 0)

    def create_activity_tab_layout(self, parent):
        container = ThemedFrame(parent)
        layout = QHBoxLayout(container)
        
        # Reduce horizontal spacing and margins
        layout.setSpacing(5)  
        layout.setContentsMargins(5, 5, 5, 5)  
        
        self.current_activity = CurrentActivity(container,log_dir=r"logs")
        self.current_activity.setMinimumWidth(700) 
        layout.addWidget(self.current_activity, 1)
        
        self.activity_ctrl = ActivityControl(container,main_win_ref =self,Current_activity_ref=self.current_activity)
        layout.addWidget(self.activity_ctrl, 3)
        
        return container
    
    def switch_to_tab_idx(self,tab_idx):
        current_index = self.tabview.currentIndex()
        next_index = (current_index + tab_idx) % self.tabview.count()
        self.tabview.setCurrentIndex(next_index)

    def create_devices_tab_layout(self, parent):
        container = ThemedFrame(parent)
        layout = QHBoxLayout(container)

        # Reduce horizontal spacing and margins
        layout.setSpacing(5)  
        layout.setContentsMargins(5, 5, 5, 5)  

        device_info = DevicesInfoLdTable(container, ActivityControl_refrance=self.activity_ctrl, MainWindow_refrance=self)
        device_info.setStyleSheet("DevicesInfoLdTable{border:2px solid rgba(128,128,128,1);border-radius:8px;}")
        layout.addWidget(device_info, 1)

        device_settings = DevicesSettings(container, device_info_frame=device_info)
        device_settings.setStyleSheet("DevicesSettings{border:2px solid rgba(128,128,128,1);border-radius:8px;}")
        layout.addWidget(device_settings, 3)

        return container
        
    def create_page_manager_tab_layout(self, parent):
        container = ThemedFrame(parent)
        layout = QGridLayout(container)

        # Reduce grid layout spacing and margins
        layout.setHorizontalSpacing(5) 
        layout.setContentsMargins(5, 5, 5, 5)  

        # Create actual widgets
        all_page_insite_frame = QFrame()
        all_page_insite_frame.setObjectName("all_page_insite_frame")
        all_page_insite_frame.setStyleSheet("QFrame#all_page_insite_frame{border:2px solid rgba(128,128,128,1);background-color:transparent;border-radius:8px;}")
        all_page_insite_frame_layout = QHBoxLayout(all_page_insite_frame)
        all_page_insite_frame_layout.setContentsMargins(5, 5, 5, 5) 

        self.all_insight = allPagesInsight(container)
        all_page_insite_frame_layout.addWidget(self.all_insight)
        layout.addWidget(all_page_insite_frame, 0, 1)

        page_row_frame = QFrame()
        page_row_frame.setObjectName("page_row_frame")
        page_row_frame.setStyleSheet("QFrame#page_row_frame{border:2px solid rgba(128,128,128,1);background-color:transparent;border-radius:8px;}")
        page_row_frame_layout = QVBoxLayout(page_row_frame)
        page_row_frame_layout.setContentsMargins(5, 5, 5, 5)  

        # Page row container for dynamic content
        self.page_manager_container = QWidget(page_row_frame)
        page_manager_container_layout = QVBoxLayout(self.page_manager_container)
        page_manager_container_layout.setContentsMargins(0, 0, 0, 0)  
        page_row_frame_layout.addWidget(self.page_manager_container)

        layout.addWidget(page_row_frame, 0, 0)

        layout.setColumnStretch(0, 1) 
        layout.setColumnStretch(1, 1)  

        # Add initial page row
        self.add_page_manager_page_row()

        return container
        
    def create_auto_upload_tab_layout(self, parent):
        container = ThemedFrame(parent)
        layout = QGridLayout(container)

        # Reduce grid layout spacing
        layout.setHorizontalSpacing(5)  
        layout.setContentsMargins(5, 5, 5, 5)  

        # Main profile frame
        profile_main_frame = ThemedFrame(container)
        profile_main_frame.setObjectName("profile_main_frame")
        profile_main_frame.setStyleSheet("""ThemedFrame#profile_main_frame{border:2px solid rgba(128,128,128,1);background-color:transparent;border-radius:8px;}""")
        layout.addWidget(profile_main_frame, 0, 1)

        profile_layout = QVBoxLayout(profile_main_frame)
        profile_layout.setContentsMargins(5, 5, 5, 5)  # Reduce profile frame margins
        self.profile_frame = MakeProfileFrame(profile_main_frame)
        profile_layout.addWidget(self.profile_frame)

        # Page row frame - reduce fixed width
        self.page_row_frame = ThemedFrame(container)
        self.page_row_frame.setFixedWidth(700)  # Reduced from 700
        self.page_row_frame.setStyleSheet("""ThemedFrame{border:2px solid rgba(128,128,128,1);background-color:transparent;border-radius:8px;}""")
        layout.addWidget(self.page_row_frame, 0, 0)

        page_row_layout = QVBoxLayout(self.page_row_frame)
        page_row_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins

        # Page row container 
        self.page_row_container = QWidget(self.page_row_frame)
        page_row_container_layout = QVBoxLayout(self.page_row_container)
        page_row_container_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        page_row_layout.addWidget(self.page_row_container)

        # Button frame
        button_frame = ThemedFrame(self.page_row_frame)
        button_frame.setStyleSheet("""ThemedFrame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(8, 5, 8, 5)  # Reduce button frame margins
        button_layout.setSpacing(8)  # Reduce spacing between button elements

        refrace_label = QLabel("Refresh this frame:", button_frame)
        refrace_label.setFont(QFont("Arial", 10, QFont.Bold))
        button_layout.addWidget(refrace_label)

        refrace_button = AnimatedHoverButton(text="Refresh", parent=button_frame)
        refrace_button.clicked.connect(self.add_auto_upload_page_row)
        refrace_button.setFixedSize(80, 25)  # Reduced width from 100 to 80
        button_layout.addWidget(refrace_button)

        # Remove one stretch or reduce stretch factor
        button_layout.addStretch(0)  

        v_line = self.create_vertical_line()
        button_layout.addWidget(v_line)

        # Remove second stretch or reduce stretch factor
        button_layout.addStretch(0) 

        self.gloabal_auto_upload = QCheckBox("Enable Upload For All")
        self.gloabal_auto_upload.clicked.connect(self.save_device_settings)
        button_layout.addWidget(self.gloabal_auto_upload)

        page_row_layout.addWidget(button_frame)

        # Set column stretching
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        # Add initial page row
        self.add_auto_upload_page_row()

        return container
        
    def create_id_active_tab_layout(self, parent):
        container = ThemedFrame(parent)
        layout = QGridLayout(container)

        # Reduce grid layout spacing
        layout.setHorizontalSpacing(5)  # Add this line
        layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins

        # Main profile frame
        profile_main_frame = ThemedFrame(container)
        profile_main_frame.setObjectName("profile_main_frame")
        profile_main_frame.setStyleSheet("""ThemedFrame#profile_main_frame{border:2px solid rgba(128,128,128,1);border-radius:8px;}""")
        layout.addWidget(profile_main_frame, 0, 1)

        profile_layout = QVBoxLayout(profile_main_frame)
        profile_layout.setContentsMargins(5, 5, 5, 5)  # Reduce profile frame margins
        self.profile_frame_id_active = make_id_active_frame(profile_main_frame)
        profile_layout.addWidget(self.profile_frame_id_active)

        # Page row frame - reduce fixed width
        self.page_row_frame_id_active = ThemedFrame(container)
        self.page_row_frame_id_active.setFixedWidth(670)  # Reduced from 700
        self.page_row_frame_id_active.setStyleSheet("""ThemedFrame{border:2px solid rgba(128,128,128,1);background-color:transparent;border-radius:8px;}""")
        layout.addWidget(self.page_row_frame_id_active, 0, 0)

        id_active_layout = QVBoxLayout(self.page_row_frame_id_active)
        id_active_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins

        # Page row container 
        self.page_row_container_id_active = QWidget()
        page_row_container_layout = QVBoxLayout(self.page_row_container_id_active)
        page_row_container_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        id_active_layout.addWidget(self.page_row_container_id_active)

        # Button frame
        button_frame = ThemedFrame(self.page_row_frame_id_active)
        button_frame.setStyleSheet("""ThemedFrame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)

        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(8, 5, 8, 5)  # Reduce button frame margins
        button_layout.setSpacing(8)  # Reduce spacing between button elements

        refrace_label = QLabel("Refresh this frame:", button_frame)
        refrace_label.setFont(QFont("Arial", 10, QFont.Bold))
        button_layout.addWidget(refrace_label)

        refrace_button = AnimatedHoverButton(text="Refresh", parent=button_frame)
        refrace_button.clicked.connect(self.add_id_active_page_row)
        refrace_button.setFixedSize(80, 25)  # Reduced width from 100 to 80
        button_layout.addWidget(refrace_button)

        # Remove one stretch or reduce stretch factor
        button_layout.addStretch(0)  # Comment out or remove this line

        v_line = self.create_vertical_line()
        button_layout.addWidget(v_line)

        # Remove second stretch or reduce stretch factor  
        button_layout.addStretch(0)  # Comment out or remove this line

        self.gloabal_id_active_checkbox = QCheckBox("Enable ID Active For All")
        self.gloabal_id_active_checkbox.clicked.connect(self.save_device_settings)
        button_layout.addWidget(self.gloabal_id_active_checkbox)

        id_active_layout.addWidget(button_frame)

        # Set column stretching - reduce first column stretch
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        # Add initial page row
        self.add_id_active_page_row()

        return container
    
    def create_vertical_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setFixedWidth(2)
        return line
    
    def add_page_manager_page_row(self):
        """Add or refresh the PageRow in the page manager tab"""
        # Clear existing widgets
        for i in reversed(range(self.page_manager_container.layout().count())): 
            widget = self.page_manager_container.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add new page row
        page_row = PageRow(
            master=self.page_manager_container,
            spawn_config_window_callback=self.all_insight
        )
        self.page_manager_container.layout().addWidget(page_row)

    def add_auto_upload_page_row(self):
        # Clear existing widgets
        for i in reversed(range(self.page_row_container.layout().count())): 
            widget = self.page_row_container.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add new page row
        page_row = PageRow(
            master=self.page_row_container,
            editable=False, 
            show_Edit_btn=False,
            show_auto_upload_checkbox=True,
            profile_config_frame=self.profile_frame,
            is_page_info_hidden=True,
            view_id_active_check_box=False,
            spawn_config_window_callback=self.profile_frame
        )
        self.page_row_container.layout().addWidget(page_row)
        
    def add_id_active_page_row(self):
        # Clear existing widgets
        for i in reversed(range(self.page_row_container_id_active.layout().count())): 
            widget = self.page_row_container_id_active.layout().itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add new page row
        page_row = PageRow(
            master=self.page_row_container_id_active, 
            editable=False,
            show_Edit_btn=False,
            view_id_active_check_box=True,
            show_auto_upload_checkbox=False,
            profile_config_frame=self.profile_frame_id_active,
            is_page_info_hidden=True,
            spawn_config_window_callback=self.profile_frame_id_active
        )
        self.page_row_container_id_active.layout().addWidget(page_row)

    def user_preferences_bar(self):
        bar_frame = ThemedFrame()
        bar_layout = QHBoxLayout(bar_frame)
        bar_layout.setContentsMargins(5, 5, 5, 5)
        
        # Name and API section
        name_api_frame = QFrame()
        name_api_layout = QHBoxLayout(name_api_frame)
        name_api_layout.setContentsMargins(0, 0, 0, 0)
        
        welcome_label = QLabel("Welcome, ")
        welcome_label.setFont(QFont("Arial", 10, QFont.Bold))
        name_api_layout.addWidget(welcome_label)
        
        user_name_label = QLabel(self.user_name)
        name_api_layout.addWidget(user_name_label)
        
        divider_label = QLabel("|")
        name_api_layout.addWidget(divider_label)
        
        api_btn = AnimatedHoverButton(text="API")
        api_btn.setFixedSize(70, 20)
        api_btn.clicked.connect(self.api_btn)
        name_api_layout.addWidget(api_btn)
        name_api_layout.setAlignment(Qt.AlignLeft)

        licence = AnimatedHoverButton(text="Licence")
        licence.setFixedSize(70, 20)
        licence.clicked.connect(self.active_btn_clicked)
        name_api_layout.addWidget(licence)
        name_api_layout.setAlignment(Qt.AlignLeft)
        
        bar_layout.addWidget(name_api_frame)
        
        # About section
        theme_frame = QFrame()
        theme_layout = QHBoxLayout(theme_frame)
        theme_layout.setContentsMargins(0, 0, 0, 0)
        
        whatsapp_btn = AnimatedHoverButton(text="About")
        whatsapp_btn.setFixedSize(70, 20)
        whatsapp_btn.clicked.connect(self.about_btn)
        theme_layout.addWidget(whatsapp_btn)
        
        bar_layout.addWidget(theme_frame, alignment=Qt.AlignRight)
        
        return bar_frame
        
    def about_btn(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()

    def active_btn_clicked(self):
        """Function called when button is clicked - creates window with delay to prevent blocking"""
        # Use QTimer to create window in next event loop iteration
        QTimer.singleShot(0, self.create_serial_window)

    def create_serial_window(self):
        """Create the SerialCodeApp window (runs in main thread)"""
        try:
            # Check if window already exists and close it
            if hasattr(self, 'serial_window') and self.serial_window:
                self.serial_window.close()

            self.serial_window = SerialCodeApp()

            # Set proper window flags to prevent console flash
            self.serial_window.setWindowFlags(
                Qt.Window | 
                Qt.WindowCloseButtonHint | 
                Qt.WindowMinimizeButtonHint |
                Qt.WindowMaximizeButtonHint |
                Qt.MSWindowsFixedSizeDialogHint  # Add this line
            )

            # Set window modality
            self.serial_window.setWindowModality(Qt.NonModal)

            self.serial_window.show()
            self.serial_window.raise_()
            self.serial_window.activateWindow()
            self.serial_window.verify_serial_code()

        except Exception as e:
            print(f"Error creating SerialCodeApp window: {e}")




    def api_btn(self):
        # Create a simple popup window
        from PySide6.QtWidgets import QDialog, QVBoxLayout
        
        window = QDialog(self)
        window.setWindowTitle("Coming Soon")
        window.setFixedSize(600, 500)
        window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(window)
        
        # Set the window icon
        try:
            from PIL import Image
            
            icon_path = r"geni\geni_ui_src\ui_assets\Icons\geni_logo_png.png"
            if os.path.exists(icon_path):
                window.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print("Failed to set icon:", e)

        label = QLabel("Your API will show here")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        window.exec()
   
    def on_theme_mode_changed(self, new_value):
        self.theme_mode = new_value
        self.save_changes()
        
    def on_theme_color_changed(self, new_value):
        self.theme_color = new_value
        self.save_changes()

    def save_user_setting(self):
        data = {
            "user_name": self.user_name,
            "saved_serial_number": "",
            "theme_mode": self.theme_mode,
            "theme_color": self.theme_color,
            "user_api": {}
        }
        return data

    def save_changes(self):
        
        self._refresh_timer.start(200)

    def _do_refresh(self):
        
        if (self.theme_mode == self._last_theme_mode and
            self.theme_color == self._last_theme_color):
            return

        # Save updated settings
        save = user_settings_json()
        save.save_changes(self.save_user_setting())
        
        # Apply theme
        self.apply_theme()
        
        # Update stored settings
        self._last_theme_mode = self.theme_mode
        self._last_theme_color = self.theme_color

    def load_device_settings(self):
        path = r"User_Data\Devices_Setting.json"

        with open(path,mode='r',encoding="utf-8") as f:
            data = json.load(f)

        global_settings = data.get("global_settings",{})
        global_auto_upload = global_settings.get("is_auto_upload_enabled",False)
        global_id_active = global_settings.get("is_id_active_enabled",False)

        self.gloabal_auto_upload.setChecked(global_auto_upload)
        self.gloabal_id_active_checkbox.setChecked(global_id_active)

    def save_device_settings(self):
        path = r"User_Data\Devices_Setting.json"

        # First, read the existing data to preserve other settings
        try:
            with open(path, mode='r', encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
           
            data = {}

        # Ensure global_settings exists
        if "global_settings" not in data:
            data["global_settings"] = {}

        # Update global settings with current checkbox states
        data["global_settings"]["is_auto_upload_enabled"] = self.gloabal_auto_upload.isChecked()
        data["global_settings"]["is_id_active_enabled"] = self.gloabal_id_active_checkbox.isChecked()

        # Write the updated data back to the file
        with open(path, mode='w', encoding="utf-8") as f:
            json.dump(data, f, indent=4) 

# Add this method to your MainWindow class to replace the empty apply_theme() method

    def apply_theme(self):
        """Apply theme styling to all widgets based on theme_mode and theme_color"""
        
        # Define color schemes
        if self.theme_mode == "light":
            # Light theme colors
            bg_color = "#FFFFFF"
            text_color = "#000000"
            widget_bg = "#F5F5F5"
            border_color = "#CCCCCC"
            hover_color = "#E0E0E0"
            input_bg = "#FFFFFF"
            tab_bg = "#F8F8F8"
            tab_selected = "#FFFFFF"
            button_bg = "#E0E0E0"
            button_hover = "#D0D0D0"
            checkbox_bg = "#FFFFFF"
            frame_bg = "#FAFAFA"
        else:
            # Dark theme colors  
            bg_color = "#2B2B2B"
            text_color = "#FFFFFF"
            widget_bg = "#3C3C3C"
            border_color = "#555555"
            hover_color = "#4A4A4A"
            input_bg = "#404040"
            tab_bg = "#333333"
            tab_selected = "#2B2B2B"
            button_bg = "#404040"
            button_hover = "#505050"
            checkbox_bg = "#404040"
            frame_bg = "#353535"
        
        # Apply accent color based on theme_color
        accent_colors = {
            "blue": "#1B56FD",
            "green": "#4CAF50", 
            "red": "#F44336",
            "purple": "#9C27B0",
            "orange": "#FF9800"
        }
        accent_color = accent_colors.get(self.theme_color, "#1B56FD")
        
        # Main application stylesheet
        main_style = f"""
        QMainWindow {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        QWidget {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        
        QTabWidget::pane {{
            border: 1px solid {border_color};
            background-color: {widget_bg};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: {tab_bg};
            color: {text_color};
            padding: 8px 16px;
            margin: 2px;
            border: 1px solid {border_color};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            min-width: 80px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {tab_selected};
            color: {text_color};
            border-bottom: 2px solid {accent_color};
            font-weight: bold;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {hover_color};
        }}
        
        QFrame {{
            background-color: {frame_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 8px;
        }}
        
        QLabel {{
            color: {text_color};
            background-color: transparent;
            border: none;
        }}
        
        QPushButton {{
            background-color: {button_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {button_hover};
            border-color: {accent_color};
        }}
        
        QPushButton:pressed {{
            background-color: {accent_color};
            color: white;
        }}
        
        QPushButton:disabled {{
            background-color: {border_color};
            color: #888888;
            border-color: #AAAAAA;
        }}
        
        QComboBox {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 4px 8px;
            min-height: 20px;
        }}
        
        QComboBox:hover {{
            border-color: {accent_color};
        }}
        
        QComboBox::drop-down {{
            border: none;
            background-color: transparent;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {text_color};
            margin-right: 5px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            selection-background-color: {accent_color};
            selection-color: white;
        }}
        
        QCheckBox {{
            color: {text_color};
            background-color: transparent;
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            background-color: {checkbox_bg};
            border: 1px solid {border_color};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {accent_color};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {accent_color};
            border-color: {accent_color};
            image: none;
        }}
        
        QCheckBox::indicator:checked::after {{
            content: "✓";
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}
        
        QScrollArea {{
            background-color: {widget_bg};
            border: 1px solid {border_color};
            border-radius: 8px;
        }}
        
        QScrollBar:vertical {{
            background-color: {widget_bg};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {border_color};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {accent_color};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QLineEdit {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 13px;
        }}
        
        QLineEdit:focus {{
            border-color: {accent_color};
            border-width: 2px;
        }}
        
        QTextEdit {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px;
            font-size: 13px;
        }}
        
        QTextEdit:focus {{
            border-color: {accent_color};
            border-width: 2px;
        }}
        
        QSpinBox, QDoubleSpinBox {{
            background-color: {input_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 4px 8px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {accent_color};
            border-width: 2px;
        }}
        
        QProgressBar {{
            background-color: {widget_bg};
            border: 1px solid {border_color};
            border-radius: 6px;
            text-align: center;
            color: {text_color};
        }}
        
        QProgressBar::chunk {{
            background-color: {accent_color};
            border-radius: 6px;
        }}
        
        QSlider::groove:horizontal {{
            border: 1px solid {border_color};
            height: 6px;
            background-color: {widget_bg};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {accent_color};
            border: 1px solid {accent_color};
            width: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {button_hover};
        }}
        
        /* Message Box Styling */
        QMessageBox {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        QMessageBox QLabel {{
            color: {text_color};
            background-color: transparent;
        }}
        
        QMessageBox QPushButton {{
            background-color: {button_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px 16px;
            min-width: 70px;
        }}
        
        QMessageBox QPushButton:hover {{
            background-color: {button_hover};
            border-color: {accent_color};
        }}
        
        QMessageBox QPushButton:pressed {{
            background-color: {accent_color};
            color: white;
        }}
        
        /* Dialog Styling */
        QDialog {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        QDialog QLabel {{
            color: {text_color};
        }}
        
        QDialog QPushButton {{
            background-color: {button_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 6px 16px;
        }}
        
        QDialog QPushButton:hover {{
            background-color: {button_hover};
            border-color: {accent_color};
        }}
        
        QDialog QPushButton:pressed {{
            background-color: {accent_color};
            color: white;
        }}
        
        /* Tooltip styling */
        QToolTip {{
            background-color: {widget_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 12px;
        }}
        
        /* Menu styling */
        QMenu {{
            background-color: {widget_bg};
            color: {text_color};
            border: 1px solid {border_color};
            border-radius: 6px;
            padding: 4px;
        }}
        
        QMenu::item {{
            background-color: transparent;
            padding: 6px 16px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {accent_color};
            color: white;
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {border_color};
            margin: 4px 8px;
        }}
        """
        
        # Apply the stylesheet to the main application
        self.setStyleSheet(main_style)
        
        # Also apply to the QApplication to ensure all dialogs are themed
        app = QApplication.instance()
        if app:
            app.setStyleSheet(main_style)

    def start_background_task(self):
        threading.Thread(target=background_task, daemon=True).start()

    def closeEvent(self, event):
        threading.Thread(target=self.activity_ctrl.quit_all_task, daemon=True).start()
        event.accept()
        
        
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


class SplashScreen(QSplashScreen):
    def __init__(self):
        # Resolve the splash image path relative to the script's location (more robust)
        script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        splash_path = r"geni\geni_ui_src\ui_assets\Icons\splash_screen_small.png"
        
        # Load and validate the pixmap
        pixmap = QPixmap(splash_path)
        if pixmap.isNull():
            # Fallback to a blank or default pixmap if image fails to load
            print(f"Warning: Could not load splash image from {splash_path}. Using blank pixmap.")
            pixmap = QPixmap(800, 600)  # Or load a bundled fallback image
        
        # Optional: Scale if needed (uncomment and adjust as required)
        # pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        super().__init__(pixmap)
        
        # Set splash screen properties
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Initial opacity (start at 0 for fade-in)
        self.setWindowOpacity(0.0)
        
        # Initial loading message
        self.showMessage("Loading GeniFlow...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, QColor(Qt.GlobalColor.white))

        # Timer to periodically raise the window (for reliable "stays on top")
        self._raise_timer = QTimer()
        self._raise_timer.timeout.connect(self.raise_)
        self._raise_timer.setInterval(50)  # Every 50ms during display

    def show_with_fade_in(self, duration=1000):
        """
        Show the splash with a fade-in animation, ensuring it's not minimized.
        
        Args:
            duration (int): Animation duration in milliseconds (default: 1000ms).
        """
        self.show()
        self._ensure_visible()  # Prevent minimized state
        self._raise_timer.start()  # Start raising timer
        self._fade_in(duration)

    def _ensure_visible(self):
        """Ensure the window is visible, active, and not minimized."""
        if self.windowState() & Qt.WindowState.WindowMinimized:
            self.setWindowState(Qt.WindowState.WindowNoState)  # Restore from minimized
        self.raise_()
        self.activateWindow()

    def _fade_in(self, duration=1000):
        """Internal method to animate fade-in from 0 to 1 opacity."""
        self._opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self._opacity_animation.setDuration(duration)
        self._opacity_animation.setStartValue(0.0)
        self._opacity_animation.setEndValue(1.0)
        self._opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._opacity_animation.start()

    def fade_out_and_finish(self, main_window, duration=500):
        """
        Fade out the splash and finish it, transferring to the main window.
        
        Args:
            main_window: The main window to finish with.
            duration (int): Animation duration in milliseconds (default: 500ms).
        """
        self._raise_timer.stop()  # Stop raising timer
        self._fade_out(duration, lambda: self.finish(main_window))

    def _fade_out(self, duration=300, callback=None):
        """Internal method to animate fade-out from 1 to 0 opacity, then call callback."""
        self._opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self._opacity_animation.setDuration(duration)
        self._opacity_animation.setStartValue(1.0)
        self._opacity_animation.setEndValue(0.0)
        self._opacity_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        def on_finished():
            if callback:
                callback()
        
        self._opacity_animation.finished.connect(on_finished)
        self._opacity_animation.start()

    def update_message(self, message: str):
        """Dynamically update the loading message (e.g., for progress steps)."""
        self.showMessage(message, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, QColor(Qt.GlobalColor.white))
        self.repaint()  # Ensure immediate refresh

def start_loading_sequence(splash):
    """Chain non-blocking loading steps with QTimers."""
    def step1():
        splash.update_message("Initializing core modules...")
        QTimer.singleShot(1000, step2)  # 1s delay

    def step2():
        splash.update_message("Loading UI components...")
        QTimer.singleShot(500, step3)  # 1s delay

    def step3():
        splash.update_message("Connecting to database...")
        QTimer.singleShot(1000, step4)  # 1s delay

    def step4():
        splash.update_message("Finalizing setup...")
        QTimer.singleShot(500, create_window)  # 1s delay

    def create_window():
        global window  # Or handle differently if preferred
        window = MainWindow()
        window.show()
        splash.fade_out_and_finish(window, duration=800)  # Fade out to main window

    # Kick off the sequence
    step1()

if __name__ == "__main__":
    # Call setup after app init if it needs Qt (move if not)
    app = QApplication(sys.argv)
    
    # Add attributes to prevent console flashing
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, True)
    
    # If setup_application() needs Qt, call it here; otherwise, before app
    setup_application()
    
    # Uncomment if needed (ensure it's non-blocking)
    update_single_package("yt-dlp")

    splash = SplashScreen()
    splash.show_with_fade_in(duration=100)  # Slightly longer for smoother feel
    
    # Start the async loading sequence
    start_loading_sequence(splash)

    sys.exit(app.exec())
        
