from pickle import FALSE
import sys
import os
import json
from PySide6.QtWidgets import (QApplication, QWidget, QDialog, QLabel, QFrame, QComboBox, 
                             QLineEdit, QCheckBox, QTextEdit, QPushButton, QFileDialog,QDoubleSpinBox,
                             QHBoxLayout, QVBoxLayout, QGridLayout, QSpinBox, QMessageBox,QAbstractSpinBox,QSizePolicy,QGroupBox)
from PySide6.QtCore import Qt, QObject, Signal, Property, QSize,QPropertyAnimation
from PySide6.QtGui import QIcon, QPixmap, QFont
from click import group
import shiboken6

from geni_ui_src.TimePickerWidget import MainScheduleTimeWidget
class ConfigureWindow(QDialog):
    def __init__(self, save_callback=None, json_file_path=r"User_Data\Page_manager.json", id_frame_idx=1, profile_name="", parent=None):
        super().__init__(parent)

        # Initialize variables
        self.current_downloader_frame = None
        self.auto_download=False
        self.selected_download_from = "Youtube"  
        self.title_from_var = "From Original Video"  
        self.link_or_id = ""
        self.no_of_video_to_download = "1"  
        self.video_qulity = "1080"  

        self.text_box_var = ""
        self.txt_file_path_var = ""
        self.Random_var = False


        self.enable_goup_sharing = False
        self.igonre_group_name = False
        self.num_of_group_sharing = 1
        self.groups_name_text = ""


        self.reels_history_var = ""

        self.save_callback = save_callback
        self.json_file_path = json_file_path
        self.id_frame_idx = id_frame_idx
        self.profile_name = profile_name

        # Setup window properties
        self.WindowSetup()
        
        # Create basic UI structure (without populating content frames yet)
        self._create_base_ui()
        
        # Now initialize the UI with the loaded data
        self.initialize_ui_with_data()
        
    def closeEvent(self, event):
        self.on_closing()
        event.accept()
        
    def WindowSetup(self):
        self.setWindowTitle("Configure")
        
        try:
            icon_path = os.path.join("geni", "geni_ui_src", "ui_assets", "Icons", "geni_logo_png.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print("Icon not set:", e)
        
        # Set window dimensions
        screen_rect = QApplication.primaryScreen().geometry()
        width = int(screen_rect.width() * 0.7)
        height = int(screen_rect.height() * 0.7)
        x = (screen_rect.width() - width) // 2
        y = (screen_rect.height() - height) // 2
        
        self.setGeometry(x, y, width, height)
        self.setMinimumSize(600, 400)

        
    def _create_base_ui(self):
        """Create just the base UI structure without populating content"""
        # Create main layout for the dialog
        main_layout = QVBoxLayout(self)
        
        # Add a QComboBox at the top
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Configuration Type:")
        selector_layout.addWidget(selector_label)
        
        self.config_type_selector = QComboBox()
        self.config_type_selector.addItems(["Reels", "Video", "Bonus","Story"])
        # Don't connect signal yet - will do that after UI is fully built
        selector_layout.addWidget(self.config_type_selector)
        selector_layout.addStretch(1)
        main_layout.addLayout(selector_layout)
        
        # Create the main frame that will hold the changing content
        self.main_content_frame = QFrame()
        self.main_content_frame.setObjectName("main_content_frame")
        self.main_content_frame.setStyleSheet("""QFrame#main_content_frame{
                                            border:2px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.1);}""")
        
        self.main_content_layout = QVBoxLayout(self.main_content_frame)
        
        main_layout.addWidget(self.main_content_frame)
        
        # Add buttons at the bottom
        button_layout = QHBoxLayout()
        save_button = AnimatedHoverButton(text="Save")
        save_button.setFixedSize(QSize(60,25))
        save_button.clicked.connect(self.on_closing)
        button_layout.addStretch(1)
        button_layout.addWidget(save_button)
        main_layout.addLayout(button_layout)
        
    def initialize_ui_with_data(self):
        """Initialize UI with loaded data after configuration is loaded"""
        # Load initial data for "Reels" (default) config
        self.load_configuration_data("reels")
        
        # Set the selected config type and populate the content frame
        self.config_type_selector.setCurrentText("Reels")
        self.refresh_main_frame("Reels")
        
        # Set download source in combobox if available
        if hasattr(self, 'download_combobox'):
            self.download_combobox.setCurrentText(self.selected_download_from)
            # Initialize the download frame based on selected source
            self.download_entry_label_manager(self.selected_download_from)
        
        # Now connect the combobox signal - after initial setup is complete
        self.config_type_selector.currentTextChanged.connect(self.on_config_type_changed)
    
    def on_config_type_changed(self, selected_type):
        """Handle config type change - load new data and refresh UI"""
        # Map the UI selection to the proper JSON key
        config_type_map = {
            "Reels": "reels",
            "Video": "videos",
            "Bonus": "image",
            "Story": "story"
        }
        config_type = config_type_map.get(selected_type, "reels")
        
        # Load the configuration for the selected type
        self.load_configuration_data(config_type)
        
        # Refresh the UI with the new data
        self.refresh_main_frame(selected_type)
    
    def _create_widget(self):
        """Legacy method - redirects to new method structure"""
        self._create_base_ui()
    
    def refresh_main_frame(self, selected_type):
        """Completely refresh the main content frame with new content"""
        # Clear the main content frame
        while self.main_content_layout.count():
            item = self.main_content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        # Reset the current_downloader_frame reference
        self.current_downloader_frame = None
        
        # Populate the frame based on selection
        if selected_type == "Reels":
            self.populate_reels_configure()
        elif selected_type == "Video":
            self.populate_video_configure()
        elif selected_type == "Bonus":
            self.populate_bonus_configure()
        elif selected_type == "Story":
            self.populate_story_configure()
    
    def populate_reels_configure(self):
            # Add title
            download_configure_label = QLabel("Reels Configuration")
            font = QFont("arial", 12)
            font.setBold(True)
            download_configure_label.setFont(font)
            self.main_content_layout.addWidget(download_configure_label)

            # Add download frame
            download_frame = self.downloadconfigure()
            self.main_content_layout.addWidget(download_frame)

            # Add horizontal container frame 
            caption_frame = QFrame(self.main_content_frame)
            caption_frame.setFrameStyle(QFrame.NoFrame) 
            caption_frame.setStyleSheet("background: transparent;") 

            captions_group_sharing = QGridLayout(caption_frame)
            captions_group_sharing.setContentsMargins(0, 0, 0, 0) 
            captions_group_sharing.setSpacing(5) 

            # Add Auto Edit section
            caption_groupbox = self.add_captions_section()
            group_sharing_groupbox = self.group_sharing_frame()

            captions_group_sharing.addWidget(caption_groupbox, 0, 0)
            captions_group_sharing.addWidget(group_sharing_groupbox, 0, 1)

            captions_group_sharing.setColumnStretch(0, 70)
            captions_group_sharing.setColumnStretch(1, 30)
            self.main_content_layout.addWidget(caption_frame)

            #schedule time group 
            self.schdule_time = MainScheduleTimeWidget()
            self.main_content_layout.addWidget(self.schdule_time)

            # Load schedule data into the widget
            if hasattr(self, 'schedule_times'):
                # Clear any existing entries (optional, since widget is new)
                if hasattr(self.schdule_time, 'schdule_widgets'):
                    while len(self.schdule_time.schdule_widgets) > 0:
                        widget = self.schdule_time.schdule_widgets[0]
                        self.schdule_time.remove_schedule_entry(widget)

                # Set the enable checkbox state
                if hasattr(self.schdule_time, 'enabel_schdule'):
                    self.schdule_time.enabel_schdule.setChecked(self.schedule_enable)

                # Add schedule entries
                sorted_keys = sorted([int(key) for key in self.schedule_times.keys() if key.isdigit()])
                for key in sorted_keys:
                    schedule_entry = self.schedule_times.get(str(key), {})
                    day = schedule_entry.get("day", "")
                    hour = schedule_entry.get("hour", "")
                    minute = schedule_entry.get("minute", "")
                    ampm = schedule_entry.get("ampm", "")
                    if hasattr(self.schdule_time, 'add_schedule_entry'):
                        self.schdule_time.add_schedule_entry(day=day, hour=hour, minute=minute, ampm=ampm)

            #add advance reels editing sections
            configure_download_frame = QGroupBox()
            configure_download_frame.setTitle("Advance Auto Video Edits")
            configure_download_frame.setObjectName("configure_download_frame")
            configure_download_frame.setStyleSheet("""QGroupBox#configure_download_frame{
                                            border:2px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            padding-top:5px;
                                            margin-top:10px;
                                            padding-right:10px;
                                            padding-left:10px;
                                            padding-bottom:5px;
                                            background-color: rgba(128,128,128,0.2);}

                                            QGroupBox#configure_download_frame::title {
                                                subcontrol-origin: margin;
                                                subcontrol-position: top left;
                                                left: 30px;
                                                border-radius:5px;
                                                padding-left: 5px;
                                                padding-right: 5px;
                                                background-color: rgba(128,128,128,0.5);
                                            }""")

            configure_layout = QHBoxLayout(configure_download_frame)

            config_label = QLabel("Advance Video Edits Configure: ")
            configure_layout.addWidget(config_label)

            configure_download_btn = AnimatedHoverButton(text="Configure")
            configure_download_btn.setFixedSize(100, 50)
            configure_download_btn.clicked.connect(self.create_comming_soon_window)
            configure_layout.addWidget(configure_download_btn)

            configure_layout.addStretch(1)
            self.main_content_layout.addWidget(configure_download_frame)

            if hasattr(self, 'download_combobox'):
                self.download_entry_label_manager(self.download_combobox.currentText())

    
    def populate_video_configure(self):
        # Add title
        title_label = QLabel("Video Configuration")
        font = QFont("arial", 12)
        font.setBold(True)
        title_label.setFont(font)
        self.main_content_layout.addWidget(title_label)

        # Add download frame
        download_frame = self.downloadconfigure()
        self.main_content_layout.addWidget(download_frame)
        
       

        # Add horizontal container frame 
        caption_frame = QFrame(self.main_content_frame)
        caption_frame.setFrameStyle(QFrame.NoFrame) 
        caption_frame.setStyleSheet("background: transparent;") 
        captions_group_sharing = QGridLayout(caption_frame)
        captions_group_sharing.setContentsMargins(0, 0, 0, 0) 
        captions_group_sharing.setSpacing(5) 
        # Add Auto Edit section
        caption_groupbox = self.add_captions_section()
        group_sharing_groupbox = self.group_sharing_frame()
        captions_group_sharing.addWidget(caption_groupbox, 0, 0)
        captions_group_sharing.addWidget(group_sharing_groupbox, 0, 1)
        captions_group_sharing.setColumnStretch(0, 70)
        captions_group_sharing.setColumnStretch(1, 30)
        self.main_content_layout.addWidget(caption_frame)



        #schedule time group 
        self.schdule_time = MainScheduleTimeWidget()
        self.main_content_layout.addWidget(self.schdule_time)

                # Load schedule data into the widget
        if hasattr(self, 'schedule_times'):
            # Clear any existing entries (optional, since widget is new)
            if hasattr(self.schdule_time, 'schdule_widgets'):
                while len(self.schdule_time.schdule_widgets) > 0:
                    widget = self.schdule_time.schdule_widgets[0]
                    self.schdule_time.remove_schedule_entry(widget)

            # Set the enable checkbox state
            if hasattr(self.schdule_time, 'enabel_schdule'):
                self.schdule_time.enabel_schdule.setChecked(self.schedule_enable)

            # Add schedule entries
            sorted_keys = sorted([int(key) for key in self.schedule_times.keys() if key.isdigit()])
            for key in sorted_keys:
                schedule_entry = self.schedule_times.get(str(key), {})
                day = schedule_entry.get("day", "")
                hour = schedule_entry.get("hour", "")
                minute = schedule_entry.get("minute", "")
                ampm = schedule_entry.get("ampm", "")
                if hasattr(self.schdule_time, 'add_schedule_entry'):
                    self.schdule_time.add_schedule_entry(day=day, hour=hour, minute=minute, ampm=ampm)

        # Advanced video edits section
        configure_download_frame = QGroupBox()
        configure_download_frame.setTitle("Advance Auto Video Edits")
        configure_download_frame.setObjectName("configure_download_frame")
        configure_download_frame.setStyleSheet("""QGroupBox#configure_download_frame{
                                        border:2px solid rgba(128,128,128,0.8);
                                        border-radius:8px;
                                        padding-top:5px;
                                        margin-top:10px;
                                        padding-right:10px;
                                        padding-left:10px;
                                        padding-bottom:5px;
                                        background-color: rgba(128,128,128,0.2);}

                                        QGroupBox#configure_download_frame::title {
                                            subcontrol-origin: margin;
                                            subcontrol-position: top left;
                                            left: 30px;
                                            border-radius:5px;
                                            padding-left: 5px;
                                            padding-right: 5px;
                                            background-color: rgba(128,128,128,0.5);
                                        }""")

        configure_layout = QHBoxLayout(configure_download_frame)
        
        config_label = QLabel("Advance Video Edits Configure: ")
        configure_layout.addWidget(config_label)
        
        configure_download_btn = AnimatedHoverButton(text="Configure")
        configure_download_btn.setFixedSize(100, 50)
        configure_download_btn.clicked.connect(self.create_comming_soon_window)
        configure_layout.addWidget(configure_download_btn)

        if hasattr(self, 'download_combobox'):
            self.download_entry_label_manager(self.download_combobox.currentText())

        configure_layout.addStretch(1)
        self.main_content_layout.addWidget(configure_download_frame)
    
    def populate_bonus_configure(self):
        # Add title
        title_label = QLabel("Bonus Configuration")
        font = QFont("arial", 12)
        font.setBold(True)
        title_label.setFont(font)
        self.main_content_layout.addWidget(title_label)
        
        # Add download frame
        download_frame = self.downloadconfigure(combo_box_value=["Pinterest"])
        self.main_content_layout.addWidget(download_frame)

        
        # Add horizontal container frame 
        caption_frame = QFrame(self.main_content_frame)
        caption_frame.setFrameStyle(QFrame.NoFrame) 
        caption_frame.setStyleSheet("background: transparent;") 
        captions_group_sharing = QGridLayout(caption_frame)
        captions_group_sharing.setContentsMargins(0, 0, 0, 0) 
        captions_group_sharing.setSpacing(5) 
        # Add Auto Edit section
        caption_groupbox = self.add_captions_section()
        group_sharing_groupbox = self.group_sharing_frame()
        captions_group_sharing.addWidget(caption_groupbox, 0, 0)
        captions_group_sharing.addWidget(group_sharing_groupbox, 0, 1)
        captions_group_sharing.setColumnStretch(0, 70)
        captions_group_sharing.setColumnStretch(1, 30)
        self.main_content_layout.addWidget(caption_frame)
        
        #schedule time group 
        self.schdule_time = MainScheduleTimeWidget()
        self.main_content_layout.addWidget(self.schdule_time)

        # Load schedule data into the widget
        if hasattr(self, 'schedule_times'):
            # Clear any existing entries (optional, since widget is new)
            if hasattr(self.schdule_time, 'schdule_widgets'):
                while len(self.schdule_time.schdule_widgets) > 0:
                    widget = self.schdule_time.schdule_widgets[0]
                    self.schdule_time.remove_schedule_entry(widget)

            # Set the enable checkbox state
            if hasattr(self.schdule_time, 'enabel_schdule'):
                self.schdule_time.enabel_schdule.setChecked(self.schedule_enable)

            # Add schedule entries
            sorted_keys = sorted([int(key) for key in self.schedule_times.keys() if key.isdigit()])
            for key in sorted_keys:
                schedule_entry = self.schedule_times.get(str(key), {})
                day = schedule_entry.get("day", "")
                hour = schedule_entry.get("hour", "")
                minute = schedule_entry.get("minute", "")
                ampm = schedule_entry.get("ampm", "")
                if hasattr(self.schdule_time, 'add_schedule_entry'):
                    self.schdule_time.add_schedule_entry(day=day, hour=hour, minute=minute, ampm=ampm)

        # Coming soon frame
        frame = QGroupBox()
        frame.setTitle("Advance Auto Photo Edits")
        frame.setObjectName("bonus_edit_frame")
        frame.setStyleSheet("""QGroupBox#bonus_edit_frame{
                                        border:2px solid rgba(128,128,128,0.8);
                                        border-radius:8px;
                                        padding-top:5px;
                                        margin-top:10px;
                                        padding-right:10px;
                                        padding-left:10px;
                                        padding-bottom:5px;
                                        background-color: rgba(128,128,128,0.2);}

                                        QGroupBox#bonus_edit_frame::title {
                                            subcontrol-origin: margin;
                                            subcontrol-position: top left;
                                            left: 30px;
                                            border-radius:5px;
                                            padding-left: 5px;
                                            padding-right: 5px;
                                            background-color: rgba(128,128,128,0.5);
                                        }""")
        frame_layout = QVBoxLayout(frame)
        

        this_feature_not_avl_label = QLabel("This Feature Is Aavailable In Pro Version")
        this_feature_not_avl_label.setAlignment(Qt.AlignCenter)
        this_feature_not_avl_label.setMinimumHeight(40)

        if hasattr(self, 'download_combobox'):
            self.download_entry_label_manager(self.download_combobox.currentText())
            
        frame_layout.addWidget(this_feature_not_avl_label)
        self.main_content_layout.addWidget(frame)
    
    def populate_story_configure(self):
        # Add title
        title_label = QLabel("Story Configuration")
        font = QFont("arial", 12)
        font.setBold(True)
        title_label.setFont(font)
        self.main_content_layout.addWidget(title_label)

        # Add download frame
        download_frame = self.downloadconfigure()
        self.main_content_layout.addWidget(download_frame)

        # Add Title from section
        self.add_captions_section(is_story=True)
        
        # Advanced video edits section
        configure_download_frame = QFrame()
        configure_download_frame.setObjectName("configure_download_frame")
        configure_download_frame.setStyleSheet("""QFrame#configure_download_frame{
                                            border:2px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.1);}""")

        configure_layout = QHBoxLayout(configure_download_frame)
        
        config_label = QLabel("Advance Video Edits Configure: ")
        configure_layout.addWidget(config_label)
        
        configure_download_btn = AnimatedHoverButton(text="Configure")
        configure_download_btn.setFixedSize(100, 50)
        configure_download_btn.clicked.connect(self.create_comming_soon_window)
        configure_layout.addWidget(configure_download_btn)

        if hasattr(self, 'download_combobox'):
            self.download_entry_label_manager(self.download_combobox.currentText())

        configure_layout.addStretch(1)
        self.main_content_layout.addWidget(configure_download_frame)
    
    def add_captions_section(self,is_story=False):
        # Title from section
        self.title_from_frame = QGroupBox("Caption configure")
        self.title_from_frame.setObjectName("title_from_frame")
        self.title_from_frame.setStyleSheet("""QGroupBox#title_from_frame{
                                        border:2px solid rgba(128,128,128,0.8);
                                        border-radius:8px;
                                        padding-top:5px;
                                        margin-top:10px;
                                        padding-right:10px;
                                        padding-left:10px;
                                        padding-bottom:5px;
                                        background-color: rgba(128,128,128,0.2);}

                                        QGroupBox#title_from_frame::title {
                                            subcontrol-origin: margin;
                                            subcontrol-position: top left;
                                            left: 30px;
                                            border-radius:5px;
                                            padding-left: 5px;
                                            padding-right: 5px;
                                            background-color: rgba(128,128,128,0.5);
                                        }""")
        title_from_layout = QVBoxLayout(self.title_from_frame)

        # Create the combobox layout first
        combobox_layout = QHBoxLayout()

        title_from_label = QLabel("Title From")
        combobox_layout.addWidget(title_from_label)

        title_from_combobox = QComboBox()
        title_from_combobox.addItems(["From Original Video", "From Text Box", "From text file"])
        title_from_combobox.setCurrentText(self.title_from_var)
        title_from_combobox.currentTextChanged.connect(self.From_original_video)
        combobox_layout.addWidget(title_from_combobox)
        combobox_layout.setAlignment(Qt.AlignLeft)

        # Add the combobox layout first
        title_from_layout.addLayout(combobox_layout)

        # Message frame for title options
        self.title_from_msg_frame = QFrame()
        self.title_from_msg_frame.setObjectName("title_from_msg_frame")
        self.title_from_msg_frame.setStyleSheet("""QFrame#title_from_msg_frame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.1);}""")

        self.title_from_msg_frame_layout = QHBoxLayout(self.title_from_msg_frame)
        title_from_layout.addWidget(self.title_from_msg_frame)

        # Add stretch at the end, not the beginning
        title_from_layout.addStretch(1)

        # Apply the current title from setting
        self.From_original_video(self.title_from_var)

        if is_story:
            self.main_content_layout.addWidget(self.title_from_frame)
        else:
            return self.title_from_frame
        
    def downloadconfigure(self,combo_box_value = ["Youtube", "Instagram", "TikTok", "Twitter"]):
        self.download_frame = QGroupBox()
        self.download_frame.setObjectName("download_frame")
        self.download_frame.setTitle("Download Configuration")
        self.download_frame.setStyleSheet("""QGroupBox#download_frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#download_frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")

        download_layout = QVBoxLayout(self.download_frame)
        
        self.local_auto_download_cheackbox =QCheckBox("Enable Auto Download")
        self.local_auto_download_cheackbox.setChecked(self.auto_download)
        download_layout.addWidget(self.local_auto_download_cheackbox)
        # Download From Frame
        download_from_frame = QFrame()
        download_from_layout = QHBoxLayout(download_from_frame)
        
        download_from_label = QLabel("Download From")
        download_from_layout.addWidget(download_from_label)
        
        self.download_combobox = QComboBox()
        self.download_combobox.addItems(combo_box_value)
        self.download_combobox.setCurrentText(self.selected_download_from)
        self.download_combobox.currentTextChanged.connect(self.download_entry_label_manager)
        download_from_layout.addWidget(self.download_combobox)
        

        download_from_layout.addStretch(1)
        download_layout.addWidget(download_from_frame)
        
        return self.download_frame
        
    def download_entry_label_manager(self, value):
        """Handle changing the downloader frame when the download source is changed"""
       
        if self.current_downloader_frame is not None:
            
            if shiboken6.isValid(self.current_downloader_frame):
               
                self.download_frame.layout().removeWidget(self.current_downloader_frame)
               
                self.current_downloader_frame.hide()
  
                self.current_downloader_frame.deleteLater()

            self.current_downloader_frame = None


        frame = self.downloader_frame()
        if frame is not None:
            self.current_downloader_frame = frame
            self.download_frame.layout().addWidget(self.current_downloader_frame)

        self.selected_download_from = value
        print("button clicked, value:", value)
        
    def downloader_frame(self):
        selected_download_option = self.download_combobox.currentText()
        
        label_text = "Channel ID"
        
        if selected_download_option == "Youtube":
            label_text = "Channel ID:"
        elif selected_download_option in ["Instagram", "TikTok", "Twitter"]:
            label_text = "ID Name:"
        elif selected_download_option in ["Pinterest"]:
            label_text = "Topic To Search:"
        else:
            return None
            
        frame = QFrame()
        frame.setObjectName("donwloder_entry_frame")
        frame.setStyleSheet("""QFrame#donwloder_entry_frame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.1);}""")
        frame_layout = QHBoxLayout(frame)
        
        # ID Label
        id_label = QLabel(label_text)
        frame_layout.addWidget(id_label)
        
        # ID Input field
        id_entry = QLineEdit()
        id_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);          
                       
                border: 1px solid rgba(128,128,128,1);           
                border-radius: 8px;                 
                padding: 2px 2px 2px 10px;           
                selection-background-color: #555555;
            }
            QLineEdit::placeholder {
                color: #888888;                    
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);      
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);         
            }
        """)
        id_entry.setText(self.link_or_id)
        id_entry.textChanged.connect(lambda text: setattr(self, 'link_or_id', text))
        id_entry.setMinimumWidth(500)
        frame_layout.addWidget(id_entry)
        
        # Number of videos label
        videos_label = QLabel("No. of videos to download")
        frame_layout.addWidget(videos_label)
        
        # Number of videos spinbox
        self.no_of_video = IntSpinBox()
        self.no_of_video.set_value(int(self.no_of_video_to_download))
        frame_layout.addWidget(self.no_of_video)
        
        # Video quality label
        quality_label = QLabel("Max Video Quality")
        frame_layout.addWidget(quality_label)
        
        # Video quality combobox
        quality_combobox = QComboBox()
        quality_combobox.addItems(["Best", "Medium", "Low"])
        quality_combobox.setCurrentText(self.video_qulity)
        quality_combobox.currentTextChanged.connect(lambda text: setattr(self, 'video_qulity', text))
        frame_layout.addWidget(quality_combobox)
        
        return frame
    
    def group_sharing_frame(self):
        
        self.group_sharing_groupbox = QGroupBox()
        self.group_sharing_groupbox.setObjectName("group_sharing_groupbox")
        self.group_sharing_groupbox.setTitle("Group Sharing")
        self.group_sharing_groupbox.setStyleSheet("""QGroupBox#group_sharing_groupbox{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#group_sharing_groupbox::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        
        group_sharing_layout = QGridLayout(self.group_sharing_groupbox)
        

        group_name_and_label_frame = QFrame(self.group_sharing_groupbox)
        group_name_and_label_frame.setObjectName("group_name_and_label_frame")

        group_name_and_label_frame.setStyleSheet("""QFrame#group_name_and_label_frame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.1);}"""
                                                 )
        
        group_names_and_label_layout = QVBoxLayout(group_name_and_label_frame)

        groups_name_label = QLabel("Groups Name:")
        group_names_and_label_layout.addWidget(groups_name_label)

        self.groups_name_textbox = QTextEdit()
        self.groups_name_textbox.setStyleSheet("""
                QTextEdit {
                background-color: rgba(128,128,128,.3);          
                color: #eeeeee;                     
                border: 1px solid rgba(128,128,128,1);           
                border-radius: 8px;                 
                padding: 2px 2px 2px 10px;           
                selection-background-color: #555555;
            }
            QTextEdit::placeholder {
                color: #888888;                    
            }
            QTextEdit:focus {
                border: 1px solid rgba(128,128,128,1);      
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QTextEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);         
            }
        """)

        self.groups_name_textbox.setMinimumSize(400, 100)
        self.groups_name_textbox.setPlaceholderText("Group1,Group2,Group3")
        self.groups_name_textbox.setText(self.groups_name_text)
        group_names_and_label_layout.addWidget(self.groups_name_textbox)
        


        num_of_share_frame = QFrame(self.group_sharing_groupbox)
        num_of_share_frame.setObjectName("num_of_share_frame")
        num_of_share_frame.setStyleSheet("""QFrame#num_of_share_frame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.1);}""")
                                            
        num_of_share_layout = QVBoxLayout(num_of_share_frame)

        self.is_group_sharing_enable = QCheckBox("Enable Sharing")
        self.is_group_sharing_enable.setChecked(self.enable_goup_sharing)
        num_of_share_layout.addWidget(self.is_group_sharing_enable)

        

        self.ignore_name = QCheckBox("Ignore Name")
        self.ignore_name.setChecked(self.igonre_group_name)
        num_of_share_layout.addWidget(self.ignore_name)

        
        self.num_of_share_spinbox = SmallIntSpinBox(save_callback=self.save_callback,support_float=False)
        Share_to_group_label = QLabel("Group Num:")
        self.num_of_share_spinbox.set_value(self.num_of_group_sharing)
        num_of_share_layout.addWidget(Share_to_group_label)
        num_of_share_layout.addWidget(self.num_of_share_spinbox)


        num_of_share_layout.addStretch(1)
        
        group_sharing_layout.addWidget(num_of_share_frame,0,0)
        group_sharing_layout.addWidget(group_name_and_label_frame,0,1)

        return self.group_sharing_groupbox

        
    def From_original_video(self, value):
        # Clear existing widgets
        for i in reversed(range(self.title_from_msg_frame_layout.count())):
            widget = self.title_from_msg_frame_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        self.title_from_var = value
        
        if value == "From Original Video":
            label = QLabel("Now title of video will be taken from original video")
            self.title_from_msg_frame_layout.addWidget(label)
            
        elif value == "From Text Box":
            label = QLabel("Text Box: ")
            self.title_from_msg_frame_layout.addWidget(label)
            
            self.title_text_box = QTextEdit()
            self.title_text_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(128,128,128,.3);          
                color: #eeeeee;                     
                border: 1px solid rgba(128,128,128,1);           
                border-radius: 8px;                 
                padding: 2px 2px 2px 10px;           
                selection-background-color: #555555;
            }
            QTextEdit::placeholder {
                color: #888888;                    
            }
            QTextEdit:focus {
                border: 1px solid rgba(128,128,128,1);      
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QTextEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);         
            }
        """)
            self.title_text_box.setMinimumSize(400, 100)
            self.title_text_box.setText(self.text_box_var)
            self.title_from_msg_frame_layout.addWidget(self.title_text_box)
            
        elif value == "From text file":
            label = QLabel("Text File Path: ")
            self.title_from_msg_frame_layout.addWidget(label)
            
            path_entry = QLineEdit()
            path_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);          
                
                border: 1px solid rgba(128,128,128,1);           
                border-radius: 8px;                 
                padding: 2px 2px 2px 10px;           
                selection-background-color: #555555;
            }
            QLineEdit::placeholder {
                color: #888888;                    
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);      
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);         
            }
        """)
            path_entry.setMinimumWidth(300)
            path_entry.setText(self.txt_file_path_var)
            path_entry.textChanged.connect(lambda text: setattr(self, 'txt_file_path_var', text))
            self.title_from_msg_frame_layout.addWidget(path_entry)
            
            browse_btn = AnimatedHoverButton(text="Browse")
            browse_btn.clicked.connect(self.browse_txt_file)
            browse_btn.setFixedSize(80, 30)
            self.title_from_msg_frame_layout.addWidget(browse_btn)
            
            random_checkbox = QCheckBox("Random")
            random_checkbox.setChecked(self.Random_var)
            random_checkbox.stateChanged.connect(lambda state: setattr(self, 'Random_var', bool(state)))
            self.title_from_msg_frame_layout.addWidget(random_checkbox)
            
        else:
            label = QLabel("None")
            self.title_from_msg_frame_layout.addWidget(label)
            
    def create_comming_soon_window(self):
        window = QDialog(self)
        window.setWindowTitle("Feature Not Aavailable")
        window.setFixedSize(600, 500)
        
        # Try to set window icon
        try:
            icon_path = os.path.join("geni", "geni_ui_src", "ui_assets", "Icons", "geni_logo_png.png")
            if os.path.exists(icon_path):
                window.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print("Failed to set icon:", e)
            
        layout = QVBoxLayout(window)
        
        label = QLabel("This Feature Is Aavailable In Pro Version")
        font = QFont("Arial", 20)
        font.setBold(True)
        label.setFont(font)
        label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label)
        
        window.exec()
        
    def load_configuration_data(self, ui_type):
        """
        Load configuration data from JSON for the configure window
    
        Parameters:
        ui_type (str): The UI type to load (reels, videos, image, story)
        """
        try:
            # Map UI type to JSON key
            type_map = {
                "reels": "reels",
                "videos": "videos", 
                "image": "image",
                "story": "story"
            }
            config_type = type_map.get(ui_type, ui_type)  # Use as-is if not in map
    
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
    
            id_key = f"Id_information.{self.id_frame_idx}"
    
            if id_key not in data:
                print(f"Error: {id_key} not found in JSON data")
                return
    
            profile_name_normalized = self.profile_name.strip().lower()
            id_data = data[id_key]
    
            # First check if this is an ID profile
            id_name = id_data.get("id_name", "").strip().lower()
    
            # We're working with an ID or a page
            if id_name == profile_name_normalized:
                # We're working with an ID profile
                id_info = id_data.get("ID_info", {})
                main_config_dict = id_info.get(f"{config_type}_config", {})
                self.download_folder = main_config_dict.get("download_folder", "")
                self.ld_folder =  main_config_dict.get("ld_folder", "")
                download_configs = main_config_dict.get("download_configuration", {})
                auto_video_edits = main_config_dict.get("auto_edit_preset", {})
                caption_config = main_config_dict.get("captions", {})
                schedule_config = main_config_dict.get("schedule_config", {})
                group_sharing_confg = main_config_dict.get("group_sharing_config",{})

    
                # Set download configuration values
                self.auto_download = download_configs.get("auto_download", False)
                self.selected_download_from = download_configs.get("download_from", "Youtube")
                self.link_or_id = download_configs.get("channel_link", "")
                self.no_of_video_to_download = download_configs.get("num_of_content_download", "1")
                self.video_qulity = download_configs.get("download_qulity", "Best")
                self.reels_history_var = download_configs.get("save_download_history", "")
    
                # Set title configuration values
                self.title_from_var = caption_config.get("caption_from", "From Original Video")
                self.text_box_var = caption_config.get("caption_text_box", "")
                self.txt_file_path_var = caption_config.get("txt_file_path", "")
                self.Random_var = caption_config.get("txt_random", False)
                
                self.schedule_times = schedule_config.get("schedule_time", {})
                self.schedule_enable = schedule_config.get("schedule_enable", False)

                # Settings load for group sharing config
                self.enable_goup_sharing = group_sharing_confg.get("enable_sharing",False)
                self.igonre_group_name = group_sharing_confg.get("ignore_name",False)
                self.num_of_group_sharing = group_sharing_confg.get("num_of_share",1)
                self.groups_name_text = group_sharing_confg.get("groups_name","")

    
            else:
                #  working with a page
                page_info = id_data.get("pages_information", {})
                found_page = False
    
                for key, page in page_info.items():
                    page_name = page.get("Page_Name", "").strip().lower()
                    if page_name == profile_name_normalized:
                        found_page = True
                        # Found the matching page
                        main_config_dict = page.get(f"{config_type}_config", {})

                        self.download_folder = main_config_dict.get("download_folder", "")
                        self.ld_folder =  main_config_dict.get("ld_folder", "")

                        download_configs = main_config_dict.get("download_configuration", {})
                        auto_video_edits = main_config_dict.get("auto_edit_preset", {})
                        caption_config = main_config_dict.get("captions", {})
                        schedule_config = main_config_dict.get("schedule_config", {})
                        group_sharing_confg = main_config_dict.get("group_sharing_config",{})
    
                        # Set download configuration values
                        self.auto_download = download_configs.get("auto_download", False)
                        self.selected_download_from = download_configs.get("download_from", "Youtube")
                        self.link_or_id = download_configs.get("channel_link", "")
                        self.no_of_video_to_download = download_configs.get("num_of_content_download", "1")
                        self.video_qulity = download_configs.get("download_qulity", "Best")
                        self.reels_history_var = download_configs.get("save_download_history", "")
    
                        # Set title configuration values
                        self.title_from_var = caption_config.get("caption_from", "From Original Video")
                        self.text_box_var = caption_config.get("caption_text_box", "")
                        self.txt_file_path_var = caption_config.get("txt_file_path", "")
                        self.Random_var = caption_config.get("txt_random", False)
                        
                        self.schedule_times = schedule_config.get("schedule_time", {})
                        self.schedule_enable = schedule_config.get("schedule_enable", False)

                        # Settings load for group sharing config
                        self.enable_goup_sharing = group_sharing_confg.get("enable_sharing",False)
                        self.igonre_group_name = group_sharing_confg.get("ignore_name",False)
                        self.num_of_group_sharing = group_sharing_confg.get("num_of_share",1)
                        self.groups_name_text = group_sharing_confg.get("groups_name","")


                        break
                    
                if not found_page:
                    print(f"Warning: No page named '{self.profile_name}' found. Using default values.")
    
        except Exception as e:
            print(f"Error loading configuration data: {e}")
            # Set default values
            self.auto_download = False
            self.selected_download_from = "Youtube"
            self.link_or_id = ""
            self.no_of_video_to_download = "1"
            self.video_qulity = "Best"
            self.reels_history_var = ""
            self.title_from_var = "From Original Video"
            self.text_box_var = ""
            self.txt_file_path_var = ""
            self.Random_var = False
            self.schedule_times = {}
            self.schedule_enable = False


    def save_configuration_data(self):
        """
        Save configuration data from the UI to JSON
        """
        try:
            # Get the current configuration type from the UI and map it to the correct JSON key
            ui_type = self.config_type_selector.currentText()
            type_map = {
                "Reels": "reels",
                "Video": "videos",
                "Bonus": "image",
                "Story": "story"
            }
            current_type = type_map.get(ui_type, "reels") 

            with open(self.json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            id_key = f"Id_information.{self.id_frame_idx}"

            if id_key not in data:
                print(f"Error: {id_key} not found in JSON data")
                return

            profile_name_normalized = self.profile_name.strip().lower()
            id_data = data[id_key]

            # First check if this is an ID profile
            id_name = id_data.get("id_name", "").strip().lower()

            # Collect data from UI widgets
            title_text_box = ""
            if self.title_from_var == "From Text Box":
                if hasattr(self, 'title_text_box') and self.title_text_box is not None:
                    if shiboken6.isValid(self.title_text_box):
                        title_text_box = self.title_text_box.toPlainText()
                    else:
                        title_text_box = self.text_box_var
            else:
                title_text_box = self.text_box_var

            # Get value from spinbox 
            no_of_videos = "1"
            if hasattr(self, 'no_of_video') and self.no_of_video is not None:
                if shiboken6.isValid(self.no_of_video):  
                    no_of_videos = str(self.no_of_video.get_value())
                else:
                    no_of_videos = self.no_of_video_to_download
            else:
                no_of_videos = self.no_of_video_to_download

            # Prepare configuration dictionaries
            download_folder = getattr(self, 'download_folder', '')
            ld_folder = getattr(self, 'ld_folder', '')

            download_configuration = {
                "auto_download": self.local_auto_download_cheackbox.isChecked(),
                "download_from": self.download_combobox.currentText() if hasattr(self, 'download_combobox') and shiboken6.isValid(self. download_combobox) else self.selected_download_from,
                "channel_link": self.link_or_id,
                "download_qulity": self.video_qulity,
                "num_of_content_download": no_of_videos,
                "save_download_history": self.reels_history_var
            }

            caption_configuration = {
                "caption_from": self.title_from_var,
                "caption_text_box": title_text_box,
                "txt_file_path": self.txt_file_path_var,
                "txt_random": self.Random_var
            }

            # Create the main config dictionary structure
            main_config = {
                "download_folder": download_folder,
                "ld_folder": ld_folder,
                "download_configuration": download_configuration,
                "captions": caption_configuration,
                "auto_edit_preset": {}  
            }

            # Process schedule configuration with proper validation
            schedule_config = {
                "schedule_enable": False,
                "schedule_time": {}
            }

            # Check if schedule widget exists and is valid before accessing
            if (hasattr(self, 'schdule_time') and 
                self.schdule_time is not None and 
                shiboken6.isValid(self.schdule_time)):

                # Check if enable checkbox exists and is valid
                if (hasattr(self.schdule_time, 'enabel_schdule') and 
                    self.schdule_time.enabel_schdule is not None and 
                    shiboken6.isValid(self.schdule_time.enabel_schdule)):
                    schedule_config["schedule_enable"] = self.schdule_time.enabel_schdule.isChecked()
                else:
                    # Fallback to stored value
                    schedule_config["schedule_enable"] = getattr(self, 'schedule_enable', False)

                # Get schedule information from all schedule entries
                if (hasattr(self.schdule_time, 'schdule_widgets') and 
                    len(self.schdule_time.schdule_widgets) > 0):

                    for idx, schedule_widget in enumerate(self.schdule_time.schdule_widgets):
                        # Check if the schedule widget is still valid
                        if schedule_widget is not None and shiboken6.isValid(schedule_widget):
                            # Check if all required attributes exist and are valid
                            if (hasattr(schedule_widget, 'day_value') and 
                                hasattr(schedule_widget, 'hour_value') and 
                                hasattr(schedule_widget, 'minute_value') and
                                schedule_widget.day_value is not None and
                                schedule_widget.hour_value is not None and
                                schedule_widget.minute_value is not None and
                                shiboken6.isValid(schedule_widget.day_value) and
                                shiboken6.isValid(schedule_widget.hour_value) and
                                shiboken6.isValid(schedule_widget.minute_value)):

                                day = schedule_widget.day_value.text()
                                hour = schedule_widget.hour_value.text()
                                minute = schedule_widget.minute_value.text()

                                ampm = ""
                                if (hasattr(schedule_widget, 'ampm_value') and
                                    schedule_widget.ampm_value is not None and
                                    shiboken6.isValid(schedule_widget.ampm_value)):
                                    ampm = schedule_widget.ampm_value.text()

                                # Create an entry for this schedule item
                                schedule_entry = {
                                    "day": day,
                                    "hour": hour,
                                    "minute": minute,
                                }

                                if ampm:
                                    schedule_entry["ampm"] = ampm

                                schedule_config["schedule_time"][str(idx + 1)] = schedule_entry
            else:
                # Fallback to stored schedule data if widget is not available
                schedule_config["schedule_enable"] = getattr(self, 'schedule_enable', False)
                schedule_config["schedule_time"] = getattr(self, 'schedule_times', {})

            # Add schedule_config to main_config
            main_config["schedule_config"] = schedule_config

            # Process group sharing configuration with proper validation
            group_sharing_config = {
                "enable_sharing": False,
                "ignore_name": False,
                "num_of_share": 1,
                "groups_name": ""
            }

            # Process group sharing configuration with proper validation
            group_sharing_config = {
                "enable_sharing": False,
                "ignore_name": False,
                "num_of_share": 1,
                "groups_name": ""
            }
            
            # Check if group sharing widgets exist and are valid before accessing
            if (hasattr(self, 'is_group_sharing_enable') and 
                self.is_group_sharing_enable is not None and 
                shiboken6.isValid(self.is_group_sharing_enable)):
                group_sharing_config["enable_sharing"] = self.is_group_sharing_enable.isChecked()
            else:
                group_sharing_config["enable_sharing"] = getattr(self, 'enable_goup_sharing', False)
            
            if (hasattr(self, 'ignore_name') and 
                self.ignore_name is not None and 
                shiboken6.isValid(self.ignore_name)):
                group_sharing_config["ignore_name"] = self.ignore_name.isChecked()
            else:
                group_sharing_config["ignore_name"] = getattr(self, 'igonre_group_name', False)
            
            if (hasattr(self, 'num_of_share_spinbox') and 
                self.num_of_share_spinbox is not None and 
                shiboken6.isValid(self.num_of_share_spinbox)):
                group_sharing_config["num_of_share"] = self.num_of_share_spinbox.get_value()
            else:
                group_sharing_config["num_of_share"] = getattr(self, 'num_of_group_sharing', 1)
            
            if (hasattr(self, 'groups_name_textbox') and 
                self.groups_name_textbox is not None and 
                shiboken6.isValid(self.groups_name_textbox)):
                group_sharing_config["groups_name"] = self.groups_name_textbox.toPlainText()
            else:
                group_sharing_config["groups_name"] = getattr(self, 'groups_name_text', "")
                

            # Add group_sharing_config to main_config
            main_config["group_sharing_config"] = group_sharing_config

            # Debug print to verify group_sharing_config values
            print(f"DEBUG: Group sharing config being saved: {group_sharing_config}")

            # We're working with an ID 
            if id_name == profile_name_normalized:
            
                if "ID_info" not in id_data:
                    id_data["ID_info"] = {}

                id_info = id_data["ID_info"]

                id_info[f"{current_type}_config"] = main_config

            else:
            
                if "pages_information" not in id_data:
                    id_data["pages_information"] = {}

                page_info = id_data["pages_information"]
                found = False

                for key, page in page_info.items():
                    page_name = page.get("Page_Name", "").strip().lower()
                    if page_name == profile_name_normalized:
                    
                        page[f"{current_type}_config"] = main_config
                        found = True
                        break
                    
                if not found:
                    print(f"Error: Page '{self.profile_name}' not found in {id_key}")
                    return

            # Write the updated data back to the file
            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print(f"Configuration for {current_type} saved successfully.")

            if self.save_callback:
                self.save_callback()

        except Exception as e:
            print(f"Error saving configuration data: {e}")
            QMessageBox.critical(self, "Error", f"Error saving configuration: {e}")
    

    def on_closing(self):
        """
        Called when the window is closing to save configuration
        """
        self.save_configuration_data()
        self.accept()


            
    def browse_txt_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Text File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            self.txt_file_path_var = file_path
            
            # Update the line edit if available
            for i in range(self.title_from_msg_frame_layout.count()):
                widget = self.title_from_msg_frame_layout.itemAt(i).widget()
                if isinstance(widget, QLineEdit):
                    widget.setText(file_path)
                    break
            
    def on_closing(self):
        self.save_configuration_data()
        if self.save_callback:
            self.save_callback()
         
             
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


class IntSpinBox(QWidget):
    value_changed = Signal(int)
    
    def __init__(self, parent=None, from_=1, to=100, initial=0, save_callback=None):
        super().__init__(parent)
        self.from_ = from_
        self.to = to
        self.save_callback = save_callback
        
        # Set size policies to prevent stretching
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # Remove spacing between elements
        
        # decrease_button
        self.decrease_button = AnimatedHoverButton("-", 5)
        self.decrease_button.setFixedSize(30, 20)
        self.decrease_button.clicked.connect(self.decrease)
        layout.addWidget(self.decrease_button)
        
        self.spin_box = QSpinBox()
        self.spin_box.setStyleSheet("""
            QSpinBox {
                background-color: rgba(128,128,128,.3);           /* dark background */
                border: 1px solid rgba(128,128,128,1);           /* subtle border */
                border-radius: 8px;                  /* rounded corners */
                selection-background-color: #555555; /* selection highlight */
            }
            QSpinBox::placeholder {
                color: #888888;                      /* muted placeholder */
            }
            QSpinBox:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
            }
            QSpinBox:hover {
                background-color: #323232;
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */
            }
        """)
        self.spin_box.setRange(from_, to)
        self.spin_box.setValue(initial)
        self.spin_box.setFixedSize(60, 20)  
        self.spin_box.setAlignment(Qt.AlignCenter)
        self.spin_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        layout.addWidget(self.spin_box)
        
        # increase button
        self.increase_button = AnimatedHoverButton("+", 5)
        self.increase_button.setFixedSize(30, 20)
        self.increase_button.clicked.connect(self.increase)
        layout.addWidget(self.increase_button)
        
        
        total_width = 40 + 60 + 40  
        self.setFixedSize(total_width, 20)
        
        if self.save_callback:
            self.spin_box.editingFinished.connect(self.save_callback)
            self.decrease_button.released.connect(self.save_callback)
            self.increase_button.released.connect(self.save_callback)
    
    def get_value(self):
        return self.spin_box.value()
    
    def set_value(self, value):
        self.spin_box.setValue(max(self.from_, min(self.to, value)))
    
    def increase(self):
        self.spin_box.setValue(self.spin_box.value() + 1)
        self.value_changed.emit(self.spin_box.value())
    
    def decrease(self):
        self.spin_box.setValue(self.spin_box.value() - 1)
        self.value_changed.emit(self.spin_box.value())

class SmallIntSpinBox(QWidget):
    value_changed = Signal(float)  
    
    def __init__(self, parent=None, save_callback=None, from_=1, to=1000, initial=0, support_float=True, size=0.8):
        super().__init__(parent)
        self.from_ = from_
        self.to = to
        self.size = max(0.1, size)  

        self.save_callback = save_callback
        self.support_float = support_float
        

        self.base_button_height = 20
        self.base_button_width = 30
        self.base_entry_height = 20
        self.base_entry_width = 55
        if support_float is False:
            self.base_entry_width = 45
       
        self.button_height = max(10, int(self.base_button_height * self.size))
        self.button_width = max(15, int(self.base_button_width * self.size))
        self.entry_height = max(10, int(self.base_entry_height * self.size))
        self.entry_width = max(30, int(self.base_entry_width * self.size))
        
        # Set size policies to prevent stretching
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)  
        
        # decrease_button
        self.decrease_button = AnimatedHoverIntSpainButton("-", border_radius_size=self.size)
        self.decrease_button.setFixedSize(self.button_width, self.button_height)
        self.decrease_button.clicked.connect(self.decrease)
        layout.addWidget(self.decrease_button)
        

        if support_float:
            self.spin_box = QDoubleSpinBox()
            self.spin_box.setDecimals(1) 
            self.spin_box.setSingleStep(0.1)  
        else:
            self.spin_box = QSpinBox()
        

        border_radius = max(3, int(8 * self.size))
        
        self.spin_box.setStyleSheet(f"""
            QSpinBox, QDoubleSpinBox {{
                background-color: rgba(128,128,128,.3);
                
                border: 1px solid rgba(128,128,128,1);
                border-radius: {border_radius}px;
                selection-background-color: #555555;
                font-size: {max(8, int(10 * self.size))}pt;
                padding: {max(1, int(2 * self.size))}px;
            }}
            QSpinBox::placeholder, QDoubleSpinBox::placeholder {{
                color: #888888;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid rgba(128,128,128,1);
                border-radius: {border_radius}px;
                background-color: rgba(128,128,128,.2);
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                background-color: rgba(128,128,128,.2);
                border-radius: {border_radius}px;
            }}
        """)
        
        self.spin_box.setRange(from_, to)
        self.spin_box.setValue(initial)
        self.spin_box.setFixedSize(self.entry_width, self.entry_height)
        self.spin_box.setAlignment(Qt.AlignCenter)
        self.spin_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        layout.addWidget(self.spin_box)
        
        # increase button
        self.increase_button = AnimatedHoverIntSpainButton("+", border_radius_size=self.size)
        self.increase_button.setFixedSize(self.button_width, self.button_height)
        self.increase_button.clicked.connect(self.increase)
        layout.addWidget(self.increase_button)
        
        # Calculate total 
        spacing_buffer = 15  
        total_width = self.button_width + self.entry_width + self.button_width + spacing_buffer
        total_height = max(self.button_height, self.entry_height)
        
    
        self.setFixedSize(total_width, total_height)
        
        if self.save_callback:
            self.spin_box.editingFinished.connect(self.save_callback)
            self.decrease_button.clicked.connect(self.save_callback)  
            self.increase_button.clicked.connect(self.save_callback)  
    
    def get_value(self):
        return self.spin_box.value()
    
    def set_value(self, value):
        self.spin_box.setValue(max(self.from_, min(self.to, value)))
    
    def increase(self):
        if self.support_float:
            self.spin_box.setValue(self.spin_box.value() + 0.1)
        else:
            self.spin_box.setValue(self.spin_box.value() + 1)
        self.value_changed.emit(self.spin_box.value())
    
    def decrease(self):
        if self.support_float:
            self.spin_box.setValue(self.spin_box.value() - 0.1)
        else:
            self.spin_box.setValue(self.spin_box.value() - 1)
        self.value_changed.emit(self.spin_box.value())

