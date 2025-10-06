from ast import Delete
import sys
import re
from datetime import datetime, time
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                              QWidget, QTableWidget, QTableWidgetItem, 
                              QHeaderView, QPushButton, QTextEdit, QLabel,QMessageBox,
                              QLineEdit, QCheckBox, QTimeEdit, QGroupBox)
from PySide6.QtCore import Qt, QTime, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor
from pathlib import Path
import logging
import os


class LogAnalyzer(QMainWindow):
    def __init__(self, log_dir, log_type="activity"):
        super().__init__()


        self.setWindowTitle("Log Activity Monitor")
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)


        self.log_file = self.log_dir / "activity.log"


        # Log file paths
        if log_type == "activity":
            self.log_file = self.log_dir / "activity.log"
        else:
            self.log_file = self.log_dir / "detailed_activity.log"


        self.setGeometry(100, 100, 1400, 900)
        # Headers as specified
        self.headers = ["LDName", "App", "Profile", "Current activity", "Others", "Last update"]
        
        # Store all parsed entries for filtering
        self.all_entries = []
        self.filtered_entries = []
        
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Add title
        title_layout = QHBoxLayout()
        title_label = QLabel("Log Activity Monitor")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")

        self.Delete_button = QPushButton("Delete All Logs")
        self.Delete_button.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px; background-color: red; color: white; border-radius: 5px; padding: 5px;")
        self.Delete_button.clicked.connect(self.delete_log_file)     
        self.Delete_button.setFixedSize(150, 50)

    
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.Delete_button)
        main_layout.addLayout(title_layout)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)


        # Make table headers bold and adjust column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)  # Allow manual resizing
        header.setSectionResizeMode(len(self.headers)-1, QHeaderView.Stretch)  # Last column stretches
        self.table.setAlternatingRowColors(True)
        
        main_layout.addWidget(self.table)
        
        # Load sample data
        self.load_data()
        self.update_delete_button_visibility()

    def update_delete_button_visibility(self):
        """Update the visibility of the Delete button based on self.log_file contents."""
        has_log_data = False
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    has_log_data = bool(f.read().strip())  # True if file has non-empty content
            except Exception:
                has_log_data = False  # Hide button if file can't be read
        if hasattr(self, 'Delete_button'):  # Ensure button exists
            self.Delete_button.setVisible(has_log_data)
            
    def parse_log_line(self, line):
        """Parse a single log line and extract components"""
        # Pattern to match: [timestamp] ldname | app | profile | activity | others
        pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s+([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|\s*([^|]+)\s*\|\s*(.+)'
        
        match = re.match(pattern, line.strip())
        if match:
            timestamp, ldname, app, profile, activity, others = match.groups()
            
            # Clean up the extracted data
            ldname = ldname.strip()
            app = app.strip()
            profile = profile.strip() if profile.strip() else "N/A"
            activity = activity.strip()
            others = others.strip()
            
            return {
                'ldname': ldname,
                'app': app,
                'profile': profile,
                'activity': activity,
                'others': others,
                'timestamp': timestamp,
                'time_obj': self.parse_time(timestamp)
            }
        return None
    
    def parse_time(self, timestamp_str):
        """Parse timestamp string to time object"""
        try:
            return datetime.strptime(timestamp_str, "%H:%M:%S").time()
        except ValueError:
            return None
    
    def is_error_entry(self, entry):
        """Check if the entry contains error information"""
        if not entry:
            return False
            
        # Check for error keywords in others field and activity
        error_keywords = ['error', 'Error', 'Errors', 'ERROR', 'failed', 'Failed']
        
        others_text = entry.get('others', '').lower()
        activity_text = entry.get('activity', '').lower()
        
        for keyword in error_keywords:
            if keyword.lower() in others_text or keyword.lower() in activity_text:
                return True
                
        return False
    
    def populate_table_with_entries(self, entries):
        """Populate the table with given entries"""
        # Set table row count
        self.table.setRowCount(len(entries))
        
        # Populate table
        for row, entry in enumerate(entries):
            # Create table items
            items = [
                QTableWidgetItem(entry['ldname']),
                QTableWidgetItem(entry['app']),
                QTableWidgetItem(entry['profile']),
                QTableWidgetItem(entry['activity']),
                QTableWidgetItem(entry['others']),
                QTableWidgetItem(entry['timestamp'])
            ]
            
            # Check if this is an error entry
            is_error = self.is_error_entry(entry)
            
            # Add items to table and set colors
            for col, item in enumerate(items):
                if is_error:
                    # Red background for error entries
                    item.setBackground(QColor(255, 200, 200))  # Light red
                    item.setForeground(QColor(139, 0, 0))      # Dark red text
                else:
                    # Gray background for normal entries
                    item.setBackground(QColor(59, 124, 237))  # Light gray
                    item.setForeground(QColor(0, 0, 0))        # Black text
                
                # Make text selectable but not editable
                item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                
                self.table.setItem(row, col, item)
        
        # Adjust column widths
        self.table.resizeColumnsToContents()
    
    def populate_table(self, log_data):
        """Populate the table with parsed log data"""
        lines = log_data.strip().split('\n')
        valid_entries = []


        # Parse all lines
        for line in lines:
            if line.strip():
                entry = self.parse_log_line(line)
                if entry:
                    valid_entries.append(entry)


        # Sort by LD name 
        valid_entries.sort(key=lambda entry: entry['ldname'])


        # Store all entries (now sorted)
        self.all_entries = valid_entries
        self.filtered_entries = valid_entries.copy()


        # Populate table with sorted entries
        self.populate_table_with_entries(self.filtered_entries)


    def load_data(self):
        """Load the sample data provided"""
        try:
            with open(file=self.log_file, mode='r', encoding='utf-8') as f:
                data = f.read()


            if data.strip():
                self.populate_table(data)  # This will now sort before populating
            else:
                # If file is empty, show empty table
                self.all_entries = []
                self.filtered_entries = []
                self.populate_table_with_entries([])


        except FileNotFoundError:
            # If file doesn't exist, create it and show empty table
            self.log_file.touch()
            self.all_entries = []
            self.filtered_entries = []
            self.populate_table_with_entries([])
        except Exception as e:
            print(f"Error loading log file: {e}")
            self.all_entries = []
            self.filtered_entries = []
            self.populate_table_with_entries([])
    
    def delete_log_file(self):
        """Clear all data in the specific log file with user confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Clearing",
            f"Are you sure you want to clear the log file '{self.log_file.name}'? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            logging.info("Clear log file cancelled by user")
            return

        try:
            if self.log_file.exists():
                with open(self.log_file, 'w') as f:
                    f.truncate(0)  # Clear the file contents
                logging.info(f"Cleared data in log file: {self.log_file}")
                QMessageBox.information(self, "Success", f"The log file '{self.log_file.name}' has been cleared.", QMessageBox.Ok)
                # Clear the table and reset entries after clearing
                self.all_entries = []
                self.filtered_entries = []
                self.table.setRowCount(0)
                self.update_delete_button_visibility()
            else:
                QMessageBox.warning(self, "No Clearing", f"No log file found at '{self.log_file}' to clear.", QMessageBox.Ok)
        except PermissionError as e:
            logging.error(f"Failed to clear {self.log_file}: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to clear {self.log_file.name}: {str(e)}", QMessageBox.Ok)
        except Exception as e:
            logging.error(f"Failed to clear logs: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to clear logs: {str(e)}", QMessageBox.Ok)



def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = LogAnalyzer(log_dir=r"logs",log_type="fd")
    window.show()
    
    sys.exit(app.exec())



if __name__ == "__main__":
    main()
