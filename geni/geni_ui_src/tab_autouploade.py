from re import A
import sys
import os
import json
import time
import threading
import asyncio
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QLineEdit, QFileDialog, QComboBox, QGridLayout,
    QMessageBox, QWidget,QGroupBox,QDialog,QVBoxLayout, QWidget,QTextEdit,QLineEdit,QFileDialog,QApplication,QMainWindow,QAbstractSpinBox,QSizePolicy,QSizePolicy,QGroupBox,QMessageBox,QDoubleSpinBox,QSpinBox,QStyle
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QObject, Property, QTimer,QPropertyAnimation
from PySide6.QtGui import QIcon, QPixmap
from openpyxl import Workbook  


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from geni.ldController.Ldcontroller_adb.LdAdb import LdAdbController
from geni.Downloaders.all_platform_shorts_downloader.UnifiedSocialMediaDownloader import UnifiedSocialMediaDownloader
from geni_ui_src.configure_window import ConfigureWindow
from geni_ui_src.configureGroupWindow import ConfigureGrpWindow


class MakeProfileFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setObjectName("profileFrame")
        #self.setStyleSheet("MakeProfileFrame#profileFrame{border:5px solid green;boder-radius:5px;}")
        
        self.main_layout = QVBoxLayout(self)
        
        self.placeholder_label = QLabel("Please select a frame to view options")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.placeholder_label)
        
    def create_frame(self, id_frame_idx, json_path):
        while self.main_layout.count():
            child = self.main_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            id_key = f"Id_information.{id_frame_idx}"
            page_names = []
            id_name = data[id_key].get("id_name", "")
            
            page_names.append(id_name)

            if id_key in data:
                id_data = data[id_key]
                page_info = id_data.get("pages_information", {})
                
                for key, page in page_info.items():
                    if "Page_Name" in page:
                        page_names.append(page["Page_Name"])
                        
                self.page_config_instance = PageConfig(
                    parent=self,
                    combo_button_value=page_names,
                    id_frame_idx=id_frame_idx,
                    json_file_path=json_path
                )
                
                main_folder = id_data.get("Main_folder_path", "")
                chrome_instance_path = id_data.get("chrome_instance_path", "")
                upload_method = id_data.get("upload_method","Without Apps Switch")
                if main_folder:
                    self.page_config_instance.main_folder_path = main_folder
                if chrome_instance_path:
                    self.page_config_instance.chrome_instance_path = chrome_instance_path
                #self.page_config_instance.upload_method_combobox.setCurrentText(upload_method)    
                self.main_layout.addWidget(self.page_config_instance)
            else:
                print(f"{id_key} not found in JSON data.")
        except Exception as e:
            print(f"Error loading id_information: {e}")

