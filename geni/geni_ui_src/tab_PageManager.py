from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFrame, QPushButton, QGraphicsOpacityEffect, QSizePolicy, QScrollArea,
    QCheckBox, QMessageBox,QGridLayout,QMenu,QDialog,QGroupBox,QComboBox,QSpinBox,QAbstractSpinBox,QProgressBar,QFileDialog
)

from PySide6.QtCore import Qt, QSize, Property, QPropertyAnimation, QEasingCurve, QThread, Signal, QObject, QTimer,QThread, Slot,QEvent
from PySide6.QtGui import QColor,QFont,QPixmap,QCursor,QAction,QIcon,QPalette

import json
import time
import os
from geni_ui_src.Page_manager_reader import DevicesJson
from geni_backend_src.bulk_config_settings_editor import BulkConfigSettingsEditors
from geni_ui_src.tab_autouploade import PageConfig
from geni_ui_src.create_folder_config_ld import create_folder_and_config

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

class AnimatedFrame(QFrame):
    """Frame with opacity animation capability that affects all child widgets"""
    def __init__(self,bg_color="rgba(128,128,128,0.2)", parent=None):
        super().__init__(parent)
        # Set background style
        self.setStyleSheet(f"background-color:{str(bg_color)};")
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create opacity effect for the entire widget and its children
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)  # Start fully transparent
        self.setGraphicsEffect(self.opacity_effect)
        
        # Create animation but don't start it yet
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)  # 500ms animation
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)  # Full opacity
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def getOpacity(self):
        return self.opacity_effect.opacity()
        
    def setOpacity(self, value):
        self.opacity_effect.setOpacity(value)
        
    def start_animation(self):
        """Start the fade-in animation"""
        self.animation.start()
        
    opacity = Property(float, getOpacity, setOpacity)

class AnimatedFrame_t(QFrame):
    """Frame with opacity animation capability that affects all child widgets"""
    def __init__(self,bg_color="rgba(128,128,128,0.2)", parent=None):
        super().__init__(parent)
        # Set background style
        self.setStyleSheet(f"background-color:{str(bg_color)};")
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create opacity effect for the entire widget and its children
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)  # Start fully transparent
        self.setGraphicsEffect(self.opacity_effect)
        
        # Create animation but don't start it yet
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)  # 500ms animation
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)  # Full opacity
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def getOpacity(self):
        return self.opacity_effect.opacity()
        
    def setOpacity(self, value):
        self.opacity_effect.setOpacity(value)
        
    def start_animation(self):
        """Start the fade-in animation"""
        self.animation.start()
        
    opacity = Property(float, getOpacity, setOpacity)

