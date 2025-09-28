import sys
import re
from datetime import datetime, time
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                              QWidget, QTableWidget, QTableWidgetItem, 
                              QHeaderView, QPushButton, QTextEdit, QLabel,
                              QLineEdit, QCheckBox, QTimeEdit, QGroupBox)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QColor
from pathlib import Path


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
        title_label = QLabel("Log Activity Monitor")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Create filters section
        self.setup_filters(main_layout)
        
        # Create table
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
        
    def setup_filters(self, main_layout):
        """Setup the filter controls"""
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)
        
        # First row: Search and Error filter
        first_row = QHBoxLayout()
        
        # LD Name search
        search_label = QLabel("Search LD Name:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter LD name to search...")
        self.search_input.textChanged.connect(self.apply_filters)
        
        first_row.addWidget(search_label)
        first_row.addWidget(self.search_input)
        
        # Error filter checkbox
        self.error_filter = QCheckBox("Show only errors")
        self.error_filter.stateChanged.connect(self.apply_filters)
        first_row.addWidget(self.error_filter)
        
        # Clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        first_row.addWidget(clear_btn)
        
        first_row.addStretch()
        filter_layout.addLayout(first_row)
        
        # Second row: Time filters
        second_row = QHBoxLayout()
        
        # Time range filter
        time_label = QLabel("Time Range:")
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(0, 0, 0))
        self.start_time.setDisplayFormat("HH:mm:ss")
        self.start_time.timeChanged.connect(self.apply_filters)
        
        to_label = QLabel("to")
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(23, 59, 59))
        self.end_time.setDisplayFormat("HH:mm:ss")
        self.end_time.timeChanged.connect(self.apply_filters)
        
        # Enable/disable time filter
        self.time_filter_enabled = QCheckBox("Enable time filter")
        self.time_filter_enabled.stateChanged.connect(self.apply_filters)
        
        second_row.addWidget(time_label)
        second_row.addWidget(self.start_time)
        second_row.addWidget(to_label)
        second_row.addWidget(self.end_time)
        second_row.addWidget(self.time_filter_enabled)
        second_row.addStretch()
        
        filter_layout.addLayout(second_row)
        
        # Status label
        self.status_label = QLabel("Showing all entries")
        self.status_label.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        filter_layout.addWidget(self.status_label)
        
        main_layout.addWidget(filter_group)
        
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
    
    def apply_filters(self):
        """Apply all active filters to the data"""
        filtered = self.all_entries.copy()
        
        # Apply LD name search filter
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered = [entry for entry in filtered 
                       if search_text in entry['ldname'].lower()]
        
        # Apply error filter
        if self.error_filter.isChecked():
            filtered = [entry for entry in filtered if self.is_error_entry(entry)]
        
        # Apply time range filter
        if self.time_filter_enabled.isChecked():
            start_time = self.start_time.time().toPython()
            end_time = self.end_time.time().toPython()
            
            filtered = [entry for entry in filtered 
                       if entry['time_obj'] and start_time <= entry['time_obj'] <= end_time]
        
        self.filtered_entries = filtered
        self.populate_table_with_entries(self.filtered_entries)
        self.update_status_label()
    
    def clear_filters(self):
        """Clear all filters and show all data"""
        self.search_input.clear()
        self.error_filter.setChecked(False)
        self.time_filter_enabled.setChecked(False)
        self.start_time.setTime(QTime(0, 0, 0))
        self.end_time.setTime(QTime(23, 59, 59))
        
        self.filtered_entries = self.all_entries.copy()
        self.populate_table_with_entries(self.filtered_entries)
        self.update_status_label()
    
    def update_status_label(self):
        """Update the status label with current filter information"""
        total_entries = len(self.all_entries)
        filtered_entries = len(self.filtered_entries)
        error_entries = sum(1 for entry in self.filtered_entries if self.is_error_entry(entry))
        
        if filtered_entries == total_entries:
            status_text = f"Showing all {total_entries} entries ({error_entries} errors)"
        else:
            status_text = f"Showing {filtered_entries} of {total_entries} entries ({error_entries} errors)"
        
        self.status_label.setText(status_text)
        
        # Update window title
        self.setWindowTitle(f"Log Activity Monitor - {filtered_entries} entries ({error_entries} errors)")
    
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
                    item.setBackground(QColor(240, 240, 240))  # Light gray
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
        self.update_status_label()



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
                self.update_status_label()

        except FileNotFoundError:
            # If file doesn't exist, create it and show empty table
            self.log_file.touch()
            self.all_entries = []
            self.filtered_entries = []
            self.populate_table_with_entries([])
            self.update_status_label()
        except Exception as e:
            print(f"Error loading log file: {e}")
            self.all_entries = []
            self.filtered_entries = []
            self.populate_table_with_entries([])
            self.update_status_label()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = LogAnalyzer(log_dir=r"logs",log_type="fd")
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
