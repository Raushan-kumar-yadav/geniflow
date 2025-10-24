from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QCheckBox, QComboBox, QFrame,
    QVBoxLayout, QHBoxLayout, QGroupBox, QTextEdit, QTabWidget, QMessageBox,
    QDialog, QScrollArea, QLineEdit, QRadioButton, QButtonGroup, QSizePolicy
)
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QKeySequence, QShortcut
from PySide6.QtCore import Qt, Property, QPropertyAnimation, Signal, QTimer
import sys
import json
import os
import random


class AnimatedHoverButton(QPushButton):
    """QPushButton subclass with smooth color transition on hover."""
    def __init__(self, text, btn_padding=3, border_radius_size=1, parent=None):
        super().__init__(text, parent)
        self._hoverLevel = 0.0
        self.button_border_radius = 8 if border_radius_size >= 0.8 else 5
        self.btn_padding = btn_padding
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)
        self._anim = QPropertyAnimation(self, b"hoverLevel", self)
        self._anim.setDuration(200)
        self.update_style()
        self.setDefault(False)
        self.setAutoDefault(False)

    def update_style(self):
        alpha = 0.5 + 0.3 * self._hoverLevel
        color = f"rgba(27,86,253,{alpha:.2f})"
        pressed_style = "rgba(27,86,253,1.0)"
        adjusted_padding = max(1, int(min(self.width() or 30, self.height() or 20) * 0.15))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: {self.button_border_radius}px;
                padding: {adjusted_padding}px;
                text-align: center;
                color: white;
                font-weight: bold;
            }}
            QPushButton:pressed {{
                background-color: {pressed_style};
            }}
            QPushButton:disabled {{
                background-color: rgba(128,128,128,0.3);
                color: rgba(255,255,255,0.5);
            }}
        """)

    def resizeEvent(self, event):
        self.update_style()
        super().resizeEvent(event)

    def enterEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._hoverLevel)
        self._anim.setEndValue(1.0)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
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


class NotificationLabel(QLabel):
    """Temporary notification label with fade effect."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(46,204,113,0.9);
                color: white;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10pt;
            }
        """)
        self.hide()
        self._opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self._opacity_anim.setDuration(300)
        
    def show_message(self, text, success=True):
        """Show notification message."""
        self.setText(text)
        bg_color = "rgba(46,204,113,0.9)" if success else "rgba(231,76,60,0.9)"
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                padding: 8px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 10pt;
            }}
        """)
        self.show()
        QTimer.singleShot(2500, self.hide)