class SelectableFrame(QFrame):
    """A frame that can be selected with a checkbox"""
    frame_selected = Signal(int)  # Signal to emit when frame is selected
    
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        
        self.is_selected = False
        self.setStyleSheet("background-color: transparent;border-radius:8px;")
        self.setCursor(Qt.PointingHandCursor)
        
        # Make sure mouse events are tracked for this widget
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        """Handle mouse press events on the frame"""
        # Toggle selection state and emit signal
        self.setSelected(True) 
        super().mousePressEvent(event)
        
    def setSelected(self, selected):
        """Set the selection state of the frame"""
        if self.is_selected == selected:
            return 
            
        self.is_selected = selected
        
        # Update visual appearance
        if self.is_selected:
            self.setStyleSheet("background-color: rgba(128,128,128,0.4);border-radius:8px;")
        else:
            self.setStyleSheet("background-color: transparent;border-radius:8px;")
            
        # Emit signal with frame index
        self.frame_selected.emit(self.index if selected else -1)
        
    def enterEvent(self, event):
        """Handle mouse entering the frame area"""
        
        if not self.is_selected:
            self.setStyleSheet("background-color: rgba(128,128,128,0.15);border-radius:8px;")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leaving the frame area"""
        # Restore original style if not selected
        if not self.is_selected:
            self.setStyleSheet("background-color: transparent;border-radius:8px;")
        super().leaveEvent(event)

# Class to manage selection of frames
class FrameSelectionManager(QObject):
    def __init__(self):
        super().__init__()
        self.currently_selected_frame = None
        
    def set_selected_frame(self, frame):
        # Deselect previous frame if it exists
        if self.currently_selected_frame and self.currently_selected_frame != frame:
            try:
                # Check if the frame is still valid before calling setSelected
                if hasattr(self.currently_selected_frame, 'setSelected'):
                    self.currently_selected_frame.setSelected(False)
            except RuntimeError:
                # Object might have been deleted
                pass

        # Set new selected frame
        self.currently_selected_frame = frame

# Global selection manager
frame_selection_manager = FrameSelectionManager()

class BulkEditTaskProcessor(QObject):
    """Worker object that processes bulk edits in a separate thread"""
    

    progress_updated = Signal(int, str, int)  
    task_completed = Signal()
    
    def __init__(self, bulk_settings_editor, source_index, target_indices, bulk_config_props):
        """Initialize the task processor
        
        Args:
            bulk_settings_editor: BulkConfigSettingsEditors instance
            source_index: Source ID to copy from
            target_indices: List of target IDs to copy to
            bulk_config_props: Dictionary of configuration properties to copy
        """
        super().__init__()
        self.bulk_settings_editor = bulk_settings_editor
        self.source_index = source_index
        self.target_indices = target_indices
        self.bulk_config_props = bulk_config_props
        self.progress_count = 0
        self.total_count = len(target_indices)
    
    def process(self):
        """Process the bulk edit task"""
        try:
            # Set up variables to track progress
            last_progress_message = ""
            last_id = 0
            
            # Start the copy process
            self.bulk_settings_editor.copy_id_info_config(
                self.source_index,
                self.target_indices,
                self.bulk_config_props
            )
            
           
            while not self.bulk_settings_editor.is_task_done:
                current_progress = self.bulk_settings_editor.task_progress
                
                
                if current_progress.startswith("Editing "):
                    try:
                        id_part = current_progress.split(" ")[1]
                        current_id = int(id_part.split(".")[0])
                        last_id = current_id
                    except (IndexError, ValueError):
                        current_id = last_id
                
               
                if current_progress.startswith("Editing Done On"):
                    try:
                        id_part = current_progress.split(" ")[3]
                        current_id = int(id_part.split(".")[0])
                        last_id = current_id
                        self.progress_count += 1
                    except (IndexError, ValueError):
                        current_id = last_id
                
               
                if current_progress != last_progress_message:
                    self.progress_updated.emit(last_id, current_progress, self.progress_count)
                    last_progress_message = current_progress
                
               
                time.sleep(0.1)
            
            # Save changes to the JSON file
            self.bulk_settings_editor.save_json_file()
            
            # Signal task completion
            self.task_completed.emit()
            
        except Exception as e:
           
            error_message = f"Error: {str(e)}"
            self.progress_updated.emit(0, error_message, 0)
            print(f"Error processing bulk edits: {error_message}")



class IdFrame(QWidget):
    def __init__(self, index, show_auto_upload_checkbox=False, is_page_info_hidden=False, edit_mode=False,main_frame_border_color=None,insite_spawn_callback=None,view_id_active_check_box=False,select_callback=None,save_callback=None):
        super().__init__()
        self.index = index

        self.show_auto_upload_checkbox = show_auto_upload_checkbox
        self.view_id_active_check_box =view_id_active_check_box
        self.page_manager_path = r"User_Data\Page_manager.json"
        self.page_widgets = []
        self.animations = []  
        self.edit_mode = edit_mode 
        self.event_filter = CheckBoxEventFilter()
        self.is_bulk_settings_edits_task_done =False
        self.insite_spawn_callback = insite_spawn_callback
        self.is_page_info_hidden = is_page_info_hidden  
        self.select_callback = select_callback
        self.savecall_back = save_callback
        self.main_fram_border_color = "128,128,128,1"

        # configuration properties
        self.bulk_config_props = {
          
            "upload_method": False,
            "download_edits": False,
            "upload_type": False,
           
            "scroll_reels_video": False,
            "scroll_feeds": False,
            "check_reply_msg": False,
            "add_confirm_friends": False,
            "post_checkin": False,
            "create_story": False,
            "check_notification": False,
            "loops": False,
           
            "Reels": {
                "download_config": False,
                "caption_config": False,
                "schedule_time": False,
                "auto_edits": False
            },
            "Video": {
                "download_config": False,
                "caption_config": False,
                "schedule_time": False,
                "auto_edits": False
            },
            "Bonus": {
                "download_config": False,
                "caption_config": False,
                "schedule_time": False,
                "auto_edits": False
            },
            "Story": {
                "download_config": False,
                "caption_config": False,
                "schedule_time": False,
                "auto_edits": False
            }
        }

        self.bulk_folder_crate_ld_config_prop = {

            "config_ld":False,
            "create_download_folder":False,
            "setup_chrome":False,
            "create_id_act_post_photo_folder":False,
            "create_id_act_post_video_folder":False,
            "create_id_act_post_cheackin_folder":False
        }

        if main_frame_border_color:
            self.main_fram_border_color = main_frame_border_color  


        self.lineedit_fields = [] 
        self.init_ui()
        
        # Enable context menu for this widget
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Create a selectable frame as the container
        self.selectable_frame = SelectableFrame(self.index)
        selectable_layout = QHBoxLayout(self.selectable_frame)
        selectable_layout.setContentsMargins(5, 5, 5, 5)
        selectable_layout.setSpacing(10)
        
        # Add checkbox
        if self.view_id_active_check_box:
            self.id_active_checkbox = QCheckBox()
            self.id_active_checkbox.setFixedSize(20, 20)
            self.id_active_checkbox.clicked.connect(self.checkbox_state_changed)
            self.id_active_checkbox.installEventFilter(self)
            selectable_layout.addWidget(self.id_active_checkbox)

        if self.show_auto_upload_checkbox:
            self.upload_checkbox = QCheckBox()
            self.upload_checkbox.setFixedSize(20, 20)
            self.upload_checkbox.clicked.connect(self.checkbox_state_changed)
            self.upload_checkbox.installEventFilter(self)
            selectable_layout.addWidget(self.upload_checkbox)
        
       
        self.id_frame = QFrame()
        
        self.id_frame.setStyleSheet(
            f"border: 2px solid rgba({self.main_fram_border_color}); border-radius: 8px; background-color:rgba(128,128,128,0.1);"
        )
        self.id_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        selectable_layout.addWidget(self.id_frame)
        
        
        self.id_frame.setContextMenuPolicy(Qt.CustomContextMenu)
        self.id_frame.customContextMenuRequested.connect(self.show_context_menu)
        
      
        main_layout.addWidget(self.selectable_frame)
        
        
        self.selectable_frame.frame_selected.connect(self.on_frame_selected)
        
       
        frame1_layout = QVBoxLayout(self.id_frame)
        frame1_layout.setSpacing(8)

        # Header
        top_frame = QFrame()
        top_frame.setStyleSheet("border:none; background:none;")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)
        index_label = QLabel(f"{self.index}.")
        index_label.setStyleSheet("font-weight:bold; font-size:14px; border:none; background:none;")
        top_layout.addWidget(index_label)
        title_label = QLabel("ID Information")
        title_label.setStyleSheet("font-weight:bold; font-size:14px; border:none; background:none;")
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        frame1_layout.addWidget(top_frame)

        # ID Fields
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color:rgba(128,128,128,0.2); border:none;")
        info_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(10)
        
        field_sets = [
            {"label_id_name": "id_name:", "placeholder": "Enter id_name"},
            {"label_package_name": "package_name:", "placeholder": "com.facebook.katana"},
            {"label_ld_name": "Ld_name:", "placeholder": "Enter Ld_name"}
        ]
        
        #-----------------id_name ------------------
        
        id_label = QLabel("ID Name:")
        id_label.setStyleSheet("background-color:none;border:none;")
        info_layout.addWidget(id_label)
        
        self.id_entry = QLineEdit()
        self.id_entry.setMinimumHeight(24)
        self.id_entry.setPlaceholderText("Enter Ld Name")
        self.id_entry.setStyleSheet(
            "background-color:rgba(128,128,128,0.2); border:2px solid rgba(128,128,128,0.5);"
        )

        self.id_entry.setReadOnly(not self.edit_mode)  
        self.lineedit_fields.append(self.id_entry)  
        info_layout.addWidget(self.id_entry)
        frame1_layout.addWidget(info_frame)

        #------------------package_name------------------

        package_label = QLabel("Package Name:")
        package_label.setStyleSheet("background-color:none;border:none;")
        info_layout.addWidget(package_label)
        
        self.package_name_entry = QLineEdit()
        self.package_name_entry.setMinimumHeight(24)
        self.package_name_entry.setPlaceholderText("Enter Package name")
        self.package_name_entry.setStyleSheet(
            "background-color:rgba(128,128,128,0.2); border:2px solid rgba(128,128,128,0.5);"
        )

        self.package_name_entry.setReadOnly(not self.edit_mode)  
        self.lineedit_fields.append(self.package_name_entry)  
        info_layout.addWidget(self.package_name_entry)
        frame1_layout.addWidget(info_frame)

        #-----------------------Ld_name-------------
        
        ld_name_label = QLabel("Ld Name:")
        ld_name_label.setStyleSheet("background-color:none;border:none;")
        info_layout.addWidget(ld_name_label)
        
        self.ld_name_entry = QLineEdit()
        self.ld_name_entry.setMinimumHeight(24)
        self.ld_name_entry.setPlaceholderText("Enter Ld name")
        self.ld_name_entry.setStyleSheet(
            "background-color:rgba(128,128,128,0.2); border:2px solid rgba(128,128,128,0.5);"
        )

        self.ld_name_entry.setReadOnly(not self.edit_mode)  
        self.lineedit_fields.append(self.ld_name_entry)  
        info_layout.addWidget(self.ld_name_entry)
        frame1_layout.addWidget(info_frame)

        
        page_info_header = QFrame()
        page_info_header.setStyleSheet("border:none; background:none;")
        page_info_header_layout = QHBoxLayout(page_info_header)
        page_info_header_layout.setContentsMargins(0, 5, 0, 5)
        
        if not self.is_page_info_hidden:
            page_info_label = QLabel("Page Information")
            page_info_label.setStyleSheet("font-weight:bold; font-size:12px; border:none; background:none;")
            page_info_header_layout.addWidget(page_info_label)
            page_info_header_layout.addStretch()
        
        frame1_layout.addWidget(page_info_header)

       
       
        self.pages_container = QFrame()
        self.pages_container.setStyleSheet("border:none; background:none;")
        self.pages_container_layout = QVBoxLayout(self.pages_container)
        self.pages_container_layout.setContentsMargins(0, 0, 0, 0)
        self.pages_container_layout.setSpacing(5)
        
        
        
        self.page_entries_container = QVBoxLayout()
        self.page_entries_container.setSpacing(5)
        self.pages_container_layout.addLayout(self.page_entries_container)

       
       
        self.button_container = QFrame()
        self.button_container.setStyleSheet("border:none; background:none;")
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 5, 0, 5)
        
       
       
        self.add_page_btn = AnimatedHoverButton("Add Page")
        self.add_page_btn.setFixedSize(QSize(100, 30))
        self.add_page_btn.setDefault(False)
        self.add_page_btn.setAutoDefault(False)
       
       
        self.add_page_btn.clicked.connect(lambda: self.add_page_entry())
        button_layout.addWidget(self.add_page_btn)
        button_layout.addStretch()
        
        self.pages_container_layout.addWidget(self.button_container)
        frame1_layout.addWidget(self.pages_container)
        
        
        self.update_edit_controls_visibility()
        
       
        self.update_page_info_visibility()




    def show_context_menu(self, position):
        """Display context menu on right-click"""
        context_menu = QMenu(self)
        
        palette = context_menu.palette()
        bg_color = palette.color(QPalette.Window)
       
        fetch_icon = QIcon.fromTheme("view-refresh", QIcon(":/icons/refresh.png"))
        bulk_edit_action = QAction(fetch_icon,"Open Bulk Configuration Edits", self)
        bulk_edit_action.triggered.connect(self.open_bulk_configuration_edits_dilogbox)
        context_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {bg_color.name()};
                border: 1px solid #999999;
                padding: 5px;
                border-radius:8px;
            }}
            QMenu::item {{
    
                padding: 6px 20px 6px 20px;
                border-radius: 3px;
            }}
            QMenu::item:selected {{
                background-color: #0078d7;
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #cccccc;
                margin: 3px 0px 3px 0px;
            }}
        """)
        
        context_menu.addAction(bulk_edit_action)
        

        # Show the context menu at the cursor position
        context_menu.exec(self.mapToGlobal(position))
    
    def open_bulk_configuration_edits_dilogbox(self):
        """Handle the 'Open Bulk Configuration Edits' action"""
        # Select the frame first (to ensure it's the active frame)
        self.selectable_frame.setSelected(True)
        frame_selection_manager.set_selected_frame(self.selectable_frame)
        
        # Perform the bulk configuration action
        print(f"Opening bulk configuration editor for ID {self.index}")
        
        self.bulk_configuration_edits_dilogbox()
        
        
        if hasattr(self, 'select_callback') and self.select_callback:
            self.select_callback(self.index, "bulk_config")

    def update_checkbox_property(self, checkbox, property_name, content_type=None):
        """Update property value when checkbox state changes"""
        state = checkbox.isChecked()
        
        if content_type is None:
            
            self.bulk_config_props[property_name] = state
        else:
            
            self.bulk_config_props[content_type][property_name] = state
            
        print(f"Updated {property_name} for {'common' if content_type is None else content_type}: {state}")


    def bulk_configuration_edits_dilogbox(self):
        """Show a dialog for fetching information about selected LDs."""
    
        self.fetch_info_dilog = QDialog(parent=self)
        self.fetch_info_dilog.setWindowTitle("Bulk Edits Configuration")
        self.fetch_info_dilog.setFixedSize(600, 800)  
        palette = self.fetch_info_dilog.palette()
        bg_color = palette.color(QPalette.Window)
        self.fetch_info_dilog.setStyleSheet(f"""
        QDialog {{
            background-color: {bg_color.name()};
        }}
    """)
    
        # Create main layout for the dialog
        dialog_layout = QVBoxLayout(self.fetch_info_dilog)
    
        auto_upload_and_id_active_frame = QFrame()
        auto_upload_and_id_active_layout = QHBoxLayout(auto_upload_and_id_active_frame)
    
        # Create a group box for organizing auto upload settings
        auto_upload_settings_groupbox = QGroupBox(title="Auto Upload Settings")
        auto_upload_settings_groupbox.setObjectName("auto_upload_settings")
        auto_upload_settings_groupbox.setStyleSheet("""QGroupBox#auto_upload_settings{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#auto_upload_settings::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        auto_upload_layout = QVBoxLayout(auto_upload_settings_groupbox)
    
        # Add checkboxes for configuration options with connection to properties
        self.upload_method_checkbox = QCheckBox("Copy Upload Method")
        self.upload_method_checkbox.setChecked(self.bulk_config_props["upload_method"])
        self.upload_method_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.upload_method_checkbox, "upload_method")
        )
        
        self.download_edits_checkbox = QCheckBox("Copy Configure Download Edits Section")
        self.download_edits_checkbox.setChecked(self.bulk_config_props["download_edits"])
        self.download_edits_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.download_edits_checkbox, "download_edits")
        )
        
        self.upload_type_checkbox = QCheckBox("Copy Configure Upload Type")
        self.upload_type_checkbox.setChecked(self.bulk_config_props["upload_type"])
        self.upload_type_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.upload_type_checkbox, "upload_type")
        )
    
        auto_upload_layout.addWidget(self.upload_method_checkbox)
        auto_upload_layout.addWidget(self.download_edits_checkbox)
        auto_upload_layout.addWidget(self.upload_type_checkbox)
    
        # Create ID Active group box
        id_active_groupbox = QGroupBox(title="ID Active")
        id_active_groupbox.setObjectName("id_active")
        id_active_groupbox.setStyleSheet("""QGroupBox#id_active{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#id_active::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        id_active_layout = QVBoxLayout(id_active_groupbox)
        
        # Create checkboxes id active checkbox
        self.scroll_reels_video_checkbox = QCheckBox("Copy scroll reels and video feed")
        self.scroll_reels_video_checkbox.setChecked(self.bulk_config_props["scroll_reels_video"])
        self.scroll_reels_video_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.scroll_reels_video_checkbox, "scroll_reels_video")
        )
        
        self.scroll_feeds_checkbox = QCheckBox("Copy scroll feeds")
        self.scroll_feeds_checkbox.setChecked(self.bulk_config_props["scroll_feeds"])
        self.scroll_feeds_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.scroll_feeds_checkbox, "scroll_feeds")
        )
        
        self.check_reply_msg_checkbox = QCheckBox("Copy check and reply msg")
        self.check_reply_msg_checkbox.setChecked(self.bulk_config_props["check_reply_msg"])
        self.check_reply_msg_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.check_reply_msg_checkbox, "check_reply_msg")
        )
        
        self.add_confirm_friends_checkbox = QCheckBox("Copy add and confirm friends")
        self.add_confirm_friends_checkbox.setChecked(self.bulk_config_props["add_confirm_friends"])
        self.add_confirm_friends_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.add_confirm_friends_checkbox, "add_confirm_friends")
        )
        
        self.post_checkin_checkbox = QCheckBox("Copy post checkIN")
        self.post_checkin_checkbox.setChecked(self.bulk_config_props["post_checkin"])
        self.post_checkin_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.post_checkin_checkbox, "post_checkin")
        )
        
        self.create_story_checkbox = QCheckBox("Copy create story")
        self.create_story_checkbox.setChecked(self.bulk_config_props["create_story"])
        self.create_story_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.create_story_checkbox, "create_story")
        )
        
        self.check_notification_checkbox = QCheckBox("Copy check notification")
        self.check_notification_checkbox.setChecked(self.bulk_config_props["check_notification"])
        self.check_notification_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.check_notification_checkbox, "check_notification")
        )
        
        self.loops_checkbox = QCheckBox("Copy loops")
        self.loops_checkbox.setChecked(self.bulk_config_props["loops"])
        self.loops_checkbox.stateChanged.connect(
            lambda: self.update_checkbox_property(self.loops_checkbox, "loops")
        )
        
        # Add checkboxes to ID Active layout
        id_active_layout.addWidget(self.scroll_reels_video_checkbox)
        id_active_layout.addWidget(self.scroll_feeds_checkbox)
        id_active_layout.addWidget(self.check_reply_msg_checkbox)
        id_active_layout.addWidget(self.add_confirm_friends_checkbox)
        id_active_layout.addWidget(self.post_checkin_checkbox)
        id_active_layout.addWidget(self.create_story_checkbox)
        id_active_layout.addWidget(self.check_notification_checkbox)
        id_active_layout.addWidget(self.loops_checkbox)
        
     
        auto_upload_and_id_active_layout.addWidget(auto_upload_settings_groupbox)
        auto_upload_and_id_active_layout.addWidget(id_active_groupbox)
        
        # Create Configure Options frame with content type selector
        configure_options_frame = QGroupBox("Configure Options")
        configure_options_frame.setObjectName("configure_options")
        configure_options_frame.setStyleSheet("""QGroupBox#configure_options{border:1px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:10px;
                                    margin-top:10px;
                                    padding-right:5px;
                                    padding-left:5px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#configure_options::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        configure_options_layout = QVBoxLayout(configure_options_frame)
    
        # Content type selector
        content_type_layout = QHBoxLayout()
        content_type_label = QLabel("Content Type:")
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems(["Reels", "Video", "Bonus", "Story"])
        content_type_layout.addWidget(content_type_label)
        content_type_layout.addWidget(self.content_type_combo)
        content_type_layout.addStretch(0)
        configure_options_layout.addLayout(content_type_layout)
    
        # Configuration options that change based on content type
        self.download_config_checkbox = QCheckBox("Copy Download Configuration")
        self.caption_config_checkbox = QCheckBox("Copy Caption Configure")
        self.schedule_time_checkbox = QCheckBox("Copy Set Schedule Time")
        self.auto_edits_checkbox = QCheckBox("Copy Auto Edits")
    
        configure_options_layout.addWidget(self.download_config_checkbox)
        configure_options_layout.addWidget(self.caption_config_checkbox)
        configure_options_layout.addWidget(self.schedule_time_checkbox)
        configure_options_layout.addWidget(self.auto_edits_checkbox)
    
        #default Reels
        initial_content_type = self.content_type_combo.currentText()
        
        # Block signals while setting initial values
        self.download_config_checkbox.blockSignals(True)
        self.caption_config_checkbox.blockSignals(True)
        self.schedule_time_checkbox.blockSignals(True)
        self.auto_edits_checkbox.blockSignals(True)
        
        self.download_config_checkbox.setChecked(self.bulk_config_props[initial_content_type]["download_config"])
        self.caption_config_checkbox.setChecked(self.bulk_config_props[initial_content_type]["caption_config"])
        self.schedule_time_checkbox.setChecked(self.bulk_config_props[initial_content_type]["schedule_time"])
        self.auto_edits_checkbox.setChecked(self.bulk_config_props[initial_content_type]["auto_edits"])
        
        self.download_config_checkbox.blockSignals(False)
        self.caption_config_checkbox.blockSignals(False)
        self.schedule_time_checkbox.blockSignals(False)
        self.auto_edits_checkbox.blockSignals(False)
        
        #initial text
        self.download_config_checkbox.setText(f"{initial_content_type} Copy Download Configuration")
        self.caption_config_checkbox.setText(f"{initial_content_type} Copy Caption Configure")
        self.schedule_time_checkbox.setText(f"{initial_content_type} Copy Set Schedule Time")
        self.auto_edits_checkbox.setText(f"{initial_content_type} Copy Auto Edits")
        
        # Connect initial signals
        self._connect_content_checkbox_signals(initial_content_type)
        
        # Set previous content type property
        self.content_type_combo.setProperty("previous_content_type", initial_content_type)
        
        # Connect the combo box to update the checkbox labels and set initial values
        self.content_type_combo.currentTextChanged.connect(self.update_config_options)
    
        # Add start button
        self.start_fetch_activity_btn = AnimatedHoverButton(text="Start")
        self.start_fetch_activity_btn.setFixedSize(200,40)
        self.start_fetch_activity_btn.clicked.connect(self.run_bulk_setting_edits) 

        enter_id_information_to_edit_groupbox = QGroupBox("Enter IDs to Edits Settings")
        enter_id_information_to_edit_groupbox.setObjectName("enter_ids_to_edits")
        enter_id_information_to_edit_groupbox.setStyleSheet("""QGroupBox#enter_ids_to_edits{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#enter_ids_to_edits::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        
        enter_id_information_to_edit_layout = QHBoxLayout(enter_id_information_to_edit_groupbox)

        enter_id_information_label = QLabel("Enter IDs To Apply Edits:")
        enter_id_information_to_edit_layout.addWidget(enter_id_information_label)


        
        self.selected_ld_label = QLabel()
        self.selected_ld_label.setText(str(self.index))
        self.selected_ld_label.setStyleSheet(
            "background-color:rgba(128,128,128,0.5);"
            "padding: 3px 8px;"
            "border-radius: 5px;"
        )
        self.selected_ld_label.setFixedHeight(25)
        enter_id_information_to_edit_layout.addWidget(self.selected_ld_label)

        to_label = QLabel("To")
        enter_id_information_to_edit_layout.addWidget(to_label)
    
        self.enter_id_informaion_to_edit_intspinbox = IntSpinBox(from_=self.index + 1)
        enter_id_information_to_edit_layout.addWidget(self.enter_id_informaion_to_edit_intspinbox)

        enter_id_information_to_edit_layout.addStretch(1)

        # Add Auto Login group
        bulk_edit_folder_and_setup = QGroupBox("Bulk Folders Edits And LD's Setup")
        bulk_edit_folder_and_setup.setObjectName("bulk_edit_folder_setup")
        bulk_edit_folder_and_setup.setStyleSheet("""QGroupBox#bulk_edit_folder_setup{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#bulk_edit_folder_setup::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
    
        bulk_edit_folder_setup_layout = QVBoxLayout(bulk_edit_folder_and_setup)

        main_folder_andld_config_groupbox = QGroupBox("Main Folder")
        main_folder_andld_config_groupbox.setObjectName("main_folder_groupbox")
        main_folder_andld_config_groupbox.setStyleSheet("""QGroupBox#main_folder_groupbox{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#main_folder_groupbox::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        
        main_folder_and_ld_config_layout= QVBoxLayout(main_folder_andld_config_groupbox)


        all_ld_folder_layout = QHBoxLayout()

        all_ld_folder_path_label = QLabel(text="Select All LD Folder:")
        all_ld_folder_layout.addWidget(all_ld_folder_path_label)

        self.all_ld_folder_path = QLineEdit() 
        all_ld_folder_layout.addWidget(self.all_ld_folder_path)
        
        


        self.all_ld_folder_path_browse_btn = AnimatedHoverButton(text="Browse")
        self.all_ld_folder_path_browse_btn.clicked.connect(self.browse_all_ld_folder)
        all_ld_folder_layout.addWidget(self.all_ld_folder_path_browse_btn)


        bulk_edit_folder_setup_layout.addWidget(main_folder_andld_config_groupbox)

        folder_and_ld_configure_cheackbox_layout=QVBoxLayout()
        self.configure_ld_player=QCheckBox("Configure Ld Player") 
        self.configure_ld_player.clicked.connect(self.check_all_ld_folder_is_given_or_not)
        self.configure_ld_player.clicked.connect(self.update_create_folder_ld_config_prop)


        folder_and_ld_configure_cheackbox_layout.addWidget(self.configure_ld_player)

        #add all the layout to main folder
        main_folder_and_ld_config_layout.addLayout(all_ld_folder_layout)
        main_folder_and_ld_config_layout.addLayout(folder_and_ld_configure_cheackbox_layout)
        
        upload_id_active_bulk_folder_create_layout = QHBoxLayout()

        auto_upload_settings_folder_groupbox = QGroupBox(title="Auto Upload Settings")
        auto_upload_settings_folder_groupbox.setObjectName("auto_upload_folder_settings")
        auto_upload_settings_folder_groupbox.setStyleSheet("""QGroupBox#auto_upload_folder_settings{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#auto_upload_folder_settings::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        auto_upload_settings_folder_layout = QVBoxLayout(auto_upload_settings_folder_groupbox)

        self.create_download_folder_checkbox = QCheckBox("Create Download Folder")
        self.create_download_folder_checkbox.setChecked(True)
        self.create_download_folder_checkbox.clicked.connect(self.check_all_ld_folder_is_given_or_not)
        self.create_download_folder_checkbox.clicked.connect(self.update_create_folder_ld_config_prop)


        auto_upload_settings_folder_layout.addWidget(self.create_download_folder_checkbox)

        self.setup_chrome = QCheckBox("Setup chrome")
        self.setup_chrome.clicked.connect(self.check_all_ld_folder_is_given_or_not)
        self.setup_chrome.clicked.connect(self.update_create_folder_ld_config_prop)
        auto_upload_settings_folder_layout.addWidget(self.setup_chrome)

        upload_id_active_bulk_folder_create_layout.addWidget(auto_upload_settings_folder_groupbox)

        id_active_settings_folder_groupbox = QGroupBox(title="Id Active Settings")
        id_active_settings_folder_groupbox.setObjectName("id_active_folder_settings")
        id_active_settings_folder_groupbox.setStyleSheet("""QGroupBox#id_active_folder_settings{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#id_active_folder_settings::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        auto_upload_settings_folder_layout = QVBoxLayout(id_active_settings_folder_groupbox)

        self.create_IACT_photo_post_download_folder_checkbox = QCheckBox("Create Photo Post Download Folder")
        self.create_IACT_photo_post_download_folder_checkbox.clicked.connect(self.check_all_ld_folder_is_given_or_not)
        self.create_IACT_photo_post_download_folder_checkbox.clicked.connect(self.update_create_folder_ld_config_prop)
        auto_upload_settings_folder_layout.addWidget(self.create_IACT_photo_post_download_folder_checkbox)

        self.create_IACT_post_checkin_download_folder_checkbox = QCheckBox("Create Photo CheckIN Download Folder")
        self.create_IACT_post_checkin_download_folder_checkbox.clicked.connect(self.check_all_ld_folder_is_given_or_not)
        self.create_IACT_post_checkin_download_folder_checkbox.clicked.connect(self.update_create_folder_ld_config_prop)
        auto_upload_settings_folder_layout.addWidget(self.create_IACT_post_checkin_download_folder_checkbox)

        self.create_IACT_story_post_download_folder_checkbox = QCheckBox("Create Story Post Download Folder")
        self.create_IACT_story_post_download_folder_checkbox.clicked.connect(self.check_all_ld_folder_is_given_or_not)
        self.create_IACT_story_post_download_folder_checkbox.clicked.connect(self.update_create_folder_ld_config_prop)
        auto_upload_settings_folder_layout.addWidget(self.create_IACT_story_post_download_folder_checkbox)

        self.start_config_ld_and_create_folder_btn = AnimatedHoverButton(text="Start")
        self.start_config_ld_and_create_folder_btn.clicked.connect(self.start_folder_creat_and_ld_config_thred)
        self.start_config_ld_and_create_folder_btn.setFixedSize(200,40)



        upload_id_active_bulk_folder_create_layout.addWidget(id_active_settings_folder_groupbox)
        bulk_edit_folder_setup_layout.addLayout(upload_id_active_bulk_folder_create_layout)
        

        

        # Add buttons at the bottom
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.addStretch(1)
    
        close_button = AnimatedHoverButton("Close")
        close_button.clicked.connect(self.fetch_info_dilog.close)
        button_layout.addWidget(close_button)
    
        # Add everything to the main dialog layout
        dialog_layout.addWidget(auto_upload_and_id_active_frame)
        auto_upload_layout.addWidget(configure_options_frame)
        dialog_layout.addWidget(enter_id_information_to_edit_groupbox)
        dialog_layout.addWidget(self.start_fetch_activity_btn,alignment=Qt.AlignCenter)
        dialog_layout.addWidget(bulk_edit_folder_and_setup)
        dialog_layout.addWidget(self.start_config_ld_and_create_folder_btn,alignment=Qt.AlignCenter)
        dialog_layout.addWidget(button_frame)

        self.is_readonly = True

        self.fetch_info_dilog.exec()

    def browse_all_ld_folder(self):

        folder_path = QFileDialog.getExistingDirectory(self, "Select all ld Folder")
        if folder_path:

            self.all_ld_folder_path.setText(folder_path)       

    def check_all_ld_folder_is_given_or_not(self):

        text = self.all_ld_folder_path.text()

        if text:
            pass
        else:
            QMessageBox.warning(self,"Info","Please select all ld folder frist")
            self.configure_ld_player.setChecked(False)
            self.create_download_folder_checkbox.setChecked(False)
            self.setup_chrome.setChecked(False)
            self.create_IACT_photo_post_download_folder_checkbox.setChecked(False)
            self.create_IACT_post_checkin_download_folder_checkbox.setChecked(False)
            self.create_IACT_story_post_download_folder_checkbox.setChecked(False)



    def start_folder_creat_and_ld_config_thred(self):
        """Create and show progress dialog for folder creation and LD configuration"""
        all_ld_folder_path_l = self.all_ld_folder_path.text()
        if not all_ld_folder_path_l:
            QMessageBox.warning(self, "Info", "Please select all LD folder first")
            return

        copy_from_id = self.index + 1
        copy_to_id = self.enter_id_informaion_to_edit_intspinbox.get_value() + 1

        if copy_from_id >= copy_to_id:
            QMessageBox.warning(self, "Invalid Range", "Please enter a valid ID range")
            return

        total_ids = copy_to_id - copy_from_id

        # Create progress dialog
        self.folder_progress_dialog = QDialog(self.fetch_info_dilog)
        self.folder_progress_dialog.setWindowTitle("Folder Creation and LD Configuration Progress")
        self.folder_progress_dialog.setFixedSize(450, 180)
        self.folder_progress_dialog.setModal(True)

        # Create layout for progress dialog
        progress_layout = QVBoxLayout(self.folder_progress_dialog)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        progress_layout.setSpacing(15)

        # Add header label
        header_label = QLabel("Processing Folder Creation and LD Configuration")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(header_label)

        # Add progress description
        self.folder_progress_label = QLabel(f"Processing {total_ids} IDs...")
        self.folder_progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.folder_progress_label)

        # Add progress bar
        self.folder_progress_bar = QProgressBar()
        self.folder_progress_bar.setRange(0, total_ids)
        self.folder_progress_bar.setValue(0)
        self.folder_progress_bar.setTextVisible(True)
        self.folder_progress_bar.setAlignment(Qt.AlignCenter)
        self.folder_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgba(128, 128, 128, 0.8);
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: rgba(128, 128, 128, 0.2);
            }
            QProgressBar::chunk {
                background-color: rgba(0, 120, 215, 0.7);
                width: 1px;
            }
        """)
        progress_layout.addWidget(self.folder_progress_bar)

        # Add current ID label
        self.folder_current_id_label = QLabel("Starting...")
        self.folder_current_id_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.folder_current_id_label)

        # Add status label
        self.folder_status_label = QLabel("")
        self.folder_status_label.setAlignment(Qt.AlignCenter)
        self.folder_status_label.setStyleSheet("color: rgba(0, 120, 215, 1);")
        progress_layout.addWidget(self.folder_status_label)

        # Show the progress dialog
        self.folder_progress_dialog.show()

        # Create and configure the task processor thread
        self.folder_thread = QThread()
        self.folder_processor = FolderCreationProcessor(
            copy_from_id,
            copy_to_id,
            self.bulk_folder_crate_ld_config_prop,
            all_ld_folder_path_l
        )
        self.folder_processor.moveToThread(self.folder_thread)

        # Connect signals and slots
        self.folder_thread.started.connect(self.folder_processor.process)
        self.folder_processor.progress_updated.connect(self.update_folder_progress)
        self.folder_processor.task_completed.connect(self.on_folder_task_completed)
        self.folder_processor.task_completed.connect(self.folder_thread.quit)

        # Start the thread
        self.folder_thread.start()

    def update_folder_progress(self, current_id, message, progress):
        """Update the folder creation progress dialog with current status"""
        self.folder_progress_bar.setValue(progress)
        self.folder_current_id_label.setText(f"Current ID: {current_id}")
        self.folder_status_label.setText(message)

        # Format the progress percentage
        percentage = int((progress / self.folder_progress_bar.maximum()) * 100) if self.folder_progress_bar.maximum() > 0 else 0
        self.folder_progress_label.setText(f"Processing... {percentage}% complete")

    def on_folder_task_completed(self):
        """Handle folder creation task completion"""
        # Update UI to show completion
        self.folder_progress_bar.setValue(self.folder_progress_bar.maximum())
        self.folder_progress_label.setText("Folder creation and LD configuration completed successfully!")
        self.folder_status_label.setText("All configurations have been completed")
        self.folder_current_id_label.setText("Done!")

        # Close progress dialog after a short delay
        QTimer.singleShot(2000, self.folder_progress_dialog.accept)


            

        
    def update_create_folder_ld_config_prop(self):
        
        is_config_ld_enable = self.configure_ld_player.isChecked()
        is_setup_chrome_enable = self.setup_chrome.isChecked()
        is_create_download_folder_enable = self.create_download_folder_checkbox.isChecked()
        is_create_id_act_post_photo_enable = self.create_IACT_photo_post_download_folder_checkbox.isChecked()
        is_create_id_act_post_cheackin_enable = self.create_IACT_post_checkin_download_folder_checkbox.isChecked()
        is_create_id_act_post_story_enable = self.create_IACT_story_post_download_folder_checkbox.isChecked()
        
        self.bulk_folder_crate_ld_config_prop = {

            "config_ld":is_config_ld_enable,
            "create_download_folder":is_create_download_folder_enable,
            "setup_chrome":is_setup_chrome_enable,
            "create_id_act_post_photo_folder":is_create_id_act_post_photo_enable,
            "create_id_act_post_video_folder":is_create_id_act_post_story_enable,
            "create_id_act_post_cheackin_folder":is_create_id_act_post_cheackin_enable
        }

        print("config updated for folder config")
        print(self.bulk_folder_crate_ld_config_prop)

    
    def _disconnect_content_checkbox_signals(self):
        """Properly disconnect all signals from content-specific checkboxes"""
        try:
            self.download_config_checkbox.stateChanged.disconnect()
        except:
            pass
        try:
            self.caption_config_checkbox.stateChanged.disconnect()
        except:
            pass
        try:
            self.schedule_time_checkbox.stateChanged.disconnect()
        except:
            pass
        try:
            self.auto_edits_checkbox.stateChanged.disconnect()
        except:
            pass


    def _connect_content_checkbox_signals(self, content_type):
        """Connect checkbox signals for content-specific options"""
        self.download_config_checkbox.stateChanged.connect(
            lambda state: self.update_checkbox_property(self.download_config_checkbox, "download_config", content_type)
        )
        self.caption_config_checkbox.stateChanged.connect(
            lambda state: self.update_checkbox_property(self.caption_config_checkbox, "caption_config", content_type)
        )
        self.schedule_time_checkbox.stateChanged.connect(
            lambda state: self.update_checkbox_property(self.schedule_time_checkbox, "schedule_time", content_type)
        )
        self.auto_edits_checkbox.stateChanged.connect(
            lambda state: self.update_checkbox_property(self.auto_edits_checkbox, "auto_edits", content_type)
        )

    def update_config_options(self, content_type):
        """Update the configuration options based on selected content type."""
        #  save current checkbox 
        previous_content_type = self.sender().property("previous_content_type")
        if previous_content_type:
            # Save current states before changing
            self.bulk_config_props[previous_content_type]["download_config"] = self.download_config_checkbox.isChecked()
            self.bulk_config_props[previous_content_type]["caption_config"] = self.caption_config_checkbox.isChecked()
            self.bulk_config_props[previous_content_type]["schedule_time"] = self.schedule_time_checkbox.isChecked()
            self.bulk_config_props[previous_content_type]["auto_edits"] = self.auto_edits_checkbox.isChecked()

        # Properly disconnect all signals before updating 
        self._disconnect_content_checkbox_signals()

        # Update checkbox text based on the selected content type
        self.download_config_checkbox.setText(f"{content_type} Copy Download Configuration")
        self.caption_config_checkbox.setText(f"{content_type} Copy Caption Configure")
        self.schedule_time_checkbox.setText(f"{content_type} Copy Set Schedule Time")
        self.auto_edits_checkbox.setText(f"{content_type} Copy Auto Edits")


        self.download_config_checkbox.blockSignals(True)
        self.caption_config_checkbox.blockSignals(True)
        self.schedule_time_checkbox.blockSignals(True)
        self.auto_edits_checkbox.blockSignals(True)

        self.download_config_checkbox.setChecked(self.bulk_config_props[content_type]["download_config"])
        self.caption_config_checkbox.setChecked(self.bulk_config_props[content_type]["caption_config"])
        self.schedule_time_checkbox.setChecked(self.bulk_config_props[content_type]["schedule_time"])
        self.auto_edits_checkbox.setChecked(self.bulk_config_props[content_type]["auto_edits"])

        self.download_config_checkbox.blockSignals(False)
        self.caption_config_checkbox.blockSignals(False)
        self.schedule_time_checkbox.blockSignals(False)
        self.auto_edits_checkbox.blockSignals(False)

        # Connect signals for the new content type
        self._connect_content_checkbox_signals(content_type)

        # Store current content type for next change
        self.sender().setProperty("previous_content_type", content_type)

    def run_bulk_setting_edits(self):
        """Handle the "Start" button click to run bulk setting edits with progress tracking"""
        # Convert into list 
        ids_list = []
        copy_from_id = self.index
        copy_to_id = self.enter_id_informaion_to_edit_intspinbox.get_value() + 1

        for n in range(copy_from_id+1, copy_to_id):
            ids_list.append(n)

        if not ids_list:
            # No IDs to process
            QMessageBox.warning(self, "No IDs to Process", 
                                "Please enter a valid target ID range to apply bulk edits.")
            return

        # Create progress dialog
        self.progress_dialog = QDialog(self.fetch_info_dilog)
        self.progress_dialog.setWindowTitle("Bulk Configuration Progress")
        self.progress_dialog.setFixedSize(400, 180)
        self.progress_dialog.setModal(True)

        # Create layout for progress dialog
        progress_layout = QVBoxLayout(self.progress_dialog)
        progress_layout.setContentsMargins(20, 20, 20, 20)
        progress_layout.setSpacing(15)

        # Add header label
        header_label = QLabel("Processing Bulk Configuration Edits")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(header_label)

        # Add progress description
        self.progress_label = QLabel(f"Processing {len(ids_list)} IDs...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(ids_list))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgba(128, 128, 128, 0.8);
                border-radius: 5px;
                text-align: center;
                height: 25px;
               
            }
            QProgressBar::chunk {
                
                width: 1px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)

        # Add current ID label
        self.current_id_label = QLabel("Starting...")
        self.current_id_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.current_id_label)

        # Add status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        progress_layout.addWidget(self.status_label)

        # Create the BulkConfigSettingsEditors instance
        self.bulk_settings_editor = BulkConfigSettingsEditors(json_file_path=self.page_manager_path)

        # Show the progress dialog
        self.progress_dialog.show()

        # Create and configure the task processor thread
        self.task_thread = QThread()
        self.task_processor = BulkEditTaskProcessor(
            self.bulk_settings_editor,
            self.index,
            ids_list,
            self.bulk_config_props
        )
        self.task_processor.moveToThread(self.task_thread)

        # Connect signals and slots
        self.task_thread.started.connect(self.task_processor.process)
        self.task_processor.progress_updated.connect(self.update_progress)
        self.task_processor.task_completed.connect(self.on_task_completed)
        self.task_processor.task_completed.connect(self.task_thread.quit)

        # Start the thread
        self.task_thread.start()

    def update_progress(self, current_id, message, progress):
        """Update the progress dialog with current status"""
        self.progress_bar.setValue(progress)
        self.current_id_label.setText(f"Current ID: {current_id}")
        self.status_label.setText(message)

        # Format the progress percentage
        percentage = int((progress / self.progress_bar.maximum()) * 100) if self.progress_bar.maximum() > 0 else 0
        self.progress_label.setText(f"Processing... {percentage}% complete")

    def on_task_completed(self):
        """Handle task completion"""
        # Update UI to show completion
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.progress_label.setText("Bulk configuration completed successfully!")
        self.status_label.setText("All IDs have been updated")
        self.current_id_label.setText("Done!")

        # Set task done flag
        self.is_bulk_settings_edits_task_done = True

        # Close progress dialog after a short delay
        QTimer.singleShot(2000, self.progress_dialog.accept)


    def update_page_info_visibility(self):
        """Update visibility of page information section based on is_page_info_hidden"""
        if hasattr(self, 'pages_container'):
            self.pages_container.setVisible(not self.is_page_info_hidden)
    
    def eventFilter(self, obj, event):
        """Filter events to prevent checkbox clicks from selecting the frame"""
        if self.show_auto_upload_checkbox:
            if obj == self.upload_checkbox and event.type() == Qt.MouseButton:
           
                return True 
            return super().eventFilter(obj, event)
        
        if self.view_id_active_check_box:
            if obj == self.id_active_checkbox and event.type() == Qt.MouseButton:
               
                return True 
            return super().eventFilter(obj, event)
    
    def checkbox_state_changed(self, state):
        """Handle checkbox state changes without affecting frame selection"""
        checked = state == Qt.Checked
        self.savecall_back()
        
    
    def on_frame_selected(self, index):
        """Handle selection of the frame"""
        if index >= 0:
            frame_selection_manager.set_selected_frame(self.selectable_frame)
            print(frame_selection_manager.currently_selected_frame)

            if self.show_auto_upload_checkbox or self.view_id_active_check_box:
                if self.insite_spawn_callback is not None:
                    self.insite_spawn_callback.create_frame(id_frame_idx=self.index, json_path=r"User_Data\Page_manager.json")
                    return index
            else:
                    if self.insite_spawn_callback is not None:
                        self.insite_spawn_callback.start_pull_data_thread(id_frame_idx=self.index)
                        return index
            return index
        else:
            return -1
            
    def add_page_entry(self,page_name=None): 
        """Add a new page entry with animation"""

        parent_widget = self.page_entries_container.parentWidget()


        page_entry_main_frame = AnimatedFrame("rgba(128,128,128,0.2)",parent_widget)

        # Now set up layout 
        page_entry_hboxlayout = QHBoxLayout(page_entry_main_frame)
        page_entry_hboxlayout.setSpacing(8)
        page_entry_hboxlayout.setContentsMargins(5, 8, 5, 8)

        page_idx = len(self.page_widgets) + 1

        page_idx_label = QLabel(f"{page_idx}.", parent=page_entry_main_frame)
        page_entry_hboxlayout.addWidget(page_idx_label)
        page_idx_label.setStyleSheet("background-color:transparent;")

        page_text_label = QLabel("Page:", parent=page_entry_main_frame)
        page_entry_hboxlayout.addWidget(page_text_label)

        page_text_label.setStyleSheet("background-color:transparent;")
        self.page_entry = QLineEdit(parent=page_entry_main_frame)
        self.page_entry.setMinimumHeight(24)
        self.page_entry.setPlaceholderText("Enter page name...")
        self.page_entry.setStyleSheet(
            "background-color:rgba(128,128,128,0.2);"
            "border:2px solid rgba(128,128,128,0.5);"
        )
        if page_name != None:
            self.page_entry.setText(page_name)

        self.page_entry.setReadOnly(not self.edit_mode) 
        self.lineedit_fields.append(self.page_entry)  
        page_entry_hboxlayout.addWidget(self.page_entry)

        remove_btn = AnimatedHoverButton("Remove Page", parent=page_entry_main_frame)
        remove_btn.setFixedSize(QSize(85, 24))
        remove_btn.clicked.connect(lambda: self.remove_page_entry(page_entry_main_frame))
        remove_btn.setVisible(self.edit_mode and not self.is_page_info_hidden)
        page_entry_hboxlayout.addWidget(remove_btn)
        page_entry_hboxlayout.addStretch()

        # Now add to layout 
        self.page_widgets.append(page_entry_main_frame)
        self.page_entries_container.addWidget(page_entry_main_frame)
        page_entry_main_frame.start_animation()
        self.animations.append(page_entry_main_frame.animation)
        page_entry_main_frame.remove_btn = remove_btn
        page_entry_main_frame.lineedit = self.page_entry 

        return page_entry_main_frame


    def remove_page_entry(self, page_widget):
        """Remove a page widget and renumber the remaining ones"""
        if page_widget in self.page_widgets:
            idx = self.page_widgets.index(page_widget)
            
            ui_page_number = idx + 1  #

           
            self.page_entries_container.removeWidget(page_widget)
            self.page_widgets.remove(page_widget)

            
            if hasattr(page_widget, 'lineedit'):
                if page_widget.lineedit in self.lineedit_fields:
                    self.lineedit_fields.remove(page_widget.lineedit)

           
            if hasattr(page_widget, 'animation'):
               
                if page_widget.animation in self.animations:
                    self.animations.remove(page_widget.animation)

            page_widget.deleteLater()

        
            for i, page in enumerate(self.page_widgets):
                labels = page.findChildren(QLabel)
                for label in labels:
                    if label.text().endswith('.'):
                        label.setText(f"{i+1}.")
                        break
                    
            # Use the UI page number (1-based) for JSON operations
            self.remove_page_entry_from_json(page_number=ui_page_number)
            self.remap_page_indices_in_json(deleted_page_number=ui_page_number)

            # Update the layout
            QApplication.processEvents()



    def remap_page_indices_in_json(self, deleted_page_number, json_path=r"User_Data\Page_manager.json"):
        """
        Remap the page indices in the JSON file after deleting a page entry.
        This ensures consistency between UI and JSON.
        JSON uses 1-based indexing for pages (Page.1, Page.2, etc.)
        """
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                page_data = json.load(file)

            id_key = f"Id_information.{self.index}"
            if id_key in page_data:
              
                page_info = page_data[id_key].get("pages_information", {})

                # Create a new page info dictionary with updated indices
                new_page_info = {}

                # Find the highest page number to iterate through
                max_page = 0
                for key in page_info.keys():
                    if key.startswith("Page."):
                        page_num = int(key.split('.')[1])
                        max_page = max(max_page, page_num)

                # Remap the page indices - remember JSON uses 1-based indexing
                for i in range(1, max_page + 1):
                    old_key = f"Page.{i}"

                    # Skip the deleted page
                    if i == deleted_page_number:
                        continue
                    
                    # If this is after the deleted page, remap it
                    if i > deleted_page_number:
                        new_key = f"Page.{i-1}"
                        if old_key in page_info:
                            new_page_info[new_key] = page_info[old_key]
                    else:
                        # If this is before the deleted page, keep the same key
                        if old_key in page_info:
                            new_page_info[old_key] = page_info[old_key]

                # Update the page info in the page data
                page_data[id_key]["pages_information"] = new_page_info

                # Save the updated data
                DevicesJson().save_changes(page_data, filepath=r"User_Data")
                print(f"Remapped page indices after deleting Page.{deleted_page_number}")
            else:
                print(f"{id_key} not found in JSON data.")
        except Exception as e:
            print(f"Error remapping page indices: {e}")
            
    def remove_page_entry_from_json(self, json_path=r"User_Data\Page_manager.json", page_number=1):
        """
        Load the JSON data, delete the specified page (by page_number) from the current Id_information entry,
        and save the changes.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                page_data = json.load(file)
        except Exception as e:
            print("Error reading JSON:", e)
            return

        id_key = f"Id_information.{self.index}"
        if id_key in page_data:
            # Get the page info dictionary.
            page_info = page_data[id_key].get("pages_information", {})
            page_key = f"Page.{page_number}"
            if page_key in page_info:
                del page_info[page_key]
                # Update the page info in the page data
                page_data[id_key]["pages_information"] = page_info
                DevicesJson().save_changes(page_data, filepath=r"User_Data")
                print(f"Deleted {page_key} from {id_key}.")
            else:
                print(f"{page_key} not found in {id_key}.")
        else:
            print(f"{id_key} not found in JSON data.")



    def update_edit_controls_visibility(self):
        """Update visibility of all edit controls based on edit mode"""
        # Check if page info is hidden - if so, don't show edit controls even in edit mode
        should_show_controls = self.edit_mode and not self.is_page_info_hidden
        
        # Update "Add Page" button visibility
        if hasattr(self, 'add_page_btn'):
            self.add_page_btn.setVisible(should_show_controls)
            self.button_container.setVisible(should_show_controls)
        
        # Update "Remove Page" buttons visibility for all page entries
        for page_widget in self.page_widgets:
            if hasattr(page_widget, 'remove_btn'):
                page_widget.remove_btn.setVisible(should_show_controls)
        
        # Update read-only state for all line edits
        self.update_lineedit_readonly_state()
        
    def update_lineedit_readonly_state(self):
        """Update the read-only state of all QLineEdit widgets based on edit mode"""
        for lineedit in self.lineedit_fields:
            lineedit.setReadOnly(not self.edit_mode)
            
            # Optional: Update the appearance based on read-only state
            if self.edit_mode:
                lineedit.setStyleSheet(
                    "background-color:rgba(128,128,128,0.2);"
                    "border:2px solid rgba(128,128,128,0.5);"
                )
            else:
                lineedit.setStyleSheet(
                    "background-color:rgba(128,128,128,0.1);"
                    "border:2px solid rgba(128,128,128,0.3);"
                    "color: white;"
                )
        
    def set_edit_mode(self, enabled):
        """Enable or disable edit mode"""
        self.edit_mode = enabled
        self.update_edit_controls_visibility()


class CheckBoxEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease,
                          QEvent.Type.MouseButtonDblClick, QEvent.Type.KeyPress):
            return True  # Block the event
        return super().eventFilter(obj, event)


