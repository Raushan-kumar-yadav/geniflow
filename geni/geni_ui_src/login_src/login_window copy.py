import sys
import requests
import json
import uuid
import datetime
import threading
import os 
import subprocess
from subprocess import CREATE_NO_WINDOW
import platform
import time



from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QPushButton, QLineEdit, QLabel, 
                               QMessageBox, QFrame, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal, QTimer,QPropertyAnimation,Property,QObject,QUrl,QMetaObject
from PySide6.QtGui import QFont, QPalette, QColor,QDesktopServices


def get_mac_address():
    """Get the MAC address of the primary network interface"""
    try:
        # Get MAC address using uuid.getnode()
        mac_num = uuid.getnode()
        mac_hex = ':'.join(f'{(mac_num >> ele) & 0xff:02x}' for ele in range(0, 8*6, 8))[::-1]
        
        # Alternative method for more reliable MAC detection
        if platform.system() == "Windows":
            try:
                result = subprocess.run(['getmac', '/fo', 'csv'], capture_output=True, text=True,creationflags=CREATE_NO_WINDOW)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        # Parse the first MAC address from CSV output
                        mac_line = lines[1].split(',')[0].strip('"')
                        mac_hex = mac_line.lower().replace('-', ':')
            except:
                pass
        elif platform.system() == "Linux":
            try:
                result = subprocess.run(['cat', '/sys/class/net/eth0/address'], capture_output=True, text=True,creationflags=CREATE_NO_WINDOW)
                if result.returncode == 0:
                    mac_hex = result.stdout.strip().lower()
                else:
                    # Try alternative interfaces
                    result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True,creationflags=CREATE_NO_WINDOW)
                    if result.returncode == 0:
                        import re
                        mac_match = re.search(r'link/ether ([a-f0-9:]{17})', result.stdout)
                        if mac_match:
                            mac_hex = mac_match.group(1)
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                result = subprocess.run(['ifconfig', 'en0'], capture_output=True, text=True,creationflags=CREATE_NO_WINDOW)
                if result.returncode == 0:
                    import re
                    mac_match = re.search(r'ether ([a-f0-9:]{17})', result.stdout)
                    if mac_match:
                        mac_hex = mac_match.group(1)
            except:
                pass
        
        # Validate MAC address format
        if len(mac_hex) == 17 and mac_hex.count(':') == 5:
            return mac_hex.lower()
        else:
            return None
            
    except Exception as e:
        return None


class DialogManager(QObject):
    """Singleton class to manage dialog instances and ensure thread safety"""
    _instance = None
    show_about_signal = Signal()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            super().__init__()
            self.about_dialog = None
            self.show_about_signal.connect(self._show_about_dialog)
            self.initialized = True
    
    def _show_about_dialog(self):
        """Show about dialog on main thread"""
        if self.about_dialog is None or not self.about_dialog.isVisible():
            self.about_dialog = AboutDialog()
        self.about_dialog.show()
        self.about_dialog.raise_()
        self.about_dialog.activateWindow()
    
    def show_about(self):
        """Thread-safe method to show about dialog"""
        # Use QMetaObject.invokeMethod for thread safety
        QMetaObject.invokeMethod(self, "_show_about_dialog", Qt.QueuedConnection)

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
        """Thread-safe URL opening"""
        QTimer.singleShot(0, lambda: QDesktopServices.openUrl(QUrl(self.url)))

import sys
import webbrowser
from PySide6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QPixmap, QPainter, QIcon, QDesktopServices

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