class AnimatedHoverIntSpainButton(QPushButton):
    """QPushButton subclass with smooth color transition on hover."""
    def __init__(self, text, btn_padding=3,border_radius_size = 1, parent=None):
        super().__init__(text, parent)
        
        self._hoverLevel = 0.0
        self.button_border_radius = 1 
        if border_radius_size >=0.8:
            self.button_border_radius = 8 
        else:
            self.button_border_radius = 5

        # Calculate padding based on button size to maintain proportions
        self.btn_padding = btn_padding
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)
        # Animation setup
        self._anim = QPropertyAnimation(self, b"hoverLevel", self)
        self._anim.setDuration(200)  # 200 ms transition
   
        self.update_style()
        
    
        self.setDefault(False)
        self.setAutoDefault(False)

    def update_style(self):
       
        alpha = 0.5 + 0.3 * self._hoverLevel
        color = f"rgba(27,86,253,{alpha:.2f})"
        pressed_style = "rgba(27,86,253,1.0)"
        

        width = self.width() if self.width() > 0 else 30
        height = self.height() if self.height() > 0 else 20
        
   
        adjusted_padding = max(1, int(min(width, height) * 0.15))
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: {self.button_border_radius}px;
                padding: {adjusted_padding}px;
                text-align: center;
            }}
            QPushButton:pressed {{
                background-color: {pressed_style};
            }}
        """)

    def resizeEvent(self, event):
        # Update style when resized to maintain proportions
        self.update_style()
        super().resizeEvent(event)

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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConfigureWindow(json_file_path=r"User_Data\Page_manager.json")
    window.show()
    sys.exit(app.exec())