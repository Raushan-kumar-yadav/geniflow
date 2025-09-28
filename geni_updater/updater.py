import sys
import os
import json
import shutil
import tempfile
import zipfile
import threading
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import subprocess

from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                               QWidget, QLabel, QProgressBar, QPushButton, QTextEdit,
                               QMessageBox, QFrame)
from PySide6.QtCore import QTimer, Signal, QObject, QThread
from PySide6.QtGui import QFont, QIcon
from PySide6.QtCore import Qt


class UpdateChecker(QObject):
    """Background thread for checking updates"""
    update_available = Signal(dict)
    no_update = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, current_version, update_url):
        super().__init__()
        self.current_version = current_version
        self.update_url = update_url
    
    def check_for_updates(self):
        try:
            # Make request to your update server
            request = Request(self.update_url)
            request.add_header('User-Agent', 'AppUpdater/1.0')
            
            with urlopen(request, timeout=10) as response:
                update_info = json.loads(response.read().decode())
            
            latest_version = update_info.get('version', '0.0.0')
            
            if self._is_newer_version(latest_version, self.current_version):
                self.update_available.emit(update_info)
            else:
                self.no_update.emit()
                
        except (URLError, HTTPError, json.JSONDecodeError) as e:
            self.error_occurred.emit(f"Failed to check for updates: {str(e)}")
    
    def _is_newer_version(self, latest, current):
        """Compare version strings (assuming format like 1.2.3)"""
        latest_parts = [int(x) for x in latest.split('.')]
        current_parts = [int(x) for x in current.split('.')]
        
        # Pad shorter version with zeros
        max_len = max(len(latest_parts), len(current_parts))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        current_parts.extend([0] * (max_len - len(current_parts)))
        
        return latest_parts > current_parts


class Downloader(QObject):
    """Background thread for downloading updates"""
    progress_updated = Signal(int)
    download_finished = Signal(str)  # file path
    download_failed = Signal(str)
    
    def __init__(self, download_url, save_path):
        super().__init__()
        self.download_url = download_url
        self.save_path = save_path
        self.cancelled = False
    
    def download(self):
        try:
            request = Request(self.download_url)
            request.add_header('User-Agent', 'AppUpdater/1.0')
            
            with urlopen(request) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                downloaded = 0
                
                with open(self.save_path, 'wb') as f:
                    while True:
                        if self.cancelled:
                            return
                        
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_updated.emit(progress)
            
            self.download_finished.emit(self.save_path)
            
        except Exception as e:
            self.download_failed.emit(str(e))
    
    def cancel(self):
        self.cancelled = True


