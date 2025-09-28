import sys 
from PySide6.QtWidgets import (QApplication,QWidget,QHBoxLayout,QVBoxLayout,QFrame,QLabel,QDialog,QPushButton,QGridLayout,QGroupBox,QScrollArea,QCheckBox,QSizePolicy,QLineEdit,QGraphicsOpacityEffect,QMessageBox,QComboBox,)
from PySide6.QtCore import (Qt,QTimer,QPointF,QTimerEvent,Signal,Property,QPropertyAnimation,QObject,QSize,QEasingCurve)
from PySide6.QtGui import (QMouseEvent,QWheelEvent,QPen,QFont,QColor,QPointerEvent,QPainter)
import json



class SelectableAnimatedFrame(QFrame):
    """A selectable frame with animation capabilities that emits a signal when selected"""
    frame_selected = Signal(int)  # Signal to emit when frame is selected
    
    def __init__(self, index, parent=None, bg_color="rgba(128,128,128,0.2)"):
        super().__init__(parent)
        self.index = index
        
        self.is_selected = False
        self.setStyleSheet(f"background-color:{str(bg_color)};border-radius:8px;")
        self.setCursor(Qt.PointingHandCursor)
        
        # Create opacity effect for animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)  # Start fully transparent
        self.setGraphicsEffect(self.opacity_effect)
        
        # Create animation for fade-in effect
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)  # 500ms animation
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)  # Full opacity
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Make sure mouse events are tracked for this widget
        self.setMouseTracking(True)
        
    def start_animation(self):
        """Start the fade-in animation"""
        self.animation.start()
        
    def getOpacity(self):
        return self.opacity_effect.opacity()
        
    def setOpacity(self, value):
        self.opacity_effect.setOpacity(value)
        
    opacity = Property(float, getOpacity, setOpacity)
        
    def mousePressEvent(self, event):
        """Handle mouse press events on the frame"""
        # Toggle selection state and emit signal
        self.setSelected(not self.is_selected)  
        super().mousePressEvent(event)
        
    def setSelected(self, selected):
        """Set the selection state of the frame"""
        if self.is_selected == selected:
            return 
            
        self.is_selected = selected
        
        # Update visual appearance
        if self.is_selected:
            self.setStyleSheet("background-color: rgba(200,200,200,0.2);border-radius:8px;")
        else:
            self.setStyleSheet("background-color: rgba(128,128,128,0.2);border-radius:8px;")
            
        # Emit signal with frame index
        self.frame_selected.emit(self.index if selected else -1)
        
    def enterEvent(self, event):
        """Handle mouse entering the frame area"""
        # Give a subtle highlight effect on hover if not already selected
        if not self.is_selected:
            self.setStyleSheet("background-color: rgba(200,200,200,0.1);border-radius:8px;")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leaving the frame area"""
        # Restore original style if not selected
        if not self.is_selected:
            self.setStyleSheet("background-color: rgba(128,128,128,0.2);border-radius:8px;")
        super().leaveEvent(event)

# Class to manage selection of frames
class FrameSelectionManager(QObject):
    def __init__(self):
        super().__init__()
        self.currently_selected_frame = None
        
    def set_selected_frame(self, frame):
        # Deselect previous frame if it exists
        if self.currently_selected_frame and self.currently_selected_frame != frame:
            try:
                # Check if the frame is still valid before calling setSelected
                if hasattr(self.currently_selected_frame, 'setSelected'):
                    self.currently_selected_frame.setSelected(False)
            except RuntimeError:
                # Object might have been deleted
                pass

        # Set new selected frame
        self.currently_selected_frame = frame

# Global selection manager
frame_selection_manager = FrameSelectionManager()


class MainScheduleTimeWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Set Schedule Timer")
        self.setObjectName("maintimerwidget")
        self.setStyleSheet("""QGroupBox#maintimerwidget{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.2);}
                                            QGroupBox#maintimerwidget::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        self.main_layout = QVBoxLayout(self)  
        self.schedule_list = []
        self.edit_mode = True  
        self.is_page_info_hidden = False
        self.schdule_widgets = []
        self.selectable_frames = []  
        self.animations = []
        self.init_ui()

    def init_ui(self):
        # Create a scroll area for schedule entries
        self.main_scrollable_area = QScrollArea()
        self.main_scrollable_area.setWidgetResizable(True)
        self.main_scrollable_area.setMinimumHeight(200)
        self.main_scrollable_area.setStyleSheet("background-color: transparent;")
        
        # Create container widget for the scroll area
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        
        # Create layout for schedule entries
        self.page_entries_container = QVBoxLayout(self.scroll_content)
        self.page_entries_container.setSpacing(8)
        self.page_entries_container.setContentsMargins(10, 10, 10, 10)
        self.page_entries_container.addStretch()
        
        # Set the widget with entries layout to the scroll area
        self.main_scrollable_area.setWidget(self.scroll_content)
        
        # Add "Add Time" button outside the scroll area
        self.button_container = QHBoxLayout()
        self.button_container.setContentsMargins(10, 5, 10, 5)
        
        self.enabel_schdule = QCheckBox("Enable Schedule") 
        self.button_container.addWidget(self.enabel_schdule)
        
        self.add_time_btn = AnimatedHoverButton("Add Time")
        self.add_time_btn.setFixedSize(QSize(100, 30))
        self.add_time_btn.clicked.connect(self.open_time_picker)
        self.button_container.addStretch()
        self.button_container.addWidget(self.add_time_btn)
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.main_scrollable_area)
        self.main_layout.addLayout(self.button_container)

    def open_time_picker(self):
        """Open the time picker dialog"""
        self.time_picker = TimerPickerWidget(self)
        self.time_picker.set_timer_btn.clicked.connect(self.on_time_selected)
        self.time_picker.cancel_btn.clicked.connect(self.time_picker.reject)
        self.time_picker.exec()
    
    def on_time_selected(self):
        """Handle user selecting a time in the time picker"""
        day = self.time_picker.dayWheel.value
        hour = self.time_picker.hourWheel.value
        minute = self.time_picker.minuteWheel.value
        ampm = self.time_picker.ampmWheel.value
        
        
        # Close the dialog
        self.time_picker.accept()
        
        # Create a schedule entry with the selected time
        self.add_schedule_entry(day=str(day), hour=f"{hour}", minute=f"{minute:02d}", ampm=ampm)
        
    def on_frame_selected(self, index):
        """Handle selection of the frame"""
        # Get the sender (the frame that was clicked)
        sender = self.sender()
        
        if index >= 0:

            frame_selection_manager.set_selected_frame(sender)
            
            # Additional logic for handling selection
            if hasattr(self, 'show_auto_upload_checkbox') and self.show_auto_upload_checkbox or hasattr(self, 'view_id_active_check_box') and self.view_id_active_check_box:
                if hasattr(self, 'insite_spawn_callback') and self.insite_spawn_callback is not None:
                    self.insite_spawn_callback.create_frame(id_frame_idx=sender.index, json_path=r"User_Data\Page_manager.json")
                    return index
            else:
                if hasattr(self, 'insite_spawn_callback') and self.insite_spawn_callback is not None:
                    self.insite_spawn_callback.start_pull_data_thread(id_frame_idx=sender.index)
                    return index
            return index
        else:
            return -1
            
    def add_schedule_entry(self, day=None, hour=None, minute=None, ampm=None):
        """Add a new schedule entry with animation"""
        # Grab the parent widget that holds our layout
        parent_widget = self.scroll_content
        
        # Create the main frame with animation and selection capability
        select_idx = len(self.schdule_widgets)
        schedule_entry_main_frame = SelectableAnimatedFrame(select_idx, parent_widget)
        
        # Set up layout and widgets
        schedule_layout = QHBoxLayout(schedule_entry_main_frame)
        schedule_layout.setSpacing(8)
        schedule_layout.setContentsMargins(5, 8, 5, 8)
        
        # Create inner content frame (non-selectable)
        content_frame = QFrame(parent=schedule_entry_main_frame)
        content_frame.setStyleSheet("background-color: transparent;")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        schedule_layout.addWidget(content_frame)
        
        # Add to the list of selectable frames
        self.selectable_frames.append(schedule_entry_main_frame)
        
        # Entry index
        entry_idx = len(self.schdule_widgets) + 1
        entry_idx_label = QLabel(f"{entry_idx}.", parent=content_frame)
        entry_idx_label.setStyleSheet("background-color:transparent;")
        content_layout.addWidget(entry_idx_label)
        
        # Day label and value
        day_text_label = QLabel("Day:", parent=content_frame)
        day_text_label.setStyleSheet("background-color:transparent;")
        content_layout.addWidget(day_text_label)
        
        # Use QLabel instead of QLineEdit
        day_value = QLabel(parent=content_frame)
        day_value.setMinimumHeight(24)
        day_value.setStyleSheet(
            "background-color:rgba(128,128,128,0.5);"
            "padding: 3px 8px;"
            "border-radius: 8px;"
        )
        if day is not None:
            day_value.setText(day)
        content_layout.addWidget(day_value)
        
        # Hour label and value
        hour_text_label = QLabel("Hour:", parent=content_frame)
        hour_text_label.setStyleSheet("background-color:transparent;")
        content_layout.addWidget(hour_text_label)
        
        # Use QLabel instead of QLineEdit
        hour_value = QLabel(parent=content_frame)
        hour_value.setMinimumHeight(24)
        hour_value.setStyleSheet(
            "background-color:rgba(128,128,128,0.5);"
            "padding: 3px 8px;"
            "border-radius: 8px;"
        )
        if hour is not None:
            hour_value.setText(hour)
        content_layout.addWidget(hour_value)
        
        # Minute label and value
        minute_text_label = QLabel("Minute:", parent=content_frame)
        minute_text_label.setStyleSheet("background-color:transparent;")
        content_layout.addWidget(minute_text_label)
        
        # Use QLabel instead of QLineEdit
        minute_value = QLabel(parent=content_frame)
        minute_value.setMinimumHeight(24)
        minute_value.setStyleSheet(
            "background-color:rgba(128,128,128,0.5);"
            "padding: 3px 8px;"
            "border-radius: 8px;"
        )
        if minute is not None:
            minute_value.setText(minute)
        content_layout.addWidget(minute_value)
        
        # AM/PM label and value
        if ampm is not None:
            ampm_text_label = QLabel("AM/PM:", parent=content_frame)
            ampm_text_label.setStyleSheet("background-color:transparent;")
            content_layout.addWidget(ampm_text_label)
            
            # Use QLabel instead of QLineEdit
            ampm_value = QLabel(parent=content_frame)
            ampm_value.setMinimumHeight(24)
            ampm_value.setStyleSheet(
                "background-color:rgba(128,128,128,0.5);"
                "padding: 3px 8px;"
                "border-radius: 8px;"
            )
            ampm_value.setText(ampm)
            content_layout.addWidget(ampm_value)
        
        # Add spacer to push content to the left
        content_layout.addStretch()
        
        # Add remove button
        remove_btn = AnimatedHoverButton("Remove", parent=schedule_entry_main_frame)
        remove_btn.setFixedSize(QSize(70, 24))
        remove_btn.clicked.connect(lambda: self.remove_schedule_entry(schedule_entry_main_frame))
        remove_btn.setVisible(self.edit_mode and not self.is_page_info_hidden)
        schedule_layout.addWidget(remove_btn)
        
        # Connect signal from selectable frame
        schedule_entry_main_frame.frame_selected.connect(self.on_frame_selected)
        
        # Add the new entry to the container
        # We need to add it before the stretch that's already in the layout
        self.page_entries_container.insertWidget(self.page_entries_container.count() - 1, schedule_entry_main_frame)
        
        # Add to tracking lists
        self.schdule_widgets.append(schedule_entry_main_frame)
        self.animations.append(schedule_entry_main_frame.animation)
        
        # Store references to components
        schedule_entry_main_frame.remove_btn = remove_btn
        schedule_entry_main_frame.day_value = day_value
        schedule_entry_main_frame.hour_value = hour_value
        schedule_entry_main_frame.minute_value = minute_value
        schedule_entry_main_frame.content_frame = content_frame  
        if ampm is not None:
            schedule_entry_main_frame.ampm_value = ampm_value
        
        # Start the animation
        schedule_entry_main_frame.start_animation()
        
        return schedule_entry_main_frame

    def remove_schedule_entry(self, schedule_widget):
        """Remove a page widget and renumber the remaining ones"""
        if schedule_widget in self.schdule_widgets:
            idx = self.schdule_widgets.index(schedule_widget)
            # Remember: UI shows index+1, but our list is zero-based
            ui_page_number = idx + 1  # Convert to 1-based for UI and JSON

            # Remove selectable frame from tracking list
            if schedule_widget in self.selectable_frames:
                self.selectable_frames.remove(schedule_widget)

            # Remove from layout and list
            self.page_entries_container.removeWidget(schedule_widget)
            self.schdule_widgets.remove(schedule_widget)

            # Delete widget with proper memory management
            if hasattr(schedule_widget, 'animation'):
                # Remove the animation from tracking list
                if schedule_widget.animation in self.animations:
                    self.animations.remove(schedule_widget.animation)

            schedule_widget.deleteLater()

            # Renumber remaining pages
            for i, page in enumerate(self.schdule_widgets):
                # Update the index for each selectable frame
                if isinstance(page, SelectableAnimatedFrame):
                    page.index = i
                
                # Find the index label (first child widget) and update its text
                labels = page.findChildren(QLabel)
                for label in labels:
                    if label.text().endswith('.'):
                        label.setText(f"{i+1}.")
                        break
                    
            # Use the UI page number (1-based) for JSON operations
            self.remove_schedule_entry_from_json(page_number=ui_page_number)
            self.remap_schedule_indices_in_json(deleted_page_number=ui_page_number)

            # Update the layout
            QApplication.processEvents()

    def update_edit_controls_visibility(self):
        """Update visibility of all edit controls based on edit mode"""
        # Check if page info is hidden - if so, don't show edit controls even in edit mode
        should_show_controls = self.edit_mode and not self.is_page_info_hidden
        
        # Update "Add Time" button visibility
        if hasattr(self, 'add_time_btn'):
            self.add_time_btn.setVisible(should_show_controls)
            self.button_container.setVisible(should_show_controls)
        
        # Update "Remove" buttons visibility for all schedule entries
        for page_widget in self.schdule_widgets:
            if hasattr(page_widget, 'remove_btn'):
                page_widget.remove_btn.setVisible(should_show_controls)
        
    def set_edit_mode(self, enabled):
        """Enable or disable edit mode"""
        self.edit_mode = enabled
        self.update_edit_controls_visibility()

    # For backward compatibility
    def remove_schedule_entry_from_json(self, page_number):
        pass
    
    def remap_schedule_indices_in_json(self, deleted_page_number):
        pass
    def load_data(self):
        page_manager_path = r"User_Data\Page_manager.json"

        #opening page_manager to load data 

        with open(page_manager_path,mode="r",encoding="utf-8") as f:
            data = json.load(f)

