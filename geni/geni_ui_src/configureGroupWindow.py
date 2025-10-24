# D:\coding\GENIFLOW\geniflow\geni\geni_ui_src\configureGroupWindow.py

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
import sys
import os

# Import GroupSharingUI from the other file
try:
    from geni_ui_src.GroupSharingUI import GroupSharingUI, AnimatedHoverButton
    SHARING_UI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import GroupSharingUI: {e}")
    SHARING_UI_AVAILABLE = False
    # Fallback
    from PySide6.QtWidgets import QPushButton as AnimatedHoverButton


class ConfigureGrpWindow(QDialog):
    """Dialog for configuring group sharing settings."""
    
    def __init__(self, json_file_path=None, id_frame_idx=None, profile_name=None, parent=None):
        super().__init__(parent)
        
        # Store all parameters
        self.json_file_path = json_file_path
        self.id_frame_idx = id_frame_idx if id_frame_idx is not None else 0
        self.current_profile = profile_name
        
        self.setWindowTitle(f"Configure Groups - {profile_name or 'Profile'}")
        self.setMinimumSize(500, 600)
        self.setModal(True)
        
        # Set dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0c10;
                color: #eeeeee;
                font-family: 'Arial';
            }
            QLabel {
                background-color: transparent;
            }
        """)
        
        # Store reference to group sharing window
        self.group_sharing_window = None
        
        # Setup UI
        self.setup_ui()
        
        # Load config if path provided
        if self.json_file_path:
            self.load_from_json()
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: rgb(34, 81, 200);
                border-radius: 10px;
            }
        """)
        header_frame.setFixedHeight(60)
        
        header_layout = QVBoxLayout(header_frame)
        header_label = QLabel("⚙️ Configure Groups")
        header_label.setStyleSheet("""
            font-size: 16pt;
            font-weight: bold;
            color: white;
            background-color: transparent;
        """)
        header_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(header_label)
        
        layout.addWidget(header_frame)
        
        # Profile info
        if self.current_profile:
            profile_label = QLabel(f"👤 Profile: {self.current_profile}")
            profile_label.setStyleSheet("""
                background-color: rgba(46,204,113,0.3);
                color: #46cc71;
                padding: 10px 15px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
            """)
            layout.addWidget(profile_label)
        
        # Info
        info_label = QLabel(
            "📋 Configure your group sharing settings below.\n"
            "Set up sharing methods and niche-based group organizations."
        )
        info_label.setStyleSheet("""
            background-color: rgba(128,128,128,0.2);
            padding: 15px;
            border-radius: 8px;
            color: #eeeeee;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # File path info
        if self.json_file_path:
            file_exists = os.path.exists(self.json_file_path)
            status = "✅" if file_exists else "⚠️"
            file_label = QLabel(f"📁 Config: {status} {self.json_file_path}")
            file_label.setStyleSheet("""
                background-color: rgba(128,128,128,0.2);
                padding: 8px;
                border-radius: 6px;
                color: #eeeeee;
                font-size: 9pt;
            """)
            file_label.setWordWrap(True)
            layout.addWidget(file_label)
        
        # Open button
        if SHARING_UI_AVAILABLE:
            open_btn = AnimatedHoverButton("📊 Open Group Sharing Manager")
        else:
            open_btn = QPushButton("📊 Open Group Sharing Manager (UI Not Available)")
            open_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgb(34, 81, 200);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgb(27, 86, 253);
                }
            """)
        
        open_btn.setFixedHeight(50)
        open_btn.setToolTip("Open the full Group Sharing configuration interface")
        open_btn.clicked.connect(self.open_group_sharing)
        layout.addWidget(open_btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        
        # Close button
        if SHARING_UI_AVAILABLE:
            close_btn = AnimatedHoverButton("✖️ Close")
        else:
            close_btn = QPushButton("✖️ Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(128,128,128,0.5);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(128,128,128,0.7);
                }
            """)
        
        close_btn.setFixedSize(120, 40)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
    
    # In configureGroupWindow.py

    # In configureGroupWindow.py

    def open_group_sharing(self):
        """Open Group Sharing UI window."""
        if not SHARING_UI_AVAILABLE:
            QMessageBox.warning(self, "Not Available", "Group Sharing UI is not available.")
            return
        
        try:
            if self.group_sharing_window is None or not self.group_sharing_window.isVisible():
                # ✅ Pass 'self' as parent to create parent-child relationship
                self.group_sharing_window = GroupSharingUI()
                
                # ✅ Set parent AFTER creation
                self.group_sharing_window.setParent(self, Qt.Window)
                
                # ✅ Set attribute to delete on close
                self.group_sharing_window.setAttribute(Qt.WA_DeleteOnClose)
                
                self.group_sharing_window.resize(1300, 850)
                
                if self.json_file_path:
                    self.group_sharing_window.config_file = self.json_file_path
                    self.group_sharing_window.load_config(silent=True)
            
            self.group_sharing_window.show()
            self.group_sharing_window.raise_()
            self.group_sharing_window.activateWindow()
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Error", f"Failed to open:\n{str(e)}")
    
    def load_from_json(self):
        """Load configuration from JSON file."""
        if self.json_file_path and os.path.exists(self.json_file_path):
            print(f"[OK] Config file found: {self.json_file_path}")
            print(f"     Frame Index: {self.id_frame_idx}")
            print(f"     Profile: {self.current_profile}")
        else:
            print(f"[WARNING] Config file not found: {self.json_file_path}")
    
    def save_to_json(self):
        """Save configuration to JSON file."""
        pass


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ConfigureGrpWindow(
        json_file_path=r"User_Data\Page_manager.json",
        id_frame_idx=0,
        profile_name="Test Profile"
    )
    window.exec()
    sys.exit(app.exec())