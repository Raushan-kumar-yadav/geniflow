from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QFrame, QPushButton, QGraphicsOpacityEffect, QSizePolicy, QScrollArea,
    QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, QSize, Property, QPropertyAnimation, QEasingCurve, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QColor

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
                border-radius: 4px;
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

class AnimatedFrame(QFrame):
    """Frame with opacity animation capability that affects all child widgets"""
    def __init__(self,bg_color="rgba(128,128,128,0.2)", parent=None):
        super().__init__(parent)
        # Set background style
        self.setStyleSheet(f"background-color:{str(bg_color)};")
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create opacity effect for the entire widget and its children
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)  # Start fully transparent
        self.setGraphicsEffect(self.opacity_effect)
        
        # Create animation but don't start it yet
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)  # 500ms animation
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)  # Full opacity
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def getOpacity(self):
        return self.opacity_effect.opacity()
        
    def setOpacity(self, value):
        self.opacity_effect.setOpacity(value)
        
    def start_animation(self):
        """Start the fade-in animation"""
        self.animation.start()
        
    opacity = Property(float, getOpacity, setOpacity)

class AnimatedFrame_t(QFrame):
    """Frame with opacity animation capability that affects all child widgets"""
    def __init__(self,bg_color="rgba(128,128,128,0.2)", parent=None):
        super().__init__(parent)
        # Set background style
        self.setStyleSheet(f"background-color:{str(bg_color)};")
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Create opacity effect for the entire widget and its children
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0.0)  # Start fully transparent
        self.setGraphicsEffect(self.opacity_effect)
        
        # Create animation but don't start it yet
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)  # 500ms animation
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)  # Full opacity
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def getOpacity(self):
        return self.opacity_effect.opacity()
        
    def setOpacity(self, value):
        self.opacity_effect.setOpacity(value)
        
    def start_animation(self):
        """Start the fade-in animation"""
        self.animation.start()
        
    opacity = Property(float, getOpacity, setOpacity)

class SelectableFrame(QFrame):
    """A frame that can be selected with a checkbox"""
    frame_selected = Signal(int)  # Signal to emit when frame is selected
    
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        
        self.is_selected = False
        self.setStyleSheet("background-color: transparent;border-radius:8px;")
        self.setCursor(Qt.PointingHandCursor)
        
        # Make sure mouse events are tracked for this widget
        self.setMouseTracking(True)
        
    def mousePressEvent(self, event):
        """Handle mouse press events on the frame"""
        # Toggle selection state and emit signal
        self.setSelected(True)  # Always select on click, don't toggle
        super().mousePressEvent(event)
        
    def setSelected(self, selected):
        """Set the selection state of the frame"""
        if self.is_selected == selected:
            return  # No change needed
            
        self.is_selected = selected
        
        # Update visual appearance
        if self.is_selected:
            self.setStyleSheet("background-color: rgba(200,200,200,0.2);border-radius:8px;")
        else:
            self.setStyleSheet("background-color: transparent;border-radius:8px;")
            
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
            self.setStyleSheet("background-color: transparent;border-radius:8px;")
        super().leaveEvent(event)

# Class to manage selection of frames
class FrameSelectionManager(QObject):
    def __init__(self):
        super().__init__()
        self.currently_selected_frame = None
        
    def set_selected_frame(self, frame):
        # Deselect previous frame if it exists
        if self.currently_selected_frame and self.currently_selected_frame != frame:
            self.currently_selected_frame.setSelected(False)
            
        # Set new selected frame
        self.currently_selected_frame = frame

# Global selection manager
frame_selection_manager = FrameSelectionManager()