class AppUpdater(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuration - modify these for your app
        self.APP_NAME = "MyApplication"
        self.CURRENT_VERSION = "1.0.0"  # Get this from your app's version
        self.UPDATE_CHECK_URL = "https://yourserver.com/api/check-update"  # Your update endpoint
        self.APP_EXECUTABLE = "MyApplication.exe"  # Your main executable name
        
        # Get application directory
        if getattr(sys, 'frozen', False):
            self.app_dir = Path(sys.executable).parent
        else:
            self.app_dir = Path(__file__).parent
        
        self.temp_dir = None
        self.update_info = None
        
        self.init_ui()
        self.setup_threads()
        
        # Auto-check for updates on startup
        QTimer.singleShot(1000, self.check_for_updates)
    
    def init_ui(self):
        self.setWindowTitle(f"{self.APP_NAME} Updater")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel(f"{self.APP_NAME} Updater")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Version info
        version_frame = QFrame()
        version_frame.setFrameStyle(QFrame.Box)
        version_layout = QVBoxLayout(version_frame)
        
        self.current_version_label = QLabel(f"Current Version: {self.CURRENT_VERSION}")
        self.latest_version_label = QLabel("Latest Version: Checking...")
        
        version_layout.addWidget(self.current_version_label)
        version_layout.addWidget(self.latest_version_label)
        layout.addWidget(version_frame)
        
        # Status label
        self.status_label = QLabel("Checking for updates...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.check_button = QPushButton("Check for Updates")
        self.check_button.clicked.connect(self.check_for_updates)
        
        self.download_button = QPushButton("Download Update")
        self.download_button.setVisible(False)
        self.download_button.clicked.connect(self.download_update)
        
        self.install_button = QPushButton("Install Update")
        self.install_button.setVisible(False)
        self.install_button.clicked.connect(self.install_update)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        
        button_layout.addWidget(self.check_button)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.install_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Add some stretch
        layout.addStretch()
    
    def setup_threads(self):
        """Setup worker threads"""
        self.update_thread = QThread()
        self.download_thread = QThread()
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.append(f"[{QTimer().remainingTime()}] {message}")
    
    def check_for_updates(self):
        """Check for available updates"""
        self.status_label.setText("Checking for updates...")
        self.check_button.setEnabled(False)
        self.log_message("Starting update check...")
        
        # Create update checker
        self.update_checker = UpdateChecker(self.CURRENT_VERSION, self.UPDATE_CHECK_URL)
        self.update_checker.moveToThread(self.update_thread)
        
        # Connect signals
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.no_update.connect(self.on_no_update)
        self.update_checker.error_occurred.connect(self.on_update_error)
        
        # Start checking
        self.update_thread.started.connect(self.update_checker.check_for_updates)
        self.update_thread.start()
    
    def on_update_available(self, update_info):
        """Handle when update is available"""
        self.update_info = update_info
        version = update_info.get('version', 'Unknown')
        
        self.latest_version_label.setText(f"Latest Version: {version}")
        self.status_label.setText(f"Update available: v{version}")
        
        self.download_button.setVisible(True)
        self.check_button.setEnabled(True)
        
        self.log_message(f"Update available: v{version}")
        
        # Show changelog if available
        if 'changelog' in update_info:
            self.log_message("Changelog:")
            for change in update_info['changelog']:
                self.log_message(f"  - {change}")
        
        self.update_thread.quit()
    
    def on_no_update(self):
        """Handle when no update is available"""
        self.latest_version_label.setText(f"Latest Version: {self.CURRENT_VERSION}")
        self.status_label.setText("You have the latest version!")
        self.check_button.setEnabled(True)
        self.log_message("No updates available")
        self.update_thread.quit()
    
    def on_update_error(self, error_message):
        """Handle update check error"""
        self.status_label.setText("Failed to check for updates")
        self.check_button.setEnabled(True)
        self.log_message(f"Error: {error_message}")
        self.update_thread.quit()
        
        QMessageBox.warning(self, "Update Check Failed", 
                          f"Failed to check for updates:\n{error_message}")
    
    def download_update(self):
        """Download the update"""
        if not self.update_info:
            return
        
        download_url = self.update_info.get('download_url')
        if not download_url:
            QMessageBox.warning(self, "Error", "No download URL provided")
            return
        
        # Create temp directory
        self.temp_dir = tempfile.mkdtemp(prefix="app_update_")
        filename = f"update_{self.update_info['version']}.zip"
        save_path = os.path.join(self.temp_dir, filename)
        
        # Setup downloader
        self.downloader = Downloader(download_url, save_path)
        self.downloader.moveToThread(self.download_thread)
        
        # Connect signals
        self.downloader.progress_updated.connect(self.on_download_progress)
        self.downloader.download_finished.connect(self.on_download_finished)
        self.downloader.download_failed.connect(self.on_download_failed)
        
        # Start download
        self.download_thread.started.connect(self.downloader.download)
        
        self.status_label.setText("Downloading update...")
        self.progress_bar.setVisible(True)
        self.download_button.setEnabled(False)
        self.log_message("Starting download...")
        
        self.download_thread.start()
    
    def on_download_progress(self, progress):
        """Update download progress"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"Downloading... {progress}%")
    
    def on_download_finished(self, file_path):
        """Handle download completion"""
        self.download_thread.quit()
        self.progress_bar.setVisible(False)
        self.status_label.setText("Download completed!")
        self.install_button.setVisible(True)
        self.log_message(f"Download completed: {file_path}")
    
    def on_download_failed(self, error_message):
        """Handle download failure"""
        self.download_thread.quit()
        self.progress_bar.setVisible(False)
        self.status_label.setText("Download failed!")
        self.download_button.setEnabled(True)
        self.log_message(f"Download failed: {error_message}")
        
        QMessageBox.critical(self, "Download Failed", 
                           f"Failed to download update:\n{error_message}")
    
    def install_update(self):
        """Install the downloaded update"""
        if not self.temp_dir:
            return
        
        # Find the downloaded file
        update_file = None
        for file in os.listdir(self.temp_dir):
            if file.endswith('.zip'):
                update_file = os.path.join(self.temp_dir, file)
                break
        
        if not update_file or not os.path.exists(update_file):
            QMessageBox.critical(self, "Error", "Update file not found!")
            return
        
        # Confirm installation
        reply = QMessageBox.question(self, "Install Update", 
                                   "This will close the application and install the update. Continue?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply != QMessageBox.Yes:
            return
        
        try:
            self.log_message("Starting installation...")
            self.status_label.setText("Installing update...")
            
            # Create backup directory
            backup_dir = self.app_dir / "backup"
            backup_dir.mkdir(exist_ok=True)
            
            # Extract update
            extract_dir = os.path.join(self.temp_dir, "extracted")
            with zipfile.ZipFile(update_file, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Create update script
            self.create_update_script(extract_dir, backup_dir)
            
            self.log_message("Update script created. Application will restart...")
            
            # Close application and run update script
            QTimer.singleShot(2000, self.run_update_script)
            
        except Exception as e:
            QMessageBox.critical(self, "Installation Error", 
                               f"Failed to install update:\n{str(e)}")
            self.log_message(f"Installation error: {str(e)}")
    
    def create_update_script(self, extract_dir, backup_dir):
        """Create a batch script to handle the update process"""
        if sys.platform.startswith('win'):
            script_path = self.temp_dir / "update.bat"
            script_content = f'''@echo off
echo Waiting for application to close...
timeout /t 3 /nobreak > nul

echo Creating backup...
xcopy "{self.app_dir}" "{backup_dir}" /E /I /Y

echo Installing update...
xcopy "{extract_dir}" "{self.app_dir}" /E /I /Y

echo Cleaning up...
rmdir /s /q "{self.temp_dir}"

echo Starting application...
start "" "{self.app_dir / self.APP_EXECUTABLE}"

echo Update completed!
exit
'''
        else:
            script_path = self.temp_dir / "update.sh"
            script_content = f'''#!/bin/bash
echo "Waiting for application to close..."
sleep 3

echo "Creating backup..."
cp -r "{self.app_dir}" "{backup_dir}"

echo "Installing update..."
cp -r "{extract_dir}"/* "{self.app_dir}/"

echo "Setting permissions..."
chmod +x "{self.app_dir / self.APP_EXECUTABLE}"

echo "Cleaning up..."
rm -rf "{self.temp_dir}"

echo "Starting application..."
"{self.app_dir / self.APP_EXECUTABLE}" &

echo "Update completed!"
exit 0
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        if not sys.platform.startswith('win'):
            os.chmod(script_path, 0o755)
        
        self.update_script_path = script_path
    
    def run_update_script(self):
        """Execute the update script and close the application"""
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen([str(self.update_script_path)], shell=True)
            else:
                subprocess.Popen(['/bin/bash', str(self.update_script_path)])
            
            # Close the application
            QApplication.quit()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run update script:\n{str(e)}")
    
    def closeEvent(self, event):
        """Clean up on close"""
        if hasattr(self, 'update_thread') and self.update_thread.isRunning():
            self.update_thread.quit()
            self.update_thread.wait()
        
        if hasattr(self, 'download_thread') and self.download_thread.isRunning():
            if hasattr(self, 'downloader'):
                self.downloader.cancel()
            self.download_thread.quit()
            self.download_thread.wait()
        
        # Clean up temp directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("App Updater")
    app.setOrganizationName("Your Company")
    
    updater = AppUpdater()
    updater.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()