class PageConfig(QFrame):
    show_message_signal = Signal(str, str)
    def __init__(self, parent=None, combo_button_value=None, id_frame_idx=1, json_file_path=None):
        super().__init__(parent)
        if combo_button_value is None:
            combo_button_value = []

        #self.setStyleSheet("PageConfig{border:2px solid rgba(128,128,128,1);border-radius:8px;}")
        self._main_folder_path = ""
        self._chrome_instance_path = ""
        self._reels_history_xlsx_path = ""
        self.json_file_path = json_file_path
        self.combo_button_value = combo_button_value
        self.id_frame_idx = id_frame_idx
        
        self.main_layout = QVBoxLayout(self)
        self._create_widget()
        self.run_add_profile_config_ones(value=self.combo_button_value)
        self.show_message_signal.connect(self.show_success_message)

        
    @property
    def main_folder_path(self):
        return self._main_folder_path
        
    @main_folder_path.setter
    def main_folder_path(self, value):
        self._main_folder_path = value
        self.main_folder_entry.setText(value)
        
    @property
    def chrome_instance_path(self):
        return self._chrome_instance_path
        
    @chrome_instance_path.setter
    def chrome_instance_path(self, value):
        self._chrome_instance_path = value
        self.chrome_folder_entry.setText(value)
        
    @property
    def reels_history_xlsx_path(self):
        return self._reels_history_xlsx_path
        
    @reels_history_xlsx_path.setter
    def reels_history_xlsx_path(self, value):
        self._reels_history_xlsx_path = value

    def _create_widget(self):

        profile_frame = QFrame()
        profile_frame.setObjectName("profile_frame")
       
        profile_layout = QHBoxLayout(profile_frame)
        
        label = QLabel("Profile/Pages: ")
        label.setStyleSheet("font-weight: bold; font-size: 15px;")
        profile_layout.addWidget(label)
        
        self.combo_button = QComboBox()
        self.combo_button.addItems(self.combo_button_value)
        self.combo_button.currentTextChanged.connect(self.add_profile_config)
        #self.combo_button.currentTextChanged.connect(self.save_changes)
        profile_layout.addWidget(self.combo_button)
        profile_layout.addStretch()
        
        self.main_layout.addWidget(profile_frame)
        
        main_folder_location_frame = QGroupBox()
        main_folder_location_frame.setObjectName("main_folder_location_frame")
        main_folder_location_frame.setStyleSheet("""QGroupBox#main_folder_location_frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#main_folder_location_frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")

        main_folder_layout = QVBoxLayout(main_folder_location_frame)
        
        main_folder_row = QFrame()
        main_folder_row_layout = QHBoxLayout(main_folder_row)
        main_folder_row_layout.setContentsMargins(5, 0, 5, 5)
        
        main_folder_label = QLabel("Main Folder: ")
        main_folder_row_layout.addWidget(main_folder_label)
        
        self.main_folder_entry = QLineEdit()
        self.main_folder_entry.setObjectName("main_folder_entry")
        self.main_folder_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  

                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;            /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
        self.main_folder_entry.setMinimumWidth(400)
        # Connect text changes to save function
        self.main_folder_entry.textChanged.connect(self.on_main_folder_text_changed)
        main_folder_row_layout.addWidget(self.main_folder_entry)
        
        main_folder_browse_btn = AnimatedHoverButton("Browse")
        main_folder_browse_btn.setFixedSize(80, 30)
        main_folder_browse_btn.clicked.connect(self.main_folder_browse)
        main_folder_row_layout.addWidget(main_folder_browse_btn)
        
        self.restart_this_ld_instance = AnimatedHoverButton("Restart LD")
        self.restart_this_ld_instance.setFixedSize(80, 30)
        self.restart_this_ld_instance.clicked.connect(self.on_restart_button_click)
        main_folder_row_layout.addWidget(self.restart_this_ld_instance)
        
        main_folder_layout.addWidget(main_folder_row)
        
        #main_folder_layout.addSpacing(10)
        chrome_folder_row = QFrame()
        chrome_folder_row_layout = QHBoxLayout(chrome_folder_row)
        chrome_folder_row_layout.setContentsMargins(5, 0, 5, 5)
        
        chrome_folder_label = QLabel("Chrome Folder: ")
        chrome_folder_row_layout.addWidget(chrome_folder_label)
        
        self.chrome_folder_entry = QLineEdit()
        self.chrome_folder_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                 
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;             /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
        self.chrome_folder_entry.setMinimumWidth(300)
        # Connect text changes to save function
        self.chrome_folder_entry.textChanged.connect(self.on_chrome_folder_text_changed)
        chrome_folder_row_layout.addWidget(self.chrome_folder_entry)
        
        chrome_folder_browse_btn = AnimatedHoverButton("Browse")
        chrome_folder_browse_btn.setFixedSize(80, 30)
        chrome_folder_browse_btn.clicked.connect(self.chrome_instance_browse)
        chrome_folder_row_layout.addWidget(chrome_folder_browse_btn)
        
        self.start_this_chrome = AnimatedHoverButton("Start Chrome")
        self.start_this_chrome.setFixedSize(80, 30)
        self.start_this_chrome.clicked.connect(self.new_thread_chrome_instance_run)
        chrome_folder_row_layout.addWidget(self.start_this_chrome)
        
        main_folder_layout.addWidget(chrome_folder_row)

        #upload method comobo box
        """         upload_method_layout = QHBoxLayout()
        uplad_method_label = QLabel("Upload Method:")
        upload_method_layout.addWidget(uplad_method_label)
        self.upload_method_combobox = QComboBox()
        self.upload_method_combobox.addItems(["Without Apps Switch","With Apps Switch"])
        self.upload_method_combobox.currentIndexChanged.connect(self.save_changes)
        upload_method_layout.addWidget(self.upload_method_combobox)
        upload_method_layout.setAlignment(Qt.AlignLeft)
        upload_method_layout.addStretch(0)

        main_folder_layout.addLayout(upload_method_layout) """
        self.main_layout.addWidget(main_folder_location_frame)
        
        self.main_layout.setAlignment(Qt.AlignTop)
        profile_config_label = QLabel("Profile Config")
        profile_config_label.setStyleSheet("font-weight: bold; font-size: 15px;")
        self.main_layout.addWidget(profile_config_label, alignment=Qt.AlignLeft | Qt.AlignTop)

    def on_main_folder_text_changed(self, text):
        if text != self._main_folder_path:
            self._main_folder_path = text
            self.save_changes()
    
    def on_chrome_folder_text_changed(self, text):
        if text != self._chrome_instance_path:
            self._chrome_instance_path = text
            self.save_changes()
            
    def show_success_message(self, title, message):
        """Slot to display a message box in the main thread."""
        QMessageBox.information(self, title, message)

    def restart_ld_inst(self):
        """Restart LD instance and emit signals instead of showing messages directly."""
        try:
            restart = LdAdbController()

            if not self.main_folder_path:
                self.show_message_signal.emit("Error","Please Select Main Folder Frist.")
                return
            restart.local_output_file_path = self.main_folder_path
            serial,error= restart.ld_inst_adb_serial_of_selected_frame_without_war(id_frame_idx=self.id_frame_idx)
            if error is None:
                restart.device_serial = serial
            else:
                self.show_message_signal.emit("Error", serial)
                return
            
            restart.close_ld_inst(id_info_idx=self.id_frame_idx)
            is_done, message = restart.set_pc_shared_folder(id_frame_idx=self.id_frame_idx)
            if not is_done:
                self.show_message_signal.emit("Error", message)  # Emit signal
                return

            local_is_done, local_message = restart.set_open_loacl_adb(self.id_frame_idx)
            if not local_is_done:
                self.show_message_signal.emit("Error", local_message)  # Emit signal
                return
            time.sleep(4)

            ld_name, _ = restart.get_id_info(self.id_frame_idx)
            restart.set_ld_instance_prop(ld_name)
            restart.start_ld_inst(self.id_frame_idx)
            restart.cheack_ld_instance_open_or_not_for_20sec(id_frame_idx=self.id_frame_idx)
            
            is_inst, inst_message = restart.check_and_install_list_of_apps(self.id_frame_idx)
            time.sleep(2)
            
            try:
                restart.set_dnd_mode()
            except Exception as e:
                print(f"Error settting dnd mode{e}")
            time.sleep(1)

            try:
                restart.allow_all_permission()
            except Exception as e :
                print(f"Error while allowing all permissoin : {e}")
            
            if not is_inst:
                msg = f"Main folder path set but default apps not installed to LD: '{ld_name}'\n{inst_message}"
                self.show_message_signal.emit("Error", msg)  # Emit signal
                return
            
            time.sleep(4)
            msg = f"Main folder path set and default apps installed to LD: '{ld_name}'"
            self.show_message_signal.emit("Successful", msg)  # Emit signal
        except Exception as e:
            self.show_message_signal.emit("Error", f"Failed to restart LD: {e}")  # Emit signal

    def on_restart_button_click(self):
        """Start the restart process in a separate thread."""
        self.restart_this_ld_instance.setEnabled(False)
        thread = threading.Thread(target=self.async_restart, daemon=True)
        thread.start()

    def async_restart(self):
        """Run restart in a worker thread."""
        self.restart_ld_inst()
        self.restart_this_ld_instance.setEnabled(True)

    def run_add_profile_config_ones(self, value=None):
        if value and len(value) > 0:
            first_value = value[0]
            self.combo_button.setCurrentText(first_value)
            self.add_profile_config(first_value)

    def add_profile_config(self, value):
        print(f"Combo value changed to: {value}")
        try:
            # Clear existing 
            for i in reversed(range(self.main_layout.count())):
                item = self.main_layout.itemAt(i)
                if item and item.widget() and isinstance(item.widget(), ProfileConfig):
                    widget = item.widget()
                    self.main_layout.removeWidget(widget)
                    widget.setParent(None) 
                    widget.deleteLater()   
                    
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
    
            id_frame_idx1 = self.id_frame_idx
            result = self.get_config_by_combo_value(page_or_Id_data=data, search_value=value, id_frame_idx=id_frame_idx1)
            
            if result is None:
                print(f"No configuration found for {value}")
                return
            
            self.profile_data, self.is_id_data, self.main_folder_path_for_profile = result
            
            if self.is_id_data:
                self.id_profile = ProfileConfig(
                    parent=self,
                    json_file_path=self.json_file_path,
                    id_frame_idx=id_frame_idx1,
                    current_profile=value,
                    savecallback=self.save_changes
                )
                self.main_layout.addWidget(self.id_profile)
                
                main_folder_path = self.profile_data.get("Main_folder_path", "")
                chrome_instance_path = self.profile_data.get("chrome_instance_path", "")
                upload_method = self.profile_data.get("upload_method", "Without Apps Switch")
                id_info = self.profile_data.get("ID_info", {})

                reels_config = id_info.get("reels_config",{})
                videos_config = id_info.get("videos_config",{})
                image_config = id_info.get("image_config",{})
                story_config = id_info.get("story_config",{})

                
                
                download_reels_folder = reels_config.get("download_folder", "")
                download_video_folder = videos_config.get("download_folder", "")
                download_image_folder = image_config.get("download_folder", "")
                download_story_folder = story_config.get("download_folder", "")

                reels_folder = reels_config.get("ld_folder", "")
                image_folder = image_config.get("ld_folder", "")
                video_folder = videos_config.get("ld_folder", "")
                story_folder = story_config.get("ld_folder", "")


                config_download = id_info.get("configure_download_bonus_edits_video_edits", {})
                auto_download = config_download.get("auto_download", False)
                auto_video_edit = config_download.get("auto_video_edits", False)
                auto_reels_edit = config_download.get("auto_reels_edits", False)
                auto_image_edit = config_download.get("auto_image_edits", False)
                auto_story_video_edit = config_download.get("auto_story_video_edits", False)

                download_configs = config_download.get("Download Configurations", {})
                save_download_history = download_configs.get("Save downloaded video history", "")
                upload_types = id_info.get("set_upload_types", {})
                reels_upload = upload_types.get("reels_upload", False)
                image_upload = upload_types.get("image_upload", False)
                video_upload = upload_types.get("video_upload", False)
                story_upload = upload_types.get("story_upload", False)
                
                reels_schedule = reels_config.get("schedule_config", "")
                image_schedule = image_config.get("schedule_config", "")
                video_schedule = videos_config.get("schedule_config", "")



                reels_count = reels_config.get("num", 1)
                images_count = image_config.get("num", 1)
                videos_count = videos_config.get("num", 1)
                storys_count = story_config.get("num", 1)
                

                story_type = story_config.get("story_type","Videos")




                self.main_folder_path = main_folder_path
                self.chrome_instance_path = chrome_instance_path
                self.reels_history_xlsx_path = save_download_history
                self.upload_method_var = upload_method
                
                self.id_profile.main_folder = main_folder_path
                self.id_profile.reel_download_entry.setText(download_reels_folder)
                self.id_profile.image_download_entry.setText(download_image_folder)
                self.id_profile.video_download_entry.setText(download_video_folder)
                self.id_profile.story_download_entry.setText(download_story_folder)

                self.id_profile.reel_ld_folder = reels_folder
                self.id_profile.image_ld_folder = image_folder
                self.id_profile.video_ld_folder = video_folder
                self.id_profile.story_video_ld_folder = story_folder

                self.id_profile.auto_download_checkbox.setChecked(auto_download)
                self.id_profile.auto_reels_edit_checkbox.setChecked(auto_reels_edit)
                self.id_profile.auto_bonus_edit_checkbox.setChecked(auto_video_edit) 
                self.id_profile.auto_image_edit_checkbox.setChecked(auto_image_edit)
                self.id_profile.auto_story_video_edit_checkbox.setChecked(auto_story_video_edit)
                
                # Here we set the download folder for download properties   
                self.id_profile.reel_download_folder = download_reels_folder
                self.id_profile.video_download_folder = download_video_folder
                self.id_profile.download_image_folder = download_image_folder
                self.id_profile.story_download_folder = download_story_folder

                self.id_profile.reels_upload_checkbox.setChecked(reels_upload) 
                self.id_profile.video_upload_checkbox.setChecked(video_upload) 
                self.id_profile.bonus_upload_checkbox.setChecked(image_upload) 
                self.id_profile.story_upload_checkbox.setChecked(story_upload)


                self.id_profile.reels_num_spinbox.set_value(reels_count)
                self.id_profile.video_count_num_spinbox.set_value(videos_count)
                self.id_profile.bonus_num_spinbox.set_value(images_count)
                self.id_profile.story_count_num_spinbox.set_value(storys_count)


                self.id_profile.story_type_combobox.setCurrentText(story_type)



                self.id_reel_schedule_config = reels_schedule
                self.id_video_schedule_config = video_schedule
                self.id_image_schedule_config = image_schedule
            else:
                self.page_profile = ProfileConfig(
                    parent=self,
                    json_file_path=self.json_file_path,
                    id_frame_idx=self.id_frame_idx,
                    current_profile=value,
                    savecallback=self.save_changes
                )
                self.main_layout.addWidget(self.page_profile)
                
                download_folder_config = self.profile_data.get("download_folder_config", {})

                reels_config = self.profile_data.get("reels_config",{})
                videos_config = self.profile_data.get("videos_config",{})
                image_config = self.profile_data.get("image_config",{})
                story_config = self.profile_data.get("story_config",{})

                
                
                download_reels_folder = reels_config.get("download_folder", "")
                download_video_folder = videos_config.get("download_folder", "")
                download_image_folder = image_config.get("download_folder", "")
                download_story_folder = story_config.get("download_folder", "")

                reels_folder = reels_config.get("ld_folder", "")
                image_folder = image_config.get("ld_folder", "")
                video_folder = videos_config.get("ld_folder", "")
                story_folder = story_config.get("ld_folder", "")



                config_download = self.profile_data.get("configure_download_bonus_edits_video_edits", {})
                auto_download = config_download.get("auto_download", False)
                auto_video_edit = config_download.get("auto_video_edits", False)
                auto_reels_edit = config_download.get("auto_reels_edits", False)
                auto_image_edit = config_download.get("auto_image_edits", False)
                auto_story_video_edit = config_download.get("auto_story_video_edits", False)

                upload_types = self.profile_data.get("set_upload_types", {})
                reels_upload = upload_types.get("reels_upload", False)
                image_upload = upload_types.get("image_upload", False)
                video_upload = upload_types.get("video_upload", False)
                story_upload = upload_types.get("story_upload", False)
                



                reels_count = reels_config.get("num", 1)
                images_count = image_config.get("num", 1)
                videos_count = videos_config.get("num", 1)
                storys_count = story_config.get("num", 1)


                story_type = story_config.get("story_type","Videos")
                







                reels_schedule = reels_config.get("schedule_config", "")
                image_schedule = image_config.get("schedule_config", "")
                video_schedule = videos_config.get("schedule_config", "")


                self.page_profile.main_folder = self.main_folder_path_for_profile
                self.page_profile.reel_download_entry.setText(download_reels_folder)
                self.page_profile.image_download_entry.setText(download_image_folder)
                self.page_profile.video_download_entry.setText(download_video_folder)  
                self.page_profile.story_download_entry.setText(download_story_folder)  


                self.page_profile.reel_ld_folder = reels_folder
                self.page_profile.image_ld_folder = image_folder
                self.page_profile.video_ld_folder = video_folder
                self.page_profile.story_video_ld_folder = story_folder

                self.page_profile.auto_download_checkbox.setChecked(auto_download)
                self.page_profile.auto_reels_edit_checkbox.setChecked(auto_reels_edit)
                self.page_profile.auto_bonus_edit_checkbox.setChecked(auto_video_edit) 
                self.page_profile.auto_image_edit_checkbox.setChecked(auto_image_edit)
                self.page_profile.auto_story_video_edit_checkbox.setChecked(auto_story_video_edit)


                self.page_profile.reels_upload_checkbox.setChecked(reels_upload)
                self.page_profile.video_upload_checkbox.setChecked(video_upload) 
                self.page_profile.bonus_upload_checkbox.setChecked(image_upload) 
                self.page_profile.story_upload_checkbox.setChecked(story_upload) 
                


                self.page_profile.reels_num_spinbox.set_value(reels_count)
                self.page_profile.video_count_num_spinbox.set_value(videos_count)
                self.page_profile.bonus_num_spinbox.set_value(images_count)
                self.page_profile.story_count_num_spinbox.set_value(storys_count)


                self.page_profile.story_type_combobox.setCurrentText(story_type)


                self.page_reel_schedule_config = reels_schedule
                self.page_video_schedule_config = video_schedule
                self.page_image_schedule_config = image_schedule
                
                # Setting download folder to profile config properties
                self.page_profile.reel_download_folder = download_reels_folder
                self.page_profile.video_download_folder =download_video_folder
                self.page_profile.download_image_folder = download_image_folder
                self.page_profile.story_download_folder = download_story_folder


        except Exception as e:
            print(f"Error in add_profile_config: {e}")

    def get_config_by_combo_value(self, page_or_Id_data, id_frame_idx, search_value):
        try:
            data = page_or_Id_data
            id_key = f"Id_information.{id_frame_idx}"
            if id_key not in data:
                print(f"{id_key} not found in JSON data.")
                return None

            id_data = data[id_key]
            main_folder_path = id_data.get("Main_folder_path", "")
            search_normalized = search_value.strip().lower()

            id_name = id_data.get("id_name", "").strip().lower()
            if id_name == search_normalized:
                return (id_data, True, main_folder_path)

            page_info = id_data.get("pages_information", {})
            for key, page_dict in page_info.items():
                page_name = page_dict.get("Page_Name", "").strip().lower()
                if page_name == search_normalized:
                    return (page_dict, False, main_folder_path)

            print(f"No configuration matching '{search_value}' found in {id_key}.")
            return None
        except Exception as e:
            print(f"Error reading JSON: {e}")
            return None
            
    def save_changes(self):
        try:
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
    
            id_key = f"Id_information.{self.id_frame_idx}"
    
            if hasattr(self, 'is_id_data') and self.is_id_data:
                if id_key in data:
                    id_data = data[id_key]
                    id_data["Main_folder_path"] = self.main_folder_path
                    id_data["chrome_instance_path"] = self.chrome_instance_path
                    #id_data["upload_method"] = self.upload_method_combobox.currentText()
                    id_info = id_data.get("ID_info", {})
                    
                    # Update reels config
                    reels_config = id_info.get("reels_config", {})
                    reels_config["download_folder"] = self.id_profile.reel_download_entry.text()
                    reels_config["ld_folder"] = self.id_profile.reel_ld_folder
                    reels_config["num"] = self.id_profile.reels_num_spinbox.get_value()
                    reels_config["schedule_config"] = self.id_reel_schedule_config
                    id_info["reels_config"] = reels_config
                    
                    # Update videos config
                    videos_config = id_info.get("videos_config", {})
                    videos_config["download_folder"] = self.id_profile.video_download_entry.text()
                    videos_config["ld_folder"] = self.id_profile.video_ld_folder
                    videos_config["num"] = self.id_profile.video_count_num_spinbox.get_value()
                    videos_config["schedule_config"] = self.id_video_schedule_config
                    id_info["videos_config"] = videos_config
                    
                    # Update images config
                    image_config = id_info.get("image_config", {})
                    image_config["download_folder"] = self.id_profile.image_download_entry.text()
                    image_config["ld_folder"] = self.id_profile.image_ld_folder
                    image_config["num"] = self.id_profile.bonus_num_spinbox.get_value()
                    image_config["schedule_config"] = self.id_image_schedule_config
                    id_info["image_config"] = image_config
                    
                    # Update story config
                    story_config = id_info.get("story_config", {})
                    story_config["download_folder"] = self.id_profile.story_download_entry.text()
                    story_config["ld_folder"] = self.id_profile.story_video_ld_folder
                    story_config["num"] = self.id_profile.story_count_num_spinbox.get_value()
                    story_config["story_type"] = self.id_profile.story_type_combobox.currentText()
                    id_info["story_config"] = story_config
    
                    # Update configuration flags
                    config_download = id_info.get("configure_download_bonus_edits_video_edits", {})
                    config_download["auto_download"] = self.id_profile.auto_download_checkbox.isChecked()
                    config_download["auto_video_edits"] = self.id_profile.auto_bonus_edit_checkbox.isChecked()
                    config_download["auto_reels_edits"] = self.id_profile.auto_reels_edit_checkbox.isChecked()
                    config_download["auto_image_edits"] = self.id_profile.auto_image_edit_checkbox.isChecked()
                    config_download["auto_story_video_edits"] = self.id_profile.auto_story_video_edit_checkbox.isChecked()
                    
                    
                    # Update download history configuration
                    download_configs = config_download.get("Download Configurations", {})
                    download_configs["Save downloaded video history"] = self.reels_history_xlsx_path
                    config_download["Download Configurations"] = download_configs
                    
                    id_info["configure_download_bonus_edits_video_edits"] = config_download
    
                    # Update upload types
                    upload_types = id_info.get("set_upload_types", {})
                    upload_types["reels_upload"] = self.id_profile.reels_upload_checkbox.isChecked()
                    upload_types["image_upload"] = self.id_profile.bonus_upload_checkbox.isChecked()
                    upload_types["video_upload"] = self.id_profile.video_upload_checkbox.isChecked()
                    upload_types["story_upload"] = self.id_profile.story_upload_checkbox.isChecked()
                    id_info["set_upload_types"] = upload_types
    
                    id_data["ID_info"] = id_info
                    
            else:  # Page profile
                if id_key in data:
                    id_data = data[id_key]
                    id_data["Main_folder_path"] = self.main_folder_path
                    id_data["chrome_instance_path"] = self.chrome_instance_path
                    #id_data["upload_method"] = self.upload_method_combobox.currentText()
                    page_info = id_data.get("pages_information", {})
                    selected_page_name = self.combo_button.currentText()
    
                    selected_page_key = None
                    for key, page in page_info.items():
                        if page.get("Page_Name", "").strip().lower() == selected_page_name.strip().lower():
                            selected_page_key = key
                            break
                        
                    if selected_page_key:
                        page_data = page_info[selected_page_key]
                        
                        # Update reels config
                        reels_config = page_data.get("reels_config", {})
                        reels_config["download_folder"] = self.page_profile.reel_download_entry.text()
                        reels_config["ld_folder"] = self.page_profile.reel_ld_folder
                        reels_config["num"] = self.page_profile.reels_num_spinbox.get_value()
                        reels_config["schedule_config"] = self.page_reel_schedule_config
                        page_data["reels_config"] = reels_config
                        
                        # Update videos config
                        videos_config = page_data.get("videos_config", {})
                        videos_config["download_folder"] = self.page_profile.video_download_entry.text()
                        videos_config["ld_folder"] = self.page_profile.video_ld_folder
                        videos_config["num"] = self.page_profile.video_count_num_spinbox.get_value()
                        videos_config["schedule_config"] = self.page_video_schedule_config
                        page_data["videos_config"] = videos_config
                        
                        # Update images config
                        image_config = page_data.get("image_config", {})
                        image_config["download_folder"] = self.page_profile.image_download_entry.text()
                        image_config["ld_folder"] = self.page_profile.image_ld_folder
                        image_config["num"] = self.page_profile.bonus_num_spinbox.get_value()
                        image_config["schedule_config"] = self.page_image_schedule_config
                        page_data["image_config"] = image_config
                        
                        # Update story config
                        story_config = page_data.get("story_config", {})
                        story_config["download_folder"] = self.page_profile.story_download_entry.text()
                        story_config["ld_folder"] = self.page_profile.story_video_ld_folder
                        story_config["num"] = self.page_profile.story_count_num_spinbox.get_value()
                        story_config["story_type"] = self.page_profile.story_type_combobox.currentText()
                        page_data["story_config"] = story_config
    
                        # Update configuration flags
                        config_download = page_data.get("configure_download_bonus_edits_video_edits", {})
                        config_download["auto_download"] = self.page_profile.auto_download_checkbox.isChecked()
                        config_download["auto_video_edits"] = self.page_profile.auto_bonus_edit_checkbox.isChecked()
                        config_download["auto_reels_edits"] = self.page_profile.auto_reels_edit_checkbox.isChecked()
                        config_download["auto_image_edits"] = self.page_profile.auto_image_edit_checkbox.isChecked()
                        config_download["auto_story_video_edits"] = self.page_profile.auto_story_video_edit_checkbox.isChecked()

                        page_data["configure_download_bonus_edits_video_edits"] = config_download
    
                        # Update upload types
                        upload_types = page_data.get("set_upload_types", {})
                        upload_types["reels_upload"] = self.page_profile.reels_upload_checkbox.isChecked()
                        upload_types["image_upload"] = self.page_profile.bonus_upload_checkbox.isChecked()
                        upload_types["video_upload"] = self.page_profile.video_upload_checkbox.isChecked()
                        upload_types["story_upload"] = self.page_profile.story_upload_checkbox.isChecked()
                        page_data["set_upload_types"] = upload_types
    
            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
    
            print("Configuration saved successfully from auto upload tab.")
        except Exception as e:
            print(f"Error saving changes: {e}")
                
    def check_duplicate_main_path(self, main_folder_path, json_path):
        with open(json_path, "r", encoding="utf-8") as file:
            id_data = json.load(file)

        if id_data[f"Id_information.{self.id_frame_idx}"].get("Main_folder_path") == main_folder_path:
            return (False, id_data[f"Id_information.{self.id_frame_idx}"])

        for id_key, details in id_data.items():
            if details.get("Main_folder_path") == main_folder_path:
                print(f"Error: This main folder path '{main_folder_path}' is already used in '{id_key}'.")
                return (True, id_key)
        return (False, id_key)
    
    def check_duplicate_chrome_instance_path(self, chrome_instance_path, json_path):
        with open(json_path, "r", encoding="utf-8") as file:
            id_data = json.load(file)
        if id_data[f"Id_information.{self.id_frame_idx}"].get("chrome_instance_path") == chrome_instance_path:
            return (False, id_data[f"Id_information.{self.id_frame_idx}"])
        for id_key, details in id_data.items():
            if details.get("chrome_instance_path") == chrome_instance_path:
                print(f"Error: This chrome instance path '{chrome_instance_path}' is already used in '{id_key}'.")
                return (True, id_key)
        return (False, id_key)

    def main_folder_browse(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Main Folder")
        if folder_path:
            is_found, id_key = self.check_duplicate_main_path(main_folder_path=folder_path, json_path=self.json_file_path)
            if is_found:
                QMessageBox.critical(self, "Error", f"This main folder path '{folder_path}' is already used in '{id_key}'.")
            else:
                self.main_folder_path = folder_path
                self.save_changes()
                self.add_profile_config(self.combo_button.currentText())
                self.restart_this_ld_instance.setEnabled(True)
    
    def chrome_instance_browse(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Chrome Instance Folder")
        if folder_path:
            is_found, id_key = self.check_duplicate_chrome_instance_path(chrome_instance_path=folder_path, json_path=self.json_file_path)
            if is_found:
                QMessageBox.critical(self, "Error", f"This chrome instance '{folder_path}' is already used in '{id_key}'.")
            else:
                self.chrome_instance_path = folder_path
                self.save_changes()
                self.add_profile_config(self.combo_button.currentText())
    
    async def create_chrome_instance(self):
        import undetected_chromedriver as uc
        

        main_folder = self.main_folder_path
        chrome_instance = self.chrome_instance_path

        if not main_folder:
            self.show_message_signal.emit("Error", "Please select a main folder first")  
            return

        chrome_path = []

        try:
            if main_folder and chrome_instance:
                chrome_path = ["chrome_path_given", chrome_instance, "Profile 1"]
            elif main_folder and not chrome_instance:
                chrome_path = ["chrome_path_not_given", main_folder, "chrome", "Profile 1"]
            else:
                print("Error while fetching chrome folder paths")
                return
        except Exception as e:
            print(f"Error: {e}")
            return

        if chrome_path[0] == "chrome_path_given":
            chrome_instance_base_path = chrome_path[1]
            chrome_instance_profile_path = chrome_path[2]

            downloader_instance = UnifiedSocialMediaDownloader(
                control_quit_callback=None,
                control_pause_callback=None,
                base_user_data_dir=chrome_instance_base_path,
                profile_dir=chrome_instance_profile_path,
                web_link="https://www.google.com/",
                keep_alive=True,
                    # Set keep_alive to True
            )

            await downloader_instance.__ainit__()  # Await async init
            #await downloader_instance.browser.get(url="https://www.google.com/")
            await downloader_instance.start_browser()
            await asyncio.sleep(2)

            self.create_history_xlsx()
            self.save_changes()

            # Keep browser open - wait for manual close
            print("Browser is running. Close it manually when done.")
            #await self.wait_for_manual_close(downloader_instance)

        elif chrome_path[0] == "chrome_path_not_given":
            main_folder_path = chrome_path[1]
            parent_path = os.path.dirname(main_folder_path)
            chrome_instance_base_path = os.path.join(parent_path, chrome_path[2])
            chrome_instance_base_path = os.path.normpath(chrome_instance_base_path)
            chrome_instance_profile_path = chrome_path[3]

            downloader_instance = UnifiedSocialMediaDownloader(
                control_quit_callback=None,
                control_pause_callback=None,
                base_user_data_dir=chrome_instance_base_path,
                profile_dir=chrome_instance_profile_path,
                web_link="https://www.google.com/",
                keep_alive=True  # Set keep_alive to True
            )

            await downloader_instance.__ainit__()  
            #await downloader_instance.browser.get(url="https://www.google.com/")
            await downloader_instance.start_browser()
            await asyncio.sleep(2)  # Wait for browser to start

            self.chrome_instance_path = chrome_instance_base_path
            self.create_history_xlsx()
            self.save_changes()

            # Keep browser open - wait for manual close
            print("Browser is running. Close it manually when done.")
            #await self.wait_for_manual_close(downloader_instance)

    async def wait_for_manual_close(self, downloader_instance):
        """Wait for the browser to be manually closed by the user"""
        try:
            while True:
                # Check if browser is still running
                if not downloader_instance.browser or not hasattr(downloader_instance.browser, 'websocket'):
                    print("Browser has been closed by user.")
                    break
                
                # Check if browser process is still alive
                try:
                    # Try to get current URL to check if browser is responsive
                    await downloader_instance.browser.get_current_url()
                    await asyncio.sleep(1)  # Check every second
                except Exception:
                    # Browser is likely closed
                    print("Browser has been closed by user.")
                    break

        except Exception as e:
            print(f"Error while waiting for browser close: {e}")
        finally:
            # Clean up if needed
            try:
                if downloader_instance.browser:
                    downloader_instance.browser.stop()
            except:
                pass

    def create_history_xlsx(self):
        path = self.chrome_instance_path
        os.makedirs(path, exist_ok=True)
        pc_xlsx_path = os.path.join(path, "reels_history.xlsx")
        pc_xlsx_path = os.path.normpath(pc_xlsx_path)

        if os.path.exists(pc_xlsx_path):
            self.reels_history_xlsx_path = pc_xlsx_path
            print("reels_history XLSX file already exists")
        else:
            wb = Workbook()
            wb.save(pc_xlsx_path)
            self.reels_history_xlsx_path = pc_xlsx_path
            print("reels_history XLSX file created")

    def new_thread_chrome_instance_run(self):
        if getattr(self, "chrome_thread_running", False):
            return
        self.chrome_thread_running = True
        self.start_this_chrome.setEnabled(False)

        # Create a new event loop for this thread
        def run_async_in_thread():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Run the async method
                loop.run_until_complete(self.create_chrome_instance())

            except Exception as e:
                print(f"Error in chrome instance thread: {e}")
            finally:
                # Clean up the loop
                try:
                    loop.close()
                except:
                    pass
                
                # Re-enable the button
                self.start_this_chrome.setEnabled(True)
                self.chrome_thread_running = False

        thread = threading.Thread(target=run_async_in_thread, daemon=True)
        thread.start()
        self.check_thread(thread)

    def check_thread(self, thread):
        if thread.is_alive():
            QTimer.singleShot(100, lambda: self.check_thread(thread))
        else:
            self.start_this_chrome.setEnabled(True)
            self.chrome_thread_running = False

class ProfileConfig(QFrame):
    def __init__(self, parent, json_file_path=None, id_frame_idx=1, current_profile="", savecallback=None):
        super().__init__(parent)
        self.main_folder = ""
        self.setStyleSheet("ProfileConfig{border:2px solid rgba(128,128,128,1);border-radius:8px;background-color:rgba(128,128,128,0.01)}")
        self.reel_download_folder = ""
        self.download_image_folder = ""
        self.video_download_folder = ""
        self.story_download_folder = ""
        self.reel_ld_folder = ""
        self.image_ld_folder = ""
        self.video_ld_folder = ""
        self.story_video_ld_folder = ""  
        self.auto_download = False
        self.auto_reels_edit = False
        self.auto_image_edit = False
        self.auto_bonus_edit = False
        self.reels_upload = False
        self.bonus_upload = False
        self.video_upload = False
        self.story_upload = False
        self.json_file_path = json_file_path
        self.id_frame_idx = id_frame_idx
        self.current_profile = current_profile
        self.savecallback = savecallback
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        
        self._create_widget()
        
    def _create_widget(self):

        folders_config_group_box = QGroupBox()
        folders_config_group_box.setObjectName("folders_config_group_box")
        folders_config_group_box.setTitle("Download Folders Configure")
        folders_config_group_box.setStyleSheet("""QGroupBox#folders_config_group_box{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#folders_config_group_box::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        download_folder_main_layout = QGridLayout(folders_config_group_box)
        


        #reels download folders
        reel_download_label = QLabel("Reels Folder:")
        reel_download_label.setStyleSheet("font-size: 14px;")
        self.reel_download_entry = QLineEdit()
        self.reel_download_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                 
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
        
        self.reel_download_entry.setMinimumWidth(300)
        video_download_button = AnimatedHoverButton("Browse")
        video_download_button.setFixedSize(80, 23)
        video_download_button.clicked.connect(self.reel_download_browse)
        

        # Setup icon 
        
        folderOpenIcon = QApplication.style().standardIcon(QStyle.SP_DirOpenIcon)

        openReelsFolderBtn = AnimatedHoverButton("")
        openReelsFolderBtn.setFixedSize(40, 15)
        openReelsFolderBtn.clicked.connect(self.openReelFolder)

        openReelsFolderBtn.setIcon(folderOpenIcon)
        openReelsFolderBtn.setFixedSize(40, 20 )
        

        download_folder_main_layout.addWidget(reel_download_label,0,0)
        download_folder_main_layout.addWidget(self.reel_download_entry,0,1)
        download_folder_main_layout.addWidget(video_download_button,0,2)
        download_folder_main_layout.addWidget(openReelsFolderBtn,0,3)
        



        #image Download folders
        image_download_label = QLabel("Image Folder:")
        image_download_label.setStyleSheet("font-size: 14px;")
        self.image_download_entry = QLineEdit()
        self.image_download_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
        
        self.image_download_entry.setMinimumWidth(300)
        image_download_button = AnimatedHoverButton("Browse")
        image_download_button.setFixedSize(80, 23)
        image_download_button.clicked.connect(self.image_download_browse)
        
        download_folder_main_layout.addWidget(image_download_label,1,0)
        download_folder_main_layout.addWidget(self.image_download_entry,1,1)
        download_folder_main_layout.addWidget(image_download_button,1,2)
        
        # Open image folder btn 
        
        openImageFolderBtn = AnimatedHoverButton("")
        openImageFolderBtn.setFixedSize(40, 20)
        download_folder_main_layout.addWidget(openImageFolderBtn,1,3)  
        openImageFolderBtn.clicked.connect(self.openImageFolder)
        
        openImageFolderBtn.setIcon(folderOpenIcon)
        openImageFolderBtn.setFixedSize(40,20)

        

        


        #video download layout
        video_download_label = QLabel("Video Folder:")
        video_download_label.setStyleSheet("font-size: 14px;")
        self.video_download_entry = QLineEdit()
        self.video_download_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                 
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;             /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
        
        self.video_download_entry.setMinimumWidth(300)
        video_download_button = AnimatedHoverButton("Browse")
        video_download_button.setFixedSize(80, 23)
        video_download_button.clicked.connect(self.video_download_browse)
        
        self.openVideoFolderBtn = AnimatedHoverButton("")
        self.openVideoFolderBtn.setFixedSize(40, 15)
        self.openVideoFolderBtn.clicked.connect(self.openVideoFolder)
        
        self.openVideoFolderBtn.setIcon(folderOpenIcon)
        self.openVideoFolderBtn.setFixedSize(40,20)
        
        #open video folder btn logic
        
        download_folder_main_layout.addWidget(video_download_label,2,0)
        download_folder_main_layout.addWidget(self.video_download_entry,2,1)
        download_folder_main_layout.addWidget(video_download_button,2,2)
        
        download_folder_main_layout.addWidget(self.openVideoFolderBtn,2,3)




        #story video download folder
        story_download_label = QLabel("Story Folder:")
        story_download_label.setStyleSheet("font-size: 14px;")
        self.story_download_entry = QLineEdit()
        self.story_download_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                                 /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
        
        self.story_download_entry.setMinimumWidth(300)
        story_download_button = AnimatedHoverButton("Browse")
        story_download_button.setFixedSize(80, 23)
        story_download_button.clicked.connect(self.story_download_browse)
        
        #open story folder btn logic
        
        openstoryFolderBtn = AnimatedHoverButton("")
        openstoryFolderBtn.setFixedSize(40, 15)
        openstoryFolderBtn.clicked.connect(self.OpenstoryFolder)
        openstoryFolderBtn.setIcon(folderOpenIcon)
        openstoryFolderBtn.setFixedSize(40,20)
        
        download_folder_main_layout.addWidget(story_download_label,3,0)
        download_folder_main_layout.addWidget(self.story_download_entry,3,1)
        download_folder_main_layout.addWidget(story_download_button,3,2)
        download_folder_main_layout.addWidget(openstoryFolderBtn,3,3)
        



        #some spacing
        download_folder_main_layout.setHorizontalSpacing(10)
        download_folder_main_layout.setVerticalSpacing(5)

        #create folder btn config
        create_download_folders_layout = QVBoxLayout()
        create_download_button = AnimatedHoverButton("Create Folders")
        create_download_button.setFixedSize(100, 50)
        create_download_button.clicked.connect(self.create_download_folder)
        #create_download_button.clicked.connect(self.create_ld_folder)
        create_download_folders_layout.addWidget(create_download_button)
        create_download_folders_layout.setAlignment(Qt.AlignCenter)
        
        
        download_folder_main_layout.addLayout(create_download_folders_layout, 0, 4, 4, 1)
        
        self.main_layout.addWidget(folders_config_group_box)
        

        
        
        configure_download_edit_group_box = QGroupBox()
        configure_download_edit_group_box.setObjectName("configure_download_edit_group_box")
        configure_download_edit_group_box.setTitle("Configure Download/Edits/Downloads")
        configure_download_edit_group_box.setStyleSheet("""QGroupBox#configure_download_edit_group_box{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#configure_download_edit_group_box::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        config_download_layout = QGridLayout(configure_download_edit_group_box)
        
        #configure download edit and download frame
        configure_download_btn_frame = QFrame()
        configure_download_btn_frame_layout = QHBoxLayout()

        config_download_label = QLabel("More Config")
        configure_download_btn = AnimatedHoverButton("Configure")
        configure_download_btn.setFixedSize(80, 80)
        configure_download_btn.clicked.connect(self.open_configure_window)
        
        
        configure_download_btn_frame_layout.addWidget(config_download_label)
        #configure_download_btn_frame_layout.setSpacing(10)
        configure_download_btn_frame_layout.addWidget(configure_download_btn)


        # Configure grp config here

        group_config_layout = QHBoxLayout()
        
        group_config_label = QLabel("Group Config")
        group_config_btn = AnimatedHoverButton("Configure")
        group_config_btn.setFixedSize(80,80)
        group_config_btn.clicked.connect(self.onGroupConfigClicked)
        
        configure_download_btn_frame.setLayout(configure_download_btn_frame_layout)
        config_download_layout.addWidget(configure_download_btn_frame, 0, 0)
        config_download_layout.setHorizontalSpacing(30)
        
        group_config_layout.addWidget(group_config_label)
        group_config_layout.addWidget(group_config_btn)
        
        configure_download_btn_frame_layout.addLayout(group_config_layout)




        #enable/disable shortcut frame
        download_enable_frame = QFrame()
        download_enable_frame.setFixedHeight(80)
        download_enable_frame.setObjectName("download_enable_frame")
        download_enable_frame.setStyleSheet("""QFrame#download_enable_frame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    background-color: rgba(128,128,128,0.2);}""")
        download_enable_layout = QGridLayout(download_enable_frame)
        
        self.auto_download_checkbox = QCheckBox("Auto Download")
        self.auto_download_checkbox.setStyleSheet("""border:none;""")
        self.auto_download_checkbox.setChecked(self.auto_download)
        self.auto_download_checkbox.clicked.connect(self.save_changes)
        
        self.auto_reels_edit_checkbox = QCheckBox("Auto Reels Edits")
        self.auto_reels_edit_checkbox.setStyleSheet("""border:none;""")
        self.auto_reels_edit_checkbox.setChecked(self.auto_reels_edit)
        self.auto_reels_edit_checkbox.clicked.connect(self.savecallback)
        #self.auto_reels_edit_checkbox.stateChanged.connect(self.switch_and_next_update)
        
        self.auto_image_edit_checkbox = QCheckBox("Auto Image Edits")
        self.auto_image_edit_checkbox.setStyleSheet("""border:none;""")
        self.auto_image_edit_checkbox.setChecked(self.auto_image_edit)
        self.auto_image_edit_checkbox.clicked.connect(self.savecallback)
        #self.auto_image_edit_checkbox.stateChanged.connect(self.switch_and_next_update)
        
        self.auto_bonus_edit_checkbox = QCheckBox("Auto Bonus Edits")
        self.auto_bonus_edit_checkbox.setStyleSheet("""border:none;""")
        self.auto_bonus_edit_checkbox.setChecked(self.auto_bonus_edit)
        self.auto_bonus_edit_checkbox.clicked.connect(self.savecallback)
        #self.auto_bonus_edit_checkbox.stateChanged.connect(self.switch_and_next_update)

        self.auto_story_video_edit_checkbox = QCheckBox("Auto story Video Edits")
        self.auto_story_video_edit_checkbox.setStyleSheet("""border:none;""")
        self.auto_story_video_edit_checkbox.setChecked(self.auto_bonus_edit)
        self.auto_story_video_edit_checkbox.clicked.connect(self.savecallback)

        
        download_enable_layout.addWidget(self.auto_download_checkbox, 0, 0)
        download_enable_layout.addWidget(self.auto_reels_edit_checkbox, 0, 1)
        download_enable_layout.addWidget(self.auto_image_edit_checkbox, 1, 0)
        download_enable_layout.addWidget(self.auto_bonus_edit_checkbox, 1, 1)
        download_enable_layout.addWidget(self.auto_story_video_edit_checkbox,2,0)


        config_download_layout.addWidget(download_enable_frame, 0, 2)
        self.main_layout.addWidget(configure_download_edit_group_box)
        


        #upload type enable and disable box
        upload_type_groupbox = QGroupBox()
        upload_type_groupbox.setObjectName("upload_type_groupbox")
        upload_type_groupbox.setTitle("Configure Upload Types")
        upload_type_groupbox.setStyleSheet("""QGroupBox#upload_type_groupbox{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#upload_type_groupbox::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
   
        upload_type_main_layout = QGridLayout(upload_type_groupbox)
        upload_type_layout = QGridLayout()
        #reels_upload settings
        reels_upload_frame = QFrame()
        reels_upload_frame.setObjectName("reels_upload_frame")
        reels_upload_frame.setStyleSheet("""QFrame#reels_upload_frame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:5px;
                                    padding-right:5px;
                                    padding-left:5px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)
        reels_upload_frame.setFixedWidth(148)
        reels_upload_frame.setFixedHeight(50)
        reels_upload_layout = QHBoxLayout()
        reel_icon_label = QLabel()
        reel_icon_pixmap = QPixmap(r"geni\geni_ui_src\ui_assets\Icons\reel_icon.png")
        reel_icon_label.setPixmap(reel_icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio))
        
        self.reels_upload_checkbox = QCheckBox("Reels Upload")
        self.reels_upload_checkbox.setChecked(self.reels_upload)
        self.reels_upload_checkbox.clicked.connect(self.savecallback)
        
        reels_upload_layout.addWidget(reel_icon_label)
        reels_upload_layout.addWidget(self.reels_upload_checkbox)
        reels_upload_layout.setAlignment(Qt.AlignLeft)
        reels_upload_frame.setLayout(reels_upload_layout)


        #image|Bonus upload settings
        bonus_upload_frame = QFrame()
        bonus_upload_frame.setObjectName("bonus_upload_frame")
        bonus_upload_frame.setStyleSheet("""QFrame#bonus_upload_frame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:5px;
                                    padding-right:5px;
                                    padding-left:5px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)
        bonus_upload_frame.setFixedWidth(152)
        bonus_upload_frame.setFixedHeight(50)
        bonus_upload_layout = QHBoxLayout()
        image_icon_label = QLabel()
        image_icon_pixmap = QPixmap(r"geni\geni_ui_src\ui_assets\Icons\Image_Icon.png")
        image_icon_label.setPixmap(image_icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio))
        
        self.bonus_upload_checkbox = QCheckBox("Bonus Upload")
        self.bonus_upload_checkbox.setChecked(self.bonus_upload)
        self.bonus_upload_checkbox.clicked.connect(self.savecallback)
        #self.bonus_upload_checkbox.stateChanged.connect(self.switch_and_next_update)
        
        bonus_upload_layout.addWidget(image_icon_label)
        bonus_upload_layout.addWidget(self.bonus_upload_checkbox)
        bonus_upload_layout.setAlignment(Qt.AlignLeft)
        bonus_upload_frame.setLayout(bonus_upload_layout)
        

        #video_upload settings
        video_upload_frame = QFrame()
        video_upload_frame.setObjectName("video_upload_frame")
        video_upload_frame.setStyleSheet("""QFrame#video_upload_frame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:5px;
                                    padding-right:5px;
                                    padding-left:5px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)
        video_upload_frame.setFixedWidth(148)
        video_upload_frame.setFixedHeight(50)
        video_upload_layout = QHBoxLayout()
        video_icon_label = QLabel()
        video_icon_pixmap = QPixmap(r"geni\geni_ui_src\ui_assets\Icons\Video_Icon.png")
        video_icon_label.setPixmap(video_icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio))
        
        self.video_upload_checkbox = QCheckBox("Video Upload")
        self.video_upload_checkbox.setChecked(self.video_upload)
        self.video_upload_checkbox.clicked.connect(self.savecallback)
        #self.video_upload_checkbox.stateChanged.connect(self.switch_and_next_update)
        
        video_upload_layout.addWidget(video_icon_label)
        video_upload_layout.addWidget(self.video_upload_checkbox)
        video_upload_layout.setAlignment(Qt.AlignLeft)
        video_upload_frame.setLayout(video_upload_layout)



        #story_upload settings
        story_upload_frame = QFrame()
        story_upload_frame.setObjectName("story_upload_frame")

        story_upload_frame.setStyleSheet("""QFrame#story_upload_frame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:5px;
                                    padding-right:5px;
                                    padding-left:5px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)
        story_upload_frame.setFixedWidth(152)
        story_upload_frame.setFixedHeight(50)
        story_upload_layout = QHBoxLayout()
        story_icon_label = QLabel()
        story_icon_pixmap = QPixmap(r"geni\geni_ui_src\ui_assets\Icons\stories_icon.png")
        story_icon_label.setPixmap(story_icon_pixmap.scaled(20, 20, Qt.KeepAspectRatio))
        
        self.story_upload_checkbox = QCheckBox("Story Upload")
        self.story_upload_checkbox.setChecked(self.story_upload)
        self.story_upload_checkbox.clicked.connect(self.savecallback)
        #self.story_upload_checkbox.stateChanged.connect(self.switch_and_next_update)
        
        story_upload_layout.addWidget(story_icon_label)
        story_upload_layout.addWidget(self.story_upload_checkbox)
        story_upload_layout.setAlignment(Qt.AlignLeft)
        story_upload_frame.setLayout(story_upload_layout)




        upload_type_layout.addWidget(reels_upload_frame, 0, 0)
        upload_type_layout.addWidget(bonus_upload_frame, 0, 1)
        upload_type_layout.addWidget(video_upload_frame, 1, 0)
        upload_type_layout.addWidget(story_upload_frame, 1, 1)
        


        number_of_content_setting = QFrame()
        number_of_content_setting.setObjectName("number_of_content_setting_frame")
        number_of_content_setting.setStyleSheet("""QFrame#number_of_content_setting_frame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    margin-top:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)
                                           
        
        
        number_of_content_setting_layout = QVBoxLayout(number_of_content_setting)


        # Reels count layout
        reels_num_content_layout = QHBoxLayout()  
        reels_num_label = QLabel("Reels Count:")
        self.reels_num_spinbox = SmallIntSpinBox(save_callback=self.savecallback, support_float=False)
        reels_num_content_layout.addWidget(reels_num_label)
        reels_num_content_layout.addWidget(self.reels_num_spinbox)



        # Bouns count layout 
        bonus_num_content_layout = QHBoxLayout()
        bonus_num_label = QLabel("Bonus Count:")
        self.bonus_num_spinbox = SmallIntSpinBox(save_callback=self.savecallback,support_float=False)
        bonus_num_content_layout.addWidget(bonus_num_label)
        bonus_num_content_layout.addWidget(self.bonus_num_spinbox)



        # Video count layout 
        video_num_content_layout = QHBoxLayout()
        video_content_label = QLabel("Videos Count:")
        self.video_count_num_spinbox = SmallIntSpinBox(save_callback=self.savecallback,support_float=False)
        video_num_content_layout.addWidget(video_content_label)
        video_num_content_layout.addWidget(self.video_count_num_spinbox)



        # Story count layout
        story_num_content_layout = QHBoxLayout()
        story_content_label = QLabel("Story Count:")
        self.story_count_num_spinbox = SmallIntSpinBox(save_callback=self.savecallback,support_float=False)
        story_num_content_layout.addWidget(story_content_label)
        story_num_content_layout.addWidget(self.story_count_num_spinbox)


        
        

        
        # Add the frame to the layout with some speacing 
        number_of_content_setting_layout.addLayout(reels_num_content_layout)
        number_of_content_setting_layout.addStretch(1) 
        number_of_content_setting_layout.addLayout(bonus_num_content_layout)
        number_of_content_setting_layout.addStretch(1)
        number_of_content_setting_layout.addLayout(video_num_content_layout)
        number_of_content_setting_layout.addStretch(1)
        number_of_content_setting_layout.addLayout(story_num_content_layout)
       


        # story type frame 
        story_type_frame = QFrame()
        story_type_frame.setObjectName("story_type_frame")
        story_type_frame.setStyleSheet("""QFrame#story_type_frame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:5px;
                                    padding-right:5px;
                                    padding-left:5px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)
        story_type_layout = QVBoxLayout(story_type_frame)
        story_type_label = QLabel("Story type:")
        self.story_type_combobox = QComboBox()
        self.story_type_combobox.addItems(["Videos","Images","Both"])
        self.story_type_combobox.currentTextChanged.connect(self.save_changes)
        story_type_layout.addWidget(story_type_label)
        story_type_layout.addWidget(self.story_type_combobox)
        story_type_layout.addStretch(1)




        
        # Add both layouts to the main layout
        upload_type_main_layout.addLayout(upload_type_layout, 0, 0)
        upload_type_main_layout.addWidget(number_of_content_setting, 0, 1)  
        upload_type_main_layout.addWidget(story_type_frame,0,2)
        #upload_type_main_layout.setAlignment(Qt.AlignLeft)
        
        self.main_layout.addWidget(upload_type_groupbox)



    def onGroupConfigClicked(self):
        

        try:
            # Create the configure window with this as parent
            configure_window = ConfigureGrpWindow(
                json_file_path=self.json_file_path,
                id_frame_idx=self.id_frame_idx,
                profile_name=self.current_profile, 
                parent=self 
            )

            configure_window.setMinimumHeight(840)
            configure_window.exec()

        except Exception as e:
            QMessageBox.critical(self, "Configure Window", f"Error opening ConfigureWindow: {e}")



        
    def save_changes(self):
        if self.savecallback:
            self.savecallback()


    def image_download_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.download_image_folder = folder
            self.image_download_entry.setText(folder)
            #self.create_ld_folder()
            if self.savecallback:
                self.savecallback()
    
    def reel_download_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.reel_download_folder = folder
            self.reel_download_entry.setText(folder)
            #self.create_ld_folder()
            if self.savecallback:
                self.savecallback()



    def openReelFolder(self):
        if os.path.exists(self.reel_download_folder):

            os.startfile(self.reel_download_folder)
        else:
            QMessageBox.critical(self, "Folder Not Found", "The specified folder does not exist.")  
            

    def openVideoFolder(self):
        if os.path.exists(self.video_download_folder):
            os.startfile(self.video_download_folder)
        else:
            QMessageBox.critical(self,"Folder Not Found ","The specified folder does not exits")
        
    def openImageFolder(self):

        if os.path.exists(self.download_image_folder):
            os.startfile(self.download_image_folder)

        else:
            QMessageBox.critical(self,"Folder Not Found","The specifed folder does not exist.Please Select folder frist")
            

    def OpenstoryFolder(self):
        if os.path.exists(self.story_download_folder):
            os.startfile(self.story_download_folder)
        else:
            QMessageBox.critical(self,"Folder Not Found","The specifed folder does not exist . Please select folder frist")



    def video_download_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.video_download_folder = folder
            self.video_download_entry.setText(folder)
            #self.create_ld_folder()
            if self.savecallback:
                self.savecallback()

    def story_download_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.story_download_folder = folder
            self.story_download_entry.setText(folder)
            #self.create_ld_folder()
            if self.savecallback:
                self.savecallback()
                
    def clean_name(self,text):
        """
        Remove all types of newline/carriage return combinations and return the clean name.

        Args:
            text (str): Input string containing name with newline characters

        Returns:
            str: Clean name without any newline characters
        """
        # Remove all combinations of \r and \n
        cleaned = text.replace('\r\n', '').replace('\n\r', '').replace('\r', '').replace('\n', '')

        # Strip whitespace and return the full clean name
        return cleaned.strip()
    
    def switch_and_next_update(self):
        self.auto_reels_edit = self.auto_reels_edit_checkbox.isChecked()
        self.auto_image_edit = self.auto_image_edit_checkbox.isChecked()
        self.auto_bonus_edit = self.auto_bonus_edit_checkbox.isChecked()
        self.bonus_upload = self.bonus_upload_checkbox.isChecked()
        self.video_upload = self.video_upload_checkbox.isChecked()
        self.story_upload = self.story_upload_checkbox.isChecked()
        
        if self.savecallback:
            self.savecallback()
        QMessageBox.information(self, "Availability", "This feature will be available from next update")
    
    def create_ld_folder(self):

        self.main_folder = self.extract_main_folder()

        if not self.main_folder:
            QMessageBox.critical(self, "Main Folder", "Please select main folder first")
            return
        
        profile_name = self.clean_name(self.current_profile)
        
        image_folder_name = f"{profile_name}_img"
        reel_folder_name = f"{profile_name}_reel"
        video_folder_name = f"{profile_name}_vid"
        story_folder_name = f"{profile_name}_story"            

        
        image_folder_path = os.path.join(self.main_folder, image_folder_name)
        image_folder_path = os.path.normpath(image_folder_path)

        reel_folder_path = os.path.join(self.main_folder, reel_folder_name)
        reel_folder_path = os.path.normpath(reel_folder_path)

        video_folder_path = os.path.join(self.main_folder, video_folder_name)
        video_folder_path = os.path.normpath(video_folder_path)

        story_folder_path = os.path.join(self.main_folder, story_folder_name)
        story_folder_path = os.path.normpath(story_folder_path)
        
        
        image_folder_created = False
        reel_folder_created = False
        video_folder_created = False
        story_folder_craated = False
        
        if self.main_folder:
            if not os.path.exists(image_folder_path):
                os.makedirs(image_folder_path, exist_ok=True)
                image_folder_created = True
            if not os.path.exists(reel_folder_path):
                os.makedirs(reel_folder_path, exist_ok=True)
                reel_folder_created = True
            if not os.path.exists(video_folder_path):
                os.makedirs(video_folder_path, exist_ok=True)
                video_folder_created = True
            if not os.path.exists(story_folder_path):
                os.makedirs(story_folder_path, exist_ok=True)
                story_folder_craated = True


            image_folder_absolute_path = os.path.abspath(image_folder_path)
            reel_folder_absolute_path = os.path.abspath(reel_folder_path)
            video_folder_absolute_path = os.path.abspath(video_folder_path)
            story_folder_absolute_path = os.path.abspath(story_folder_path)
            
            self.image_ld_folder = image_folder_absolute_path
            self.reel_ld_folder = reel_folder_absolute_path  
            self.video_ld_folder = video_folder_absolute_path
            self.story_video_ld_folder = story_folder_absolute_path
            
            """             self.image_folder_entry.setText(image_folder_absolute_path)
            self.video_folder_entry.setText(video_folder_absolute_path) """

            """             if image_folder_created and reel_folder_created:
                QMessageBox.information(self, "Folder Created", "Folder created successfully")
            elif image_folder_created:
                QMessageBox.information(self, "Folder Created", "Image Folder created successfully, video folder already exists")
            elif reel_folder_created:
                QMessageBox.information(self, "Folder Created", "Video Folder created successfully, image folder already exists")
            else:
                QMessageBox.information(self, "Folder Exists", "Folders already exist") """
        else:
            QMessageBox.critical(self, "Main Folder", "Please select main folder first")
    
    def create_download_folder(self):

        self.main_folder = self.extract_main_folder()

        if not self.main_folder:
            QMessageBox.critical(self, "Main Folder", "Please select main folder first")
            return
        main_folder_for_download = os.path.dirname(self.main_folder) if self.main_folder else ""
        
        profile_name = self.clean_name(self.current_profile)

        
        download_image_folder_name = f"{profile_name}_download_img"
        download_reel_folder_name = f"{profile_name}_download_reel"
        download_video_folder_name = f"{profile_name}_download_vid"
        download_story_folder_name = f"{profile_name}_download_story"

        
        download_image_folder_path = os.path.join(main_folder_for_download,profile_name, download_image_folder_name)
        download_image_folder_path = os.path.normpath(download_image_folder_path)

        download_reel_folder_path = os.path.join(main_folder_for_download,profile_name,download_reel_folder_name)
        download_reel_folder_path = os.path.normpath(download_reel_folder_path)
        
        download_video_folder_path = os.path.join(main_folder_for_download,profile_name,download_video_folder_name)
        download_video_folder_path = os.path.normpath(download_video_folder_path)

        download_story_folder_path = os.path.join(main_folder_for_download,profile_name,download_story_folder_name)
        download_story_folder_path = os.path.normpath(download_story_folder_path)
        
        image_folder_created = False
        reel_folder_created = False
        video_folder_created = False
        story_folder_crated = False

        
        if main_folder_for_download:
            if not os.path.exists(download_image_folder_path):
                os.makedirs(download_image_folder_path, exist_ok=True)
                image_folder_created = True

            if not os.path.exists(download_reel_folder_path):
                os.makedirs(download_reel_folder_path, exist_ok=True)
                reel_folder_created = True

            if not os.path.exists(download_video_folder_path):
                os.makedirs(download_video_folder_path, exist_ok=True)
                video_folder_created = True

            if not os.path.exists(download_story_folder_path):
                os.makedirs(download_story_folder_path, exist_ok=True)
                story_folder_crated = True

            
            image_folder_absolute_path = os.path.abspath(download_image_folder_path)
            reel_folder_absolute_path = os.path.abspath(download_reel_folder_path)
            video_folder_absolute_path = os.path.abspath(download_video_folder_path)
            story_folder_absolute_path = os.path.abspath(download_story_folder_path)

            
            self.download_image_folder = image_folder_absolute_path
            self.reel_download_folder = reel_folder_absolute_path
            self.video_download_folder = video_folder_absolute_path
            self.story_download_folder = story_folder_absolute_path

            
            self.image_download_entry.setText(image_folder_absolute_path)
            self.reel_download_entry.setText(reel_folder_absolute_path)
            self.video_download_entry.setText(video_folder_absolute_path)
            self.story_download_entry.setText(story_folder_absolute_path)
            
            #self.create_ld_folder()

            if self.savecallback:
                self.savecallback()
                
            if image_folder_created and reel_folder_created:
                QMessageBox.information(self, "Folder Created", "Folder created successfully")
            elif image_folder_created:
                QMessageBox.information(self, "Folder Created", "Image Folder created successfully, video folder already exists")
            elif reel_folder_created:
                QMessageBox.information(self, "Folder Created", "Video Folder created successfully, image folder already exists")
            else:
                QMessageBox.information(self, "Folder Exists", "Folders already exist")
        else:
            QMessageBox.critical(self, "Main Folder", "Please select main folder first")
    
    def extract_main_folder(self):
        if self.main_folder:
            return self.main_folder
    
    def open_configure_window(self):
        try:
            # Create the configure window with this as parent
            configure_window = ConfigureWindow(
                json_file_path=self.json_file_path,
                id_frame_idx=self.id_frame_idx,
                profile_name=self.current_profile, 
                parent=self 
            )

            configure_window.setMinimumHeight(840)
            configure_window.exec()

        except Exception as e:
            QMessageBox.critical(self, "Configure Window", f"Error opening ConfigureWindow: {e}")


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






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    profile_frame = MakeProfileFrame()
    window.setCentralWidget(profile_frame)
    # Example usage: create_frame(1, "path/to/config.json")
    profile_frame.create_frame(id_frame_idx=1,json_path=r"E:\geni_flow_ui_v1.0\facebook_tool_0.8\User_Data\Page_manager.json")
    window.show()
    sys.exit(app.exec())