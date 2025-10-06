from re import X
import sys

import webbrowser
from PySide6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea)
from PySide6.QtCore import Qt, QUrl, QSize
from PySide6.QtGui import QFont, QPixmap, QPainter, QIcon, QDesktopServices

class SocialButton(QPushButton):
    def __init__(self, text, url, icon_path, parent=None):
        super().__init__("", parent)  # no text, only icon
        self.url = url
        self.setCursor(Qt.PointingHandCursor)

        # Use icon if provided
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setText(text)
            self.setFixedSize(200,50)
            self.setIconSize(QSize(32, 32))  # adjust size as needed
            self.setToolTip(text)  # show platform name on hover
        
        # Dark mode button styling
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #3A5998, stop:1 #2D4373);
                    color: #FFFFFF;
                    border: 1px solid #404040;
                    border-radius: 12px;
                    font-family: 'Segoe UI';
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px, 10px;
                    padding-left: 30px;           
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
        
  
        self.clicked.connect(self.open_link)
    
    def open_link(self):
        QDesktopServices.openUrl(QUrl(self.url))

class SquareSocialButton(QPushButton):
    def __init__(self,iconpath, url, parent=None):
        super().__init__("", parent)  # no text, only icon
        self.url = url
        self.setCursor(Qt.PointingHandCursor)

        # Use icon if provided
        if iconpath:
            self.setIcon(QIcon(iconpath))
            self.setFixedSize(70, 70)  # width=50, height=50
            self.setIconSize(QSize(30, 30))  # adjust size as needed
        
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
                text-align: Center;
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

        self.clicked.connect(self.open_link)

    def open_link(self):
        QDesktopServices.openUrl(QUrl(self.url))
        


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeniFlow - About")
        self.setModal(True)
        self.setFixedSize(650, 800)
        
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
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignCenter)

        
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
                background: rgba(128,128,128,0.3);
                border-radius: 10px;
                border: 1px solid #555555;
                padding: 0px 10px 0px 10px;
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
                font-size: 40px;
                font-weight: bold;
                margin-bottom: 10px;
                background: rgba(128,128,128,0.4);
                border :1px solid rgba(255, 255, 255,.5);              
            }
        """)

        app_name.setAlignment(Qt.AlignCenter)
        
        
        # App description
        app_desc = QLabel("Your Ultimate Productivity Companion",font=QFont("Segoe UI", 16))
        app_desc.setStyleSheet("""
            QLabel {
            
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
              
                padding-right: 5px;
                padding-left: 5px;
                padding-top: 5px;
                padding-bottom: 5px;
                               
                                            
                                
                background: rgba(128,128,128,0.4);
                border :0px solid rgba(255, 255, 255,.5);              
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
                background: rgba(128,128,128,0.3);
                border-radius: 10px;
                border: 1px solid #555555;
            }
        """)
        
        social_layout = QVBoxLayout(social_frame)
        social_layout.setContentsMargins(30, 30, 30, 30)
        
        social_title = QLabel("Connect With Us",font=QFont("Segoe UI", 16))
        social_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 30px;
                font-weight: bold;
                margin-bottom: 10px;
                background: rgba(128,128,128,0.4);
                border :1px solid rgba(255, 255, 255,.5);              
            }
        """)
        social_title.setAlignment(Qt.AlignCenter)
        # Social media buttons grid
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Row 1
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        

            # Social media buttons
        
        self.FbIcon=r"geni\geni_ui_src\ui_assets\Icons\facebook.svg"
        self.XIcon=r"geni\geni_ui_src\ui_assets\Icons\x.svg"
        self.instagramIcon=r"geni\geni_ui_src\ui_assets\Icons\instagram.svg"
        self.linkedinIcon=r"geni\geni_ui_src\ui_assets\Icons\Linkdin.svg"
        self.youtubeIcon=r"geni\geni_ui_src\ui_assets\Icons\youtube.svg"
        self.githubIcon=r"geni\geni_ui_src\ui_assets\Icons\github.svg"
        
        
        
        facebook_btn = SquareSocialButton(self.FbIcon,"https://facebook.com/geniflow")
        
        x_btn = SquareSocialButton(self.XIcon,"https://x.com/GeniFlow_ai")        
        instagram_btn = SquareSocialButton(self.instagramIcon, "https://www.instagram.com/geniflow_official")
        linkedin_btn = SquareSocialButton(self.linkedinIcon, "https://www.linkedin.com/in/geni-flow-718941369/")
        youtube_btn = SquareSocialButton(self.youtubeIcon, "https://youtube.com/@geniflow")
        github_btn = SquareSocialButton(self.githubIcon, "https://github.com/geniflow")
        
        row1.addWidget(facebook_btn)
        row1.addWidget(x_btn)
        row1.addWidget(instagram_btn)
        row1.addWidget(linkedin_btn)
        row1.addWidget(youtube_btn)
        row1.addWidget(github_btn)
        
        buttons_layout.addLayout(row1)
        
        
        social_layout.addWidget(social_title)
        social_layout.addLayout(buttons_layout)
        
        layout.addWidget(social_frame)
    
    def create_contact_section(self, layout):
        contact_frame = QFrame()
        contact_frame.setStyleSheet("""
            QFrame {
                background: rgba(128,128,128,0.3);
                border-radius: 10px;
                border: 1px solid #555555;
            }
        """)
        
        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setContentsMargins(30, 30, 30, 30)
        
        contact_title = QLabel("Get In Touch",font=QFont("Segoe UI", 16))
        contact_title.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 30px;
                font-weight: bold;
                margin-bottom: 20px;             
                background: rgba(128,128,128,0.4);
                border :1px solid rgba(255, 255, 255,.5);              
            }
        """)
        contact_title.setAlignment(Qt.AlignCenter)
        
        # Contact buttons
        contact_buttons_layout = QVBoxLayout()
        contact_buttons_layout.setSpacing(15)
        
        # Row 1
        contact_row1 = QHBoxLayout()
        contact_row1.setSpacing(15)


        self.WhatsappIcon=r"geni\geni_ui_src\ui_assets\Icons\whatsapp.svg"
        self.TelegramIcon=r"geni\geni_ui_src\ui_assets\Icons\telegram.svg"
        self.WebsiteIcon=r"geni\geni_ui_src\ui_assets\Icons\website.svg"
        self.EmailIcon=r"geni\geni_ui_src\ui_assets\Icons\gmail.svg"
        
        whatsapp_btn = SocialButton("WhatsApp", "https://wa.me/919113161106",self.WhatsappIcon)
        telegram_btn = SocialButton("Telegram", "https://t.me/geniflow", self.TelegramIcon)
        
        contact_row1.addWidget(whatsapp_btn)
        contact_row1.addWidget(telegram_btn)
        
        # Row 2
        contact_row2 = QHBoxLayout()
        contact_row2.setSpacing(15)
        
        website_btn = SocialButton("Visit Website", "http://geniflow.in/", self.WebsiteIcon)
        email_btn = SocialButton("Email Us", "mailto:hello@geniflow.com", self.EmailIcon)
        
        contact_row2.addWidget(website_btn)
        contact_row2.addWidget(email_btn)
        
        contact_buttons_layout.addLayout(contact_row1)
        contact_buttons_layout.addLayout(contact_row2)
        
        contact_layout.addWidget(contact_title)
        contact_layout.addLayout(contact_buttons_layout)
        
        layout.addWidget(contact_frame)
        layout.setAlignment(Qt.AlignCenter)
    
    def create_footer(self, layout):
        footer_frame = QFrame()
        footer_frame.setStyleSheet("""
            QFrame {
                background:rgba(128,128,128,0.3);
                border-radius: 10px;
                
                padding: 10px;
                border: 1px solid #444444;
            }
        """)
        # footer_frame.setFixedSize(600, 200)  # width=600, height=100

        
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setAlignment(Qt.AlignCenter)
        
        footer_text = QLabel("© 2024 GeniFlow. All rights reserved.")
        footer_text.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
                background: rgba(128,128,128,0.3);
                border :0px solid rgba(255, 255, 255,.5);              
            }
        """)
        footer_text.setAlignment(Qt.AlignCenter)
        
        version_text = QLabel("Beta Version 1.0.11")
        version_text.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: semi-bold;
                margin-bottom: 10px;
                background: rgba(128,128,128,0.3);
                border :px solid rgba(255, 255, 255,.5);              
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

        close_layout.addWidget(close_btn)

        
        layout.addLayout(close_layout)

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setApplicationName("About | Team GeniFlow | Support")
    app.setStyle('Fusion')
    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 14px;
            color: #FFFFFF;
        }
    """)
    
    
    dialog = AboutDialog()
    # dialog.setFixedSize(650, 800) 
    dialog.exec()
if __name__ == "__main__":
    main()
    