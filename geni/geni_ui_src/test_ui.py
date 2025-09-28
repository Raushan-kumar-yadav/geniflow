"""
geniflow_ui.py

Standalone UI-only version of your original code.
- All external backend imports removed (LDTaskExecutor, DeviceSettingsFlatten, etc.)
- Long-running / multiprocessing logic replaced with simple stubs / placeholders.
- Logging to files simplified.
- UI classes preserved (CurrentActivity table, ActivityControl panel, AnimatedHoverButton, SocialButton, AboutDialog, MainWindow).

Requires: PySide6
Run: python geniflow_ui.py
"""

import sys
import time
import threading
import queue
from pathlib import Path
from typing import Dict, Any

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QVBoxLayout, QHBoxLayout, QDialog,
    QPushButton, QLabel, QScrollArea, QGridLayout, QMessageBox, QListView, QTableView,
    QHeaderView, QAbstractItemView, QGroupBox
)
from PySide6.QtCore import Qt, QTimer, Signal, QSize, Slot, Property
from PySide6.QtGui import QPixmap, QFontDatabase, QIcon, QStandardItemModel, QStandardItem, QColor, QFont, QDesktopServices
from PySide6.QtCore import QUrl

# -----------------------
# UI Helpers & Classes
# -----------------------

class StyledFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(2)
        self.setStyleSheet("""
            StyledFrame {
                background-color: rgba(128,128,128,.06);
                border: 2px solid gray;
                border-radius: 8px;
            }
        """)

class CurrentActivity(StyledFrame):
    """UI-only current activity table. Backend queue replaced with local queue.Queue.
       Methods that previously referenced backend executors are stubbed/kept minimal.
    """
    HEADERS = ["LDName", "App", "Profile", "Current activity", "Others", "Last update"]

    def __init__(self, parent=None, log_dir="logs"):
        super().__init__(parent)

        # Create log directory (UI safe)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Model / Table
        self.model = QStandardItemModel(0, len(self.HEADERS), self)
        self.model.setHorizontalHeaderLabels(self.HEADERS)

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setStretchLastSection(True)

        lay = QVBoxLayout(self)
        lay.addWidget(self.table)

        # Simple queue for UI updates (was multiprocessing.Queue in original)
        self.queue = queue.Queue()
        self.row_for_no: Dict[str, int] = {}
        self.process_data: Dict[str, Dict[str, Any]] = {}
        self.finished_processes = set()

        # Timer to poll queue (UI thread)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._drain_queue)
        self.timer.start(50)

    def _drain_queue(self):
        """Drain a few items from the queue each tick to update UI."""
        processed = 0
        while processed < 200:
            try:
                data = self.queue.get_nowait()
            except queue.Empty:
                break
            processed += 1
            command = data[0]
            if command == "UPDATE":
                _, ldname, app, profile, current, others, ts = data
                self._apply_update(ldname, app, profile, current, others, ts)
            elif command == "DELETE":
                _, ldname = data
                self._delete_process(ldname)
            elif command == "FINISHED":
                _, ldname, app, profile, current, others, ts = data
                self.finished_processes.add(ldname)
                self._apply_update(ldname, app, profile, current, others, ts)
            elif command == "LOG":
                # just save to detail log for demo
                _, ldname, app, profile, current, others, ts, _ = data
                self._save_to_detail_log(ldname, app, profile, current, others, ts)

    def _apply_update(self, ldname, app, profile, current, others, ts):
        self.process_data[ldname] = {
            'ldname': ldname, 'app': app,
            'profile': profile, 'current': current,
            'others': others, 'timestamp': ts
        }

        # Insert or update row
        if ldname not in self.row_for_no:
            row = self.model.rowCount()
            self.model.insertRow(row)
            self.row_for_no[ldname] = row
        else:
            row = self.row_for_no[ldname]

        for column, text in enumerate((ldname, app, profile, current, others, ts)):
            item = self.model.item(row, column)
            if item is None:
                item = QStandardItem()
                item.setTextAlignment(Qt.AlignCenter)
                self.model.setItem(row, column, item)
            item.setText(str(text))

        self._apply_row_colors(row, current, ldname in self.finished_processes)

    def _delete_process(self, ldname):
        if ldname not in self.row_for_no:
            return
        row_to_delete = self.row_for_no[ldname]
        self.model.removeRow(row_to_delete)
        updated = {}
        for k, v in self.row_for_no.items():
            if k == ldname:
                continue
            if v > row_to_delete:
                updated[k] = v - 1
            else:
                updated[k] = v
        self.row_for_no = updated
        if ldname in self.process_data:
            del self.process_data[ldname]
        if ldname in self.finished_processes:
            self.finished_processes.remove(ldname)

    def _apply_row_colors(self, row, status, is_finished):
        # simplified color mapping
        try:
            status_l = status.lower() if isinstance(status, str) else ""
        except Exception:
            status_l = ""
        if is_finished or status_l in ["finished", "completed"]:
            color = QColor(27,86,253,128)
        elif status_l in ["error", "failed"]:
            color = QColor(255,200,200)
        elif status_l in ["starting", "initializing"]:
            color = QColor(200,255,200)
        else:
            color = QColor(240,240,240,30)

        for col in range(self.model.columnCount()):
            item = self.model.item(row, col)
            if item:
                item.setBackground(color)

    def _save_to_detail_log(self, ldname, app, profile, current, others, timestamp):
        try:
            path = self.log_dir / "detailed_activity.log"
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {ldname} | {app} | {profile} | {current} | {others}\n")
        except Exception as e:
            print("Error writing detailed log:", e)

    # Public helper methods (UI friendly)
    def add_process(self, device_name, app, profile, status, others=""):
        ts = time.strftime("%H:%M:%S")
        self.queue.put(("UPDATE", device_name, app, profile, status, others, ts))

    def mark_process_finished(self, device_name, app, profile, status, others=""):
        ts = time.strftime("%H:%M:%S")
        self.queue.put(("FINISHED", device_name, app, profile, status, others, ts))

    def delete_process_by_no(self, device_name):
        self.queue.put(("DELETE", device_name))

    def log_activity(self, device_name, app, profile, status, others="", log_type="s"):
        ts = time.strftime("%H:%M:%S")
        # log_type kept for compatibility; in UI-only it writes detail log
        self.queue.put(("LOG", device_name, app, profile, status, others, ts, log_type))