class FolderCreationProcessor(QObject):
    """Worker class to process folder creation and LD configuration in a separate thread"""
    progress_updated = Signal(int, str, int)  # current_id, message, progress
    task_completed = Signal()
    
    def __init__(self, start_id, end_id, config_props, all_ld_folder_path):
        super().__init__()
        self.start_id = start_id
        self.end_id = end_id
        self.config_props = config_props
        self.all_ld_folder_path = all_ld_folder_path
        
    def process(self):
        """Process folder creation and LD configuration tasks"""
        total_ids = self.end_id - self.start_id
        processed = 0
        
        for current_id in range(self.start_id, self.end_id):
            # Update progress
            message = f"Creating folders and configuring LD for ID {current_id}"
            self.progress_updated.emit(current_id, message, processed)
            
            # Create folders and configure LD
            create_folder_and_config_obj = create_folder_and_config(
                current_id_index=current_id,
                create_folder_config_ld_prop=self.config_props,
                all_ld_folder_path=self.all_ld_folder_path
            )
            create_folder_and_config_obj.main_create_folder_and_ld_config()
            
            # Increment processed count and emit progress
            processed += 1
            progress = processed
            self.progress_updated.emit(current_id, "Completed", progress)
            
        # Signal completion
        self.task_completed.emit()



    