class APIWorker(QThread):
    """Worker thread for API calls to prevent UI freezing"""
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, endpoint, method="GET", data=None):
        super().__init__()
        self.endpoint = endpoint
        self.method = method
        self.data = data
        self.base_url = "http://93.127.198.127:3006/"
        self._should_stop = False
    
    def stop(self):
        """Signal the thread to stop"""
        self._should_stop = True
    
    def run(self):
        try:
            if self._should_stop:
                return
                
            url = f"{self.base_url}{self.endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            if self._should_stop:
                return
            
            if self.method == "POST":
                response = requests.post(url, json=self.data, headers=headers, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            
            if self._should_stop:
                return
            
            # Check if response is successful
            if response.status_code != 200:
                if not self._should_stop:
                    error_text = response.json().get("error", "Unknown error")
                    self.error.emit(f"HTTP {response.status_code}: {error_text}")
                return
            
            # Check if response has content
            if not response.text.strip():
                if not self._should_stop:
                    self.error.emit("Server returned empty response")
                return
            
            # Try to parse JSON
            try:
                json_response = response.json()
                if not self._should_stop:
                    self.finished.emit(json_response)
            except json.JSONDecodeError as e:
                if not self._should_stop:
                    self.error.emit(f"Invalid JSON response: {str(e)}")
                
        except requests.exceptions.ConnectionError:
            if not self._should_stop:
                self.error.emit("Connection Error: Cannot connect to server.")
        except requests.exceptions.Timeout:
            if not self._should_stop:
                self.error.emit("Timeout Error: Request took too long to complete")
        except requests.exceptions.RequestException as e:
            if not self._should_stop:
                self.error.emit(f"Request Error: {str(e)}")
        except Exception as e:
            if not self._should_stop:
                self.error.emit(f"Unexpected error: {str(e)}")


class VerificationWorker(QThread):
    """Dedicated thread for complete verification pipeline"""
    step_started = Signal(str)  # Step description
    step_completed = Signal(str, dict)  # Step name, result data
    verification_completed = Signal(dict)  # Final validation data
    verification_failed = Signal(str, str)  # Step name, error message
    
    def __init__(self, serial_code, mac_address, device_info):
        super().__init__()
        self.serial_code = serial_code
        self.mac_address = mac_address
        self.device_info = device_info
        self.base_url = "http://93.127.198.127:3006/"
        self._should_stop = False
        self.validation_data = {}
    
    def stop(self):
        """Signal the thread to stop"""
        self._should_stop = True
    
    def run(self):
        """Run the complete verification pipeline"""
        try:
            # Step 1: Input Validation
            if self._should_stop:
                return
            
            self.step_started.emit("Validating input format...")
            if not self.validate_input():
                return
            self.step_completed.emit("Input Validation", {})
            
            # Small delay for UI feedback
            self.msleep(300)
            
            # Step 2: Status Check
            if self._should_stop:
                return
                
            self.step_started.emit("Checking code status...")
            if not self.check_code_status():
                return
            self.step_completed.emit("Status Check", {})
            
            # Small delay for UI feedback
            self.msleep(300)
            
            # Step 3: Server Validation
            if self._should_stop:
                return
                
            self.step_started.emit("Validating with server...")
            if not self.validate_with_server():
                return
            self.step_completed.emit("Server Validation", self.validation_data)
            
            # All steps completed successfully
            if not self._should_stop:
                self.verification_completed.emit(self.validation_data)
                
        except Exception as e:
            if not self._should_stop:
                self.verification_failed.emit("Pipeline Error", f"Unexpected error in verification pipeline: {str(e)}")
    
    def validate_input(self):
        """Step 1: Validate input format and prerequisites"""
        try:
            # Check MAC address
            if not self.mac_address:
                self.verification_failed.emit("Input Validation", "MAC address is required for device binding")
                return False
            
            # Validate serial code format
            if not self.serial_code or not self.is_valid_format(self.serial_code):
                self.verification_failed.emit("Input Validation", "Invalid serial code format. Use: XXXX-XXXX-XXXX-XXXX-XXXX")
                return False
            
            return True
            
        except Exception as e:
            self.verification_failed.emit("Input Validation", f"Input validation error: {str(e)}")
            return False
    
    def check_code_status(self):
        """Step 2: Check code status with server"""
        try:
            url = f"{self.base_url}/api/status/{self.serial_code}"
            headers = {'Content-Type': 'application/json'}

            response = requests.get(url, headers=headers, timeout=10)

            if self._should_stop:
                return False

            if response.status_code != 200:
                error_text = response.json().get("error", "Unknown error")
                self.verification_failed.emit("Status Check", f"HTTP {response.status_code}: {error_text}")
                return False

            # Check if response has content
            if not response.text.strip():
                self.verification_failed.emit("Status Check", "Server returned empty response")
                return False

            # Try to parse JSON
            try:
                json_response = response.json()
            except json.JSONDecodeError as e:
                self.verification_failed.emit("Status Check", f"Invalid JSON response: {str(e)}")
                return False

            if json_response.get('success'):
                data = json_response.get('data', {})
                status = data.get('status')
                device_binding = data.get('deviceBinding', {})

                if status == 'active':
                    # Check device binding
                    if device_binding.get('isBound') and device_binding.get('macAddress') != self.mac_address:
                        bound_mac = device_binding.get('macAddress', 'unknown')
                        error_msg = f"Code is bound to different device."
                        self.verification_failed.emit("Device Binding Check", error_msg)
                        return False

                    return True
                else:
                    error_msg = f"Code status: {status}"
                    if status == 'used':
                        error_msg += " (usage limit exceeded)"
                    elif status == 'expired':
                        error_msg += " (code has expired)"
                    elif status == 'revoked':
                        error_msg += " (code has been revoked)"

                    self.verification_failed.emit("Status Check", error_msg)
                    return False
            else:
                error = json_response.get('error', 'Unknown error')
                self.verification_failed.emit("Status Check", f"Status check failed: {error}")
                return False

        except requests.exceptions.ConnectionError:
            self.verification_failed.emit("Status Check", "Connection Error: Cannot connect to server.")
            return False
        except requests.exceptions.Timeout:
            self.verification_failed.emit("Status Check", "Timeout Error: Request took too long to complete")
            return False
        except Exception as e:
            self.verification_failed.emit("Status Check", f"Status check error: {str(e)}")
            return False

    
    def validate_with_server(self):
        """Step 3: Validate code with server"""
        try:
            url = f"{self.base_url}/api/validate"
            headers = {'Content-Type': 'application/json'}
            data = {
                "code": self.serial_code,
                "macAddress": self.mac_address,
                "userId": "Raushan",
                "deviceInfo": self.device_info
            }

            response = requests.post(url, json=data, headers=headers, timeout=10)

            if self._should_stop:
                return False

            if response.status_code != 200:
                error_text = response.json().get("error", "Unknown error")
                self.verification_failed.emit("Server Validation", f"HTTP {response.status_code}: {error_text}")
                return False

            # Check if response has content
            if not response.text.strip():
                self.verification_failed.emit("Server Validation", "Server returned empty response")
                return False

            # Try to parse JSON
            try:
                json_response = response.json()
            except json.JSONDecodeError as e:
                self.verification_failed.emit("Server Validation", f"Invalid JSON response: {str(e)}")
                return False

            if json_response.get('success'):
                data = json_response.get('data', {})

                # Store validation data
                self.validation_data = {
                    'token': data.get('token'),
                    'productName': data.get('productName', 'Unknown Product'),
                    'expiresAt': data.get('expiresAt', 'Unknown'),
                    'deviceBinding': data.get('deviceBinding', {}),
                    'response': json_response
                }

                return True
            else:
                error = json_response.get('error', 'Validation failed')
                self.verification_failed.emit("Server Validation", error)
                return False

        except requests.exceptions.ConnectionError:
            self.verification_failed.emit("Server Validation", "Connection Error: Cannot connect to server.")
            return False
        except requests.exceptions.Timeout:
            self.verification_failed.emit("Server Validation", "Timeout Error: Request took too long to complete")
            return False
        except Exception as e:
            self.verification_failed.emit("Server Validation", f"Server validation error: {str(e)}")
            return False
    
    def is_valid_format(self, code):
        """Check if serial code has valid format"""
        if len(code) != 24:  # 20 chars + 4 hyphens
            return False
        
        parts = code.split('-')
        if len(parts) != 5:
            return False
        
        for part in parts:
            if len(part) != 4:
                return False
            if not part.isalnum():
                return False
        
        return True


class SerialCodeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.session_token = None
        self.serial_code = None
        self.show_success_message = False
        self.code_validated = False
        self.user_setting_path = r"User_Data\user_setting.json"
        self.saved_serial_number = ""
        self.mac_address = None
        self.device_info = {}
        self.worker = None
        self.verification_worker = None
        
        # Verification pipeline state
        self.verification_callback = None
        self.validation_data = {}
        
        self.init_device_info()
        self.load_serial_code()
        self.init_ui()
        
    
    def closeEvent(self, event):
        """Handle application close event"""
        self.cleanup_workers()
        event.accept()
    
    def cleanup_workers(self):
        """Safely cleanup worker threads"""
        # Cleanup API worker
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.quit()
            if not self.worker.wait(3000):  # Wait up to 3 seconds
                self.worker.terminate()
                self.worker.wait()
            self.worker = None
        
        # Cleanup verification worker
        if self.verification_worker and self.verification_worker.isRunning():
            self.verification_worker.stop()
            self.verification_worker.quit()
            if not self.verification_worker.wait(3000):
                self.verification_worker.terminate()
                self.verification_worker.wait()
            self.verification_worker = None
    
    def init_device_info(self):
        """Initialize device information including MAC address"""
        self.mac_address = get_mac_address()
        
        # Collect device information
        self.device_info = {
            "deviceName": platform.node(),
            "platform": f"{platform.system()} {platform.release()}",
            "version": platform.version(),
            "processor": platform.processor() or platform.machine()
        }
        
        if not self.mac_address:
            self.show_error("MAC Address Detection Failed", 
                          "Unable to detect MAC address. This application requires MAC address for device binding.")
            
            # Show AboutDialog after error
            about_dialog = AboutDialog(self)
            about_dialog.exec()
    
    def init_ui(self):
        self.setWindowTitle("Serial Code Authentication")
        self.setFixedSize(400, 350)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Spacer
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Serial code input section
        code_frame = QFrame()
        code_frame.setObjectName("inputFrame")
        code_frame.setStyleSheet("""QFrame#inputFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.4);}""")
        
        
        code_layout = QVBoxLayout(code_frame)

        code_label = QLabel("Enter Serial Code:")
        code_label.setObjectName("inputLabel")
        code_layout.addWidget(code_label)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("XXXX-XXXX-XXXX-XXXX-XXXX")
        self.code_input.setObjectName("codeInput")
        self.code_input.setStyleSheet("""
            QLineEdit#codeInput {
                background-color: rgba(128,128,128,.3);          
                color: #eeeeee;                     
                border: 1px solid rgba(128,128,128,1);           
                border-radius: 8px;                 
                padding: 2px 2px 2px 10px;           
                selection-background-color: #555555;
            }
            QLineEdit#codeInput::placeholder {
                color: #888888;                    
            }
            QLineEdit#codeInput:focus {
                border: 1px solid rgba(128,128,128,1);      
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit#codeInput:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);         
            }
        """)
        self.code_input.textChanged.connect(self.format_serial_code)
        code_layout.addWidget(self.code_input)

        layout.addWidget(code_frame)

        # Buttons section
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)

        self.verify_button = AnimatedHoverButton("Verify Serial Code")
        self.verify_button.setObjectName("primaryButton")
        self.verify_button.clicked.connect(self.verify_serial_code)
        self.verify_button.setEnabled(bool(self.mac_address))
        button_layout.addWidget(self.verify_button)

        # New button for complete verification
        """         self.complete_verify_button = QPushButton("Complete Verification")
        self.complete_verify_button.setObjectName("secondaryButton")
        self.complete_verify_button.clicked.connect(self.run_complete_verification)
        self.complete_verify_button.setEnabled(bool(self.mac_address))
        button_layout.addWidget(self.complete_verify_button) """

        layout.addLayout(button_layout)

        # Load saved serial code if available
        if self.saved_serial_number:
            self.code_input.setText(self.saved_serial_number)

        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def run_complete_verification(self, callback_method=None,timer_callback=None,show_err_callback = None):
        """
        Run all verification methods in sequence using a dedicated thread.
        If all verifications pass, execute the callback_method.
        If any verification fails, show appropriate error message.
        
        Args:
            callback_method: Function to call if all verifications pass
        """
        # Check if already running
        if self.verification_worker and self.verification_worker.isRunning():
            return
        
        # Validate input first
        code = self.code_input.text().strip()
        if not code:
            """ self.show_error("Input Required", "Please enter a serial code") """
            show_err_callback.emit()
            return
        
        if not self.is_valid_format(code):
            """             self.show_error("Invalid Format", 
                          "Invalid serial code format. Use: XXXX-XXXX-XXXX-XXXX-XXXX")
             """
            show_err_callback.emit()
            return
        
        # Reset validation state before starting
        self.validation_data = {}
        self.session_token = None
        self.code_validated = False
        
        self.timer_callback = timer_callback
        # Set the callback method
        self.verification_callback = callback_method or self.default_success_callback
        
        # Update UI
        #self.complete_verify_button.setEnabled(False)
        #self.complete_verify_button.setText("Starting Verification...")
        
        # Cleanup any existing verification worker
        if self.verification_worker:
            self.verification_worker.stop()
            self.verification_worker.quit()
            self.verification_worker.wait()
        
        # Create and start verification worker
        self.verification_worker = VerificationWorker(code, self.mac_address, self.device_info)
        
        # Connect signals
        self.verification_worker.step_started.connect(self.on_verification_step_started)
        self.verification_worker.step_completed.connect(self.on_verification_step_completed)
        self.verification_worker.verification_completed.connect(self.on_all_verifications_complete)
        self.verification_worker.verification_failed.connect(self.on_verification_failed)
        
        # Start the verification
        self.verification_worker.start()
    
    def on_verification_step_started(self, description):
        """Handle verification step started"""
        #self.complete_verify_button.setText(description)
    
    def on_verification_step_completed(self, step_name, result_data):
        """Handle verification step completed"""
        #print(f"✅ {step_name} completed successfully")
    
    def on_all_verifications_complete(self, validation_data):
        """Handle successful completion of all verification steps"""
        try:
            # Store validation data
            self.validation_data = validation_data
            self.session_token = validation_data.get('token')
            self.code_validated = True
            self.serial_code = self.code_input.text().strip()

            # Update UI
            #self.complete_verify_button.setText("✅ All Verified")
            #self.complete_verify_button.setStyleSheet("background-color: #4CAF50;")

            # Save the serial code
            self.save_serial_code(self.serial_code)

            self.timer_callback()
            # Execute the callback ONLY if all verifications actually passed
            if self.verification_callback and callable(self.verification_callback):
                threading.Thread(
                    target=self.verification_callback,
                    daemon=True
                ).start()

            # Re-enable button after 2 seconds
            #QTimer.singleShot(2000, self.reset_complete_verify_button)

        except Exception as e:
            # If there's an error in completion, treat it as a failure
            self.on_verification_failed("Completion Error", f"Error completing verification: {str(e)}")
    
    def on_verification_failed(self, step_name, error_message):
        """Called when any verification step fails"""
        try:
            # Reset UI
            #self.reset_complete_verify_button()

            # Clear any validation data and tokens since verification failed
            self.validation_data = {}
            self.session_token = None
            self.code_validated = False

            # Always show error messages
            self.show_error(f"{step_name} Failed", error_message)

            # Show AboutDialog after error
            about_dialog = AboutDialog(self)
            about_dialog.exec()

        except Exception as e:
            print(f"Error in on_verification_failed: {e}")
    
    def reset_complete_verify_button(self):
        """Reset complete verification button state"""
        self.complete_verify_button.setEnabled(bool(self.mac_address))
        self.complete_verify_button.setText("Complete Verification")
        self.complete_verify_button.setStyleSheet("")
    
    def default_success_callback(self):
        """Default callback method when all verifications pass - no arguments"""
        try:
            # Access validation data from instance variable
            validation_data = getattr(self, 'validation_data', {})

            product_name = validation_data.get('productName', 'Unknown Product')
            expires_at = validation_data.get('expiresAt', 'Unknown')
            device_binding = validation_data.get('deviceBinding', {})

            success_msg = f"Complete verification successful!\n\n"
            success_msg += f"Product: {product_name}\n"
            success_msg += f"Expires: {expires_at}\n"
            #success_msg += f"Device MAC: {device_binding.get('macAddress', self.mac_address)}\n"
            success_msg += f"Session Token: {validation_data.get('token', 'N/A')[:20] if validation_data.get('token') else 'N/A'}...\n"

            if device_binding.get('isNewBinding'):
                success_msg += f"\nDevice bound successfully (new binding)"
            else:
                success_msg += f"\nDevice already bound (existing binding)"

            success_msg += f"\n\nAll systems verified and ready!"

            # Only show success message if show_success_message is True
            if self.show_success_message:
                self.show_success("Complete Verification Successful", success_msg)

            #print("🎉 All verifications passed! Ready to proceed with main application.")

        except Exception as e:
            #print(f"Error in default_success_callback: {e}")
            if self.show_success_message:
                self.show_error("Callback Error", f"Error in success callback: {str(e)}")

    def start_api_request(self, endpoint, method="GET", data=None, success_callback=None, error_callback=None):
        """Start a new API request, cleaning up any existing worker"""
        try:
            # Clean up existing worker
            if self.worker and self.worker.isRunning():
                self.worker.stop()
                self.worker.quit()
                if not self.worker.wait(3000):
                    self.worker.terminate()
                    self.worker.wait()
                self.worker = None
            
            # Create new worker
            self.worker = APIWorker(endpoint, method, data)
            
            # Connect signals
            if success_callback:
                self.worker.finished.connect(success_callback)
            if error_callback:
                self.worker.error.connect(error_callback)
            else:
                self.worker.error.connect(self.on_api_error)
            
            # Start the worker
            self.worker.start()
            
        except Exception as e:
            error_msg = f"Failed to start API request: {str(e)}"
            #print(error_msg)
            if error_callback:
                error_callback(error_msg)
            else:
                self.on_api_error(error_msg)
    
    def format_serial_code(self, text):
        """Format serial code input with hyphens"""
        # Remove all non-alphanumeric characters and convert to uppercase
        cleaned = ''.join(c.upper() for c in text if c.isalnum())
        
        # Add hyphens every 4 characters
        formatted = ''
        for i, char in enumerate(cleaned):
            if i > 0 and i % 4 == 0:
                formatted += '-'
            formatted += char
        
        # Limit to 24 characters (20 + 4 hyphens)
        if len(formatted) > 24:
            formatted = formatted[:24]
        
        # Update the input field if different
        if formatted != text:
            cursor_pos = self.code_input.cursorPosition()
            self.code_input.setText(formatted)
            # Adjust cursor position
            if cursor_pos < len(formatted):
                self.code_input.setCursorPosition(cursor_pos)
    
    def verify_serial_code(self):
        """Verify the entered serial code (original method)"""
        if not self.mac_address:
            self.show_error("MAC Address Required", 
                          "MAC address is required for device binding. Please restart the application.")
            return
            
        code = self.code_input.text().strip()
        
        if not code:
            self.show_error("Input Required", "Please enter a serial code")
            return
        
        if not self.is_valid_format(code):
            self.show_error("Invalid Format", 
                          "Invalid serial code format. Use: XXXX-XXXX-XXXX-XXXX-XXXX")
            return
        
        self.serial_code = code
        self.verify_button.setEnabled(False)
        self.verify_button.setText("Verifying...")
        
        # First check the status
        self.start_api_request(f"/api/status/{code}", "GET", None, 
                              self.on_status_check_complete)
    
    def on_status_check_complete(self, response):
        """Handle status check response (original method)"""
        if response.get('success'):
            data = response.get('data', {})
            status = data.get('status')
            device_binding = data.get('deviceBinding', {})

            if status == 'active':
                # Check if device is already bound to a different MAC
                if device_binding.get('isBound') and device_binding.get('macAddress') != self.mac_address:
                    bound_mac = device_binding.get('macAddress', 'unknown')
                    self.show_error("Device Binding Error", 
                                  f"This serial code is already bound to a different device.")

                    # Show AboutDialog after error
                    about_dialog = AboutDialog(self)
                    about_dialog.exec()

                    self.reset_verify_button()
                    return

                # Now validate the code
                self.validate_code()
            else:
                error_msg = f"Code status: {status}"
                if status == 'used':
                    error_msg += " (usage limit exceeded)"
                elif status == 'expired':
                    error_msg += " (code has expired)"
                elif status == 'revoked':
                    error_msg += " (code has been revoked)"

                self.show_error("Invalid Code", error_msg)

                # Show AboutDialog after error
                about_dialog = AboutDialog(self)
                about_dialog.exec()

                self.reset_verify_button()
        else:
            error = response.get('error', 'Unknown error')
            self.show_error("Status Check Failed", f"Status check failed: {error}")

            # Show AboutDialog after error
            about_dialog = AboutDialog(self)
            about_dialog.exec()

            self.reset_verify_button()
    
    def validate_code(self):
        """Validate and activate the serial code with MAC address (original method)"""
        data = {
            "code": self.serial_code,
            "macAddress": self.mac_address,
            "userId": "Raushan",
            "deviceInfo": self.device_info
        }
        
        self.start_api_request("/api/validate", "POST", data, 
                              self.on_validate_complete)
    
    def on_validate_complete(self, response):
        """Handle validation response (original method)"""
        if response.get('success'):
            data = response.get('data', {})
            self.session_token = data.get('token')
            product_name = data.get('productName', 'Unknown Product')
            expires_at = data.get('expiresAt', 'Unknown')
            device_binding = data.get('deviceBinding', {})

            self.code_validated = True

            success_msg = f"Serial code validated successfully!\n\n"
            success_msg += f"Product: {product_name}\n"
            success_msg += f"Expires: {expires_at}\n"
            

            if device_binding.get('isNewBinding'):
                success_msg += f"\nDevice bound successfully (new binding)"
            else:
                success_msg += f"\nDevice already bound (existing binding)"

            # Always show success message for normal verification
            self.show_success("Validation Successful", success_msg)
            self.verify_button.setText("✅ Verified")
            self.verify_button.setStyleSheet("background-color: #4CAF50;")
            self.save_serial_code(self.serial_code)

        else:
            error = response.get('error', 'Validation failed')

            # Handle specific device binding errors
            if "device already bound" in error.lower() or "different mac" in error.lower():
                self.show_error("Device Binding Error", 
                              f"Device binding failed:\n{error}\n\n")
            else:
                self.show_error("Validation Error", error)

            # Show AboutDialog after error
            about_dialog = AboutDialog(self)
            about_dialog.exec()

            self.reset_verify_button()
    
    def on_api_error(self, error):
        """Handle API errors"""
        # Always show error messages
        self.show_error("API Error", error)

        # Show AboutDialog after error
        about_dialog = AboutDialog(self)
        about_dialog.exec()

        self.reset_verify_button()
        #self.reset_complete_verify_button()
    
    def reset_verify_button(self):
        """Reset verify button state"""
        self.verify_button.setEnabled(bool(self.mac_address))
        self.verify_button.setText("Enter Serial Code")
        self.verify_button.setStyleSheet("")
    
    def is_valid_format(self, code):
        """Check if serial code has valid format"""
        if len(code) != 24:  # 20 chars + 4 hyphens
            return False
        
        parts = code.split('-')
        if len(parts) != 5:
            return False
        
        for part in parts:
            if len(part) != 4:
                return False
            if not part.isalnum():
                return False
        
        return True
    
    def show_error(self, title, message):
        """Show error message box"""
        QMessageBox.critical(self, title, message)
    
    def show_success(self, title, message):
        """Show success message box"""
        QMessageBox.information(self, title, message)

    def load_serial_code(self):
        """Load saved serial code from user settings"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.user_setting_path), exist_ok=True)

            # Check if file exists
            if os.path.exists(self.user_setting_path):
                with open(self.user_setting_path, mode='r', encoding="utf-8") as f:
                    data = json.load(f)
                self.saved_serial_number = data.get("saved_serial_number", "")
            else:
                # Create empty settings file
                self.save_serial_code("")

        except json.JSONDecodeError:
            self.save_serial_code("")
        except Exception as e:
            self.saved_serial_number = ""

    def save_serial_code(self, serial_code):
        """Save serial code to user settings"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.user_setting_path), exist_ok=True)

            # Load existing data or create new
            data = {}
            if os.path.exists(self.user_setting_path):
                try:
                    with open(self.user_setting_path, mode='r', encoding="utf-8") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, Exception):
                    data = {}

            # Update with new serial code and timestamp
            data["saved_serial_number"] = serial_code
            data["last_saved"] = datetime.datetime.now().isoformat() 
        
            # Save to file
            with open(self.user_setting_path, mode='w', encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.saved_serial_number = serial_code

        except Exception as e:
            self.show_error("Save Error", f"Failed to save serial code: {str(e)}")

    def clear_saved_serial_code(self):
        """Clear saved serial code"""
        self.save_serial_code("")
        self.code_input.clear()

    def custom_success_callback(self):
        """Example custom callback method - no arguments"""
        #print("🎉 Custom callback executed!")

        # Access validation data from instance variable
        validation_data = getattr(self, 'validation_data', {})
        #print(f"Token: {validation_data.get('token')}")
        #print(f"Product: {validation_data.get('productName')}")

        # Add your custom logic here
        # For example: open main window, start services, etc.

        # Only show success message if show_success_message is True
        if self.show_success_message:
            self.show_success("Custom Success", "All verifications passed! Custom callback executed.")

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

    
def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Serial Code Authentication")
    app.setApplicationVersion("1.0.0")
    
    window = SerialCodeApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()