class AnimatedHoverButton(QPushButton):
    """QPushButton subclass with smooth color transition on hover."""
    def __init__(self, text="", btn_padding=3, parent=None):
        super().__init__(text, parent)
        self._hoverLevel = 0.0
        self.btn_padding = btn_padding
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)

        # animation property handled by QPropertyAnimation if needed in future
        self.update_style()
        self.setDefault(False)
        self.setAutoDefault(False)

    def update_style(self):
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
                color: white;
                font-weight: 600;
            }}
            QPushButton:pressed {{
                background-color: {pressed_style};
            }}
        """)

    def enterEvent(self, event):
        self._hoverLevel = 1.0
        self.update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hoverLevel = 0.0
        self.update_style()
        super().leaveEvent(event)

    def getHoverLevel(self):
        return self._hoverLevel

    def setHoverLevel(self, value):
        self._hoverLevel = value
        self.update_style()

    hoverLevel = Property(float, getHoverLevel, setHoverLevel)

class SocialButton(QPushButton):
    def __init__(self, text, url, icon_text="", parent=None):
        super().__init__(text, parent)
        self.url = url
        self.setMinimumHeight(50)
        self.setMinimumWidth(200)
        self.setCursor(Qt.PointingHandCursor)
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
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2C2C2C, stop:1 #1E1E1E);
                color: #FFFFFF;
            }
        """)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #3C3C3C; width: 12px; border-radius: 6px; }
            QScrollBar::handle:vertical { background: #5A9FD4; border-radius: 6px; min-height: 20px; }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(30)
        content_layout.setContentsMargins(40, 40, 40, 40)

        # Header
        self.create_header_section(content_layout)
        # Contact / Social
        self.create_contact_section(content_layout)
        self.create_social_section(content_layout)
        # Footer
        self.create_footer(content_layout)
        # Close button
        self.create_close_button(content_layout)

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

        app_name = QLabel("GeniFlow")
        app_name.setStyleSheet("color: #FFFFFF; font-size: 36px; font-weight: bold;")
        app_name.setAlignment(Qt.AlignCenter)

        app_desc = QLabel("Your Ultimate Productivity Companion")
        app_desc.setStyleSheet("color: #B0B0B0; font-size: 18px;")
        app_desc.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(app_name)
        header_layout.addWidget(app_desc)
        layout.addWidget(header_frame)

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
        contact_title.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold;")

        contact_buttons_layout = QVBoxLayout()
        contact_buttons_layout.setSpacing(15)

        contact_row1 = QHBoxLayout()
        whatsapp_btn = SocialButton("WhatsApp", "https://wa.me/919113161106", "💬")
        telegram_btn = SocialButton("Telegram", "https://t.me/geniflow", "✈️")
        contact_row1.addWidget(whatsapp_btn)
        contact_row1.addWidget(telegram_btn)

        contact_row2 = QHBoxLayout()
        website_btn = SocialButton("Visit Website", "https://geniflow.com", "🌐")
        email_btn = SocialButton("Email Us", "mailto:hello@geniflow.com", "📧")
        contact_row2.addWidget(website_btn)
        contact_row2.addWidget(email_btn)

        contact_buttons_layout.addLayout(contact_row1)
        contact_buttons_layout.addLayout(contact_row2)

        contact_layout.addWidget(contact_title)
        contact_layout.addLayout(contact_buttons_layout)
        layout.addWidget(contact_frame)

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
        social_title.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold;")

        buttons_layout = QVBoxLayout()
        row1 = QHBoxLayout()
        facebook_btn = SocialButton("Facebook", "https://facebook.com/geniflow", "📘")
        twitter_btn = SocialButton("Twitter", "https://twitter.com/geniflow", "🐦")
        row1.addWidget(facebook_btn)
        row1.addWidget(twitter_btn)

        row2 = QHBoxLayout()
        instagram_btn = SocialButton("Instagram", "https://instagram.com/geniflow", "📷")
        linkedin_btn = SocialButton("LinkedIn", "https://linkedin.com/company/geniflow", "💼")
        row2.addWidget(instagram_btn)
        row2.addWidget(linkedin_btn)

        row3 = QHBoxLayout()
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
        footer_text.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        footer_text.setAlignment(Qt.AlignCenter)

        version_text = QLabel("Version 1.0.0")
        version_text.setStyleSheet("color: #B0B0B0; font-size: 12px;")
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
        """)
        close_btn.clicked.connect(self.accept)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        close_layout.addStretch()
        layout.addLayout(close_layout)

class ActivityControl(StyledFrame):
    """UI-only activity control panel. Backend integrations replaced with stubs.
       Methods that previously launched tasks now call placeholders and update UI table for demo.
    """
    pause_signal = Signal()
    show_about_dialog_signal = Signal()

    def __init__(self, parent=None, main_win_ref=None, current_activity_ref: CurrentActivity = None):
        super().__init__(parent)
        self.state = "stopped"
        self.current_activity_type = "main"
        self.main_win_ref = main_win_ref
        self.current_activity_ref = current_activity_ref

        # icons - using placeholders (empty pixmap if not found)
        try:
            self.play_icon = QPixmap("geni/geni_ui_src/ui_assets/Icons/play.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except Exception:
            self.play_icon = QPixmap(80, 80)
        try:
            self.pause_icon = QPixmap("geni/geni_ui_src/ui_assets/Icons/stop.png").scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        except Exception:
            self.pause_icon = QPixmap(80, 80)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.setInterval(1000)

        self.elapsed_time = 0
        self.start_time = 0

        self.stop_event = threading.Event()

        # connect signals
        self.pause_signal.connect(self.handle_pause_from_thread)
        self.show_about_dialog_signal.connect(self.show_about_box)

        self._create_widgets()

    def _create_widgets(self):
        layout = QVBoxLayout(self)
        header = QLabel("Activity Controls")
        header.setStyleSheet("font-size: 12pt; font-weight: bold; background-color:none;")
        layout.addWidget(header, alignment=Qt.AlignLeft)

        play_pause_frame = QGroupBox()
        play_pause_frame.setTitle("Play/Pause Controls")
        play_pause_frame.setObjectName("play_pause_frame")
        play_pause_frame.setStyleSheet("""QGroupBox#play_pause_frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px; padding-top:5px; margin-top:10px;
                                    padding-right:10px; padding-left:10px; padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.06);}""")
        play_pause_layout = QHBoxLayout(play_pause_frame)

        play_btn_widget = QWidget()
        play_btn_layout = QHBoxLayout(play_btn_widget)

        self.activity_type_label = QLabel("Main Activity")
        self.activity_type_label.setStyleSheet("background-color:none; font-weight:bold;")
        self.activity_type_label.setFixedWidth(120)
        play_btn_layout.addWidget(self.activity_type_label)

        self.play_pause_button = AnimatedHoverButton(text="")
        self.play_pause_button.setIcon(QIcon(self.play_icon))
        self.play_pause_button.setIconSize(QSize(64, 64))
        self.play_pause_button.setFixedSize(100, 100)
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        play_btn_layout.addWidget(self.play_pause_button)
        play_pause_layout.addWidget(play_btn_widget)

        timer_widget = QWidget()
        timer_layout = QHBoxLayout(timer_widget)
        timer_label = QLabel("Elapsed Time:")
        timer_label.setFixedWidth(100)
        timer_layout.addWidget(timer_label)

        font_id = QFontDatabase.addApplicationFont("geni/geni_ui_src/ui_assets/Icons/fonts/Digital Dismay.otf") if Path("geni/geni_ui_src/ui_assets/Icons/fonts/Digital Dismay.otf").exists() else -1
        digital_font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"

        self.timer_display = QLabel("00:00:00")
        timer_font = QFont(digital_font_family, 30)
        self.timer_display.setFont(timer_font)
        self.timer_display.setStyleSheet("color: red;")
        timer_layout.addWidget(self.timer_display)

        play_pause_layout.addWidget(timer_widget)
        layout.addWidget(play_pause_frame)
        layout.setSpacing(15)

        # Quit section
        quit_frame = QGroupBox()
        quit_frame.setObjectName("quit_frame")
        quit_frame.setTitle("Quit All")
        quit_frame.setStyleSheet("""QGroupBox#quit_frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px; padding-top:5px; margin-top:10px; background-color: rgba(128,128,128,0.06);}""")
        quit_layout = QHBoxLayout(quit_frame)

        quit_btn_label = QLabel("Quit All:")
        quit_btn_label.setFixedWidth(80)
        quit_layout.addWidget(quit_btn_label)

        quit_button = AnimatedHoverButton(text="Quit All")
        quit_button.setFixedSize(100, 100)
        quit_button.clicked.connect(self.handle_quit)
        quit_layout.addWidget(quit_button)
        quit_layout.addStretch()
        layout.addWidget(quit_frame)

        # Logs group
        View_logs_details = QGroupBox()
        View_logs_details.setObjectName("Log_Frame")
        View_logs_details.setTitle("Log Frame")
        View_logs_details.setStyleSheet("""QGroupBox#Log_Frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px; padding-top:5px; margin-top:10px; background-color: rgba(128,128,128,0.06);}""")
        view_log_layout = QHBoxLayout(View_logs_details)

        view_activity_log_label = QLabel("View Activity Log:")
        view_activity_log_btn = AnimatedHoverButton("Show")
        view_activity_log_btn.setFixedSize(80, 70)
        view_activity_log_btn.clicked.connect(self.open_activities_log)

        view_log_layout.addWidget(view_activity_log_label)
        view_log_layout.addWidget(view_activity_log_btn)

        view_log_layout.addStretch()
        layout.addWidget(View_logs_details)
        layout.addStretch()

    def open_activities_log(self):
        # UI-only: show an about-like dialog that indicates this is a log viewer stub
        dlg = QDialog(self)
        dlg.setWindowTitle("Activity Log (UI Stub)")
        dlg.setModal(True)
        v = QVBoxLayout(dlg)
        v.addWidget(QLabel("This is a UI-only stub for the activity log."))
        btn = QPushButton("Close")
        btn.clicked.connect(dlg.accept)
        v.addWidget(btn)
        dlg.resize(400, 200)
        dlg.exec()

    def verify_serial_and_start_activity(self):
        # Stubbed serial verification for UI demo
        self.start_activity()

    def show_about_box(self):
        About = AboutDialog(self)
        About.exec()

    def handle_pause_from_thread(self):
        if self.state == "running":
            self.pause_timer()
            self.state = "paused"

    def set_activity_type(self, activity_type):
        if self.state != "stopped":
            QMessageBox.warning(self, "Warning!", f"Cannot change activity type while {self.state}. Please stop current activity first.")
            return
        self.current_activity_type = activity_type
        self.activity_type_label.setText("Main Activity" if activity_type == "main" else "Fetch Activity")

    def toggle_play_pause(self):
        if self.state == "stopped":
            self.stop_event.clear()
            if self.current_activity_type == "main":
                threading.Thread(target=self.verify_serial_and_start_activity, daemon=True).start()
            else:
                threading.Thread(target=self._start_fetch_activity_stub, daemon=True).start()
            self.start_timer()
            self.state = "running"
        elif self.state == "running":
            self.pause_timer()
            self.state = "paused"
        elif self.state == "paused":
            self.start_timer(resume=True)
            self.state = "running"

    def _start_fetch_activity_stub(self):
        # A simple stub that simulates generating some activity updates
        if self.current_activity_ref:
            for i in range(5):
                if self.stop_event.is_set():
                    break
                self.current_activity_ref.add_process(f"LD-{i}", "AppX", f"profile-{i}", "starting", "")
                time.sleep(0.5)
            # mark finished
            if self.current_activity_ref:
                self.current_activity_ref.mark_process_finished("LD-0", "AppX", "profile-0", "finished", "")

    def start_timer(self, resume=False):
        if not resume:
            self.start_time = time.time()
            self.elapsed_time = 0
        else:
            self.start_time = time.time() - self.elapsed_time
        self.play_pause_button.setIcon(QIcon(self.pause_icon))
        self.timer.start()

    def pause_timer(self):
        self.timer.stop()
        self.elapsed_time = time.time() - self.start_time
        self.play_pause_button.setIcon(QIcon(self.play_icon))

    @Slot()
    def update_timer(self):
        if self.state == "running":
            self.elapsed_time = time.time() - self.start_time
            formatted_time = time.strftime("%H:%M:%S", time.gmtime(self.elapsed_time))
            self.timer_display.setText(formatted_time)

    def handle_quit(self):
        if self.state == "stopped":
            QMessageBox.warning(self, "Warning!", "No active tasks. Please start the tool first.", QMessageBox.Ok)
            return
        reply = QMessageBox.warning(self, "Confirm Quit", "Are you sure you want to quit all processes?", QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if reply == QMessageBox.Ok:
            self.stop_event.set()
            self.reset_ui()

    def reset_ui(self):
        self.state = "stopped"
        self.elapsed_time = 0
        self.timer_display.setText("00:00:00")
        self.play_pause_button.setIcon(QIcon(self.play_icon))
        self.stop_event.clear()

# -----------------------
# Main Window
# -----------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Activity Control Application (UI-only)")
        self.resize(1000, 650)
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #222222; color: white; }
            QPushButton { background-color: #3a3a3a; color: white; border: 1px solid #555555; border-radius: 5px; padding: 5px; }
            QPushButton:hover { background-color: #4a4a4a; }
            QPushButton:pressed { background-color: #555555; }
            QLabel { color: white; }
            QScrollArea { border: none; }
        """)

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        current_activity_frame = CurrentActivity(log_dir="logs")
        activity_control_frame = ActivityControl(main_win_ref=self, current_activity_ref=current_activity_frame)

        # For demo: add a few example entries
        current_activity_frame.add_process("LD-Example-1", "ExampleApp", "Default", "starting", "none")
        current_activity_frame.add_process("LD-Example-2", "Downloader", "ProfileA", "initializing", "dl=2")

        main_layout.addWidget(current_activity_frame, 3)
        main_layout.addWidget(activity_control_frame, 1)

        self.setCentralWidget(central_widget)

# -----------------------
# Run UI
# -----------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