class PreviewDialog(QDialog):
    """Preview dialog showing sharing mappings."""
    def __init__(self, from_groups, to_groups, mode, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sharing Preview")
        self.setMinimumSize(650, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #0b0c10;
                color: #eeeeee;
                font-family: 'Arial';
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: rgb(34, 81, 200);border-radius: 8px;")
        header_frame.setFixedHeight(40)
        bg_layout = QVBoxLayout(header_frame)
        header = QLabel("📊 Sharing Preview")
        header.setStyleSheet("font-size: 13pt; font-weight: bold; background-color: none; color: white;")
        bg_layout.addWidget(header, alignment=Qt.AlignCenter)
        layout.addWidget(header_frame)
        
        # Stats row
        stats_layout = QHBoxLayout()
        
        mode_label = QLabel(f"📋 {mode}")
        mode_label.setStyleSheet("""
            background-color: none;
            color: #46cc71;
            padding: 6px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 9pt;
        """)
        
        from_count = QLabel(f"📤 {len(from_groups)}")
        from_count.setStyleSheet("""
            background-color: rgba(27,86,253,0.3);
            color: #1b56fd;
            padding: 6px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 9pt;
        """)
        
        to_count = QLabel(f"📥 {len(to_groups)}")
        to_count.setStyleSheet("""
            background-color: rgba(230,126,34,0.3);
            color: #e67e22;
            padding: 6px 10px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 9pt;
        """)
        
        stats_layout.addWidget(mode_label)
        stats_layout.addWidget(from_count)
        stats_layout.addWidget(to_count)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid rgba(128,128,128,0.5);
                border-radius: 8px;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(128,128,128,0.2);
                width: 10px;
                border-radius: 5px; 
            }
            QScrollBar::handle:vertical {
                background-color: rgba(27,86,253,0.5);
                border-radius: 5px;
                min-height: 20px;
            }
        """)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(8)
        
        # Generate mappings
        mappings = self.generate_mappings(from_groups, to_groups, mode)
        
        if not mappings:
            no_data = QLabel("⚠️ No valid mappings")
            no_data.setStyleSheet("color: #e67e22; font-size: 12pt; padding: 20px;")
            no_data.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(no_data)
        else:
            for idx, (from_g, to_gs) in enumerate(mappings, 1):
                mapping_widget = self.create_mapping_row(idx, from_g, to_gs)
                content_layout.addWidget(mapping_widget)
        
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # Button layout
        btn_layout = QHBoxLayout()
        
        export_btn = AnimatedHoverButton("💾 Export")
        export_btn.setFixedSize(90, 30)
        export_btn.clicked.connect(lambda: self.export_preview(mappings))
        
        close_btn = AnimatedHoverButton("✖️ Close")
        close_btn.setFixedSize(90, 30)
        close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
        self.mappings = mappings
    
    def generate_mappings(self, from_list, to_list, mode):
        """Generate mappings based on mode."""
        mappings = []
        
        if not from_list or not to_list:
            return mappings
        
        base_mode = mode.split(" (")[0] if "(" in mode else mode
        
        if base_mode == "1 to 1 Posting":
            max_len = max(len(from_list), len(to_list))
            for i in range(max_len):
                from_g = from_list[i] if i < len(from_list) else "❌ No Group"
                to_g = to_list[i] if i < len(to_list) else "❌ No Group"
                mappings.append((from_g, [to_g]))
        
        elif base_mode == "Share to All":
            for from_g in from_list:
                mappings.append((from_g, to_list.copy()))
        
        elif base_mode == "Randomize":
            shuffled = to_list.copy()
            random.shuffle(shuffled)
            for i, from_g in enumerate(from_list):
                to_g = shuffled[i % len(shuffled)]
                mappings.append((from_g, [to_g]))
        
        else:
            for i, from_g in enumerate(from_list):
                to_g = to_list[i % len(to_list)]
                mappings.append((from_g, [to_g]))
        
        return mappings
    
    def create_mapping_row(self, idx, from_group, to_groups):
        """Create a single mapping row."""
        row = QWidget()
        row.setStyleSheet("""
            QWidget {
                background-color: rgba(128,128,128,0.15);
                border: 1px solid rgba(128,128,128,0.4);
                border-radius: 6px;
                padding: 8px;
                margin: 2px;
            }
        """)
        
        layout = QHBoxLayout(row)
        layout.setSpacing(10)
        
        idx_label = QLabel(f"#{idx}")
        idx_label.setStyleSheet("""
            background-color: rgba(27,86,253,0.6);
            color: white;
            font-weight: bold;
            padding: 5px 8px;
            border-radius: 4px;
            font-size: 9pt;
        """)
        idx_label.setFixedWidth(40)
        idx_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(idx_label)
        
        from_label = QLabel(f"📤 {from_group}")
        from_label.setStyleSheet("""
            background-color: rgba(27,86,253,0.3);
            padding: 6px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 9pt;
        """)
        from_label.setWordWrap(True)
        from_label.setMinimumWidth(150)
        layout.addWidget(from_label)
        
        arrow = QLabel("➜")
        arrow.setStyleSheet("font-size: 16px; color: #46cc71; font-weight: bold;")
        layout.addWidget(arrow)
        
        to_container = QWidget()
        to_layout = QVBoxLayout(to_container)
        to_layout.setContentsMargins(0, 0, 0, 0)
        to_layout.setSpacing(5)
        
        for to_g in to_groups:
            to_label = QLabel(f"📥 {to_g}")
            to_label.setStyleSheet("""
                background-color: rgba(46,204,113,0.3);
                padding: 6px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 9pt;
            """)
            to_label.setWordWrap(True)
            to_label.setMinimumWidth(150)
            to_layout.addWidget(to_label)
        
        layout.addWidget(to_container, 1)
        
        return row
    
    def export_preview(self, mappings):
        """Export preview to text file."""
        try:
            filename = "sharing_preview.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=== SHARING PREVIEW ===\n\n")
                for idx, (from_g, to_gs) in enumerate(mappings, 1):
                    f.write(f"#{idx}\n")
                    f.write(f"From: {from_g}\n")
                    f.write(f"To: {', '.join(to_gs)}\n")
                    f.write("-" * 50 + "\n\n")
            QMessageBox.information(self, "Exported", f"✅ Preview exported to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Export failed:\n{e}")


class GroupSharingUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Group Sharing Manager")
        self.config_file = "User_Data/group_sharing_config.json"
        self.has_unsaved_changes = False
        
        self.setStyleSheet("""
            QWidget {
                background-color: #0b0c10;
                color: #eeeeee;
                font-family: 'Arial';
                font-size: 11px;
            }
            QTabWidget::pane {
                border: 2px solid rgba(128,128,128,0.5);
                border-radius: 8px;
                background-color: rgba(128,128,128,0.1);
            }
            QTabBar::tab {
                background-color: rgba(128,128,128,0.3);
                color: #eeeeee;
                padding: 8px 18px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: rgb(34, 81, 200);
                color: white;
            }
        """)
        
        self.method_blocks = []
        self.niche_blocks = []
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Notification
        self.notification = NotificationLabel(self)
        self.notification.setFixedHeight(35)
        layout.addWidget(self.notification)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # ✅ Normal tab with scroll area
        normal_scroll = QScrollArea()
        normal_scroll.setWidgetResizable(True)
        normal_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(128,128,128,0.2);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(27,86,253,0.5);
                border-radius: 5px;
            }
        """)
        
        normal_content = QWidget()
        normal_layout = QVBoxLayout(normal_content)
        normal_layout.setContentsMargins(5, 5, 5, 5)
        normal_layout.addWidget(self.create_normal_group())
        normal_layout.addStretch(1)
        normal_scroll.setWidget(normal_content)
        
        # ✅ Niche tab with scroll area
        niche_scroll = QScrollArea()
        niche_scroll.setWidgetResizable(True)
        niche_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(128,128,128,0.2);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(155,89,182,0.5);
                border-radius: 5px;
            }
        """)
        
        niche_content = QWidget()
        niche_layout = QVBoxLayout(niche_content)
        niche_layout.setContentsMargins(5, 5, 5, 5)
        niche_layout.addWidget(self.create_niche_group())
        niche_layout.addStretch(1)
        niche_scroll.setWidget(niche_content)
        
        self.tabs.addTab(normal_scroll, "📋 Normal")
        self.tabs.addTab(niche_scroll, "🎯 Niche")
        
        layout.addWidget(self.tabs)
        
        # Bottom button layout
        btn_layout = QHBoxLayout()
        
        clear_btn = AnimatedHoverButton("🗑️ Clear")
        clear_btn.setFixedSize(100, 32)
        clear_btn.clicked.connect(self.clear_all)
        
        load_btn = AnimatedHoverButton("📂 Load")
        load_btn.setFixedSize(100, 32)
        load_btn.clicked.connect(self.load_config)
        
        save_btn = AnimatedHoverButton("💾 Save")
        save_btn.setFixedSize(100, 32)
        save_btn.clicked.connect(self.save_config)
        
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(load_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_config)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.load_config)
        
        # Auto-load config
        QTimer.singleShot(100, self.auto_load_config)

    def create_normal_group(self):
        """Create normal sharing group."""
        main_group = QGroupBox("")
        main_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(128,128,128,0.8);
                border-radius: 8px;
                padding: 10px;
                margin-top: 5px;
                background-color: rgba(128,128,128,0.15);
            }
        """)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: rgb(34, 81, 200);border-radius: 8px;")
        header_frame.setFixedHeight(40)
        header_frame.setFixedWidth(160)
        bg_layout = QVBoxLayout(header_frame)
        main_layout.addWidget(header_frame, alignment=Qt.AlignCenter)

        header = QLabel("📋 Group Sharing")
        header.setStyleSheet("font-size: 11pt; font-weight: bold; background-color: none; color: white;")
        bg_layout.addWidget(header, alignment=Qt.AlignCenter)

        # Add first method block
        block = self.create_method_block("Methods", "Methods")
        main_layout.addWidget(block)
        self.method_blocks.append(block)
        
        # Add method button
        add_btn = AnimatedHoverButton("➕ Add Method")
        add_btn.setFixedSize(120, 28)
        add_btn.clicked.connect(self.add_method_block)
        main_layout.addWidget(add_btn, alignment=Qt.AlignLeft)
        
        main_group.setLayout(main_layout)
        self.normal_main_layout = main_layout
        return main_group

    def create_niche_group(self):
        """Create niche-wise sharing group."""
        main_group = QGroupBox("")
        main_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(128,128,128,0.8);
                border-radius: 8px;
                padding: 10px;
                margin-top: 5px;
                background-color: rgba(128,128,128,0.15);
            }
        """)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: rgb(155,89,182);border-radius: 8px;")
        header_frame.setFixedHeight(40)
        header_frame.setFixedWidth(180)
        bg_layout = QVBoxLayout(header_frame)
        main_layout.addWidget(header_frame, alignment=Qt.AlignCenter)

        header = QLabel("🎯 Niche-wise Sharing")
        header.setStyleSheet("font-size: 11pt; font-weight: bold; background-color: none; color: white;")
        bg_layout.addWidget(header, alignment=Qt.AlignCenter)

        # Info
        info = QLabel("ℹ️ 'Share to All' recommended for niches")
        info.setStyleSheet("""
            background-color: rgba(155,89,182,0.2);
            color: #9b59b6;
            padding: 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 9pt;
        """)
        main_layout.addWidget(info)

        # Add first niche block
        niche_block = self.create_niche_block("Technology")
        main_layout.addWidget(niche_block)
        self.niche_blocks.append(niche_block)
        
        # Add niche button
        add_niche_btn = AnimatedHoverButton("➕ Add Niche")
        add_niche_btn.setFixedSize(120, 28)
        add_niche_btn.clicked.connect(self.add_niche_block)
        main_layout.addWidget(add_niche_btn, alignment=Qt.AlignLeft)
        
        main_group.setLayout(main_layout)
        self.niche_main_layout = main_layout
        return main_group

    def create_niche_block(self, niche_name):
        """Create niche block."""
        container = QWidget()
        wrapper = QVBoxLayout(container)
        wrapper.setSpacing(8)
        
        # Enable checkbox
        enable_checkbox = QCheckBox("✓ Enable")
        enable_checkbox.setChecked(True)
        enable_checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 6px;
                color: #eeeeee;
                font-weight: bold;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid rgba(128,128,128,0.8);
                background-color: rgba(128,128,128,0.3);
            }
            QCheckBox::indicator:checked {
                background-color: rgb(155,89,182);
                border: 2px solid rgb(155,89,182);
            }
        """)
        enable_checkbox.stateChanged.connect(self.mark_unsaved_changes)
        wrapper.addWidget(enable_checkbox)
        
        # Main block
        block_group = QGroupBox()
        block_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(155,89,182,0.8);
                border-radius: 8px;
                padding: 10px;
                margin-top: 5px;
                background-color: rgba(155,89,182,0.1);
            }
        """)
        block_layout = QVBoxLayout()
        block_layout.setSpacing(8)
        
        # Niche name
        name_layout = QHBoxLayout()
        name_label = QLabel("🏷️ Niche:")
        name_label.setStyleSheet("color: #eeeeee; font-weight: bold; font-size: 10pt;")
        
        niche_input = QLineEdit()
        niche_input.setPlaceholderText("e.g., Technology")
        niche_input.setText(niche_name)
        niche_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.25);
                color: #eeeeee;
                border: 2px solid rgba(155,89,182,0.6);
                border-radius: 6px;
                padding: 6px;
                font-size: 10pt;
            }
            QLineEdit:focus {
                border: 2px solid rgb(155,89,182);
            }
        """)
        niche_input.textChanged.connect(self.mark_unsaved_changes)
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(niche_input, 1)
        block_layout.addLayout(name_layout)
        
        # Horizontal layout
        sharing_layout = QHBoxLayout()
        sharing_layout.setSpacing(10)
        
        left_box = self.create_share_box("🎯 From", "Groups", is_niche=True)
        right_box = self.create_share_box("🎯 To", "Groups", is_niche=True)
        options_box = self.create_options_box(is_niche=True)
        
        sharing_layout.addWidget(left_box, 1)
        sharing_layout.addWidget(right_box, 1)
        sharing_layout.addWidget(options_box)
        
        block_layout.addLayout(sharing_layout)
        block_group.setLayout(block_layout)
        wrapper.addWidget(block_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        preview_btn = AnimatedHoverButton("👁️ Preview")
        preview_btn.setFixedSize(100, 28)
        preview_btn.clicked.connect(lambda: self.show_niche_preview(niche_input, left_box, right_box, options_box))
        
        remove_btn = AnimatedHoverButton("🗑️ Remove")
        remove_btn.setFixedSize(100, 28)
        remove_btn.clicked.connect(lambda: self.remove_niche_block(container))
        
        btn_layout.addStretch()
        btn_layout.addWidget(preview_btn)
        btn_layout.addWidget(remove_btn)
        wrapper.addLayout(btn_layout)
        
        container.setLayout(wrapper)
        
        # Store references
        container.enable_checkbox = enable_checkbox
        container.niche_input = niche_input
        container.left_box = left_box
        container.right_box = right_box
        container.options_box = options_box
        
        return container

    def create_method_block(self, share_from_text, share_to_text):
        """Create method block."""
        container = QWidget()
        wrapper = QVBoxLayout(container)
        wrapper.setSpacing(8)
        
        # Enable checkbox
        enable_checkbox = QCheckBox("✓ Enable")
        enable_checkbox.setChecked(True)
        enable_checkbox.setStyleSheet("""
            QCheckBox {
                spacing: 6px;
                color: #eeeeee;
                font-weight: bold;
                font-size: 10pt;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid rgba(128,128,128,0.8);
                background-color: rgba(128,128,128,0.3);
            }
            QCheckBox::indicator:checked {
                background-color: rgb(34, 81, 200);
                border: 2px solid rgb(34, 81, 200);
            }
        """)
        enable_checkbox.stateChanged.connect(self.mark_unsaved_changes)
        wrapper.addWidget(enable_checkbox)
        
        # Main block
        block_group = QGroupBox()
        block_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgba(128,128,128,0.8);
                border-radius: 8px;
                padding: 10px;
                margin-top: 5px;
                background-color: rgba(128,128,128,0.2);
            }
        """)
        block_layout = QHBoxLayout()
        block_layout.setSpacing(10)
        
        left_box = self.create_share_box("📤 From", share_from_text)
        right_box = self.create_share_box("📥 To", share_to_text)
        options_box = self.create_options_box()
        
        block_layout.addWidget(left_box, 1)
        block_layout.addWidget(right_box, 1)
        block_layout.addWidget(options_box)
        block_group.setLayout(block_layout)
        wrapper.addWidget(block_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        preview_btn = AnimatedHoverButton("👁️ Preview")
        preview_btn.setFixedSize(100, 28)
        preview_btn.clicked.connect(lambda: self.show_preview(left_box, right_box, options_box))
        
        remove_btn = AnimatedHoverButton("🗑️ Remove")
        remove_btn.setFixedSize(100, 28)
        remove_btn.clicked.connect(lambda: self.remove_method_block(container))
        
        btn_layout.addStretch()
        btn_layout.addWidget(preview_btn)
        btn_layout.addWidget(remove_btn)
        wrapper.addLayout(btn_layout)
        
        container.setLayout(wrapper)
        
        # Store references
        container.enable_checkbox = enable_checkbox
        container.left_box = left_box
        container.right_box = right_box
        container.options_box = options_box
        
        return container

    def create_share_box(self, title, combo_text, is_niche=False):
        """Create share box - COMPACT VERSION."""
        box = QGroupBox(title)
        
        border_color = "rgba(155,89,182,0.6)" if is_niche else "rgba(128,128,128,0.6)"
        title_bg = "rgba(155,89,182,0.4)" if is_niche else "rgba(27,86,253,0.4)"
        
        box.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 8px;
                margin-top: 8px;
                background-color: rgba(128,128,128,0.15);
                font-weight: bold;
                font-size: 9pt;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 3px 8px;
                border-radius: 4px;
                background-color: {title_bg};
                color: white;
            }}
        """)
        layout = QVBoxLayout()
        layout.setSpacing(6)
        
        # ✅ REDUCED TEXT BOX SIZE
        text_box = QTextEdit()
        text_box.setPlaceholderText("Group names (one per line)")
        text_box.setMinimumSize(200, 80)  # Reduced from 380x120
        text_box.setMaximumHeight(120)
        text_box.setStyleSheet(f"""
            QTextEdit {{
                background-color: rgba(128,128,128,.25);
                color: #eeeeee;
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 6px;
                selection-background-color: rgba(27,86,253,0.5);
                font-size: 9pt;
            }}
            QTextEdit:focus {{
                border: 2px solid {'rgb(155,89,182)' if is_niche else 'rgb(34, 81, 200)'};
            }}
        """)
        text_box.textChanged.connect(self.mark_unsaved_changes)
        
        # Group count
        count_label = QLabel("📊 0")
        count_label.setStyleSheet("""
            background-color: rgba(46,204,113,0.3);
            color: #46cc71;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 8pt;
        """)
        text_box.textChanged.connect(lambda: self.update_group_count(text_box, count_label))
        
        check_btn = AnimatedHoverButton("✓")
        check_btn.setFixedSize(50, 24)
        check_btn.clicked.connect(lambda: self.validate_groups(text_box))
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(count_label)
        btn_layout.addStretch()
        btn_layout.addWidget(check_btn)
        
        layout.addWidget(text_box)
        layout.addLayout(btn_layout)
        box.setLayout(layout)
        
        # Store references
        box.text_box = text_box
        box.count_label = count_label
        
        return box

    def create_options_box(self, is_niche=False):
        """Create options box - COMPACT VERSION."""
        box = QGroupBox("⚙️ Mode")
        
        border_color = "rgba(155,89,182,0.6)" if is_niche else "rgba(128,128,128,0.6)"
        title_bg = "rgba(155,89,182,0.4)" if is_niche else "rgba(27,86,253,0.4)"
        checked_color = "rgb(155,89,182)" if is_niche else "rgb(34, 81, 200)"
        
        box.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 8px;
                margin-top: 8px;
                background-color: rgba(128,128,128,0.15);
                font-weight: bold;
                min-width: 140px;
                max-width: 180px;
                font-size: 9pt;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 3px 8px;
                border-radius: 4px;
                background-color: {title_bg};
                color: white;
            }}
        """)
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Radio buttons
        radio_group = QButtonGroup(box)
        radio_buttons = {}
        
        if is_niche:
            modes = [
                ("Share to All", "All groups"),
                ("Round Robin", "Rotate"),
                ("1 to 1 Posting", "Direct"),
                ("Randomize", "Random")
            ]
        else:
            modes = [
                ("1 to 1 Posting", "Direct"),
                ("Share to All", "All groups"),
                ("Randomize", "Random"),
                ("Round Robin", "Rotate")
            ]
        
        for idx, (text, tooltip) in enumerate(modes):
            radio = QRadioButton(text)
            radio.setToolTip(tooltip)
            
            font_size = "10pt" if (is_niche and text == "Share to All") else "9pt"
            
            radio.setStyleSheet(f"""
                QRadioButton {{
                    spacing: 6px;
                    color: #eeeeee;
                    font-weight: bold;
                    font-size: {font_size};
                }}
                QRadioButton::indicator {{
                    width: 14px;
                    height: 14px;
                    border-radius: 7px;
                    border: 2px solid rgba(128,128,128,0.8);
                    background-color: rgba(128,128,128,0.3);
                }}
                QRadioButton::indicator:checked {{
                    background-color: {checked_color};
                    border: 2px solid {checked_color};
                }}
            """)
            radio.toggled.connect(self.mark_unsaved_changes)
            radio_group.addButton(radio)
            radio_buttons[text] = radio
            layout.addWidget(radio)
        
        default_mode = "Share to All" if is_niche else "1 to 1 Posting"
        radio_buttons[default_mode].setChecked(True)
        
        layout.addStretch()
        box.setLayout(layout)
        box.radio_buttons = radio_buttons
        box.radio_group = radio_group
        
        return box

    def update_group_count(self, text_box, count_label):
        """Update group count label."""
        groups = self.parse_groups(text_box.toPlainText())
        count = len(groups)
        count_label.setText(f"📊 {count}")
        
        if count == 0:
            color = "rgba(231,76,60,0.3)"
            text_color = "#e74c3c"
        elif count < 5:
            color = "rgba(230,126,34,0.3)"
            text_color = "#e67e22"
        else:
            color = "rgba(46,204,113,0.3)"
            text_color = "#46cc71"
        
        count_label.setStyleSheet(f"""
            background-color: {color};
            color: {text_color};
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 8pt;
        """)

    def parse_groups(self, text):
        """Parse groups from text."""
        return [line.strip() for line in text.strip().split('\n') if line.strip()]

    def get_selected_mode(self, options_box):
        """Get selected mode from radio buttons."""
        for mode, radio in options_box.radio_buttons.items():
            if radio.isChecked():
                return mode
        return "1 to 1 Posting"

    def validate_groups(self, text_box):
        """Validate groups."""
        groups = self.parse_groups(text_box.toPlainText())
        
        if not groups:
            QMessageBox.warning(self, "Validation", "❌ Empty list!")
        else:
            msg = f"✅ {len(groups)} group(s)"
            QMessageBox.information(self, "Valid", msg)

    def reset_textbox_border(self, text_box):
        """Reset textbox border."""
        pass

    def show_preview(self, left_box, right_box, options_box):
        """Show preview."""
        from_groups = self.parse_groups(left_box.text_box.toPlainText())
        to_groups = self.parse_groups(right_box.text_box.toPlainText())
        
        if not from_groups or not to_groups:
            QMessageBox.warning(self, "Preview", "❌ Fill both lists!")
            return
        
        mode = self.get_selected_mode(options_box)
        dialog = PreviewDialog(from_groups, to_groups, mode, self)
        dialog.exec()

    def show_niche_preview(self, niche_input, left_box, right_box, options_box):
        """Show niche preview."""
        niche_name = niche_input.text().strip()
        from_groups = self.parse_groups(left_box.text_box.toPlainText())
        to_groups = self.parse_groups(right_box.text_box.toPlainText())
        
        if not niche_name or not from_groups or not to_groups:
            QMessageBox.warning(self, "Preview", "❌ Fill all fields!")
            return
        
        mode = self.get_selected_mode(options_box)
        dialog = PreviewDialog(from_groups, to_groups, f"{mode} ({niche_name})", self)
        dialog.exec()

    def add_method_block(self):
        """Add method block."""
        block = self.create_method_block("Methods", "Methods")
        self.normal_main_layout.insertWidget(self.normal_main_layout.count() - 1, block)
        self.method_blocks.append(block)
        self.mark_unsaved_changes()

    def remove_method_block(self, block):
        """Remove method block."""
        if len(self.method_blocks) <= 1:
            QMessageBox.warning(self, "Cannot Remove", "⚠️ Keep at least one!")
            return
        
        block.deleteLater()
        self.method_blocks.remove(block)
        self.mark_unsaved_changes()

    def add_niche_block(self):
        """Add niche block."""
        block = self.create_niche_block("New Niche")
        self.niche_main_layout.insertWidget(self.niche_main_layout.count() - 1, block)
        self.niche_blocks.append(block)
        self.mark_unsaved_changes()

    def remove_niche_block(self, block):
        """Remove niche block."""
        if len(self.niche_blocks) <= 1:
            QMessageBox.warning(self, "Cannot Remove", "⚠️ Keep at least one!")
            return
        
        block.deleteLater()
        self.niche_blocks.remove(block)
        self.mark_unsaved_changes()

    def mark_unsaved_changes(self):
        """Mark unsaved changes."""
        self.has_unsaved_changes = True
        if not self.windowTitle().endswith("*"):
            self.setWindowTitle(self.windowTitle() + " *")

    def clear_unsaved_changes(self):
        """Clear unsaved changes flag."""
        self.has_unsaved_changes = False
        self.setWindowTitle(self.windowTitle().replace(" *", ""))

    def clear_all(self):
        """Clear all configurations."""
        reply = QMessageBox.question(self, "Clear All", "🗑️ Clear all?", QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            while len(self.method_blocks) > 1:
                block = self.method_blocks[-1]
                block.deleteLater()
                self.method_blocks.remove(block)
            
            if self.method_blocks:
                block = self.method_blocks[0]
                block.left_box.text_box.clear()
                block.right_box.text_box.clear()
            
            while len(self.niche_blocks) > 1:
                block = self.niche_blocks[-1]
                block.deleteLater()
                self.niche_blocks.remove(block)
            
            if self.niche_blocks:
                block = self.niche_blocks[0]
                block.niche_input.setText("Technology")
                block.left_box.text_box.clear()
                block.right_box.text_box.clear()
            
            self.notification.show_message("✅ Cleared!", True)
            self.mark_unsaved_changes()

    def auto_load_config(self):
        """Auto-load config."""
        if os.path.exists(self.config_file):
            try:
                self.load_config(silent=True)
            except:
                pass

    def load_config(self, silent=False):
        """Load configuration."""
        if not os.path.exists(self.config_file):
            if not silent:
                QMessageBox.warning(self, "Load", "❌ No config found!")
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Clear existing
            while len(self.method_blocks) > 0:
                self.method_blocks[-1].deleteLater()
                self.method_blocks.pop()
            
            while len(self.niche_blocks) > 0:
                self.niche_blocks[-1].deleteLater()
                self.niche_blocks.pop()
            
            # Load normal
            for method_config in config.get("normal_sharing", []):
                block = self.create_method_block("Methods", "Methods")
                block.enable_checkbox.setChecked(method_config.get("enabled", True))
                block.left_box.text_box.setPlainText("\n".join(method_config.get("from_groups", [])))
                block.right_box.text_box.setPlainText("\n".join(method_config.get("to_groups", [])))
                
                mode = method_config.get("mode", "1 to 1 Posting")
                if mode in block.options_box.radio_buttons:
                    block.options_box.radio_buttons[mode].setChecked(True)
                
                self.normal_main_layout.insertWidget(self.normal_main_layout.count() - 1, block)
                self.method_blocks.append(block)
            
            # Load niche
            for niche_config in config.get("niche_sharing", []):
                niche_name = niche_config.get("niche_name", "New Niche")
                block = self.create_niche_block(niche_name)
                block.enable_checkbox.setChecked(niche_config.get("enabled", True))
                block.niche_input.setText(niche_name)
                block.left_box.text_box.setPlainText("\n".join(niche_config.get("from_groups", [])))
                block.right_box.text_box.setPlainText("\n".join(niche_config.get("to_groups", [])))
                
                mode = niche_config.get("mode", "Share to All")
                if mode in block.options_box.radio_buttons:
                    block.options_box.radio_buttons[mode].setChecked(True)
                
                self.niche_main_layout.insertWidget(self.niche_main_layout.count() - 1, block)
                self.niche_blocks.append(block)
            
            # Ensure one block
            if not self.method_blocks:
                block = self.create_method_block("Methods", "Methods")
                self.normal_main_layout.insertWidget(self.normal_main_layout.count() - 1, block)
                self.method_blocks.append(block)
            
            if not self.niche_blocks:
                block = self.create_niche_block("Technology")
                self.niche_main_layout.insertWidget(self.niche_main_layout.count() - 1, block)
                self.niche_blocks.append(block)
            
            if not silent:
                self.notification.show_message("✅ Loaded!", True)
            self.clear_unsaved_changes()
            
        except Exception as e:
            if not silent:
                QMessageBox.critical(self, "Error", f"❌ Load failed:\n{e}")

    def save_config(self):
        """Save configuration."""
        config = {
            "normal_sharing": [],
            "niche_sharing": []
        }
        
        for block in self.method_blocks:
            config["normal_sharing"].append({
                "enabled": block.enable_checkbox.isChecked(),
                "from_groups": self.parse_groups(block.left_box.text_box.toPlainText()),
                "to_groups": self.parse_groups(block.right_box.text_box.toPlainText()),
                "mode": self.get_selected_mode(block.options_box)
            })
        
        for block in self.niche_blocks:
            config["niche_sharing"].append({
                "enabled": block.enable_checkbox.isChecked(),
                "niche_name": block.niche_input.text().strip(),
                "from_groups": self.parse_groups(block.left_box.text_box.toPlainText()),
                "to_groups": self.parse_groups(block.right_box.text_box.toPlainText()),
                "mode": self.get_selected_mode(block.options_box)
            })
        
        try:
            os.makedirs("User_Data", exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.notification.show_message("✅ Saved!", True)
            self.clear_unsaved_changes()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Save failed:\n{e}")

    def closeEvent(self, event):
        """Handle close event."""
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved",
                "⚠️ Save changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_config()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = GroupSharingUI()
    
    screen = app.primaryScreen().availableGeometry()
    
    # ✅ SMALLER SIZE
    width = min(900, int(screen.width() * 0.65))
    height = min(650, int(screen.height() * 0.7))
    
    ui.resize(width, height)
    ui.setMinimumSize(1000, 700)
    
    # Center
    ui.move(
        screen.x() + (screen.width() - ui.width()) // 2,
        screen.y() + (screen.height() - ui.height()) // 2
    )
    
    ui.show()
    sys.exit(app.exec())