class PageRow(QWidget):
    def __init__(self, show_Edit_btn: bool = True,spawn_config_window_callback=None,view_id_active_check_box: bool=False,is_page_info_hidden:bool = False,show_auto_upload_checkbox:bool = False,select_callback=None, **kwargs):
        super().__init__()
        self.id_frames = []
        self.edit_mode = False
        self.show_edit_btn = show_Edit_btn
        self.view_id_active_check_box =view_id_active_check_box
        self.show_auto_upload_checkbox = show_auto_upload_checkbox
        self.is_page_info_hidden = is_page_info_hidden
        self.spawn_config_window_callback = spawn_config_window_callback
        self.next_widget_index = 1  
        self.select_callback = select_callback
        self.init_ui()
        self.load_data_or_create()
        self.load_data()
    def init_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        #main_layout.setSpacing(10)
        


        
        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setStyleSheet("QScrollArea#scroll_area{ background-color:rgba(128,128,128,0.1); border-radius:8px;}")
        self.scroll_area.viewport().setStyleSheet("background-color:rgba(102,102,102,0.001);")
        self.scroll_area.setWidgetResizable(True)
        
        # Create a container widget 
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        
        
        self.next_widget_index = len(self.id_frames) + 1
            
        self.scroll_layout.addStretch()  
        
        
        self.scroll_area.setWidget(self.scroll_content)
        
        # Add the scroll area 
        main_layout.addWidget(self.scroll_area)


        #add buttons
        if self.show_edit_btn:

            button_frame = QFrame()
            button_frame.setStyleSheet("""QFrame{border:1px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    background-color: rgba(128,128,128,0.2);}
                                           """)
            # Add top controls layout
            top_controls_layout = QHBoxLayout(button_frame)

            # Add edit mode toggle button at the top
            self.edit_button = AnimatedHoverButton("Edit Mode: Off")
            self.edit_button.setFixedSize(QSize(120, 30))
            self.edit_button.clicked.connect(self.toggle_edit_mode)
            top_controls_layout.addWidget(self.edit_button)

            
            top_controls_layout.addStretch()

        
            self.add_widget_button = AnimatedHoverButton("Add ID")
            self.add_widget_button.setFixedSize(QSize(120, 30))
            self.add_widget_button.clicked.connect(self.add_new_id)
            top_controls_layout.addWidget(self.add_widget_button)


            self.remove_widget_button = AnimatedHoverButton("Remove ID")
            self.remove_widget_button.setFixedSize(QSize(120, 30))
            self.remove_widget_button.clicked.connect(self.remove_selected_widget)
            top_controls_layout.addWidget(self.remove_widget_button)

           
            main_layout.addWidget(button_frame)
        
    def toggle_edit_mode(self):
        """Toggle edit mode for all page widgets"""
        self.edit_mode = not self.edit_mode
        
        # Update button text and style
        self.edit_button.setText(f"Edit Mode: {'On' if self.edit_mode else 'Off'}")
        
        if self.edit_mode == False:
            self.Apply_setting_to_json()

        if self.edit_mode:
            self.edit_button.setStyleSheet("font-weight: bold;")
        else:
            self.edit_button.setStyleSheet("")
        
        # Update all page widgets
        for widget in self.id_frames:
            widget.set_edit_mode(self.edit_mode)
        
        # Process events to ensure UI updates
        QApplication.processEvents()
    
    def add_new_id(self,main_frame_border_color = None):
        """Add a new PageEntryWidget to the scroll area"""
        # Create animation frame to hold the widget 
        container_frame = QFrame(self.scroll_content)
        container_layout = QVBoxLayout(container_frame)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        
        
        widget = IdFrame(
            index=self.next_widget_index,
            edit_mode=self.edit_mode,
            is_page_info_hidden=self.is_page_info_hidden,
            show_auto_upload_checkbox=self.show_auto_upload_checkbox,
            view_id_active_check_box=self.view_id_active_check_box,
            main_frame_border_color = main_frame_border_color,
            insite_spawn_callback=self.spawn_config_window_callback,
            save_callback=self.Apply_setting_to_json
        )
        
        
        self.id_frames.append(widget)
        self.next_widget_index += 1
        
      
        container_layout.addWidget(widget)
        
        
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, container_frame)
        
       
        QApplication.processEvents()
        
        if self.show_edit_btn:
            QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()
            ))
        
        
        return widget
    
    def remove_selected_widget(self):
        """Remove the currently selected PageEntryWidget"""

        if frame_selection_manager.currently_selected_frame is None:
            QMessageBox.information(self, "No Selection", "Please select a widget to remove first.")
            return

        # Store the index before removing the widget
        selected_index = None
        if hasattr(frame_selection_manager.currently_selected_frame, 'index'):
            selected_index = frame_selection_manager.currently_selected_frame.index

        selected_widget = None
        for widget in self.id_frames:
            if hasattr(widget, 'selectable_frame') and widget.selectable_frame == frame_selection_manager.currently_selected_frame:
                selected_widget = widget
                break
            
        if not selected_widget:
            QMessageBox.information(self, "Selection Error", "Could not determine which widget to remove.")
            return

        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal", 
                                     f"Remove widget #{selected_widget.index}?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.No:
            return

        # Store the index before removing if we couldn't get it earlier
        if selected_index is None:
            selected_index = selected_widget.index

        self.id_frames.remove(selected_widget)
        self.del_id_entry_from_json(selected_index)  # Pass the index explicitly
        self.remap_json_indices(deleted_index=selected_index)  # Use the stored index

        container = None
        if hasattr(selected_widget, 'container_frame'):
            container = selected_widget.container_frame
            self.scroll_layout.removeWidget(container)
            container.deleteLater()
        else:
            self.scroll_layout.removeWidget(selected_widget)
            selected_widget.deleteLater()

        # Clear reference after deletion
        frame_selection_manager.currently_selected_frame = None

        self.renumber_widgets()

        # Update layout
        QApplication.processEvents()
    

    def renumber_widgets(self):
        """Renumber all PageEntryWidgets sequentially"""
        for i, widget in enumerate(self.id_frames):
            new_index = i + 1
            widget.index = new_index
            
         
            if hasattr(widget, 'id_frame'):
                
                labels = widget.findChildren(QLabel)
                for label in labels:
                    if label.text().endswith('.') and '.' in label.text():
              
                        label.setText(f"{new_index}.")
                        break
        
 
        self.next_widget_index = len(self.id_frames) + 1

    def del_id_entry_from_json(self, deleted_index=None, json_path=r"User_Data\Page_manager.json"):
        """
        Delete the entire Id_information entry for this frame from the JSON file.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                page_data = json.load(file)
        except Exception as e:
            print("Error reading JSON:", e)
            return
    
        # Use the passed index, or try to get it from the currently selected frame
        index_to_delete = deleted_index
        if index_to_delete is None and frame_selection_manager.currently_selected_frame:
            try:
                index_to_delete = frame_selection_manager.currently_selected_frame.index
            except (AttributeError, RuntimeError):
                print("Could not get index from currently selected frame")
                return
    
        if index_to_delete is None:
            print("No index available to delete")
            return
    
        id_key = f"Id_information.{index_to_delete}"
        if id_key in page_data:
            del page_data[id_key]
            DevicesJson().save_changes(page_data, filepath=r"User_Data")
            print(f"Deleted {id_key} from JSON data.")
        else:
            print(f"{id_key} not found in JSON data.")



    def remap_json_indices(self, deleted_index, json_path=r"User_Data\Page_manager.json"):
        """Remap JSON indices after deleting an ID frame to keep them sequential."""
        try:
            with open(json_path, "r", encoding="utf-8") as file:
                page_data = json.load(file)

            # Find all existing ID keys
            id_keys = [key for key in page_data.keys() if key.startswith("Id_information.")]
            id_keys.sort(key=lambda x: int(x.split('.')[-1]))

            new_page_data = {}
            new_index = 1
            for key in id_keys:
                current_index = int(key.split('.')[-1])
                if current_index == deleted_index:
                    continue  
                elif current_index > deleted_index:
                    new_key = f"Id_information.{new_index}"
                    new_page_data[new_key] = page_data[key]
                    new_index += 1
                else:
                    new_key = f"Id_information.{new_index}"
                    new_page_data[new_key] = page_data[key]
                    new_index += 1

            DevicesJson().save_changes(new_page_data, filepath=r"User_Data")
        except FileNotFoundError:
            print(f"JSON file not found at {json_path}")
        except Exception as e:
            print(f"Error remapping JSON indices: {e}")


    def load_data_or_create(self):
        
        file_path = r"User_Data"
        data = DevicesJson().load_or_create_json(filepath=file_path)



    def Apply_setting_to_json(self, json_path=r"User_Data\Page_manager.json"):
        try:
            # Load the current JSON data
            with open(json_path, "r", encoding="utf-8") as file:
                page_data = json.load(file)
    
            # Iterate over each IdFrame in the UI
            for id_frame in self.id_frames:
                id_frame_idx = id_frame.index 
                
                # Create or update the JSON entry for this ID
                if f"Id_information.{id_frame_idx}" not in page_data:
                    device_json_instance = DevicesJson()
                    create_id_frame = device_json_instance.create_id_frame(
                        idx=id_frame_idx,
                        id_name=id_frame.id_entry.text(),  
                        Package_name=id_frame.package_name_entry.text(),
                        ld_name=id_frame.ld_name_entry.text()
                    )
                    page_data.update(create_id_frame)
                else:
                    page_data[f"Id_information.{id_frame_idx}"]["id_name"] = id_frame.id_entry.text()
                    page_data[f"Id_information.{id_frame_idx}"]["package_name"] = id_frame.package_name_entry.text()
                    page_data[f"Id_information.{id_frame_idx}"]["Ld_name"] = id_frame.ld_name_entry.text()
                    
                    # Handle "Upload" checkbox
                    if self.show_auto_upload_checkbox:
                        page_data[f"Id_information.{id_frame_idx}"]["Upload"] = (
                            id_frame.upload_checkbox.isChecked() if hasattr(id_frame, 'upload_checkbox') else False
                        )
                    elif "Upload" not in page_data[f"Id_information.{id_frame_idx}"]:
                        page_data[f"Id_information.{id_frame_idx}"]["Upload"] = False
        
                    # Handle "id_active_enable" checkbox
                    if self.view_id_active_check_box:
                        page_data[f"Id_information.{id_frame_idx}"]["id_active_enable"] = (
                            id_frame.id_active_checkbox.isChecked() if hasattr(id_frame, 'id_active_checkbox') else False
                        )
                    elif "id_active_enable" not in page_data[f"Id_information.{id_frame_idx}"]:
                        page_data[f"Id_information.{id_frame_idx}"]["id_active_enable"] = False
    
                # Handle page information
                if f"Id_information.{id_frame_idx}" in page_data:
                   
                    if "pages_information" not in page_data[f"Id_information.{id_frame_idx}"]:
                        page_data[f"Id_information.{id_frame_idx}"]["pages_information"] = {}
                    
                    page_info_dic = page_data[f"Id_information.{id_frame_idx}"]["pages_information"]
                    
                    # Process each page widget
                    for page_idx, page_widget in enumerate(id_frame.page_widgets):
                        page_num = page_idx + 1
                        page_key = f"Page.{page_num}"
                        
                        # Access the line edit directly from the page widget
                        if hasattr(page_widget, 'lineedit'):
                            page_name = page_widget.lineedit.text()
                            
                            if page_key not in page_info_dic:
                                page_create_instance = DevicesJson().add_page_data(idx=page_num, page_name=page_name)
                                page_info_dic.update(page_create_instance)
                            else:
                                page_info_dic[page_key]["Page_Name"] = page_name
                    
                    # Update the JSON with the modified page information
                    page_data[f"Id_information.{id_frame_idx}"]["pages_information"] = page_info_dic
            
            # Save changes to the JSON file
            DevicesJson().save_changes(page_data, filepath=r"User_Data")
            print("JSON data updated successfully")
            
        except Exception as e:
            print(f"Error updating JSON data: {e}")



    def check_setup(self, data):

        """Check if setup is available in the data."""

        # Check ID_info insights
        id_insights = data.get("ID_info", {}).get("Insights", {})
        if id_insights.get("is_setup_available") == True:
            return True

        # Check pages_information (note the correct key name)
        pages = data.get("pages_information", {})  
        for page_key, page_data in pages.items():
            insights = page_data.get("Insights", {})
            if insights.get("is_setup_available") == True:
                return True

        return False

    def load_data(self, json_path=r"User_Data\Page_manager.json"):
        # Load data from the JSON file into the UI.
        with open(json_path, "r", encoding="utf-8") as file:
            page_data = json.load(file)

            for key, value in page_data.items():
                if key.startswith("Id_information."):
                    id_name = value["id_name"]
                    Package_name = value["package_name"]
                    Ld_name = value["Ld_name"]
                    upload_selected = value["Upload"]
                    id_active_checkbox = value["id_active_enable"]
                    is_setup = self.check_setup(value)

                    # Reset border_color for each ID based on its setup status
                    border_color = "0,156,99,1" if is_setup else ""

                    ID_frame = self.add_new_id(main_frame_border_color=border_color)
                    ID_frame.id_entry.setText(id_name)
                    ID_frame.package_name_entry.setText(Package_name)
                    ID_frame.ld_name_entry.setText(Ld_name)

                    if self.show_auto_upload_checkbox and hasattr(ID_frame, 'upload_checkbox'):
                        ID_frame.upload_checkbox.setChecked(upload_selected)
                    if self.view_id_active_check_box and hasattr(ID_frame, 'id_active_checkbox'):
                        ID_frame.id_active_checkbox.setChecked(id_active_checkbox)

                    page_info_dic = value.get("pages_information", {})

                    for p_key, p_value in page_info_dic.items():
                        page_name = p_value["Page_Name"]
                        ID_frame.add_page_entry(page_name=page_name)

    


class ImageViewer(QWidget):
    def __init__(self, parent=None, image_paths=None):
        super().__init__(parent)
        if image_paths is None:
            image_paths = []
        
        self.image_paths = image_paths
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        if self.image_paths:
            for img_path in self.image_paths:
                if os.path.exists(img_path):
                    # Create thumbnail container with hover effect
                    thumbnail_container = ImageThumbnail(img_path)
                    thumbnail_container.clicked.connect(self.open_image_popup)
                    layout.addWidget(thumbnail_container)
                else:
                    error_label = QLabel(f"Image not found: {os.path.basename(img_path)}")
                    layout.addWidget(error_label)
        else:
            no_image_label = QLabel("No Image available to show")
            no_image_label.setFont(QFont("Arial", 14, QFont.Bold))
            layout.addWidget(no_image_label)
        # Add stretch to prevent thumbnails from expanding too much
        layout.addStretch()
    
    def open_image_popup(self, img_path):
        """Open the image in a new window at appropriate size"""
        self.image_popup = ImagePopup(img_path)
        self.image_popup.show()


class ImageThumbnail(QFrame):
    """A clickable thumbnail with hover highlight effect but no scaling"""
    clicked = Signal(str)  # Signal to emit the image path when clicked
    
    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path
        self.hovered = False
        
        # Set frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setAutoFillBackground(True)
        self.setCursor(Qt.PointingHandCursor)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Load image at original size
        self.pixmap = QPixmap(img_path)
        
        # Create thumbnail for display
        # Small images stay at original size, larger ones are scaled down
        max_thumb_size = 150

        if self.pixmap.width() > max_thumb_size or self.pixmap.height() > max_thumb_size:
            thumbnail = self.pixmap.scaled(max_thumb_size, max_thumb_size, 
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            thumbnail = self.pixmap  # Use original size for small images
        
        # Create image label
        self.image_label = QLabel()
        self.image_label.setPixmap(thumbnail)
        self.image_label.setAlignment(Qt.AlignCenter)
        
       
        # Add widgets to layout
        layout.addWidget(self.image_label)
    
        
        # Set normal appearance
        self.update_style()
    
    def update_style(self):
        """Update the frame style based on hover state"""
        if self.hovered:
            # Highlighted style (blue border and background)
            self.setStyleSheet("""
                QFrame {
                    border: 2px solid #3399FF;
                    border-radius: 5px;
                    background-color: rgba(230, 240, 255, 150);
                }
            """)
        else:
            # Normal style (light gray border)
            self.setStyleSheet("""
                QFrame {
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    background-color: transparent;
                }
            """)
    
    def enterEvent(self, event):
        """Handle mouse enter event for hover effect"""
        self.hovered = True
        self.update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event to remove hover effect"""
        self.hovered = False
        self.update_style()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.img_path)
        super().mousePressEvent(event)


