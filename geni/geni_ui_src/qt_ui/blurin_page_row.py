from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFrame, QPushButton, QGraphicsOpacityEffect, QGraphicsBlurEffect
)
from PySide6.QtCore import Qt, QSize, Property, QPropertyAnimation, QEasingCurve, QThread, Signal, QObject, QParallelAnimationGroup
from PySide6.QtGui import QColor

class AnimatedHoverButton(QPushButton):
    """QPushButton subclass with smooth color transition on hover."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        # hoverLevel: 0.0 (normal) to 1.0 (hovered)
        self._hoverLevel = 0.0
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)
        # Animation setup
        self._anim = QPropertyAnimation(self, b"hoverLevel", self)
        self._anim.setDuration(200)  # 200 ms transition
        # Initial style
        self.update_style()

    def update_style(self):
        # interpolate alpha between 0.5 and 0.8 based on hoverLevel
        alpha = 0.5 + 0.3 * self._hoverLevel
        color = f"rgba(27,86,253,{alpha:.2f})"
        pressed_style = "rgba(27,86,253,1.0)"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 4px;
                padding: 6px;
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

class BlurSpawnFrame(QFrame):
    """Frame with blur-in spawn animation that properly handles nested effects"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Set background style
        self.setStyleSheet("background-color: rgba(128,128,128,0.2);")
        
        # We'll use a simpler approach - just one effect and animate opacity with stylesheet
        self._opacity = 0.0
        self._blurRadius = 15.0
        
        # Create blur effect
        self.blur_effect = QGraphicsBlurEffect(self)
        self.blur_effect.setBlurRadius(self._blurRadius)
        self.setGraphicsEffect(self.blur_effect)
        
        # Setup animations
        self.animation_group = QParallelAnimationGroup(self)
        
        self.blur_animation = QPropertyAnimation(self, b"blurRadius")
        self.blur_animation.setDuration(600)  # 600ms animation
        self.blur_animation.setStartValue(15.0)
        self.blur_animation.setEndValue(0.0)  # No blur at end
        self.blur_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(500)  # 500ms animation
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)  # Full opacity
        self.opacity_animation.setEasingCurve(QEasingCurve.InQuad)
        
        # Add animations to group
        self.animation_group.addAnimation(self.blur_animation)
        self.animation_group.addAnimation(self.opacity_animation)
        
        # Initial state - invisible
        self.setStyleSheet("background-color: rgba(128,128,128,0.2); opacity: 0;")
        
    def getBlurRadius(self):
        return self._blurRadius
        
    def setBlurRadius(self, value):
        self._blurRadius = value
        self.blur_effect.setBlurRadius(value)
        
    def getOpacity(self):
        return self._opacity
        
    def setOpacity(self, value):
        self._opacity = value
        # Apply opacity via stylesheet instead of another effect
        self.setStyleSheet(f"background-color: rgba(128,128,128,0.2); opacity: {value};")
        
    def start_animation(self):
        """Start the blur-in spawn animation"""
        self.animation_group.start()
        
    blurRadius = Property(float, getBlurRadius, setBlurRadius)
    opacity = Property(float, getOpacity, setOpacity)

class PageEntryWidget(QWidget):
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.page_widgets = []
        self.animation_objects = []  # Track animation objects to prevent garbage collection
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)

        frame1 = QFrame()
        frame1.setStyleSheet(
            "border: 2px solid #444; border-radius: 8px; background-color: rgba(128,128,128,0.2);"
        )
        frame1_layout = QVBoxLayout(frame1)

        # Header
        top_frame = QFrame()
        top_frame.setStyleSheet("border:none; background:none;")
        top_layout = QHBoxLayout(top_frame)
        index_label = QLabel(f"{self.index}.")
        index_label.setStyleSheet("font-weight:bold; font-size:14px; border:none; background:none;")
        top_layout.addWidget(index_label)
        title_label = QLabel("ID Information")
        title_label.setStyleSheet("font-weight:bold; font-size:14px; border:none; background:none;")
        top_layout.addWidget(title_label)
        top_layout.addStretch()
        frame1_layout.addWidget(top_frame)

        # ID Fields
        info_frame = QFrame()
        info_frame.setStyleSheet("border:none; background:none;")
        info_layout = QHBoxLayout(info_frame)
        for text in ("ID Name:", "Package Name:", "LD Name:"):
            info_layout.addWidget(QLabel(text))
            entry = QLineEdit()
            entry.setStyleSheet(
                "background-color:rgba(128,128,128,0.2); border:2px solid rgba(128,128,128,0.5);"
            )
            info_layout.addWidget(entry)
        frame1_layout.addWidget(info_frame)

        # Pages section
        page_info_label = QLabel("Page Information")
        page_info_label.setStyleSheet("font-weight:bold; font-size:12px; border:none; background:none;")
        frame1_layout.addWidget(page_info_label)

        pages_container = QFrame()
        pages_container.setStyleSheet("border:none; background:none;")
        pages_layout = QVBoxLayout(pages_container)
        self.page_entries_container = QVBoxLayout()
        pages_layout.addLayout(self.page_entries_container)

        # Add Page button using AnimatedHoverButton
        self.add_page_btn = AnimatedHoverButton("Add Page")
        self.add_page_btn.setMinimumSize(QSize(100, 40))
        self.add_page_btn.setMaximumSize(QSize(100, 40))
        self.add_page_btn.clicked.connect(self.add_page_entry)
        pages_layout.addWidget(self.add_page_btn)

        frame1_layout.addWidget(pages_container)
        self.main_layout.addWidget(frame1)

    def add_page_entry(self):
        # Create a container widget 
        content_widget = QWidget()
        
        # Create layout for content
        page_entry_hboxlayout = QHBoxLayout(content_widget)
        page_entry_hboxlayout.setSpacing(5)  
        page_entry_hboxlayout.setContentsMargins(5, 5, 5, 5) 

        page_idx = len(self.page_widgets) + 1  

        page_idx_label = QLabel(text=str(page_idx) + ".")
        page_idx_label.setStyleSheet("background-color:none;")
        page_entry_hboxlayout.addWidget(page_idx_label)
        
        page_text_label = QLabel(text="Page")
        page_text_label.setStyleSheet("background-color:none;")
        page_entry_hboxlayout.addWidget(page_text_label)
        
        entry = QLineEdit()
        entry.setFixedSize(QSize(300, 20))
        entry.setPlaceholderText("Enter page detail...")
        entry.setStyleSheet(
            "background-color:rgba(128,128,128,0.2); border:2px solid rgba(128,128,128,0.5);"
        )
        page_entry_hboxlayout.addWidget(entry)
        
        # Add stretch to keep content left-aligned
        page_entry_hboxlayout.addStretch()
        
        # Create blur spawn frame
        page_entry_main_frame = BlurSpawnFrame()
        frame_layout = QVBoxLayout(page_entry_main_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.addWidget(content_widget)

        # Add the frame to our layout
        self.page_widgets.append(page_entry_main_frame)
        self.page_entries_container.addWidget(page_entry_main_frame)
        
        # Keep a reference to avoid garbage collection of animations
        self.animation_objects.append(page_entry_main_frame.animation_group)
        
        # Start the animation after widget is added to layout
        page_entry_main_frame.start_animation()

    
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout(window)
    widget = PageEntryWidget(index=1)
    layout.addWidget(widget)
    window.setWindowTitle("PySide Page UI with Blur-in Spawn Animation")
    window.resize(800, 300)
    window.show()
    sys.exit(app.exec())