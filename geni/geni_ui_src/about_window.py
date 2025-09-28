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
                background: rgba(128,128,128,0.5);
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
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                background: rgba(128,128,128,0.8);
                border :1px solid rgba(255, 255, 255,.5);              
            }
        """)

        app_name.setAlignment(Qt.AlignCenter)
        
        
        # App description
        app_desc = QLabel("Your Ultimate Productivity Companion")
        app_desc.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                background: rgba(128,128,128,0.8);
                border :1px solid rgba(255, 255, 255,.5);              
            }
        """)
        app_desc.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(app_name)
   
        
        layout.addWidget(header_frame)
    
    def create_social_section(self, layout):
        social_frame = QFrame()
        social_frame.setStyleSheet("""
            QFrame {
                background: rgba(128,128,128,0.5);
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
                background: rgba(128,128,128,0.8);
                border :1px solid rgba(255, 255, 255,.5);              
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
                background: rgba(128,128,128,0.5);
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
                background: rgba(128,128,128,0.8);
                border :1px solid rgba(255, 255, 255,.5);              
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
                background:rgba(128,128,128,0.5);
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
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                background: rgba(128,128,128,0.8);
                border :1px solid rgba(255, 255, 255,.5);              
            }
        """)
        footer_text.setAlignment(Qt.AlignCenter)
        
        version_text = QLabel("Version 1.0.0")
        version_text.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                background: rgba(128,128,128,0.8);
                border :1px solid rgba(255, 255, 255,.5);              
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

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    dialog = AboutDialog()
    dialog.exec()

if __name__ == "__main__":
    main()