class ImagePopup(QWidget):
    """A popup window to display an image without scaling small images"""
    
    def __init__(self, img_path):
        super().__init__(None, Qt.Window)
        self.img_path = img_path
        self.initUI()
    
    def initUI(self):
        # Set window title
        self.setWindowTitle(os.path.basename(self.img_path))
        
        # Load the image
        self.pixmap = QPixmap(self.img_path)
        img_width = self.pixmap.width()
        img_height = self.pixmap.height()
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scroll")
        scroll_area.setStyleSheet("QScrollArea#scroll{ background-color:rgba(128,128,128,0.1); border-radius:8px;}")
        scroll_area.viewport().setStyleSheet("background-color:rgba(102,102,102,0.001);")  # Fixed: use scroll_area instead of self.scroll_area
        scroll_area.setWidgetResizable(True)
        
        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        # Image label
        image_label = QLabel()
        image_label.setPixmap(self.pixmap)  # Use original size
        image_label.setAlignment(Qt.AlignCenter)
        
        # Info and button area
        info_label = QLabel(f"Dimensions: {img_width} × {img_height} pixels")
        info_label.setAlignment(Qt.AlignCenter)
        
        close_btn = AnimatedHoverButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setMaximumWidth(100)
        
        # Add widgets to layout
        content_layout.addWidget(image_label)
        content_layout.addWidget(info_label)
        content_layout.addWidget(close_btn, 0, Qt.AlignCenter)
        
        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)
        
        
        self.resize_window_to_content()
        self.center_on_screen()
    
    def resize_window_to_content(self):
        """Size the window based on the image with reasonable constraints"""
        # Get screen size
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Calculate margins for window decoration
        margin_w = 50
        margin_h = 100
        
        # Calculate window size
        width = min(self.pixmap.width() + margin_w, screen.width() * 0.9)
        height = min(self.pixmap.height() + margin_h, screen.height() * 0.9)
        
        # Set minimum window size
        min_width = 400
        min_height = 300
        width = max(width, min_width)
        height = max(height, min_height)
        
        self.resize(int(width), int(height))
    
    def center_on_screen(self):
        """Center the window on the screen"""
        frame = self.frameGeometry()
        center = QApplication.primaryScreen().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())
    
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)

