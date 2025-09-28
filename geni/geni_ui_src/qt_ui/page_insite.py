from PySide6.QtWidgets import (
    QApplication, QFrame, QLabel, QScrollArea, QVBoxLayout, QHBoxLayout, 
    QPushButton, QWidget, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QSize, QThread, Slot
from PySide6.QtGui import QFont, QPixmap,QColor,QCursor
import json
import threading
import os

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
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setMaximumWidth(100)
        
        # Add widgets to layout
        content_layout.addWidget(image_label)
        content_layout.addWidget(info_label)
        content_layout.addWidget(close_btn, 0, Qt.AlignCenter)
        
        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)
        
        # Size the window appropriately
        self.resize_window_to_content()
        self.center_on_screen()
    
    def resize_window_to_content(self):
        """Size the window based on the image with reasonable constraints"""
        # Get screen size
        screen = QApplication.primaryScreen().availableGeometry()
        
        # Add margins for window frame and UI elements
        margin_w = 50
        margin_h = 100
        
        # Calculate window size
        width = min(self.pixmap.width() + margin_w, screen.width() * 0.9)
        height = min(self.pixmap.height() + margin_h, screen.height() * 0.9)
        
        # Ensure minimum window size
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
        self.toggle_button = QPushButton(f"► {title}")
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
        self.main_layout.addWidget(self.content_frame)  # Add the content frame to layout immediately
        
        # Initially hide content
        self.content_frame.setVisible(False)  # Use setVisible instead of hide

    
    def toggle(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.toggle_button.setText(f"▼ {self.toggle_button.text()[2:]}")
            self.content_frame.setVisible(True)  # Use setVisible instead of show
        else:
            self.toggle_button.setText(f"► {self.toggle_button.text()[2:]}")
            self.content_frame.setVisible(False)  # Use setVisible instead of hide
    
class ProfileInsite(QFrame):
    def __init__(self, parent=None, profile_name="None", followers=0, views=0, engagement=0, images=None, is_setup=False):
        super().__init__(parent)
        
        self.profile_name = profile_name
        self.followers = followers
        self.views = views
        self.engagement = engagement
        self.is_setup = "Yes" if is_setup else "No"
        self.images = images if images is not None else []
        
        # Set frame style
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
        self.setLineWidth(2)
        
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
            id_name = id_information.get("ID Name", "Unknown") + " " + "(ID)"
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
            page_info_dic = id_information.get("Page Infromation", {})
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


class AllPagesInsight(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        main_layout = QVBoxLayout(self)
        
        # Create scrollable area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Box)
        self.scroll_area.setLineWidth(3)
        
        # Content widget for the scroll area
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        
        # Add placeholder
        self.placeholder_label = QLabel("Please select a frame to view options")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.placeholder_label)
        
        # Set scroll content widget
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)
    
    def start_pull_data_thread(self, id_frame_idx=1):
        # Create a data loader thread
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


# Example usage:
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # Create main window
    window = QWidget()
    window.setWindowTitle("Profile Insights")
    layout = QVBoxLayout(window)
    
    # Add AllPagesInsight widget
    all_insights = AllPagesInsight()
    layout.addWidget(all_insights)
    
    # Optional: Add a button to load data
    load_button = QPushButton("Load Data")
    load_button.clicked.connect(lambda: all_insights.start_pull_data_thread(id_frame_idx=2))
    layout.addWidget(load_button)
    
    window.resize(800, 600)
    window.show()
    
    sys.exit(app.exec())