class WheelComponent(QWidget):
    valueChanged = Signal(int)
    
    def __init__(self, items, parent=None):
        super().__init__(parent)
        
        self.items = items
        self.currentIndex = 0
        self._value = 0
        self.itemHeight = 40
        self.visibleItems = 5
        self.offset = 0
        self.momentum = 0
        self.inertiaTimer = QTimer(self)
        self.inertiaTimer.setInterval(16)  
        self.inertiaTimer.timeout.connect(self.applyInertia)
        self.lastMouseY = 0
        
        self.setMinimumHeight(self.itemHeight * self.visibleItems)
        self.setMinimumWidth(100)
        
        # Properties for animation
        self._scrollPosition = 0
        
    def getValue(self):
        return self._value
        
    def setValue(self, value):
        if self._value != value:
            self._value = value
            self.valueChanged.emit(value)
            self.update()
    
    value = Property(int, getValue, setValue)


    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y()
        
        # scrolling speed and direction
        self.offset += delta / 8
        
        #  momentum based on the wheel delta
        self.momentum = delta / 12
        
        #  bounds
        maxOffset = 0
        minOffset = -((len(self.items) - 1) * self.itemHeight)
        
        if self.offset > maxOffset:
            self.offset = maxOffset
            self.momentum = 0
        elif self.offset < minOffset:
            self.offset = minOffset
            self.momentum = 0
        
        # current index and set the value
        self.currentIndex = int(round(-self.offset / self.itemHeight))
        self.currentIndex = max(0, min(self.currentIndex, len(self.items) - 1))
        self.setValue(self.items[self.currentIndex])
        
        # Start inertia timer
        if not self.inertiaTimer.isActive():
            self.inertiaTimer.start()
        
        self.update()
        event.accept()
    
    def applyInertia(self):
        # Apply deceleration
        self.momentum *= 0.95
        
        # Apply momentum to offset
        if abs(self.momentum) > 0.1:
            self.offset += self.momentum
            
            # Apply bounds
            maxOffset = 0
            minOffset = -((len(self.items) - 1) * self.itemHeight)
            
            if self.offset > maxOffset:
                self.offset = maxOffset
                self.momentum = 0
            elif self.offset < minOffset:
                self.offset = minOffset
                self.momentum = 0
            
            # Calculate the current index and set the value
            self.currentIndex = int(round(-self.offset / self.itemHeight))
            self.currentIndex = max(0, min(self.currentIndex, len(self.items) - 1))
            self.setValue(self.items[self.currentIndex])
            
            self.update()
        else:
            # Snap to nearest item position
            targetOffset = -self.currentIndex * self.itemHeight
            
            if abs(self.offset - targetOffset) > 0.5:
                self.offset = 0.8 * self.offset + 0.2 * targetOffset
                self.update()
            else:
                self.offset = targetOffset
                self.inertiaTimer.stop()
                self.update()
    
    def mousePressEvent(self, event):
        # Stop any ongoing inertia
        self.inertiaTimer.stop()
        self.lastMouseY = event.position().y()
        self.momentum = 0
        event.accept()
    
    def mouseMoveEvent(self, event):
        deltaY = event.position().y() - self.lastMouseY
        self.lastMouseY = event.position().y()
        
        # Update offset based on mouse movement
        self.offset += deltaY
        
        # Apply bounds
        maxOffset = 0
        minOffset = -((len(self.items) - 1) * self.itemHeight)
        
        if self.offset > maxOffset:
            self.offset = maxOffset
        elif self.offset < minOffset:
            self.offset = minOffset
        
        # Calculate momentum
        self.momentum = deltaY * 0.8
        
        # Calculate the current index and set the value
        self.currentIndex = int(round(-self.offset / self.itemHeight))
        self.currentIndex = max(0, min(self.currentIndex, len(self.items) - 1))
        self.setValue(self.items[self.currentIndex])
        
        self.update()
        event.accept()
    
    def mouseReleaseEvent(self, event):
        # Start inertia timer
        if abs(self.momentum) > 0.1:    
            self.inertiaTimer.start()
        else:
            # Snap to nearest item position
            self.offset = -self.currentIndex * self.itemHeight
            self.update()
        event.accept()
    
    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Calculate center item position
        centerY = height / 2
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor(55,70,85))
        
        # Draw highlight for selected item with transparency 
        painter.setPen(Qt.NoPen)
        highlightColor = QColor(210, 210, 210, 25) 
        painter.fillRect(0, centerY - self.itemHeight/2, width, self.itemHeight, highlightColor)
        
        # Draw items
        for i, item in enumerate(self.items):
            y = centerY + (i * self.itemHeight) + self.offset
            
            # Only draw visible items
            if y < -self.itemHeight or y > height + self.itemHeight:
                continue
            
            # Calculate distance from center for opacity and size
            distFromCenter = abs(y - centerY)
            opacity = 1.0 - min(distFromCenter / (self.visibleItems * self.itemHeight / 2), 0.8)
            fontScale = 1.0 - min(distFromCenter / (self.visibleItems * self.itemHeight / 2), 0.3)
            
            # Prepare font
            font = painter.font()
            fontSize = 16 * fontScale
            font.setPointSizeF(fontSize)
            painter.setFont(font)
            
            # Set color with opacity
            color = QColor(255, 255, 255)
            color.setAlphaF(opacity)
            painter.setPen(color)
            
            # Draw text
            text = str(item).zfill(2) if isinstance(item, int) else str(item)
            painter.drawText(0, int(y - self.itemHeight/2 + fontSize/2), width, self.itemHeight, 
                            Qt.AlignCenter, text)
        
        # Draw top and bottom divider lines
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawLine(0, centerY - self.itemHeight/2, width, centerY - self.itemHeight/2)
        painter.drawLine(0, centerY + self.itemHeight/2, width, centerY + self.itemHeight/2)

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        # Using QHBoxLayout with no margins for full width usage
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create a container for title that fills the space
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(10, 5, 0, 5)
        
        self.title = QLabel(self.parent.windowTitle())
        title_layout.addWidget(self.title)
        
        # Close button in its own container for proper positioning
        btn_container = QWidget()
        btn_container.setFixedHeight(30)
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 10, 0)
        
        btn_close = QPushButton("✕")
        btn_close.setFixedSize(20, 20)
        btn_close.clicked.connect(self.parent.reject)
        btn_layout.addWidget(btn_close)
        
        # Add widgets to main layout
        layout.addWidget(title_container, 1) 
        layout.addWidget(btn_container, 0)    
        
        self.setFixedHeight(30)  

    def mousePressEvent(self, event):
        self.old_pos = event.globalPosition()

    def mouseMoveEvent(self, event):
        delta = event.globalPosition() - self.old_pos
        self.parent.move(self.parent.x() + int(delta.x()), self.parent.y() + int(delta.y()))
        self.old_pos = event.globalPosition()


