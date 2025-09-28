import sys
import os
import re
from typing import List, Dict, Callable
import subprocess
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QFrame, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QLineEdit, QCheckBox, 
                              QSpinBox, QComboBox, QScrollArea, QGridLayout, QFileDialog,
                              QMessageBox, QDialog,QTableView,QHeaderView,QAbstractSpinBox,QAbstractItemView,QAbstractItemView,QGroupBox,QSizePolicy,QMenu,QTextEdit)
from PySide6.QtCore import Qt, QSize, Signal,QMargins,QPropertyAnimation,QEasingCurve,QSequentialAnimationGroup,Property,QAbstractAnimation
from PySide6.QtGui import QFont,QStandardItemModel,QStandardItem,QColor,QCursor,QIcon,QPalette

import GPUtil
from geni_ui_src.DevicesJsonReader import DevicesJson

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from geni.ldController.Ldcontroller_adb.LdAdb import LdAdbController
import queue


class DevicesInfoLdTable(QFrame):
    def __init__(self, parent=None, ActivityControl_refrance=None,MainWindow_refrance = None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)
        self.total_ld_selected = 0
        title_label = QLabel("Devices Info")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(title_label)
        self.ActivityControl_refrance = ActivityControl_refrance
        
        self.main_window_refrance = MainWindow_refrance
        self.total_ld_selected_list = []

        # Create table view for device info (has built-in scrolling)
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        
        # Enable multiple row selection
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection) 
        
        # Make table header visible and enable sorting
        self.table_view.horizontalHeader().setVisible(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.setMinimumWidth(400)
        
        # Create model for table data
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["No", "LD Name", "LD Serial"])
        self.table_view.setModel(self.table_model)
        
        # Make headers fill the width of the table
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        main_layout.addWidget(self.table_view)
        
        self.table_view.setStyleSheet("""
                                        QTableView::item:selected:active {
                                        background-color:rgba(27,86,253,0.5);  /* Active selection color */
                                        color: white;
                                        border-radius:8px;

                                                }""")

        for i in range(3):
            self.table_view.setColumnWidth(i, 100)
        
        # Enable context menu
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # Initialize with sample data
        self.update_device_info_frame(ld_list=[["0", "LDPlayer0", "SN001"], 
                                              ["1", "LDPlayer1", "SN002"],
                                              ["2", "LDPlayer2", "SN003"]])
        
    def update_device_info_frame(self, ld_list=None, refresh=False):
        """Update the device info table with the provided ld_list."""
        if refresh or ld_list is not None:
            # Clear existing table data
            self.table_model.removeRows(0, self.table_model.rowCount())
            
            # Populate with new data
            if ld_list:
                self.device_info_table(ld_list)
                
    def device_info_table(self, ld_list):
        """Populate the table model with device information safely."""
        if not ld_list:
            return
            
        try:
            for ld_data in ld_list:
                if not ld_data or len(ld_data) < 2:  # Skip invalid data
                    continue
                    
                row_items = []
                # Ensure we use exactly 3 items (No, Name, Serial)
                for i in range(3):
                    try:
                        if i < len(ld_data) and ld_data[i] is not None:
                            # Clean the text to remove problematic characters
                            text = str(ld_data[i]).strip()
                            text = ''.join(char for char in text if char.isprintable() or char.isspace())
                            item = QStandardItem(text)
                        else:
                            item = QStandardItem("") 
                        
                        item.setTextAlignment(Qt.AlignCenter)
                        row_items.append(item)
                    except Exception as item_error:
                        print(f"Error creating table item: {item_error}")
                        item = QStandardItem("Error")
                        item.setTextAlignment(Qt.AlignCenter)
                        row_items.append(item)
                        
                if row_items:  # Only add if we have valid items
                    self.table_model.appendRow(row_items)
                    
        except Exception as e:
            print(f"Error in device_info_table: {e}")
            QMessageBox.warning(self, "Warning", f"Error updating device table: {str(e)}")

    
    def show_context_menu(self, position):
        """Show a context menu when right-clicking on a table row."""
        # Get selected indices
        self.selected_indices = self.table_view.selectionModel().selectedRows()
        self.total_ld_selected = len(self.selected_indices)
        
        # Check if there are any selected rows
        if not self.selected_indices:
            QMessageBox.warning(self, "Warning", "No LDs selected. Please select at least one LD.")
            return
            
        # Create the context menu with improved styling
        context_menu = QMenu(self)
        palette = context_menu.palette()
        bg_color = palette.color(QPalette.Window)
        # Apply custom styling to make the menu more visible
        context_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {bg_color.name()};
                border: 1px solid #999999;
                padding: 5px;
                border-radius:8px;
            }}
            QMenu::item {{
                background-color: transparent;
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
        
        fetch_icon = QIcon.fromTheme("view-refresh", QIcon(":/icons/refresh.png"))
        fetch_action = context_menu.addAction(fetch_icon, "Fetch ID info for selected LD")
        
        context_menu.addSeparator()
        info_action = context_menu.addAction(f"{self.total_ld_selected} item(s) selected")
        info_action.setEnabled(False)  
        
        # Connect the action to a function
        fetch_action.triggered.connect(self.fetch_info_dilogbox)
        
        # Show the context menu at the cursor position
        context_menu.exec(self.table_view.viewport().mapToGlobal(position))

    def fetch_info_dilogbox(self):
        """Show a dialog for fetching information about selected LDs."""
        # Get the selected LDs list first and store it
        self.selected_ld_list = self.get_selected_lds()
        
        # If no LDs are selected, show warning and return
        if not self.selected_ld_list:
            QMessageBox.warning(self, "Warning", "No LDs selected. Please select at least one LD.")
            return
        
        # Set the selected LDs to ActivityControl reference immediately
        if self.ActivityControl_refrance:
            self.ActivityControl_refrance.selected_ld_list = self.selected_ld_list

        self.fetch_info_dilog = QDialog(parent=self)
        self.fetch_info_dilog.setWindowTitle("Fetch Profiles Information")
        self.fetch_info_dilog.setFixedSize(450, 350)

        # Create main layout for the dialog
        dialog_layout = QVBoxLayout(self.fetch_info_dilog)

        # Create a group box for organizing content
        fetch_info_main_groupbox = QGroupBox(title="Fetch Info")
        fetch_info_main_groupbox.setObjectName("fetch_info")
        fetch_info_main_groupbox.setStyleSheet("""QGroupBox#fetch_info{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#fetch_info::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        fetch_info_main_layout = QVBoxLayout(fetch_info_main_groupbox)

        # Package name input
        enter_package_name_frame = QFrame()
        enter_package_name_layout = QHBoxLayout(enter_package_name_frame)
        label = QLabel(text="Enter Package Name:")
        enter_package_name_layout.addWidget(label)

        self.package_entry = QLineEdit()
        self.package_entry.setFixedWidth(200)
        self.package_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                                      /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 5px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;           /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:5px;
                background-color:rgba(128,128,128,.2);

            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:5px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)

        self.package_entry.setPlaceholderText("com.facebook.katana")
        self.package_entry.setText("com.facebook.katana")
        self.package_entry.textChanged.connect(self.update_package_name)
        enter_package_name_layout.addWidget(self.package_entry)
        enter_package_name_layout.addStretch(0)

        fetch_info_main_layout.addWidget(enter_package_name_frame)

        # Total selected LDs
        total_selected_frame = QFrame()
        total_selected_layout = QHBoxLayout(total_selected_frame)  

        total_ld_selected_num_label = QLabel("Total Selected LD:")
        total_selected_layout.addWidget(total_ld_selected_num_label)

        self.selected_ld_label = QLabel()
        self.selected_ld_label.setText(str(len(self.selected_ld_list)))
        self.selected_ld_label.setStyleSheet(
            "background-color:rgba(128,128,128,0.5);"
            "padding: 3px 8px;"
            "border-radius: 5px;"
        )
        total_selected_layout.addWidget(self.selected_ld_label)
        total_selected_layout.addStretch(1)

        fetch_info_main_layout.addWidget(total_selected_frame)

        self.sleep_checkbox = QCheckBox("Auto Sleep After Task Completion")
        fetch_info_main_layout.addWidget(self.sleep_checkbox)
        
        self.start_fetch_activity_btn = AnimatedHoverButton(text="Start")
        self.start_fetch_activity_btn.setMinimumHeight(40)
        self.start_fetch_activity_btn.clicked.connect(self.start_fetch_activity) 

        fetch_info_main_layout.addWidget(self.start_fetch_activity_btn)
        fetch_info_main_layout.addStretch(1)

        # Add a results area
        auto_login_group = QGroupBox("Auto Login")
        auto_login_group.setObjectName("Auto_Login")
        auto_login_group.setStyleSheet("""QGroupBox#Auto_Login{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#Auto_Login::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")

        auto_login_layout = QVBoxLayout(auto_login_group)

        self.results_text = QLabel()
        self.results_text.setText("Coming Soon")
        auto_login_layout.addWidget(self.results_text)

        # Add buttons at the bottom
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.addStretch(1)

        close_button = AnimatedHoverButton("Close")
        close_button.clicked.connect(self.fetch_info_dilog.close)
        button_layout.addWidget(close_button)

        

        # Add everything to the main dialog layout
        dialog_layout.addWidget(fetch_info_main_groupbox)
        dialog_layout.addWidget(auto_login_group)
        dialog_layout.addWidget(button_frame)
        
        self.fetch_info_dilog.exec()
        
    def update_package_name(self):
        """Update the package name in the ActivityControl reference."""
        if self.ActivityControl_refrance:
            self.ActivityControl_refrance.package_name = self.package_entry.text()

    def start_fetch_activity(self):
        """Start the ID fetch activity and close the dialog."""
        # Double-check that the selected list is still available
        if not self.selected_ld_list or (self.ActivityControl_refrance and not self.ActivityControl_refrance.selected_ld_list):
            QMessageBox.warning(self, "Warning", "No LDs selected. Please select at least one LD.")
            return
        
        is_sleep_enable =self.sleep_checkbox.isChecked() 
        # Set the activity type and start the process
        if self.ActivityControl_refrance:
            self.ActivityControl_refrance.is_auto_sleep_enable_in_id_fetch=is_sleep_enable
            self.ActivityControl_refrance.current_activity_type = "id_fetch_activity"
            self.ActivityControl_refrance.toggle_play_pause()
            
        self.fetch_info_dilog.close()
        self.main_window_refrance.switch_to_tab_idx(-1)
        #QMessageBox.information(self, "Info", "Check Activity tab for more control")

    def get_selected_lds(self):
        """Get information about selected LDs from the table."""
        selected_ld_list = []
        
        # Check if selected_indices exists and has values
        if not hasattr(self, 'selected_indices') or not self.selected_indices:
            # Get fresh selection
            self.selected_indices = self.table_view.selectionModel().selectedRows()
            if not self.selected_indices:
                return []
                
        for index in self.selected_indices:
            row = index.row()
            # Get data from each column
            ld_number = self.table_model.item(row, 0).text()
            ld_name = self.table_model.item(row, 1).text()
            ld_serial = self.table_model.item(row, 2).text()
            
            # Add the LD name to the list
            selected_ld_list.append(ld_name)
    
        return selected_ld_list

    def test(self):
        """Test method for debugging."""
        list = self.get_selected_lds()
        for l in list:
            print(l)




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
            self.spin_box.valueChanged.connect(self.save_callback)
            self.decrease_button.clicked.connect(self.save_callback)
            self.increase_button.clicked.connect(self.save_callback)
    
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

class LabelPlacer:
    def __init__(self, parent, text="Label", font_size=12, bold=True):
        self.parent = parent
        self.text = text
        self.font_size = font_size
        self.bold = bold

    def Label(self):
        label = QLabel(self.text, self.parent)
        font = QFont("Arial", self.font_size)
        if self.bold:
            font.setBold(True)
        label.setFont(font)
        return label


class AddMoreApps(QDialog):
    def __init__(self, ld_list=None, save_callback=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add More Apps")
        self.setFixedSize(650, 550)
        self.save_callback = save_callback
        self.ld_list = ld_list.copy() if ld_list else []
        self.app_entries = []
        
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Container for entries
        self.entries_widget = QWidget()
        self.entries_layout = QVBoxLayout(self.entries_widget)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.entries_widget)
        
        scroll_area.setStyleSheet("""
            QScrollArea {
                border:2px solid rgba(128,128,128,0.8);
                border-radius:8px;
                padding-top:5px;
                margin-top:10px;
                padding-right:10px;
                padding-left:10px;
                padding-bottom:5px;
                background-color: rgba(128,128,128,0.2)
            }""")


        main_layout.addWidget(scroll_area)
        
        # If list is provided, create entries; otherwise, create two default entries
        if self.ld_list:
            for address in self.ld_list:
                self.add_app_entry(address)
        else:
            self.add_app_entry()
            self.add_app_entry()
        
        # Buttons at the bottom
        buttons_layout = QHBoxLayout()
        
        add_button = AnimatedHoverButton("Add Another App")
        add_button.clicked.connect(self.add_app_row)
        buttons_layout.addWidget(add_button)
        
        remove_button = AnimatedHoverButton("Remove App")
        remove_button.clicked.connect(self.remove_app_entry)
        buttons_layout.addWidget(remove_button)
        
        save_button = AnimatedHoverButton("Save")
        save_button.clicked.connect(self.save_added_pages)
        buttons_layout.addWidget(save_button)
        
        main_layout.addLayout(buttons_layout)
    
    def add_app_entry(self, address=None):
        index = len(self.app_entries) + 1
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(5, 5, 5, 5)
        
        label = QLabel(f"{index}. App Path:")
        label.setFont(QFont("Arial", 12))
        row_layout.addWidget(label)
        
        line_edit = QLineEdit()
        if address:
            line_edit.setText(address)
        line_edit.setMinimumWidth(400)
        line_edit.setStyleSheet("""
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
        row_layout.addWidget(line_edit)
        
        browse_button = AnimatedHoverButton("Browse")
        browse_button.setFixedSize(80, 30)
        browse_button.clicked.connect(lambda: self.browse_file(line_edit))
        row_layout.addWidget(browse_button)
        
        self.entries_layout.addWidget(row_widget)
        self.app_entries.append({"widget": row_widget, "line_edit": line_edit})
        
        # Update label numbers for all entries
        self.update_labels()
    
    def update_labels(self):
        """Update the labels to show correct numbering"""
        for i, entry in enumerate(self.app_entries):
            # Find the label in the widget's layout
            layout = entry["widget"].layout()
            if layout and layout.itemAt(0):
                label = layout.itemAt(0).widget()
                if isinstance(label, QLabel):
                    label.setText(f"{i + 1}. App Path:")
    
    def browse_file(self, line_edit):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select an App", "", "APK Files (*.apk);;All Files (*.*)"
        )
        if file_path:
            line_edit.setText(file_path)
    
    def add_app_row(self):
        if len(self.app_entries) >= 11:
            QMessageBox.warning(self, "Warning!", "Max number of Apps reached")
            return
        self.add_app_entry()
    
    def remove_app_entry(self):
        if len(self.app_entries) <= 2:
            QMessageBox.warning(self, "Warning!", "Two Apps is Default")
            return
        
        last_entry = self.app_entries.pop()
        last_entry["widget"].deleteLater()
        self.update_labels()
    
    def save_added_pages(self):
        # Get all non-empty paths
        self.ld_list = [entry["line_edit"].text().strip() for entry in self.app_entries if entry["line_edit"].text().strip()]
        
        # Ensure we have at least 2 entries (first two are the default apps)
        while len(self.ld_list) < 2:
            self.ld_list.append("")
            
        if self.save_callback:
            self.save_callback(updated_list=self.ld_list)
        self.accept()


class DevicesSettings(QFrame):
    def __init__(self, parent=None, device_info_frame=None):
        super().__init__(parent)
        self.device_info_frame = device_info_frame
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(2)
        
        # Initialize variables
        self.default_delay = 5
        gpus = GPUtil.getGPUs()
        self.is_GPU_avlaible = len(gpus) > 0
        self.hardware_accelerated_var = self.is_GPU_avlaible
        self.enable_nvidia_var = self.is_GPU_avlaible
        self.APP_Paths_list = ["", ""]  # Initialize with at least 2 empty strings
        self.Ld_list = []
        
        # Initialize JSON reader
        self.devices_json = DevicesJson()
        self.json_filepath = "User_Data"
        
        self._create_widgets()
        self.load_settings()
    
    def _create_widgets(self):
        main_layout = QVBoxLayout(self)
        
        title_label = QLabel("Devices Settings")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(title_label, alignment=Qt.AlignLeft)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addSpacing(15)
        
        # Locations section
        main_layout.addWidget(self.create_location_selector())
        main_layout.addSpacing(15)
        # Times Settings
        main_layout.addWidget(self.create_time_selector())
        main_layout.addSpacing(15)
        
        # Default Apps
        main_layout.addWidget(self.create_default_apps())
        
        main_layout.addSpacing(15)
        
        # Settings container
        settings_container = QWidget()
        settings_layout = QHBoxLayout(settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        
        settings_layout.addWidget(self.create_ldplayer_settings())
        settings_layout.addWidget(self.create_ld_instance())
        settings_layout.addWidget(self.create_gpu_settings())
        
        main_layout.addWidget(settings_container)

        #remove comment these tow line to alingtop and stick to top
        main_layout.addStretch(1)
        #main_layout.setAlignment(Qt.AlignTop)
    
    def create_location_selector(self):
        loaction_groupbox = QGroupBox("Locations")
        loaction_groupbox.setObjectName("loaction_groupbox")
        loaction_groupbox.setStyleSheet("""QGroupBox#loaction_groupbox{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#loaction_groupbox::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        layout = QGridLayout(loaction_groupbox)
        
        # LD Location
        
        layout.addWidget(QLabel("LD Location:", loaction_groupbox, font=QFont("Arial", 10)), 0, 0)
        self.ld_location_entry = QLineEdit(loaction_groupbox)
        self.ld_location_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;           /* right padding for icon */  
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
        layout.addWidget(self.ld_location_entry, 0, 1)
        layout.setHorizontalSpacing(20)
        ld_browse_button = AnimatedHoverButton(text="Browse", parent=loaction_groupbox)
        ld_browse_button.setFixedSize(70, 30)
        ld_browse_button.clicked.connect(self.LD_folder_browse)
        layout.addWidget(ld_browse_button, 0, 2)
        
        # Geni Data
        layout.addWidget(QLabel("Geni Data:", loaction_groupbox, font=QFont("Arial", 10)), 1, 0)
        self.geni_data_entry = QLineEdit(loaction_groupbox)
        layout.addWidget(self.geni_data_entry, 1, 1)
        self.geni_data_entry.setStyleSheet("""
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
        geni_browse_button = AnimatedHoverButton(text="Browse", parent=loaction_groupbox)
        geni_browse_button.setFixedSize(70, 30)
        geni_browse_button.clicked.connect(self.GiniFlow_data_browse)
        layout.addWidget(geni_browse_button, 1, 2)
        
        # Refresh button
        refresh_button = AnimatedHoverButton(text="Refresh", parent=loaction_groupbox)
        refresh_button.setFixedSize(80, 40)
        refresh_button.clicked.connect(self.refrace_button)
        layout.addWidget(refresh_button, 0, 3, 2, 1)
        
        return loaction_groupbox
    
    def create_time_selector(self):
        time_group_box = QGroupBox()
        time_group_box.setTitle("Time Settings")
        time_group_box.setObjectName("time_group_box")
        time_group_box.setStyleSheet("""QGroupBox#time_group_box{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#time_group_box::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")

        layout = QGridLayout(time_group_box)
        
        # LD Opening Delay
        layout.addWidget(QLabel("LD Opening :", time_group_box, font=QFont("Arial", 10)), 0, 0)
        self.ld_opening_spinbox = IntSpinBox(time_group_box, initial=self.default_delay,to=10000, save_callback=self.save_settings)
        layout.addWidget(self.ld_opening_spinbox, 0, 1)
        
        # Account Switching Delay
        layout.addWidget(QLabel("Account Switching :", time_group_box, font=QFont("Arial", 10)), 0, 2)
        self.account_switching_spinbox = IntSpinBox(time_group_box, initial=self.default_delay,to=10000, save_callback=self.save_settings)
        layout.addWidget(self.account_switching_spinbox, 0, 3)
        
        # reels_uploading Delay
        layout.addWidget(QLabel("Reels Uploading :", time_group_box, font=QFont("Arial", 10)), 0, 4)
        self.reels_uploading_spinbox = IntSpinBox(time_group_box, initial=self.default_delay, to=10000,save_callback=self.save_settings)
        layout.addWidget(self.reels_uploading_spinbox, 0, 5)
        
        # Random Delay
        layout.addWidget(QLabel("Delay Btw Click:", time_group_box, font=QFont("Arial", 10)), 0, 6)
        self.anythings_spinbox = IntSpinBox(time_group_box, initial=self.default_delay,to=10000, save_callback=self.save_settings)
        layout.addWidget(self.anythings_spinbox, 0, 7)
        
        # Insight Delay
        layout.addWidget(QLabel("Insight (day):", time_group_box, font=QFont("Arial", 10)), 1, 0)
        self.insights_update_spinbox = IntSpinBox(time_group_box, initial=1,to=10000,save_callback=self.save_settings)
        layout.addWidget(self.insights_update_spinbox, 1, 1)
        
        layout.addWidget(QLabel("Video Uploading :", time_group_box, font=QFont("Arial", 10)), 1, 2)
        self.video_uploading_delay_spinbox = IntSpinBox(time_group_box, initial=1, to=10000,save_callback=self.save_settings)
        layout.addWidget(self.video_uploading_delay_spinbox, 1, 3)


        layout.addWidget(QLabel("Before Any Task :", time_group_box, font=QFont("Arial", 10)), 1, 4)
        self.before_any_task_delay_spinbox = IntSpinBox(time_group_box, initial=1, to=10000,save_callback=self.save_settings)
        layout.addWidget(self.before_any_task_delay_spinbox, 1, 5)


        return time_group_box
    
    def create_default_apps(self):

        default_app_group_box = QGroupBox()
        default_app_group_box.setObjectName("default_app_group_box")
        default_app_group_box.setStyleSheet("""QGroupBox#default_app_group_box{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#default_app_group_box::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        default_app_group_box.setTitle("Default Apps")
        layout = QGridLayout(default_app_group_box)
        
        # App 1
        layout.addWidget(QLabel("1. App Path", default_app_group_box, font=QFont("Arial", 10)), 0, 0)
        self.app1_entry = QLineEdit(default_app_group_box)
        self.app1_entry.setStyleSheet("""
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
        
        self.app1_entry.textChanged.connect(self.update_app1_path)
        layout.addWidget(self.app1_entry, 0, 1)
        app1_browse_button = AnimatedHoverButton(text="Browse",parent= default_app_group_box)
        layout.setHorizontalSpacing(20)
        app1_browse_button.setFixedSize(70, 30)
        app1_browse_button.clicked.connect(self.app1_paths_selector)
        layout.addWidget(app1_browse_button, 0, 2)
        
        
        # App 2
        layout.addWidget(QLabel("2. App Path", default_app_group_box, font=QFont("Arial", 10)), 1, 0)
        self.app2_entry = QLineEdit(default_app_group_box)
        self.app2_entry.setStyleSheet("""
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
        
        layout.addWidget(self.app2_entry, 1, 1)
        app2_browse_button = AnimatedHoverButton(text="Browse", parent=default_app_group_box)
        layout.setHorizontalSpacing(20)
        app2_browse_button.setFixedSize(70, 30)
        app2_browse_button.clicked.connect(self.app2_paths_selector)
        self.app2_entry.textChanged.connect(self.update_app2_path)
        layout.addWidget(app2_browse_button, 1, 2)
        
        # Add More Apps button
        add_more_button = AnimatedHoverButton(text="Add More Apps", parent=default_app_group_box)
        layout.setHorizontalSpacing(20)
        add_more_button.setFixedSize(100, 40)
        add_more_button.clicked.connect(self.open_add_more_apps)
        layout.addWidget(add_more_button, 0, 3, 2, 1)
        
        return default_app_group_box
    
    def create_ldplayer_settings(self):

        ld_player_settings_group_box = QGroupBox()
        ld_player_settings_group_box.setObjectName("ld_player_settings_group_box")
        ld_player_settings_group_box.setTitle("Ld Player Setting And Enable/Disable")
        ld_player_settings_group_box.setStyleSheet("""QGroupBox#ld_player_settings_group_box{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.1);}
                                            QGroupBox#ld_player_settings_group_box::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        main_layout = QVBoxLayout(ld_player_settings_group_box)
        
        # LD Settings section
        settings_group = QGroupBox("Ld Player Settings")
        
        settings_group.setObjectName("settings_group")
        settings_group.setStyleSheet("""QGroupBox#settings_group{border:1px solid rgba(128,128,128,0.8);
                                     border-radius:8px;
                                     padding-top:20px;
                                     margin-top:10px;
                                     padding-right:10px;
                                     padding-left:10px;
                                     background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#settings_group::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top center;
                                                            border-radius:5px;
                                                            padding: 0 3px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        settings_layout = QGridLayout(settings_group)
        settings_layout.setContentsMargins(5, 5, 5, 5)
        
        # Resolution
        settings_layout.addWidget(QLabel("Resolution:", settings_group, font=QFont("Arial", 10)), 0, 0)
        self.resolution_combo = QComboBox(settings_group)
        self.resolution_combo.setStyleSheet("""QComboBox{background-color:rgba(27,86,253,0.7);padding-left:5px; padding-right:5px;padding-bottom:2px;padding-top:2px;}
                                            QComboBox::hover:{border-color:rgba(27,86,253,1)}
                                            QComboBox::drop-down{margin-left:5px;}
                                            """)
                                            
        self.resolution_combo.addItems(["1080x1920", "900x1600", "720x1280", "540x960 (Recommended)"])
        self.resolution_combo.setCurrentText("540x960 (Recommended)")
        self.resolution_combo.currentIndexChanged.connect(self.save_settings)
        settings_layout.addWidget(self.resolution_combo, 0, 1)
        
        # CPU
        settings_layout.addWidget(QLabel("CPU:", settings_group, font=QFont("Arial", 10)), 1, 0)
        self.cpu_combo = QComboBox(settings_group)
        self.cpu_combo.setStyleSheet("""QComboBox{background-color:rgba(27,86,253,0.7);padding-left:5px; padding-right:5px;padding-bottom:2px;padding-top:2px;}
                                            QComboBox::hover:{border-color:rgba(27,86,253,1)}
                                            QComboBox::drop-down{margin-left:5px;}
                                            """)
        self.cpu_combo.addItems(["1 Core", "2 Cores (Recommended)", "3 Cores", "4 Cores", "6 Cores"])
        self.cpu_combo.setCurrentText("2 Cores (Recommended)")
        self.cpu_combo.currentIndexChanged.connect(self.save_settings)
        settings_layout.addWidget(self.cpu_combo, 1, 1)
        
        # RAM
        settings_layout.addWidget(QLabel("RAM:", settings_group, font=QFont("Arial", 10)), 2, 0)
        self.ram_combo = QComboBox(settings_group)
        self.ram_combo.setStyleSheet("""QComboBox{background-color:rgba(27,86,253,0.7);padding-left:5px; padding-right:5px;padding-bottom:2px;padding-top:2px;}
                                            QComboBox::hover:{border-color:rgba(27,86,253,1)}
                                            QComboBox::drop-down{margin-left:5px;}
                                            """)
        self.ram_combo.addItems(["512MB", "768MB", "1024MB (Recommended)", "1536MB", "2048MB", "4096MB"])
        self.ram_combo.setCurrentText("1024MB (Recommended)")
        self.ram_combo.currentIndexChanged.connect(self.save_settings)
        settings_layout.addWidget(self.ram_combo, 2, 1)
        
        # Display
        settings_layout.addWidget(QLabel("Display:", settings_group, font=QFont("Arial", 10)), 3, 0)
        self.display_combo = QComboBox(settings_group)
        self.display_combo.addItems(["Display1 [1920x1080]"])
        self.display_combo.setStyleSheet("""QComboBox{background-color:rgba(27,86,253,0.7);padding-left:5px; padding-right:5px;padding-bottom:2px;padding-top:2px;}
                                            QComboBox::hover:{border-color:rgba(27,86,253,1)}
                                            QComboBox::drop-down{margin-left:5px;}
                                            """)
        self.display_combo.setCurrentText("Display1 [1920x1080]")
        self.display_combo.currentIndexChanged.connect(self.save_settings)
        settings_layout.addWidget(self.display_combo, 3, 1)
        
        # LD Per Row
        settings_layout.addWidget(QLabel("LD Per Row:", settings_group, font=QFont("Arial", 10)), 4, 0)
        self.ld_per_row_spinbox = IntSpinBox(settings_group, initial=4, save_callback=self.ld_per_row_save)
        settings_layout.addWidget(self.ld_per_row_spinbox, 4, 1)
        
        # Startup Time Delay
        settings_layout.addWidget(QLabel("Run At Startup Time Delay (sec):", settings_group, font=QFont("Arial", 10)), 5, 0)
        self.startup_delay_spinbox = IntSpinBox(settings_group, initial=10, save_callback=self.save_settings)
        settings_layout.addWidget(self.startup_delay_spinbox, 5, 1)
        


        
        # Settings Enable/Disable section

        #enable_widget = QWidget()
        #enable_widget.setObjectName("enable_widget")
        settings_enable_group = QGroupBox("Setting Enable/Disable")
        settings_enable_group.setObjectName("settings_enable_group")
        settings_enable_group.setStyleSheet("""QGroupBox#settings_enable_group{border:1px solid rgba(128,128,128,.8);
                                            border-radius:8px;margin-top: 10px;
                                            background-color: rgba(128,128,128,0.2);
                                            padding-left:10px;
                                            padding-right:10px;}
                                            
                                            QGroupBox#settings_enable_group::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top center;
                                                            border-radius:5px;
                                                            padding: 0 3px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")

        enable_layout = QVBoxLayout(settings_enable_group)
        enable_layout.setContentsMargins(5, 5, 5, 5)
        
        self.check_internet_checkbox = QCheckBox("Check for internet at startup", settings_enable_group)
        self.check_internet_checkbox.setChecked(True)
        self.check_internet_checkbox.setStyleSheet("""QCheckBox{}
                                        """)
        self.check_internet_checkbox.clicked.connect(self.save_settings)
        enable_layout.addWidget(self.check_internet_checkbox)
        
        self.check_vpn_connection_checkbox = QCheckBox("Check Vpn Connnection", settings_enable_group)
        #self.check_vpn_connection_checkbox.setChecked(True)
        self.check_vpn_connection_checkbox.toggled.connect(self.save_settings)
        enable_layout.addWidget(self.check_vpn_connection_checkbox)

        self.select_vpn_combobox = QComboBox(settings_enable_group)
        self.select_vpn_combobox.addItems(["HMA Pro","Surfshark","VPN super","Turbo VPN"])
        self.select_vpn_combobox.setCurrentText("Surfshark")
        self.select_vpn_combobox.setStyleSheet("""QComboBox{background-color:rgba(27,86,253,0.7);padding-left:5px; padding-right:5px;padding-bottom:2px;padding-top:2px;}
                                            QComboBox::hover:{border-color:rgba(27,86,253,1)}
                                            QComboBox::drop-down{margin-left:5px;}
                                            """)
        self.select_vpn_combobox.currentIndexChanged.connect(self.save_settings)
        enable_layout.addWidget(self.select_vpn_combobox)
        
        self.check_apply_ld_checkbox = QCheckBox("Check and apply ld config", settings_enable_group)
        self.check_apply_ld_checkbox.setChecked(True)
        self.check_apply_ld_checkbox.clicked.connect(self.save_settings)
        enable_layout.addWidget(self.check_apply_ld_checkbox)
        
        self.auto_arrange_checkbox = QCheckBox("Auto arrange ld player", settings_enable_group)
        self.auto_arrange_checkbox.setChecked(True)
        self.auto_arrange_checkbox.clicked.connect(self.auto_arr_ld)
        enable_layout.addWidget(self.auto_arrange_checkbox)
        
        self.auto_shutdown_checkbox = QCheckBox("Auto Sleep after task completion", settings_enable_group)
        self.auto_shutdown_checkbox.setChecked(False)
        self.auto_shutdown_checkbox.clicked.connect(self.save_settings)
        enable_layout.addWidget(self.auto_shutdown_checkbox)

        #ebable_group.setLayout(ebable_group)
        settings_and_enable_disable_layout = QHBoxLayout()
        settings_and_enable_disable_layout.addWidget(settings_group)
        settings_and_enable_disable_layout.addWidget(settings_enable_group)
        main_layout.addLayout(settings_and_enable_disable_layout)
        
        return ld_player_settings_group_box
    
    def create_ld_instance(self):
        frame = QGroupBox()
        frame.setTitle("Instance Settings")
        frame.setObjectName("frame")
        frame.setStyleSheet("""QGroupBox#frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        
        # Chrome instances

        chrome_instance_vlayout = QVBoxLayout()
        chrome_instance_vlayout.addWidget(QLabel("Chrome instance at a time:", frame, font=QFont("Arial", 10)))
        self.num_chrome_instances_spinbox = IntSpinBox(frame, initial=1, save_callback=self.save_settings)
        chrome_instance_vlayout.addWidget(self.num_chrome_instances_spinbox, alignment=Qt.AlignTop)
        layout.addLayout(chrome_instance_vlayout)

        # LD instances
        ld_instance_vlayout = QVBoxLayout()
        ld_instance_vlayout.addWidget(QLabel("LD instance at a time:", frame, font=QFont("Arial", 10)))
        ld_instance_vlayout.setSpacing(2)
        self.num_ld_instances_spinbox = IntSpinBox(frame, initial=1, save_callback=self.save_settings)
        ld_instance_vlayout.addWidget(self.num_ld_instances_spinbox, alignment=Qt.AlignTop)
        layout.addLayout(ld_instance_vlayout)

        
        # Install default apps checkbox
        self.install_default_apps_checkbox = QCheckBox("Install default apps", frame)
        self.install_default_apps_checkbox.setChecked(True)
        self.install_default_apps_checkbox.clicked.connect(self.save_settings)
        layout.addWidget(self.install_default_apps_checkbox)
        
        # Placeholder checkbox (can be removed or replaced with actual functionality)
        self.something_checkbox = QCheckBox("Something", frame)
        self.something_checkbox.clicked.connect(self.save_settings)
        layout.addWidget(self.something_checkbox)
        
        return frame
    
    def create_gpu_settings(self):

        frame = QGroupBox()

        frame.setMinimumHeight(300)
        frame.setObjectName("frame")
        frame.setTitle("GPU Settings")

        frame.setStyleSheet("""QGroupBox#frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        layout = QGridLayout(frame)
        
        # "Check GPU" button
        check_for_GPU_btn = AnimatedHoverButton("Check GPU")
        check_for_GPU_btn.setMinimumHeight(80)
        check_for_GPU_btn.clicked.connect(self.button_check_GPU)
        layout.addWidget(check_for_GPU_btn, 0, 0, 1, 1)
        
        layout.setVerticalSpacing(50)
        layout.setAlignment(Qt.AlignTop)
        # "Hardware accelerated" checkbox
        self.hardware_accelerated_chk = QCheckBox("Hardware accelerated")
        self.hardware_accelerated_chk.setChecked(self.hardware_accelerated_var)
        self.hardware_accelerated_chk.toggled.connect(self.update_hardware_accelerated)
        layout.addWidget(self.hardware_accelerated_chk, 1, 0, 1, 1, Qt.AlignLeft)
        
        # "Enable Nvidia GPU" checkbox
        self.enable_nvidia_chk = QCheckBox("Enable Nvidia GPU")
        self.enable_nvidia_chk.setChecked(self.enable_nvidia_var)
        self.enable_nvidia_chk.setEnabled(self.is_GPU_avlaible)
        self.enable_nvidia_chk.toggled.connect(self.update_nvidia_gpu)
        layout.addWidget(self.enable_nvidia_chk, 2, 0, 1, 1, Qt.AlignLeft)
        
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setVerticalSpacing(10)
        
        
        return frame
    
    def update_hardware_accelerated(self, checked):
        self.hardware_accelerated_var = checked
        self.save_settings()
    
    def update_nvidia_gpu(self, checked):
        self.enable_nvidia_var = checked
        self.save_settings()
    


    def button_check_GPU(self):
        gpus = GPUtil.getGPUs()
        self.is_GPU_avlaible = len(gpus) > 0

        if self.is_GPU_avlaible:
            # Check if any GPU is NVIDIA
            nvidia_gpus = [gpu for gpu in gpus if 'nvidia' in gpu.name.lower()]

            if nvidia_gpus:
                # Found NVIDIA GPU(s)
                gpu_info = []
                has_capable_gpu = False

                for gpu in nvidia_gpus:
                    gpu_info.append(f"• {gpu.name}")
                    gpu_info.append(f"  Memory: {gpu.memoryTotal}MB")
                    gpu_info.append(f"  Usage: {gpu.memoryUsed}MB / {gpu.memoryTotal}MB")

                    # Check if GPU is 2000 series or newer (RTX 20XX, 30XX, 40XX, etc.)
                    if self.is_gpu_capable(gpu.name):
                        has_capable_gpu = True

                # Show GPU information
                gpu_details = "\n".join(gpu_info)

                if has_capable_gpu:
                    QMessageBox.information(
                        self, 
                        "GPU Available", 
                        f"NVIDIA GPU(s) detected and ready for AI features:\n\n{gpu_details}"
                    )
                    self.enable_nvidia_chk.setEnabled(True)
                    self.enable_nvidia_var = True
                    self.enable_nvidia_chk.setChecked(True)
                    self.hardware_accelerated_var = True
                    self.hardware_accelerated_chk.setChecked(True)
                else:
                    QMessageBox.warning(
                        self, 
                        "GPU Available (Limited)", 
                        f"NVIDIA GPU(s) detected but some AI features may be missing due to older hardware:\n\n{gpu_details}\n\nRecommended: RTX 2000 series or newer for full AI   capabilities."
                    )
                    self.enable_nvidia_chk.setEnabled(True)
                    self.enable_nvidia_var = False
                    self.enable_nvidia_chk.setChecked(False)
                    self.hardware_accelerated_var = False
                    self.hardware_accelerated_chk.setChecked(False)
            else:
                # Non-NVIDIA GPU found
                non_nvidia_gpus = [gpu.name for gpu in gpus]
                gpu_list = "\n".join([f"• {name}" for name in non_nvidia_gpus])

                QMessageBox.warning(
                    self, 
                    "NVIDIA GPU Required", 
                    f"GPU(s) detected but NVIDIA GPU is required for AI features:\n\n{gpu_list}\n\nPlease install an NVIDIA GPU to use AI acceleration."
                )
                self.enable_nvidia_chk.setEnabled(False)
                self.enable_nvidia_var = False
                self.enable_nvidia_chk.setChecked(False)
                self.hardware_accelerated_var = False
                self.hardware_accelerated_chk.setChecked(False)
        else:
            # No GPU available
            QMessageBox.critical(
                self, 
                "No GPU Available", 
                "No GPU detected on this system.\n\nAI features will not be available. Please install an NVIDIA GPU (RTX 2000 series or newer recommended) to enable hardware   acceleration."
            )
            self.enable_nvidia_chk.setEnabled(False)
            self.enable_nvidia_var = False
            self.enable_nvidia_chk.setChecked(False)
            self.hardware_accelerated_var = False
            self.hardware_accelerated_chk.setChecked(False)

        self.save_settings()

    def is_gpu_capable(self, gpu_name):
        """Check if GPU is RTX 2000 series or newer"""
        gpu_name_lower = gpu_name.lower()

        # Check for RTX series (2000, 3000, 4000, etc.)
        rtx_pattern = r'rtx\s*(\d{4})'
        rtx_match = re.search(rtx_pattern, gpu_name_lower)
        if rtx_match:
            series = int(rtx_match.group(1))
            return series >= 2000

        # Check for newer architecture names
        capable_architectures = [
            'rtx', 'a100', 'a40', 'a30', 'a10', 'a6000', 'a5000', 'a4000',
            'tesla v100', 'tesla p100', 'tesla p40', 'quadro rtx'
        ]

        return any(arch in gpu_name_lower for arch in capable_architectures)

    
    def LD_folder_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select LDPlayer Directory")
        if folder:
            self.ld_location_entry.setText(folder)
            
            self.refrace_button()
    
    def GiniFlow_data_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Geni Data Directory")
        if folder:
            self.geni_data_entry.setText(folder)
            self.save_settings()
    
    def app1_paths_selector(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select App 1", "", "APK Files (*.apk);;All Files (*.*)")
        if file_path:
            self.app1_entry.setText(file_path)
 
    
    def app2_paths_selector(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select App 2", "", "APK Files (*.apk);;All Files (*.*)")
        if file_path:
            self.app2_entry.setText(file_path)

    
    def open_add_more_apps(self):
        dialog = AddMoreApps(ld_list=self.APP_Paths_list, save_callback=self.save_app_paths_list, parent=self)
        dialog.exec()


    def update_app1_path(self):
        if len(self.APP_Paths_list) >= 1:
            self.APP_Paths_list[0] = self.app1_entry.text()
        else:
            self.APP_Paths_list.append(self.app1_entry.text())
        self.save_settings()

    def update_app2_path(self):
        if len(self.APP_Paths_list) >= 2:
            self.APP_Paths_list[1] = self.app2_entry.text()
        else:
            self.APP_Paths_list.append(self.app2_entry.text())
        self.save_settings()

    def save_app_paths_list(self, updated_list=None):
        if updated_list is not None:
            self.APP_Paths_list = updated_list
            if len(self.APP_Paths_list) >= 1:
                self.app1_entry.setText(self.APP_Paths_list[0])
            else:
                self.app1_entry.setText("")
            if len(self.APP_Paths_list) >= 2:
                self.app2_entry.setText(self.APP_Paths_list[1])
            else:
                self.app2_entry.setText("")
            self.save_settings()
    
    
    def get_ld_list(self, path):
        ld_controller = LdAdbController()
        ld_list = ld_controller.get_ld_list(path)
        self.Ld_list = ld_list
        return ld_list
    
    def refrace_button(self):
        ld_path = self.ld_location_entry.text()
        if ld_path and os.path.exists(ld_path):
            ld_list = self.get_ld_list(ld_path)
            self.device_info_frame.update_device_info_frame(ld_list=ld_list, refresh=True)
            self.save_settings()
    
    def ld_per_row_save(self):
        ld_controller = LdAdbController()
        ld_controller.set_ld_multi_player_config(
            key="windowsRowCount",
            to_set_value=self.ld_per_row_spinbox.get_value(),
            if_key_not_avl_after_val=7
        )
        self.save_settings()
    
    def auto_arr_ld(self):
        ld_controller = LdAdbController()
        ld_controller.set_ld_multi_player_config(
            key="windowsAutoSize",
            to_set_value=int(self.auto_arrange_checkbox.isChecked()),
            if_key_not_avl_after_val=9
        )
        self.save_settings()
    
    def get_settings(self) -> dict:
        settings = {
            "Locations": {
                "LD Location": self.ld_location_entry.text(),
                "Geni Data": self.geni_data_entry.text()
            },
            "Times Setting": {
                "LD Opening Delay": self.ld_opening_spinbox.get_value(),
                "video_uploading_delay":self.video_uploading_delay_spinbox.get_value(),
                "Account Switching Delay": self.account_switching_spinbox.get_value(),
                "Reels Uploading Delay": self.reels_uploading_spinbox.get_value(),
                "Anythings Delay": self.anythings_spinbox.get_value(),
                "Update_insights_delay": self.insights_update_spinbox.get_value(),
                "before_any_task_delay": self.before_any_task_delay_spinbox.get_value(),
            },
            "Default Apps": self.APP_Paths_list,
            "LDPlayer Settings": {
                "Ld Settings": {
                    "Resolution": self.resolution_combo.currentText(),
                    "CPU": self.cpu_combo.currentText(),
                    "RAM": self.ram_combo.currentText(),
                    "Display": self.display_combo.currentText(),
                    "LD Per Row": self.ld_per_row_spinbox.get_value(),
                    "Run At Startup Time Delay (sec)": self.startup_delay_spinbox.get_value()
                },
                "Settings Enable/Disable": {
                    "Check for internet at startup": self.check_internet_checkbox.isChecked(),
                    "check_vpn_connnection": self.check_vpn_connection_checkbox.isChecked(),
                    "Check and apply ld config": self.check_apply_ld_checkbox.isChecked(),
                    "Auto arrange ld player": self.auto_arrange_checkbox.isChecked(),
                    "Auto shutdown after task completion": self.auto_shutdown_checkbox.isChecked()
                }
            },
            "LD Instance Settings": {
                "Number of instance at a time": self.num_ld_instances_spinbox.get_value(),
                "Number of chrome instance at a time": self.num_chrome_instances_spinbox.get_value(),
                "Install default apps": self.install_default_apps_checkbox.isChecked(),
                "Something": self.something_checkbox.isChecked()
            },
            "GPU settings": {
                "Hardware accelerated": self.hardware_accelerated_var,
                "Enable Nvidia GPU": self.enable_nvidia_var
            },
            "vpn":{"vpn_app_name":self.select_vpn_combobox.currentText()}
            # Removed: "Devices Info": self.Ld_list
        }
        return settings

    def apply_settings(self, settings: dict):
        loc = settings.get("Locations", {})
        self.ld_location_entry.setText(loc.get("LD Location", ""))
        self.geni_data_entry.setText(loc.get("Geni Data", ""))
    
        times = settings.get("Times Setting", {})
        self.ld_opening_spinbox.set_value(times.get("LD Opening Delay",20))
        self.video_uploading_delay_spinbox.set_value(times.get("video_uploading_delay",50))
        self.account_switching_spinbox.set_value(times.get("Account Switching Delay", 4))
        self.reels_uploading_spinbox.set_value(times.get("Reels Uploading Delay", 10))
        self.anythings_spinbox.set_value(times.get("Anythings Delay", 1))
        self.insights_update_spinbox.set_value(times.get("Update_insights_delay", 1))
        self.before_any_task_delay_spinbox.set_value(times.get("before_any_task_delay",1))
    
        ldsettings = settings.get("LDPlayer Settings", {}).get("Ld Settings", {})
        self.resolution_combo.setCurrentText(ldsettings.get("Resolution", "540x960 (Recommended)"))
        self.cpu_combo.setCurrentText(ldsettings.get("CPU", "2 Cores (Recommended)"))
        self.ram_combo.setCurrentText(ldsettings.get("RAM", "1024MB (Recommended)"))
        self.display_combo.setCurrentText(ldsettings.get("Display", "Display1 [1920x1080]"))
        self.ld_per_row_spinbox.set_value(ldsettings.get("LD Per Row", 4))
        self.startup_delay_spinbox.set_value(ldsettings.get("Run At Startup Time Delay (sec)", 10))
    
        ldAppList = settings.get("Default Apps", [])
        self.APP_Paths_list = ldAppList
        if len(ldAppList) >= 1:
            self.app1_entry.setText(ldAppList[0])
        if len(ldAppList) >= 2:
            self.app2_entry.setText(ldAppList[1])
    
        ldinstance = settings.get("LD Instance Settings", {})
        self.num_ld_instances_spinbox.set_value(ldinstance.get("Number of instance at a time", 1))
        self.num_chrome_instances_spinbox.set_value(ldinstance.get("Number of chrome instance at a time", 1))
        self.install_default_apps_checkbox.setChecked(ldinstance.get("Install default apps", True))
        self.something_checkbox.setChecked(ldinstance.get("Something", False)) 
    
        gpu = settings.get("GPU settings", {})
        self.hardware_accelerated_var = gpu.get("Hardware accelerated", self.is_GPU_avlaible)
        self.enable_nvidia_var = gpu.get("Enable Nvidia GPU", self.is_GPU_avlaible)
        self.hardware_accelerated_chk.setChecked(self.hardware_accelerated_var)
        self.enable_nvidia_chk.setChecked(self.enable_nvidia_var)
        self.enable_nvidia_chk.setEnabled(self.is_GPU_avlaible)
    
        ld_enable = settings.get("LDPlayer Settings", {}).get("Settings Enable/Disable", {})
        self.check_internet_checkbox.setChecked(ld_enable.get("Check for internet at startup", True))
        self.check_vpn_connection_checkbox.setChecked(ld_enable.get("check_vpn_connnection", False))
        self.check_apply_ld_checkbox.setChecked(ld_enable.get("Check and apply ld config", True))
        self.auto_arrange_checkbox.setChecked(ld_enable.get("Auto arrange ld player", True))
        self.auto_shutdown_checkbox.setChecked(ld_enable.get("Auto shutdown after task completion", False))

        vpn_settings = settings.get("vpn",{})
        vpn_app_name = vpn_settings.get("vpn_app_name","")
        self.select_vpn_combobox.setCurrentText(vpn_app_name)
    
        # Fetch LD list dynamically instead of loading from settings
        ld_path = self.ld_location_entry.text()
        if ld_path and os.path.exists(ld_path):
            self.Ld_list = self.get_ld_list(ld_path)
        else:
            self.Ld_list = []
        self.device_info_frame.update_device_info_frame(ld_list=self.Ld_list)   
        
    
    def save_settings(self):
        settings = self.get_settings()
        self.devices_json.save_changes(settings)
    
    def load_settings(self):
        settings = self.devices_json.load_or_create_json(self.json_filepath)
        self.apply_settings(settings)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    device_info = DevicesInfoLdTable()
    settings = DevicesSettings(device_info_frame=device_info)
    # Stack the DevicesInfor and DevicesSettings vertically in the main window
    central_widget = QWidget()
    layout = QHBoxLayout(central_widget)
    layout.addWidget(device_info)
    layout.addWidget(settings)
    window.setCentralWidget(central_widget)
    window.show()
    sys.exit(app.exec())