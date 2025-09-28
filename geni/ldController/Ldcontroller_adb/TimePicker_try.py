import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QFrame)
from PySide6.QtCore import Qt, QPointF, QTimer, Signal, Property, QPropertyAnimation
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QWheelEvent

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
        self.inertiaTimer.setInterval(16)  # ~60 FPS
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
        
        # Adjust scrolling speed and direction
        self.offset += delta / 8
        
        # Calculate momentum based on the wheel delta
        self.momentum = delta / 12
        
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
        painter.fillRect(0, 0, width, height, QColor(245, 245, 245))
        
        # Draw highlight for selected item with transparency (0.1 opacity)
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
            color = QColor(0, 0, 0)
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


class TimePickerWidget(QWidget):
    timeChanged = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)  
        
        self.setWindowTitle("iPhone-Style Time Picker")
        self.resize(300, 300)
        
        # Create layout
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        titleLabel = QLabel("Select Time")
        titleLabel.setAlignment(Qt.AlignCenter)
        font = titleLabel.font()
        font.setPointSize(18)
        titleLabel.setFont(font)
        mainLayout.addWidget(titleLabel)
        
        # Container for wheels with shadow effect
        wheelContainer = QFrame()
        wheelContainer.setFrameShape(QFrame.StyledPanel)
        wheelContainer.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #dddddd;
            }
        """)
        
        # Time picker wheels layout
        wheelLayout = QHBoxLayout(wheelContainer)
        
        # Hour wheel (12-hour format)
        hours = list(range(1, 13))  # 1-12
        self.hourWheel = WheelComponent(hours)
        self.hourWheel.setValue(12)  # Default to 12
        self.hourWheel.valueChanged.connect(self.onTimeChanged)
        
        # Minute wheel
        minutes = list(range(0, 60))  # 0-59
        self.minuteWheel = WheelComponent(minutes)
        self.minuteWheel.valueChanged.connect(self.onTimeChanged)
        
        # AM/PM wheel
        ampm = ["AM", "PM"]
        self.ampmWheel = WheelComponent(ampm)
        self.ampmWheel.valueChanged.connect(self.onTimeChanged)
        
        # Add wheels to layout
        wheelLayout.addWidget(self.hourWheel, 1)
        
        # Colon label
        colonLabel = QLabel(":")
        colonLabel.setAlignment(Qt.AlignCenter)
        font = colonLabel.font()
        font.setPointSize(24)
        font.setBold(True)
        colonLabel.setFont(font)
        wheelLayout.addWidget(colonLabel, 0)
        
        wheelLayout.addWidget(self.minuteWheel, 1)
        wheelLayout.addWidget(self.ampmWheel, 1)
        
        mainLayout.addWidget(wheelContainer)
        
        # Display selected time
        self.timeDisplay = QLabel()
        self.timeDisplay.setAlignment(Qt.AlignCenter)
        font = self.timeDisplay.font()
        font.setPointSize(16)
        self.timeDisplay.setFont(font)
        mainLayout.addWidget(self.timeDisplay)
        
        # Initial time display update
        self.onTimeChanged()
    
    def onTimeChanged(self):
        hour = self.hourWheel.value
        minute = self.minuteWheel.value
        ampm = self.ampmWheel.value
        
        # Format time string
        timeString = f"{hour}:{minute:02d} {ampm}"
        self.timeDisplay.setText(f"Selected time: {timeString}")
        
        # Emit signal
        self.timeChanged.emit(hour, minute)


if __name__ == "__main__": 
    app = QApplication(sys.argv)
    window = TimePickerWidget()
    window.show()
    sys.exit(app.exec())