class PageEntryWidget(QWidget):
    def __init__(self, index, show_auto_upload_checkbox=False, is_page_info_hidden=False, edit_mode=False,editable:bool =True,main_frame_border_color=None):
        super().__init__()
        self.index = index
        self.show_auto_upload_checkbox = show_auto_upload_checkbox
        self.page_widgets = []
        self.animations = []  # Track animation objects to prevent garbage collection
        self.edit_mode = edit_mode  # Add edit_mode property
        self.is_page_info_hidden = is_page_info_hidden  # Store this value

        if main_frame_border_color is None:
            self.main_fram_border_color = "128,128,128,1"
        else:
            self.main_fram_border_color = main_frame_border_color
            
        self.lineedit_fields = []  # List to store all QLineEdit widgets
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        # Create a selectable frame as the container
        self.selectable_frame = SelectableFrame(self.index)
        selectable_layout = QHBoxLayout(self.selectable_frame)
        selectable_layout.setContentsMargins(5, 5, 5, 5)
        selectable_layout.setSpacing(10)
        
        # Add checkbox
        if self.show_auto_upload_checkbox:
            self.checkbox = QCheckBox()
            self.checkbox.setFixedSize(20, 20)
            # Connect checkbox directly to state changed signal
            self.checkbox.stateChanged.connect(self.checkbox_state_changed)
            # Prevent click events on checkbox from selecting the frame
            self.checkbox.installEventFilter(self)
            selectable_layout.addWidget(self.checkbox)
        
        # Create id_frame inside the selectable frame
        self.id_frame = QFrame()
        self.id_frame.setStyleSheet(
            f"border: 2px solid rgba({self.main_fram_border_color}); border-radius: 8px; background-color:none;"
        )
        self.id_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        selectable_layout.addWidget(self.id_frame)
        
        # Add the selectable frame to the main layout
        main_layout.addWidget(self.selectable_frame)
        
        # Connect selectable frame signal to handle selection
        self.selectable_frame.frame_selected.connect(self.on_frame_selected)
        
        # Continue with the rest of the widget setup inside id_frame
        frame1_layout = QVBoxLayout(self.id_frame)
        frame1_layout.setSpacing(8)

        # Header
        top_frame = QFrame()
        top_frame.setStyleSheet("border:none; background:none;")
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)
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
        info_frame.setStyleSheet("background-color:rgba(128,128,128,0.2); border:none;")
        info_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setSpacing(10)
        
        field_sets = [
            {"label": "ID Name:", "placeholder": "Enter ID name"},
            {"label": "Package Name:", "placeholder": "com.facebook.katana"},
            {"label": "LD Name:", "placeholder": "Enter ld name"}
        ]
        
        for field in field_sets:
            text_label = QLabel(field["label"])
            text_label.setStyleSheet("background-color:none;border:none;")
            info_layout.addWidget(text_label)
            
            entry = QLineEdit()
            entry.setMinimumHeight(24)
            entry.setPlaceholderText(field["placeholder"])
            entry.setStyleSheet(
                "background-color:rgba(128,128,128,0.2); border:2px solid rgba(128,128,128,0.5);"
            )
            entry.setReadOnly(not self.edit_mode)  # Initial state based on edit_mode
            self.lineedit_fields.append(entry)  # Add to our list to manage later
            info_layout.addWidget(entry)
        
        frame1_layout.addWidget(info_frame)

        # Page Information section 
        page_info_header = QFrame()
        page_info_header.setStyleSheet("border:none; background:none;")
        page_info_header_layout = QHBoxLayout(page_info_header)
        page_info_header_layout.setContentsMargins(0, 5, 0, 5)
        
        if not self.is_page_info_hidden:
            page_info_label = QLabel("Page Information")
            page_info_label.setStyleSheet("font-weight:bold; font-size:12px; border:none; background:none;")
            page_info_header_layout.addWidget(page_info_label)
            page_info_header_layout.addStretch()
        
        frame1_layout.addWidget(page_info_header)

        # Container for page entries
        self.pages_container = QFrame()
        self.pages_container.setStyleSheet("border:none; background:none;")
        self.pages_container_layout = QVBoxLayout(self.pages_container)
        self.pages_container_layout.setContentsMargins(0, 0, 0, 0)
        self.pages_container_layout.setSpacing(5)
        
        # Container for page entries
        self.page_entries_container = QVBoxLayout()
        self.page_entries_container.setSpacing(5)
        self.pages_container_layout.addLayout(self.page_entries_container)

        # Add Page button using AnimatedHoverButton
        self.button_container = QFrame()
        self.button_container.setStyleSheet("border:none; background:none;")
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 5, 0, 5)
        
        # Fix: Ensure the button is properly configured to avoid triggering dialog
        self.add_page_btn = AnimatedHoverButton("Add Page")
        self.add_page_btn.setFixedSize(QSize(100, 30))
        self.add_page_btn.setDefault(False)
        self.add_page_btn.setAutoDefault(False)
        # Use lambda to avoid passing the clicked signal's boolean parameter
        self.add_page_btn.clicked.connect(lambda: self.add_page_entry())
        button_layout.addWidget(self.add_page_btn)
        button_layout.addStretch()
        
        self.pages_container_layout.addWidget(self.button_container)
        frame1_layout.addWidget(self.pages_container)
        
        # Set initial visibility for edit mode controls
        self.update_edit_controls_visibility()
        
        # Initial visibility of page information section
        self.update_page_info_visibility()
    
    def update_page_info_visibility(self):
        """Update visibility of page information section based on is_page_info_hidden"""
        if hasattr(self, 'pages_container'):
            self.pages_container.setVisible(not self.is_page_info_hidden)
    
    def eventFilter(self, obj, event):
        """Filter events to prevent checkbox clicks from selecting the frame"""
        if obj == self.checkbox and event.type() == Qt.MouseButton:
            # Stop event propagation
            return True  # Event handled, don't propagate
        return super().eventFilter(obj, event)
    
    def checkbox_state_changed(self, state):
        """Handle checkbox state changes without affecting frame selection"""
        checked = state == Qt.Checked
        # No need to update frame selection here
    
    def on_frame_selected(self, index):
        """Handle selection of the frame"""
        if index >= 0:
            # This frame was selected
            frame_selection_manager.set_selected_frame(self.selectable_frame)
            return index
        else:
            return -1
    
    def add_page_entry(self):
        """Add a new page entry with animation"""
        # Grab the actual widget that holds our layout
        parent_widget = self.page_entries_container.parentWidget()

        # Pass parent so it's never a standalone window:
        page_entry_main_frame = AnimatedFrame("rgba(128,128,128,0.2)",parent_widget)

        # Now set up layout and widgets as before...
        page_entry_hboxlayout = QHBoxLayout(page_entry_main_frame)
        page_entry_hboxlayout.setSpacing(8)
        page_entry_hboxlayout.setContentsMargins(5, 8, 5, 8)

        page_idx = len(self.page_widgets) + 1

        page_idx_label = QLabel(f"{page_idx}.", parent=page_entry_main_frame)
        page_entry_hboxlayout.addWidget(page_idx_label)
        page_idx_label.setStyleSheet("background-color:transparent;")

        page_text_label = QLabel("Page:", parent=page_entry_main_frame)
        page_entry_hboxlayout.addWidget(page_text_label)

        page_text_label.setStyleSheet("background-color:transparent;")
        entry = QLineEdit(parent=page_entry_main_frame)
        entry.setMinimumHeight(24)
        entry.setPlaceholderText("Enter page name...")
        entry.setStyleSheet(
            "background-color:rgba(128,128,128,0.2);"
            "border:2px solid rgba(128,128,128,0.5);"
        )
        entry.setReadOnly(not self.edit_mode)  # Set read-only based on current edit mode
        self.lineedit_fields.append(entry)  # Add to our list to manage later
        page_entry_hboxlayout.addWidget(entry)

        remove_btn = AnimatedHoverButton("Remove Page", parent=page_entry_main_frame)
        remove_btn.setFixedSize(QSize(85, 24))
        remove_btn.clicked.connect(lambda: self.remove_page_entry(page_entry_main_frame))
        remove_btn.setVisible(self.edit_mode and not self.is_page_info_hidden)
        page_entry_hboxlayout.addWidget(remove_btn)
        page_entry_hboxlayout.addStretch()

        # Now add to layout and start animation
        self.page_widgets.append(page_entry_main_frame)
        self.page_entries_container.addWidget(page_entry_main_frame)
        page_entry_main_frame.start_animation()
        self.animations.append(page_entry_main_frame.animation)
        page_entry_main_frame.remove_btn = remove_btn
        page_entry_main_frame.lineedit = entry  # Save reference to access later

        return page_entry_main_frame


    def remove_page_entry(self, page_widget):
        """Remove a page widget and renumber the remaining ones"""
        if page_widget in self.page_widgets:
            idx = self.page_widgets.index(page_widget)
            # Remove from layout and list
            self.page_entries_container.removeWidget(page_widget)
            self.page_widgets.remove(page_widget)
            
            # Remove line edit from our tracking list if it exists
            if hasattr(page_widget, 'lineedit'):
                if page_widget.lineedit in self.lineedit_fields:
                    self.lineedit_fields.remove(page_widget.lineedit)
            
            # Delete widget with proper memory management
            if hasattr(page_widget, 'animation'):
                # Remove the animation from tracking list
                if page_widget.animation in self.animations:
                    self.animations.remove(page_widget.animation)
            
            page_widget.deleteLater()
            
            # Renumber remaining pages
            for i, page in enumerate(self.page_widgets):
                # Find the index label (first child widget) and update its text
                labels = page.findChildren(QLabel)
                for label in labels:
                    if label.text().endswith('.'):
                        label.setText(f"{i+1}.")
                        break
            
            # Update the layout
            QApplication.processEvents()
        
    def update_edit_controls_visibility(self):
        """Update visibility of all edit controls based on edit mode"""
        # Check if page info is hidden - if so, don't show edit controls even in edit mode
        should_show_controls = self.edit_mode and not self.is_page_info_hidden
        
        # Update "Add Page" button visibility
        if hasattr(self, 'add_page_btn'):
            self.add_page_btn.setVisible(should_show_controls)
            self.button_container.setVisible(should_show_controls)
        
        # Update "Remove Page" buttons visibility for all page entries
        for page_widget in self.page_widgets:
            if hasattr(page_widget, 'remove_btn'):
                page_widget.remove_btn.setVisible(should_show_controls)
        
        # Update read-only state for all line edits
        self.update_lineedit_readonly_state()
        
    def update_lineedit_readonly_state(self):
        """Update the read-only state of all QLineEdit widgets based on edit mode"""
        for lineedit in self.lineedit_fields:
            lineedit.setReadOnly(not self.edit_mode)
            
            # Optional: Update the appearance based on read-only state
            if self.edit_mode:
                lineedit.setStyleSheet(
                    "background-color:rgba(128,128,128,0.2);"
                    "border:2px solid rgba(128,128,128,0.5);"
                )
            else:
                lineedit.setStyleSheet(
                    "background-color:rgba(128,128,128,0.1);"
                    "border:2px solid rgba(128,128,128,0.3);"
                    "color: white;"
                )
        
    def set_edit_mode(self, enabled):
        """Enable or disable edit mode"""
        self.edit_mode = enabled
        self.update_edit_controls_visibility()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.page_widgets = []
        self.edit_mode = False
        self.next_widget_index = 1  # Track the next index to use
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Improved PySide Page UI with Animations")
        self.resize(800, 400)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Add top controls layout
        top_controls_layout = QHBoxLayout()
        
        # Add edit mode toggle button at the top
        self.edit_button = AnimatedHoverButton("Edit Mode: Off")
        self.edit_button.setFixedSize(QSize(120, 30))
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        top_controls_layout.addWidget(self.edit_button)
        
        # Add spacer to push buttons apart
        top_controls_layout.addStretch()
        
        # Add widget control buttons
        self.add_widget_button = AnimatedHoverButton("Add Widget")
        self.add_widget_button.setFixedSize(QSize(120, 30))
        self.add_widget_button.clicked.connect(self.add_page_entry_widget)
        top_controls_layout.addWidget(self.add_widget_button)
        
        self.remove_widget_button = AnimatedHoverButton("Remove Widget")
        self.remove_widget_button.setFixedSize(QSize(120, 30))
        self.remove_widget_button.clicked.connect(self.remove_selected_widget)
        top_controls_layout.addWidget(self.remove_widget_button)
        
        # Add the top controls to the main layout
        main_layout.addLayout(top_controls_layout)
        
        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Create a container widget for the scroll area content
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        
        # Create initial widgets
        for r in range(1, 4): 
            
            is_hidden = (r % 3 == 0) 
            widget = PageEntryWidget(
                index=r, 
                edit_mode=self.edit_mode,
                is_page_info_hidden=is_hidden,
                show_auto_upload_checkbox=True,
                main_frame_border_color="0,144,63,1"
            )
            self.page_widgets.append(widget)
            self.scroll_layout.addWidget(widget)
        
        self.next_widget_index = len(self.page_widgets) + 1
            
        self.scroll_layout.addStretch()  # Push widgets to top
        
        # Set the content widget to the scroll area
        self.scroll_area.setWidget(self.scroll_content)
        
        # Add the scroll area to the main layout
        main_layout.addWidget(self.scroll_area)
    
    def toggle_edit_mode(self):
        """Toggle edit mode for all page widgets"""
        self.edit_mode = not self.edit_mode
        
        # Update button text and style
        self.edit_button.setText(f"Edit Mode: {'On' if self.edit_mode else 'Off'}")
        
        # If in edit mode, make the button more prominent
        if self.edit_mode:
            self.edit_button.setStyleSheet("font-weight: bold;")
        else:
            self.edit_button.setStyleSheet("")
        
        # Update all page widgets
        for widget in self.page_widgets:
            widget.set_edit_mode(self.edit_mode)
        
        # Process events to ensure UI updates
        QApplication.processEvents()
    
    def add_page_entry_widget(self):
        """Add a new PageEntryWidget to the scroll area"""
        # Create animation frame to hold the widget for smooth appearance
        container_frame = QFrame(self.scroll_content)
        container_layout = QVBoxLayout(container_frame)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the widget with the next index
        is_hidden = True  # Set default for new widgets
        widget = PageEntryWidget(
            index=self.next_widget_index,
            edit_mode=self.edit_mode,
            is_page_info_hidden=is_hidden,
            show_auto_upload_checkbox=True
        )
        
        # Add the widget to our tracking list and increment the index
        self.page_widgets.append(widget)
        self.next_widget_index += 1
        
        # Add the widget to the container frame
        container_layout.addWidget(widget)
        
        # Add the container frame to the scroll layout before the stretch
        self.scroll_layout.insertWidget(self.scroll_layout.count() - 1, container_frame)
        
        # Process events to ensure the widget is rendered
        QApplication.processEvents()
        
        # Scroll to the bottom of the scroll area using a QTimer for reliable scrolling
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
        
        # Return the created widget
        return widget
    
    def remove_selected_widget(self):
        """Remove the currently selected PageEntryWidget"""
        # Check if we have a selected frame
        if frame_selection_manager.currently_selected_frame is None:
            QMessageBox.information(self, "No Selection", "Please select a widget to remove first.")
            return
        
        # Find which widget contains the selected frame
        selected_widget = None
        for widget in self.page_widgets:
            if hasattr(widget, 'selectable_frame') and widget.selectable_frame == frame_selection_manager.currently_selected_frame:
                selected_widget = widget
                break
        
        if not selected_widget:
            QMessageBox.information(self, "Selection Error", "Could not determine which widget to remove.")
            return
        
        # Confirm removal
        reply = QMessageBox.question(self, "Confirm Removal", 
                                     f"Remove widget #{selected_widget.index}?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
        
        # Remove the widget from our list and layout
        self.page_widgets.remove(selected_widget)
        
        # Determine if widget has a container frame
        container = None
        if hasattr(selected_widget, 'container_frame'):
            container = selected_widget.container_frame
            self.scroll_layout.removeWidget(container)
            container.deleteLater()
        else:
            # Direct removal if no container
            self.scroll_layout.removeWidget(selected_widget)
            selected_widget.deleteLater()
        
        # Reset the selection manager
        frame_selection_manager.currently_selected_frame = None
        
        # Renumber the remaining widgets
        self.renumber_widgets()
        
        # Update the layout
        QApplication.processEvents()
    
    def renumber_widgets(self):
        """Renumber all PageEntryWidgets sequentially"""
        for i, widget in enumerate(self.page_widgets):
            new_index = i + 1
            widget.index = new_index
            
            # Update the visible index label
            if hasattr(widget, 'id_frame'):
                # Find the index label in the top frame
                labels = widget.findChildren(QLabel)
                for label in labels:
                    if label.text().endswith('.') and '.' in label.text():
                        # This looks like an index label
                        label.setText(f"{new_index}.")
                        break
        
        # Update the next index to use
        self.next_widget_index = len(self.page_widgets) + 1

if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())