class ExpandableFrame(QWidget):
    def __init__(self, parent=None, title="Expandable Section"):
        super().__init__(parent)
        self.expanded = False
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Toggle button
        self.toggle_button = AnimatedHoverButton(f"► {title}")
        self.toggle_button.setObjectName("expand_button")
        self.toggle_button.setFixedSize(QSize(150,25))
        self.toggle_button.setStyleSheet("""QPushButton#expand_button:{text-align: left;}  
                                            QPushButton#expand_button:hover{backbround-color:blue;}
                                            QPushButton#expand_button:{background-color:light blue};
                                            QPushButton#expand_button:pressed{background:blue;}""")
        self.toggle_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_button.clicked.connect(self.toggle)
        
        # Content frame
        self.content_frame = QFrame()
        self.content_layout = QVBoxLayout(self.content_frame)
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.toggle_button)
        self.main_layout.addWidget(self.content_frame)  
        

        self.content_frame.setVisible(False) 

    
    def toggle(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.toggle_button.setText(f"▼ {self.toggle_button.text()[2:]}")
            self.content_frame.setVisible(True)  
        else:
            self.toggle_button.setText(f"► {self.toggle_button.text()[2:]}")
            self.content_frame.setVisible(False)  
    
class ProfileInsite(QFrame):
    def __init__(self, parent=None, profile_name="None", followers=0, views=0, engagement=0, images=None, is_setup=False):
        super().__init__(parent)
        
        self.profile_name = profile_name
        self.followers = followers
        self.views = views
        self.engagement = engagement
        self.is_setup = "Yes" if is_setup else "No"
        self.images = images if images is not None else []
        self.setObjectName("profile_insite_frame")
        self.setStyleSheet("ProfileInsite#profile_insite_frame{border:2px solid rgba(128,128,128,1);border-radius:8px;background:rgba(128,128,128,0.1)}")
        # Set frame style
        """         self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(2) """
        
        self._create_widgets()
    
    def _create_widgets(self):
        main_layout = QVBoxLayout(self)
        
        # Header frames
        id_insite_label_frame = QFrame()
        id_insite_layout = QHBoxLayout(id_insite_label_frame)
        id_insite_layout.setContentsMargins(5, 5, 5, 0)
        
        name_label_frame = QFrame()
        name_layout = QHBoxLayout(name_label_frame)
        name_layout.setContentsMargins(10, 10, 10, 10)
        
        # Header labels
        insights_label = QLabel("Insights")
        insights_label.setFont(QFont("Arial", 14, QFont.Bold))
        id_insite_layout.addWidget(insights_label, 0, Qt.AlignLeft)
        
        profile_name_label = QLabel(self.profile_name)
        profile_name_label.setStyleSheet("background-color:rgba(128,128,128,0.1); padding:10px;border-radius:8px")
        profile_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        name_layout.addWidget(profile_name_label, 0, Qt.AlignLeft)
        
        # Insights grid frame
        insite_frame = QFrame()
        insite_frame.setObjectName("insite_frame")
        #insite_frame.setStyleSheet()
        insite_layout = QGridLayout(insite_frame)
        
        # Followers frame
        followers_frame = QFrame()
        followers_frame.setObjectName("followers_frame")
        followers_frame.setStyleSheet("""
                                    QFrame#followers_frame{background-color:rgba(128,128,128,0.2);border:2px solid rgba(128,128,128,1);border-radius:8px}""")
        followers_frame.setFrameShape(QFrame.Box)
        followers_layout = QHBoxLayout(followers_frame)
        followers_label = QLabel("Followers:")
        followers_label.setStyleSheet("border:none;background-color:none")
        followers_layout.addWidget(followers_label)
        followers_count = QLabel(str(self.followers))
        followers_count.setFont(QFont("Arial", 30, QFont.Bold))
        followers_count.setStyleSheet("border:none;background-color:none")
        followers_layout.addWidget(followers_count)
        insite_layout.addWidget(followers_frame, 0, 0)
        
        # Views frame
        views_frame = QFrame()
        views_frame.setFrameShape(QFrame.Box)
        views_frame.setObjectName("views_frame")
        views_frame.setStyleSheet("""
                                    QFrame#views_frame{background-color:rgba(128,128,128,0.2);border:2px solid rgba(128,128,128,1);border-radius:8px}""")
        views_layout = QHBoxLayout(views_frame)
        views_label = QLabel("Views:")
        views_label.setStyleSheet("border:none;background-color:none")
        views_layout.addWidget(views_label)
        views_count = QLabel(str(self.views))
        views_count.setStyleSheet("border:none;background-color:none")
        views_count.setFont(QFont("Arial", 30, QFont.Bold))
        views_layout.addWidget(views_count)
        insite_layout.addWidget(views_frame, 0, 1)
        
        # Engagement frame
        engagement_frame = QFrame()
        engagement_frame.setObjectName("engagement_frame")
        engagement_frame.setStyleSheet("""
                                    QFrame#engagement_frame{background-color:rgba(128,128,128,0.2);border:2px solid rgba(128,128,128,1);border-radius:8px}""")
        engagement_frame.setFrameShape(QFrame.Box)
        engagement_layout = QHBoxLayout(engagement_frame)
        engagement_label = QLabel("Engagement:")
        engagement_label.setStyleSheet("border:none;background-color:none")
        engagement_layout.addWidget(engagement_label)
        engagement_count = QLabel(str(self.engagement))
        engagement_count.setStyleSheet("border:none;background-color:none")
        engagement_count.setFont(QFont("Arial", 30, QFont.Bold))
        engagement_layout.addWidget(engagement_count)
        insite_layout.addWidget(engagement_frame, 0, 2)
        
        # Setup frame
        setup_frame = QFrame()
        setup_frame.setObjectName("setup_frame")
        setup_frame.setStyleSheet("""
                                    QFrame#setup_frame{background-color:rgba(128,128,128,0.2);border:2px solid rgba(128,128,128,1);border-radius:8px}""")
        setup_frame.setFrameShape(QFrame.Box)
        setup_layout = QHBoxLayout(setup_frame)
        setup_label = QLabel("Setup Available:")
        setup_label.setStyleSheet("border:none;background-color:none")
        setup_layout.addWidget(setup_label)
        setup_status = QLabel(self.is_setup)
        setup_status.setStyleSheet("border:none;background-color:none")
        setup_status.setFont(QFont("Arial", 30, QFont.Bold))
        setup_layout.addWidget(setup_status)
        insite_layout.addWidget(setup_frame, 0, 3)
        
        # Images section
        images_label = QLabel("Images")
        images_label.setFont(QFont("Arial", 15, QFont.Bold))
        
        # Expandable image frame
        expandable_frame = ExpandableFrame(title="Click to view image")
        image_viewer = ImageViewer(parent=expandable_frame.content_frame, image_paths=self.images)
        expandable_frame.content_layout.addWidget(image_viewer)
        
        # Add all widgets to main layout
        main_layout.addWidget(id_insite_label_frame)
        main_layout.addWidget(name_label_frame)
        main_layout.addWidget(insite_frame)
        main_layout.addWidget(images_label)
        main_layout.addWidget(expandable_frame)


class DataLoaderThread(QThread):
    data_loaded = Signal(list)
    
    def __init__(self, json_path, id_frame_idx):
        super().__init__()
        self.json_path = json_path
        self.id_frame_idx = id_frame_idx
    
    def run(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as file:
                page_data = json.load(file)
        except Exception as e:
            print("Error reading JSON:", e)
            return
        
        processed_data = []
        key_id = f"Id_information.{self.id_frame_idx}"
        
        if key_id in page_data:
            id_information = page_data[key_id]
            # Process ID information
            id_name = id_information.get("id_name", "Unknown") + " " + "(ID)"
            id_info = id_information.get("ID_info", {})
            id_insite_info = id_info.get("Insights", {})
            id_followers = id_insite_info.get("Followers", 0)
            id_views = id_insite_info.get("Views", 0)
            id_engagement = id_insite_info.get("Engagement", 0)
            id_is_setup = id_insite_info.get("is_setup_available", False)
            id_screenshot_img = id_insite_info.get("Screenshot Images", [])
            
            processed_data.append({
                "profile_name": id_name,
                "followers": id_followers,
                "views": id_views,
                "engagement": id_engagement,
                "images": id_screenshot_img,
                "is_setup": id_is_setup
            })
            
            # Process page insights
            page_info_dic = id_information.get("pages_information", {})
            for key, value in page_info_dic.items():
                if key.startswith("Page."):
                    page_name = value.get("Page_Name", "Unknown")
                    page_insite = value.get("Insights", {})
                    page_followers = page_insite.get("Followers", 0)
                    page_views = page_insite.get("Views", 0)
                    page_engagement = page_insite.get("Engagement", 0)
                    page_is_setup = page_insite.get("is_setup_available", False)
                    page_screenshot_img = page_insite.get("Screenshot Images", [])
                    
                    processed_data.append({
                        "profile_name": page_name,
                        "followers": page_followers,
                        "views": page_views,
                        "engagement": page_engagement,
                        "images": page_screenshot_img,
                        "is_setup": page_is_setup
                    })
        
        self.data_loaded.emit(processed_data)


class allPagesInsight(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        main_layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_area.setStyleSheet("QScrollArea#scroll_area{ background-color:rgba(128,128,128,0.1); border-radius:8px;}")
        self.scroll_area.viewport().setStyleSheet("background-color:rgba(102,102,102,0.001);")
        self.scroll_area.setWidgetResizable(True)
        #self.scroll_area.setFrameShape(QFrame.Box)
        #self.scroll_area.setLineWidth(3)
        
      
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        

        self.placeholder_label = QLabel("Please select a frame to view options")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.placeholder_label)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
    
    def start_pull_data_thread(self, id_frame_idx=1):

        self.data_thread = DataLoaderThread(r"User_Data/Page_manager.json", id_frame_idx)
        self.data_thread.data_loaded.connect(self.update_ui_with_data)
        self.data_thread.start()
    
    @Slot(list)
    def update_ui_with_data(self, processed_data):
        # Clear existing widgets
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Create new profile insight widgets
        for data in processed_data:
            insight = ProfileInsite(
                parent=self.scroll_content,
                profile_name=data["profile_name"],
                followers=data["followers"],
                views=data["views"],
                engagement=data["engagement"],
                images=data["images"],
                is_setup=data["is_setup"]
            )
            self.scroll_layout.addWidget(insight)
            
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
                color: #eeeeee;                      /* light text */
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




if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    window = PageRow()
    window.show()
    sys.exit(app.exec())