class TimerPickerWidget(QDialog):
    timeChanged = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Time")
        self.resize(400, 400)
        #self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        
        # Enable transparency for the window (needed for rounded corners)
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create a frame inside the dialog to hold the content
        self.frame = QFrame(self)
        self.frame.setObjectName("mainFrame")
        
        self.setStyleSheet("""
            /* Main frame holds the actual content with background */
            #mainFrame {
                background-color: #1B232A;
                border-radius: 15px;
            }
            
            QPushButton {
                border: none;
                background-color: transparent;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff6b6b;
                color: white;
                border-radius: 10px;
            }
        """)
        
        # Main layout for the dialog (transparent)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.addWidget(self.frame)
        
        # Layout for the frame (holds the actual content)
        main_layout = QVBoxLayout(self.frame)
        main_layout.setContentsMargins(0, 0, 0, 10)  
        
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Add a separator line
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: #cccccc;")
        main_layout.addWidget(separator)
        
        # Content area with increased margins
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 25, 20, 20)  
        content_layout.setSpacing(15)  

        main_layout.addLayout(content_layout)

        wheelContainer = QFrame()
        wheelContainer.setContentsMargins(10, 10, 10, 10)
        wheelContainer.setFrameShape(QFrame.StyledPanel)
        wheelContainer.setStyleSheet("""
            QFrame {
                background-color: #374655;
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255,.5);
            }
        """)
        
        # Time picker wheels layout
        wheelLayout = QGridLayout(wheelContainer)
        wheelLayout.setContentsMargins(15, 15, 15, 15)  
        
        #day label 
        day_label = QLabel(text="Day",alignment=Qt.AlignCenter)
        day_label.setObjectName("day_label")
        day_label.setStyleSheet("QLabel#day_label{background:rgba(115,125,136,.2);border:1px solid rgba(115,125,136,.8);border-radius:8px;}")
        # day wheel (12-hour format)
        day = list(range(0, 32))  # 1-31
        self.dayWheel = WheelComponent(day)
        self.dayWheel.setValue(00)  # Default to 12
        self.dayWheel.valueChanged.connect(self.onTimeChanged)
        
        #hour label
        hour_label = QLabel(text="Hour",alignment=Qt.AlignCenter)
        hour_label.setObjectName("hour_label")
        hour_label.setStyleSheet("QLabel#hour_label{background:rgba(115,125,136,.2);border:1px solid rgba(115,125,136,.8);border-radius:8px;}")
        # Hour wheel (12-hour format)
        hours = list(range(1, 13))  # 1-12
        self.hourWheel = WheelComponent(hours)
        self.hourWheel.setValue(1)  # Default to 12
        self.hourWheel.valueChanged.connect(self.onTimeChanged)
        
        #min_label 
        min_lable = QLabel(text="Minute",alignment=Qt.AlignCenter)
        min_lable.setObjectName("min_lable")
        min_lable.setStyleSheet("QLabel#min_lable{background:rgba(115,125,136,.2);border:1px solid rgba(115,125,136,.8);border-radius:8px;}")
        # Minute wheel
        minutes = list(range(0, 60))  # 0-59
        self.minuteWheel = WheelComponent(minutes)
        self.minuteWheel.valueChanged.connect(self.onTimeChanged)
        
        #AMPM label 
        ampm_label = QLabel(text="AM/PM",alignment=Qt.AlignCenter)
        ampm_label.setObjectName("ampm_label")
        ampm_label.setStyleSheet("QLabel#ampm_label{background:rgba(115,125,136,.2);border:1px solid rgba(115,125,136,.8);border-radius:8px;}")
        # AM/PM wheel
        ampm = ["AM", "PM"]
        self.ampmWheel = WheelComponent(ampm)
        self.ampmWheel.setValue("AM")
        self.ampmWheel.valueChanged.connect(self.onTimeChanged)
        

        #Add labels 
        wheelLayout.addWidget(day_label, 1,1)
        wheelLayout.addWidget(hour_label, 1,2)
        wheelLayout.addWidget(min_lable, 1,3)
        wheelLayout.addWidget(ampm_label, 1,4)

        # Add wheels to layout
        wheelLayout.addWidget(self.dayWheel, 2,1)
        wheelLayout.addWidget(self.hourWheel, 2,2)
        wheelLayout.addWidget(self.minuteWheel, 2,3)
        wheelLayout.addWidget(self.ampmWheel, 2,4)
        
        # Add wheelContainer to content_layout instead of main_layout
        content_layout.addWidget(wheelContainer)
        
        # Replace the button layout section with this:
        btn_layout = QHBoxLayout()

        # Add stretch before buttons to push them toward center
        btn_layout.addStretch(1)


        self.cancel_btn = AnimatedHoverButton(text="Cancel")
        self.cancel_btn.setFixedWidth(80)
        self.cancel_btn.setFixedHeight(30)
        btn_layout.addWidget(self.cancel_btn)

        # Set Time button
        self.set_timer_btn = AnimatedHoverButton(text="Set Time")
        self.set_timer_btn.setFixedWidth(80)
        self.set_timer_btn.setFixedHeight(30)
        btn_layout.addWidget(self.set_timer_btn)

        # Add stretch after buttons to push them toward center
        btn_layout.addStretch(1)

        content_layout.addLayout(btn_layout)
        
        # Initial time display update
        self.onTimeChanged()
    
    def onTimeChanged(self):
        day = self.dayWheel.value
        hour = self.hourWheel.value
        minute = self.minuteWheel.value
        ampm = self.ampmWheel.value
        
        # Format time string
        timeString = f"{day} - {hour}:{minute:02d} {ampm}"
        #self.timeDisplay.setText(f"Selected time: {timeString}")
        
        # Emit signal
        self.timeChanged.emit(hour, minute)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainScheduleTimeWidget()
    window.show()
    sys.exit(app.exec())