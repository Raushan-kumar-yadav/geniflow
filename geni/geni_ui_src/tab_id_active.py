from PySide6.QtWidgets import (QFrame, QLabel, QCheckBox, QComboBox, QSpinBox, 
                               QDoubleSpinBox, QPushButton, QGridLayout, QHBoxLayout, QDialog,
                               QVBoxLayout, QWidget,QTextEdit,QLineEdit,QFileDialog,QApplication,QMainWindow,QAbstractSpinBox,QSizePolicy,QSizePolicy,QGroupBox,QMessageBox)
from PySide6.QtCore import Qt, QSize, Signal, Property,QPropertyAnimation
from PySide6.QtGui import QFont

import os
import json




class make_id_active_frame(QFrame):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Set frame styling - equivalent to border settings in ctk
        self.setStyleSheet("""
            MakeIdActiveFrame {
                border: 2px solid gray;
                border-radius: 8px;
            }
        """)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        
        # Add placeholder text
        self.placeholder_label = QLabel("Please select a frame to view options")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.placeholder_label)
        #self.main_layout.setContentsMargins(5, 5, 5, 5)
        
    def create_frame(self, id_frame_idx, json_path):
        # Clear existing widgets - remove all widgets from the layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            id_key = f"Id_information.{id_frame_idx}"
            id_names = []
            id_name = data[id_key].get("id_name", "")
            
            id_names.append(id_name)
            
            if id_names:
                # Set main folder value
                main_folder = data[id_key].get("Main_folder_path", "")
                chrome_instance_path = data[id_key].get("chrome_instance_path", "")
                
                # Create ID configuration widget - we'll assume id_configuration is also converted to PySide6
                self.page_config_instance = IdConfiguration(
                    master=self,
                    combo_button_value=id_names,
                    id_frame_idx=id_frame_idx,
                    json_file_path=json_path,
                    main_folder_path=main_folder
                )
                
                # Add the widget to layout
                self.main_layout.addWidget(self.page_config_instance)
                
                # Commented out code in the original is also commented out here
                # if main_folder:
                #     self.page_config_instance.main_folder_path.set(main_folder)
                #
                # if chrome_instance_path:
                #     self.page_config_instance.chorme_instance_path.set(chrome_instance_path)
                
            else:
                print(f"{id_key} not found in JSON data.")
        
        except Exception as e:
            print("Error loading id_information:", e)

class IdConfiguration(QFrame):
    def __init__(self, master, main_folder_path, combo_button_value=[], id_frame_idx=1, json_file_path=None, **kwargs):
        super().__init__(master)
    
        
        self.json_file_path = json_file_path
        self.combo_button_value = combo_button_value
        self.id_frame_idx = id_frame_idx
        self.current_profile = combo_button_value[0] if combo_button_value else ""
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        #self.main_layout.setContentsMargins(10, 10, 10, 10)
        #self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignTop)
        
        # Initialize all variables
        self.init_variables(main_folder_path)
        
        # Create all UI elements
        self._create_widget()
        
        # Load profile configuration
        if combo_button_value:
            self.run_add_profile_config_ones(value=self.combo_button_value)

        self.add_id_active_config_config()
    def init_variables(self, main_folder_path):
        # Initialize all the boolean and string variables
        
        # Main paths
        self.main_folder_path = main_folder_path
        self.chorme_instance_path = ""
        self.reels_history_xlsx_path = ""
        
        # Checkbox states - using boolean
        self.shuffle_check_box_enable = False
        self.post_photo_enable = False
        self.is_post_checkin_enable_var = False
        self.is_create_stroy_enable_var = False
        self.check_notification_enable = False
        self.is_check_msg_enable = False
        self.reply_msg_enable = False
        self.add_friend_enable = False
        self.confirm_friend_enable = False
        self.is_scroll_reels_enable_var = False
        self.is_scroll_video_enable_var = False
        self.is_scroll_feed_enable_var = False
        
        # Scroll reels/video settings
        self.scroll_reels_video_is_like_post_enable_var = False
        self.scroll_reels_video_is_react_post_enable_var = False
        self.scroll_reels_video_comments_is_enable_var = False
        self.scroll_reels_video_groups_is_enable_var = False
        self.scroll_reels_video_share_post_to_story_is_enable_var = False
        
        # Scroll feed settings
        self.scroll_feed_is_like_post_enable_var = False
        self.scroll_feed_is_react_post_enable_var = False
        self.scroll_feed_comments_is_enable_var = False
        self.scroll_feed_groups_is_enable_var = False
        self.scroll_feed_share_post_to_story_is_enable_var = False
        
        # Photo post settings
        self.photo_post_image_folder = ""
        self.photo_post_download_image_folder  = ""
        self.photo_captions_from_var = ""
        self.photo_captions_txt_file_path_var = ""
        self.photo_captions_text_box_var = ""
        self.photo_Random_var = ""
        
        # Check-in post settings
        self.post_checkin_num_var = 1
        self.post_checkin_Download_photo_Folder = ""
        self.add_photo_to_checkin_post_var = False
        self.location_of_checkin_post_var = ""
        self.post_checkin_ld_photo_folder = ""
        self.post_checkin_captions_from_var = ""
        self.post_checkin_captions_txt_file_path_var = ""
        self.checkin_photo_captions_txt_file_path_var = ""
        self.post_checkin_captions_text_box_var = ""
        self.post_checkin_text_caption_Random_var = ""
        
        # Story settings
        self.story_video_Download_Folder = ""
        self.story_video_Folder = ""
        self.story_video_captions_from_var = ""
        self.story_video_captions_txt_file_path_var = ""
        self.story_video_captions_text_box_var = ""
        self.story_video_text_caption_Random_var = ""
        
        # Check messages settings
        self.check_msg_min_min = ""
        self.check_msg_max_min = ""
        self.reply_msg_min_chat = ""
        self.reply_msg_max_chat = ""
        
        # Add friends settings
        self.add_friend_min_frid = ""
        self.add_friend_max_frid = ""
        self.confirm_friend_min_frid = ""
        self.confirm_friend_max_frid = ""
        
        # Scroll reels/video interactions
        self.scroll_reels_video_like_post_prob_var = ""
        self.scroll_reels_video_react_post_prob_var = ""
        self.scroll_reels_video_comments_prob_var = ""
        self.scroll_reels_video_comments_txt_box_var = ""
        self.scroll_reels_video_comments_from_var = ""
        self.scroll_reels_video_comments_txt_file_random_var = ""
        self.scroll_reels_video_comments_txt_file_path_var = ""
        self.scroll_reels_video_groups_prob_var = ""
        self.scroll_reels_video_groups_txt_box_var = ""
        self.scroll_reels_video_groups_from_var = ""
        self.scroll_reels_video_groups_txt_file_random = ""
        self.scroll_reels_video_groups_txt_file_path_var = ""
        
        # Scroll feed interactions
        self.scroll_feed_like_post_prob_var = ""
        self.scroll_feed_react_post_prob_var = ""
        self.scroll_feed_comments_prob_var = ""
        self.scroll_feed_comments_txt_box_var = ""
        self.scroll_feed_comments_from_var = ""
        self.scroll_feed_comments_txt_file_random = ""
        self.scroll_feed_comments_txt_file_path_var = ""
        self.scroll_feed_groups_prob_var = ""
        self.scroll_feed_groups_txt_box_var = ""
        self.scroll_feed_groups_from_var = ""
        self.scroll_feed_groups_txt_file_random = ""
        self.scroll_feed_groups_txt_file_path_var = ""
        self.scroll_feed_share_post_to_story_prob_var = ""


        
    def _create_widget(self):
        # Profile selection frame
        profile_frame = QFrame()
        profile_frame.setFrameShape(QFrame.Box)
        profile_frame.setLineWidth(2)
        profile_frame.setStyleSheet("QFrame { border:none;  background-color: transparent; }")
        profile_layout = QGridLayout(profile_frame)
        
        profile_label = QLabel("ID Name: ")
        profile_label.setStyleSheet("font-weight: bold; font-size: 15px;border:none;")
        profile_layout.addWidget(profile_label, 0, 0)
        
        self.combo_button = QComboBox()
        self.combo_button.addItems(self.combo_button_value)
        profile_layout.addWidget(self.combo_button, 0, 1)
        profile_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.addWidget(profile_frame)
        

        
        # ID active options frame
        id_active_options_frame = QGroupBox()
        id_active_options_frame.setObjectName("id_active_options_frame")
        id_active_options_frame.setTitle("Configure Id Active")
        id_active_options_frame.setStyleSheet("""QGroupBox#id_active_options_frame{border:2px solid rgba(128,128,128,1);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:5px;
                                    padding-right:5px;
                                    padding-left:5px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.1);}
                                            QGroupBox#id_active_options_frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        id_active_layout = QVBoxLayout(id_active_options_frame)
        id_active_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create sub-frames for organization
        scroll_reels_video_feed_frame = QWidget()
        scroll_reels_video_feed_layout = QHBoxLayout(scroll_reels_video_feed_frame)
        scroll_reels_video_feed_layout.setContentsMargins(5, 5, 5, 5)
        id_active_layout.addWidget(scroll_reels_video_feed_frame)
        
        check_msg_and_other_options_frame = QWidget()
        check_msg_layout = QHBoxLayout(check_msg_and_other_options_frame)
        check_msg_layout.setContentsMargins(5, 0, 5, 0)
        id_active_layout.addWidget(check_msg_and_other_options_frame)
        
        photo_and_checkin_frame = QWidget()
        photo_checkin_layout = QHBoxLayout(photo_and_checkin_frame)
        photo_checkin_layout.setContentsMargins(5, 0, 5, 0)
        id_active_layout.addWidget(photo_and_checkin_frame)
        
        create_story_main_frame = QWidget()
        create_story_layout = QHBoxLayout(create_story_main_frame)
        create_story_layout.setContentsMargins(5, 0, 5, 10)
        id_active_layout.addWidget(create_story_main_frame)
        
        # ---- SCROLL VIDEO FEED FRAME ----
        scroll_video_feed_frame = QFrame()
        scroll_video_feed_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.2);}""")
        scroll_video_feed_layout = QVBoxLayout(scroll_video_feed_frame)
        
        # Scroll video feed buttons frame
        scroll_video_feed_btn_frame = QWidget()
        scroll_btn_layout = QGridLayout(scroll_video_feed_btn_frame)
        scroll_btn_layout.setContentsMargins(10, 10, 10, 5)
        
        # Scroll reels feed row
        self.scroll_reels_feed_check_box_btn = QCheckBox("Scroll Reels")
        self.scroll_reels_feed_check_box_btn.setStyleSheet("font-weight: bold; font-size: 12px;")
        scroll_btn_layout.addWidget(self.scroll_reels_feed_check_box_btn, 0, 0)
        self.scroll_reels_feed_check_box_btn.clicked.connect(lambda: setattr(self, 'is_scroll_reels_enable_var', self.scroll_reels_feed_check_box_btn.isChecked()))
        self.scroll_reels_feed_check_box_btn.clicked.connect(lambda:self.save_id_active_config())
        self.scroll_reels_feed_min_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        scroll_btn_layout.addWidget(self.scroll_reels_feed_min_intspain_box, 0, 1)
        
        scroll_reels_to_label = QLabel("To")
        scroll_reels_to_label.setStyleSheet("border:none;")
        scroll_btn_layout.addWidget(scroll_reels_to_label, 0, 2)
        
        self.scroll_reels_max_min_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        scroll_btn_layout.addWidget(self.scroll_reels_max_min_intspain_box, 0, 3)
        
        scroll_reels_min_label = QLabel("Min")
        scroll_reels_min_label.setStyleSheet("border:none;")
        scroll_btn_layout.addWidget(scroll_reels_min_label, 0, 4)
        
        # Scroll video feed row
        self.scroll_video_feed_combo_btn = QCheckBox("Scroll Video Feed")
        self.scroll_video_feed_combo_btn.setStyleSheet("font-weight: bold; font-size: 12px;")
        scroll_btn_layout.addWidget(self.scroll_video_feed_combo_btn, 1, 0)
        self.scroll_video_feed_combo_btn.clicked.connect(lambda: setattr(self, 'is_scroll_video_enable_var', self.scroll_video_feed_combo_btn.isChecked()))
        self.scroll_video_feed_combo_btn.clicked.connect(lambda:self.save_id_active_config())
        
        self.scroll_video_feed_min_min_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        scroll_btn_layout.addWidget(self.scroll_video_feed_min_min_intspain_box, 1, 1)
        
        scroll_video_to_label = QLabel("To")
        scroll_video_to_label.setStyleSheet("border:none;")
        scroll_btn_layout.addWidget(scroll_video_to_label, 1, 2)
        
        self.scroll_video_feed_max_min_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        scroll_btn_layout.addWidget(self.scroll_video_feed_max_min_intspain_box, 1, 3)
        
        scroll_video_min_label = QLabel("Min")
        scroll_video_min_label.setStyleSheet("border:none;")
        scroll_btn_layout.addWidget(scroll_video_min_label, 1, 4)
        
        scroll_video_feed_layout.addWidget(scroll_video_feed_btn_frame)
        
        # Scroll video feed options frame 
        scroll_video_feed_options_frame = QFrame()
        scroll_video_feed_options_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.1);}""")
        scroll_options_layout = QGridLayout(scroll_video_feed_options_frame)

        # Like posts row
        self.scroll_video_feed_like_post_check_box = QCheckBox("Like Posts")
        scroll_options_layout.addWidget(self.scroll_video_feed_like_post_check_box, 0, 0)
        self.scroll_video_feed_like_post_check_box.clicked.connect(lambda: setattr(self, 'scroll_reels_video_is_like_post_enable_var', self.scroll_video_feed_like_post_check_box.isChecked()))
        self.scroll_video_feed_like_post_check_box.clicked.connect(lambda:self.save_id_active_config())
        self.scroll_video_feed_like_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_options_layout.addWidget(self.scroll_video_feed_like_prob_intspain_box, 0, 1)
        
        scroll_video_feed_like_prob_label = QLabel("Prob")
        scroll_video_feed_like_prob_label.setStyleSheet("border:none;")
        scroll_options_layout.addWidget(scroll_video_feed_like_prob_label, 0, 2)
        
        # React to posts row
        self.scroll_video_feed_react_post_check_box = QCheckBox("React To Posts")
        scroll_options_layout.addWidget(self.scroll_video_feed_react_post_check_box, 1, 0)
        self.scroll_video_feed_react_post_check_box.clicked.connect(lambda: setattr(self, 'scroll_reels_video_is_react_post_enable_var', self.scroll_video_feed_react_post_check_box.isChecked()))
        self.scroll_video_feed_react_post_check_box.clicked.connect(lambda:self.save_id_active_config())
        
        self.scroll_video_feed_react_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_options_layout.addWidget(self.scroll_video_feed_react_prob_intspain_box, 1, 1)
        
        scroll_video_feed_react_prob_label = QLabel("Prob")
        scroll_video_feed_react_prob_label.setStyleSheet("border:none;")
        scroll_options_layout.addWidget(scroll_video_feed_react_prob_label, 1, 2)
        
        # Comment on posts row
        self.scroll_video_feed_comment_on_post_check_box = QCheckBox("Comment On Posts")
        scroll_options_layout.addWidget(self.scroll_video_feed_comment_on_post_check_box, 2, 0)
        self.scroll_video_feed_comment_on_post_check_box.clicked.connect(lambda: setattr(self, 'scroll_reels_video_comments_is_enable_var', self.scroll_video_feed_comment_on_post_check_box.isChecked()))
        self.scroll_video_feed_comment_on_post_check_box.clicked.connect(lambda:self.save_id_active_config())

        
        self.scroll_video_feed_comment_on_post_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_options_layout.addWidget(self.scroll_video_feed_comment_on_post_prob_intspain_box, 2, 1)
        
        scroll_video_feed_comment_on_post_prob_label = QLabel("Prob")
        scroll_video_feed_comment_on_post_prob_label.setStyleSheet("border:none;")
        scroll_options_layout.addWidget(scroll_video_feed_comment_on_post_prob_label, 2, 2)
        
        scroll_video_feed_comment_on_post_divider_label = self.create_vertical_line()
        scroll_options_layout.addWidget(scroll_video_feed_comment_on_post_divider_label, 2, 3)
        scroll_options_layout.setAlignment(Qt.AlignLeft)

        #scroll_options_layout.setVerticalSpacing(10)
        scroll_video_feed_comment_on_post_config_btn = AnimatedHoverButton(text="Config")
        scroll_video_feed_comment_on_post_config_btn.setFixedSize(50, 20)
        scroll_video_feed_comment_on_post_config_btn.clicked.connect(self.open_scroll_reels_videos_comments_config)
        scroll_options_layout.addWidget(scroll_video_feed_comment_on_post_config_btn, 2, 4)
        
        # Share post to groups row
        self.scroll_video_feed_share_post_to_groups_check_box = QCheckBox("Share Post To Groups")
        self.scroll_video_feed_share_post_to_groups_check_box.clicked.connect(lambda:self.save_id_active_config())
        scroll_options_layout.addWidget(self.scroll_video_feed_share_post_to_groups_check_box, 3, 0)

        
        self.scroll_video_feed_share_random_post_to_groups_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_options_layout.addWidget(self.scroll_video_feed_share_random_post_to_groups_prob_intspain_box, 3, 1)
        
        scroll_video_feed_share_random_post_to_groups_prob_label = QLabel("Prob")
        scroll_video_feed_share_random_post_to_groups_prob_label.setStyleSheet("border:none;")
        scroll_options_layout.addWidget(scroll_video_feed_share_random_post_to_groups_prob_label, 3, 2)
        
        scroll_video_feed_share_random_post_divider_label = self.create_vertical_line()
        scroll_options_layout.addWidget(scroll_video_feed_share_random_post_divider_label, 3, 3)

        
        scroll_video_feed_share_random_post_config_btn = AnimatedHoverButton(text="Config")
        scroll_video_feed_share_random_post_config_btn.setFixedSize(50, 20)
        scroll_video_feed_share_random_post_config_btn.clicked.connect(self.open_scroll_reels_videos_groups_config)
        scroll_options_layout.addWidget(scroll_video_feed_share_random_post_config_btn, 3, 4)
        
        # Share post to story row
        self.scroll_video_feed_share_post_to_story_check_box = QCheckBox("Share Post To Story")
        self.scroll_video_feed_share_post_to_story_check_box.clicked.connect(lambda:self.save_id_active_config())
        scroll_options_layout.addWidget(self.scroll_video_feed_share_post_to_story_check_box, 4, 0)

        
        self.scroll_video_feed_share_random_post_to_story_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_options_layout.addWidget(self.scroll_video_feed_share_random_post_to_story_prob_intspain_box, 4, 1)
        
        scroll_video_feed_share_random_post_to_story_prob_label = QLabel("Prob")
        scroll_video_feed_share_random_post_to_story_prob_label.setStyleSheet("border:none;")
        scroll_options_layout.addWidget(scroll_video_feed_share_random_post_to_story_prob_label, 4, 2)
        #scroll_options_layout.setAlignment(Qt.AlignLeft)
        scroll_video_feed_layout.addWidget(scroll_video_feed_btn_frame)
        scroll_video_feed_layout.addWidget(scroll_video_feed_options_frame)
        scroll_reels_video_feed_layout.addWidget(scroll_video_feed_frame)
        scroll_reels_video_feed_layout.setAlignment(Qt.AlignLeft)
        




        # ------------------ SCROLL FEED FRAME ---------------------------------------
        
        scroll_feed_frame = QFrame()
        scroll_feed_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.2);}""")
        scroll_feed_layout = QVBoxLayout(scroll_feed_frame)
        
        # Scroll feed buttons frame 
        scroll_feed_btn_frame = QWidget()
        scroll_feed_btn_layout = QGridLayout(scroll_feed_btn_frame)
        #scroll_feed_btn_layout.setContentsMargins(10, 10, 10, 5)
        
        self.scroll_feed_checkbox_btn = QCheckBox("Scroll Feed")
        self.scroll_feed_checkbox_btn.setStyleSheet("font-weight: bold; font-size: 12px;")
        scroll_feed_btn_layout.addWidget(self.scroll_feed_checkbox_btn, 0, 0)
        self.scroll_feed_checkbox_btn.clicked.connect(lambda: setattr(self, 'is_scroll_feed_enable_var', self.scroll_feed_checkbox_btn.isChecked()))
        self.scroll_feed_checkbox_btn.clicked.connect(lambda:self.save_id_active_config())
        
        self.scroll_feed_min_min_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        scroll_feed_btn_layout.addWidget(self.scroll_feed_min_min_intspain_box, 0, 1)
        
        scroll_feed_to_label = QLabel("To")
        scroll_feed_to_label.setStyleSheet("border:none;")
        scroll_feed_btn_layout.addWidget(scroll_feed_to_label, 0, 2)
        
        self.scroll_feed_max_min_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        scroll_feed_btn_layout.addWidget(self.scroll_feed_max_min_intspain_box, 0, 3)
        
        scroll_feed_min_label = QLabel("Min")
        scroll_feed_min_label.setStyleSheet("border:none;")
        scroll_feed_btn_layout.addWidget(scroll_feed_min_label, 0, 4)
        
        scroll_feed_layout.addWidget(scroll_feed_btn_frame)

        
        # 1. Scroll feed options frame - similar to scroll video feed options
        scroll_feed_options_frame = QFrame()
        scroll_feed_options_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.1);}""")
        scroll_feed_options_layout = QGridLayout(scroll_feed_options_frame)

        # Like posts row
        self.scroll_feed_like_post_check_box = QCheckBox("Like Posts")
        scroll_feed_options_layout.addWidget(self.scroll_feed_like_post_check_box, 0, 0)
        self.scroll_feed_like_post_check_box.clicked.connect(lambda:self.save_id_active_config())

        
        self.scroll_feed_like_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_feed_options_layout.addWidget(self.scroll_feed_like_prob_intspain_box, 0, 1)
        
        scroll_feed_feed_like_prob_label = QLabel("Prob")
        scroll_feed_feed_like_prob_label.setStyleSheet("border:none;")
        scroll_feed_options_layout.addWidget(scroll_feed_feed_like_prob_label, 0, 2)
        
        # React to posts row
        self.scroll_feed_react_post_check_box = QCheckBox("React To Posts")
        scroll_feed_options_layout.addWidget(self.scroll_feed_react_post_check_box, 1, 0)
        self.scroll_feed_react_post_check_box.clicked.connect(lambda:self.save_id_active_config())

        
        self.scroll_feed_react_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_feed_options_layout.addWidget(self.scroll_feed_react_prob_intspain_box, 1, 1)
        
        scroll_feed_feed_react_prob_label = QLabel("Prob")
        scroll_feed_feed_react_prob_label.setStyleSheet("border:none;")
        scroll_feed_options_layout.addWidget(scroll_feed_feed_react_prob_label, 1, 2)
        
        # Comment on posts row
        self.scroll_feed_comment_on_post_check_box = QCheckBox("Comment On Posts")
        scroll_feed_options_layout.addWidget(self.scroll_feed_comment_on_post_check_box, 2, 0)
        self.scroll_feed_comment_on_post_check_box.clicked.connect(lambda:self.save_id_active_config())

        
        self.scroll_feed_comment_on_post_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_feed_options_layout.addWidget(self.scroll_feed_comment_on_post_prob_intspain_box, 2, 1)
        
        scroll_feed_feed_comment_on_post_prob_label = QLabel("Prob")
        scroll_feed_feed_comment_on_post_prob_label.setStyleSheet("border:none;")
        scroll_feed_options_layout.addWidget(scroll_feed_feed_comment_on_post_prob_label, 2, 2)
        
        scroll_feed_feed_comment_on_post_divider_label = self.create_vertical_line()
        scroll_feed_options_layout.addWidget(scroll_feed_feed_comment_on_post_divider_label, 2, 3)
        
        scroll_feed_feed_comment_on_post_config_btn = AnimatedHoverButton(text="Config")
        scroll_feed_feed_comment_on_post_config_btn.setFixedSize(50, 20)
        scroll_feed_feed_comment_on_post_config_btn.clicked.connect(self.open_scroll_feed_comments_config)
        scroll_feed_options_layout.addWidget(scroll_feed_feed_comment_on_post_config_btn, 2, 4)
        #scroll_feed_options_layout.setVerticalSpacing(10)


        # Share post to groups row
        self.scroll_feed_share_post_to_groups_check_box = QCheckBox("Share Post To Groups")
        self.scroll_feed_share_post_to_groups_check_box.clicked.connect(lambda:self.save_id_active_config())
        scroll_feed_options_layout.addWidget(self.scroll_feed_share_post_to_groups_check_box, 3, 0)
        
        self.scroll_feed_share_random_post_to_groups_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_feed_options_layout.addWidget(self.scroll_feed_share_random_post_to_groups_prob_intspain_box, 3, 1)
        
        scroll_feed_feed_share_random_post_to_groups_prob_label = QLabel("Prob")
        scroll_feed_feed_share_random_post_to_groups_prob_label.setStyleSheet("border:none;")
        scroll_feed_options_layout.addWidget(scroll_feed_feed_share_random_post_to_groups_prob_label, 3, 2)
        
        scroll_feed_feed_share_random_post_divider_label = self.create_vertical_line()
        scroll_feed_options_layout.addWidget(scroll_feed_feed_share_random_post_divider_label, 3, 3)
        scroll_feed_options_layout.setAlignment(Qt.AlignLeft)
        
        scroll_feed_feed_share_random_post_config_btn = AnimatedHoverButton(text="Config")
        scroll_feed_feed_share_random_post_config_btn.setFixedSize(50, 20)
        scroll_feed_feed_share_random_post_config_btn.clicked.connect(self.open_scroll_feed_groups_config)
        scroll_feed_options_layout.addWidget(scroll_feed_feed_share_random_post_config_btn, 3, 4)
        
        # Share post to story row
        self.scroll_feed_share_post_to_story_check_box = QCheckBox("Share Post To Story")
        self.scroll_feed_share_post_to_story_check_box.clicked.connect(lambda:self.save_id_active_config())
        scroll_feed_options_layout.addWidget(self.scroll_feed_share_post_to_story_check_box, 4, 0)
        
        self.scroll_feed_share_random_post_to_story_prob_intspain_box = SmallIntSpinBox(save_callback=self.save_id_active_config)
        scroll_feed_options_layout.addWidget(self.scroll_feed_share_random_post_to_story_prob_intspain_box, 4, 1)
        
        scroll_feed_feed_share_random_post_to_story_prob_label = QLabel("Prob")
        scroll_feed_feed_share_random_post_to_story_prob_label.setStyleSheet("border:none;")
        scroll_feed_options_layout.addWidget(scroll_feed_feed_share_random_post_to_story_prob_label, 4, 2)
        
        scroll_feed_layout.addWidget(scroll_feed_btn_frame)
        scroll_feed_layout.addWidget(scroll_feed_options_frame)
        scroll_reels_video_feed_layout.addWidget(scroll_feed_frame)
        
        scroll_feed_layout.addWidget(scroll_feed_options_frame)
        scroll_reels_video_feed_layout.addWidget(scroll_feed_frame)
        




        # 2. Check message and reply frame
        check_msg_reply_frame = QFrame()
        check_msg_reply_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.2);}""")
        check_msg_layout.addWidget(check_msg_reply_frame)
        
        check_msg_reply_layout = QGridLayout(check_msg_reply_frame)
        
        # Check Message
        self.check_msg_check_box = QCheckBox("Check Message")
        self.check_msg_check_box.setFont("arial 12 bold")
        check_msg_reply_layout.addWidget(self.check_msg_check_box, 0, 0, 1, 1, Qt.AlignLeft)
        self.check_msg_check_box.clicked.connect(lambda:self.save_id_active_config())
        
        self.check_msg_min_min_int_spinbox = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        check_msg_reply_layout.addWidget(self.check_msg_min_min_int_spinbox, 0, 1, 1, 1, Qt.AlignLeft)
        
        check_msg_to_label = QLabel("To")
        check_msg_to_label.setStyleSheet("border:none;")
        check_msg_reply_layout.addWidget(check_msg_to_label, 0, 2, 1, 1)
        
        self.check_msg_max_min_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        check_msg_reply_layout.addWidget(self.check_msg_max_min_intspain_box, 0, 3, 1, 1, Qt.AlignLeft)
        
        check_msg_min_label = QLabel("Min")
        check_msg_min_label.setStyleSheet("border:none;")
        check_msg_reply_layout.addWidget(check_msg_min_label, 0, 4, 1, 1, Qt.AlignLeft)
        
        # Reply to message
        self.reply_msg_check_box = QCheckBox("Reply Msg")
        self.reply_msg_check_box.setFont("arial 12 bold")
        self.reply_msg_check_box.clicked.connect(lambda:self.save_id_active_config())
        check_msg_reply_layout.addWidget(self.reply_msg_check_box, 1, 0, 1, 1, Qt.AlignLeft)
        
        self.reply_msgmin_chats_int_spinbox = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        check_msg_reply_layout.addWidget(self.reply_msgmin_chats_int_spinbox, 1, 1, 1, 1, Qt.AlignLeft)
        
        reply_msg_to_label = QLabel("To")
        reply_msg_to_label.setStyleSheet("border:none;")
        check_msg_reply_layout.addWidget(reply_msg_to_label, 1, 2, 1, 1)
        
        self.reply_msg_max_chats_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        check_msg_reply_layout.addWidget(self.reply_msg_max_chats_intspain_box, 1, 3, 1, 1, Qt.AlignLeft)
        
        reply_msg_min_label = QLabel("Chats")
        reply_msg_min_label.setStyleSheet("border:none;")
        check_msg_reply_layout.addWidget(reply_msg_min_label, 1, 4, 1, 1, Qt.AlignLeft)
        check_msg_reply_layout.setAlignment(Qt.AlignLeft)
 


        # 3. Add and confirm friends frame
        add_and_confirm_friends_frame = QFrame()
        add_and_confirm_friends_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.2);}""")
        check_msg_layout.addWidget(add_and_confirm_friends_frame)
        
        add_confirm_layout = QGridLayout(add_and_confirm_friends_frame)
        
        # Add Friends
        self.add_friends_box = QCheckBox("Add Friends")
        self.add_friends_box.setFont("arial 12 bold")
        self.add_friends_box.clicked.connect(lambda:self.save_id_active_config())
        add_confirm_layout.addWidget(self.add_friends_box, 0, 0, 1, 1, Qt.AlignLeft)
        
        self.add_friends_min_int_spinbox = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        add_confirm_layout.addWidget(self.add_friends_min_int_spinbox, 0, 1, 1, 1, Qt.AlignLeft)
        
        add_friends_to_label = QLabel("To")
        add_friends_to_label.setStyleSheet("border:none;")
        add_confirm_layout.addWidget(add_friends_to_label, 0, 2, 1, 1)
        
        self.add_friends_max_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        add_confirm_layout.addWidget(self.add_friends_max_intspain_box, 0, 3, 1, 1, Qt.AlignLeft)
        
        add_friends_min_label = QLabel("Friends")
        add_friends_min_label.setStyleSheet("border:none;")
        add_confirm_layout.addWidget(add_friends_min_label, 0, 4, 1, 1, Qt.AlignLeft)
        
        # Confirm friends
        self.confirm_friends_check_box = QCheckBox("Confirm Friends")
        self.confirm_friends_check_box.setFont("arial 12 bold")
        self.confirm_friends_check_box.clicked.connect(lambda:self.save_id_active_config())
        add_confirm_layout.addWidget(self.confirm_friends_check_box, 1, 0, 1, 1, Qt.AlignLeft)
        
        self.confirm_friends_min_int_spinbox = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        add_confirm_layout.addWidget(self.confirm_friends_min_int_spinbox, 1, 1, 1, 1, Qt.AlignLeft)
        
        confirm_friends_to_label = QLabel("To")
        confirm_friends_to_label.setStyleSheet("border:none;")
        add_confirm_layout.addWidget(confirm_friends_to_label, 1, 2, 1, 1)
        
        self.confirm_friends_max_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        add_confirm_layout.addWidget(self.confirm_friends_max_intspain_box, 1, 3, 1, 1, Qt.AlignLeft)
        add_confirm_layout.setAlignment(Qt.AlignLeft)
        confirm_friends_min_label = QLabel("Friends")
        confirm_friends_min_label.setStyleSheet("border:none;")
        add_confirm_layout.addWidget(confirm_friends_min_label, 1, 4, 1, 1, Qt.AlignLeft)
        





        # 4. Post photos frame
        
        post_photos_frame = QFrame()
        post_photos_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.2);}""")
        photo_checkin_layout.addWidget(post_photos_frame)
        
        post_photos_layout = QGridLayout(post_photos_frame)

        self.post_photos_check_box = QCheckBox("Post Photos")
        self.post_photos_check_box.setFont("arial 12 bold")
        self.post_photos_check_box.clicked.connect(lambda:self.save_id_active_config())
        post_photos_layout.addWidget(self.post_photos_check_box, 0, 0, 1, 1, Qt.AlignLeft)
        
        self.post_photos_int_spinbox = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        post_photos_layout.addWidget(self.post_photos_int_spinbox, 0, 1, 1, 1, Qt.AlignLeft)
        
        post_photos_num_label = QLabel("Posts")
        post_photos_num_label.setStyleSheet("border:none;")
        post_photos_layout.addWidget(post_photos_num_label, 0, 2, 1, 1, Qt.AlignBottom)
        
        post_photos_diff_label = self.create_vertical_line()
        post_photos_layout.addWidget(post_photos_diff_label, 0, 3, 1, 1)
        post_photos_layout.setAlignment(Qt.AlignLeft)
        post_photos_configure_label = QLabel("Config:")
        post_photos_configure_label.setStyleSheet("border:none;")
        post_photos_layout.addWidget(post_photos_configure_label, 0, 4, 1, 1)
        
        post_photos_configure_btn = AnimatedHoverButton(text="Config")
        post_photos_configure_btn.setFixedSize(50, 20)
        post_photos_configure_btn.clicked.connect(self.open_photo_config_window)
        post_photos_layout.addWidget(post_photos_configure_btn, 0, 5, 1, 1)
        
        
        
        # 5. Create post checkin frame
        create_post_checkin_frame = QFrame()
        create_post_checkin_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.2);}""")
        photo_checkin_layout.addWidget(create_post_checkin_frame)
        
        create_post_checkin_layout = QGridLayout(create_post_checkin_frame)
        
        self.create_post_checkin_check_box = QCheckBox("Post CheckIN")
        self.create_post_checkin_check_box.setFont("arial 12 bold")
        self.create_post_checkin_check_box.clicked.connect(lambda:self.save_id_active_config())
        create_post_checkin_layout.addWidget(self.create_post_checkin_check_box, 0, 0, 1, 1, Qt.AlignLeft)
        
        self.create_post_checkin_num_int_spinbox = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        create_post_checkin_layout.addWidget(self.create_post_checkin_num_int_spinbox, 0, 1, 1, 1, Qt.AlignLeft)
        
        create_post_checkin_num_label = QLabel("Posts")
        create_post_checkin_num_label.setStyleSheet("border:none;")
        create_post_checkin_layout.addWidget(create_post_checkin_num_label, 0, 2, 1, 1, Qt.AlignBottom)
        
        create_post_checkin_diff_label = self.create_vertical_line()
        create_post_checkin_layout.addWidget(create_post_checkin_diff_label, 0, 3, 1, 1)
        
        create_post_checkin_configure_label = QLabel("Config:")
        create_post_checkin_configure_label.setStyleSheet("border:none;")
        create_post_checkin_layout.addWidget(create_post_checkin_configure_label, 0, 4, 1, 1)
        
        create_post_checkin_configure_btn = AnimatedHoverButton("Config")
        create_post_checkin_configure_btn.setFixedSize(50, 20)
        create_post_checkin_configure_btn.clicked.connect(self.open_checkin_config_window)
        create_post_checkin_layout.addWidget(create_post_checkin_configure_btn, 0, 5, 1, 1)
        create_post_checkin_layout.setAlignment(Qt.AlignLeft)
        




        # 6. Create story frame
        create_story_frame = QFrame()
        create_story_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.2);}""")
        create_story_layout.addWidget(create_story_frame)
        
        story_layout = QGridLayout(create_story_frame)
        
        self.create_story_check_box = QCheckBox("Create Story")
        self.create_story_check_box.setFont("arial 12 bold")
        self.create_story_check_box.clicked.connect(lambda:self.save_id_active_config())
        story_layout.addWidget(self.create_story_check_box, 0, 0, 1, 1, Qt.AlignLeft)
        
        self.create_story_num_int_spinbox = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        story_layout.addWidget(self.create_story_num_int_spinbox, 0, 1, 1, 1, Qt.AlignLeft)
        
        create_story_num_label = QLabel("Posts")
        create_story_num_label.setStyleSheet("border:none;")
        story_layout.addWidget(create_story_num_label, 0, 2, 1, 1, Qt.AlignBottom)
        
        create_story_diff_label = self.create_vertical_line()
        story_layout.addWidget(create_story_diff_label, 0, 3, 1, 1)
        
        create_story_configure_label = QLabel("Config:")
        create_story_configure_label.setStyleSheet("border:none;")
        story_layout.addWidget(create_story_configure_label, 0, 4, 1, 1)
        
        create_story_configure_btn = AnimatedHoverButton("Config")
        create_story_configure_btn.setFixedSize(50, 20)
        create_story_configure_btn.clicked.connect(self.open_post_story_config_window)
        story_layout.addWidget(create_story_configure_btn, 0, 5, 1, 1)
        story_layout.setAlignment(Qt.AlignLeft)



        
        # 7. Check notifications frame
        check_notification_frame = QFrame()
        check_notification_frame.setStyleSheet("""QFrame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            background-color: rgba(128,128,128,0.2);}""")
        
        create_story_layout.addWidget(check_notification_frame)
        
        notification_layout = QGridLayout(check_notification_frame)

        self.check_notification_check_box = QCheckBox("Check Notifications")
        self.check_notification_check_box.setFont("arial 12 bold")
        self.check_notification_check_box.clicked.connect(lambda:self.save_id_active_config())
        notification_layout.addWidget(self.check_notification_check_box, 0, 0, 1, 1, Qt.AlignLeft)
        
        self.check_notification_min_min_int_spinbox = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        notification_layout.addWidget(self.check_notification_min_min_int_spinbox, 0, 1, 1, 1, Qt.AlignLeft)
        
        check_notification_to_label = QLabel("To")
        check_notification_to_label.setStyleSheet("border:none;")
        notification_layout.addWidget(check_notification_to_label, 0, 2, 1, 1)
        
        self.check_notification_max_min_intspain_box = SmallIntSpinBox(support_float=False,save_callback=self.save_id_active_config)
        notification_layout.addWidget(self.check_notification_max_min_intspain_box, 0, 3, 1, 1, Qt.AlignLeft)
        
        check_notification_min_label = QLabel("Min")
        check_notification_min_label.setStyleSheet("border:none;")
        notification_layout.addWidget(check_notification_min_label, 0, 4, 1, 1, Qt.AlignLeft)
        notification_layout.setAlignment(Qt.AlignLeft)

        
        # Add the main active options frame to the layout
        self.main_layout.addWidget(id_active_options_frame)
        





        
       # Loops configuration section
        active_loops_main_frame = QGroupBox()
        active_loops_main_frame.setObjectName("active_loops_main_frame")
        active_loops_main_frame.setTitle("Loops Configure")
        active_loops_main_frame.setFixedHeight(180)
        active_loops_main_frame.setStyleSheet("""QGroupBox#active_loops_main_frame{
                                            border:2px solid rgba(128,128,128,1);
                                            border-radius:8px;
                                            padding-top:5px;
                                            margin-top:5px;
                                            padding-right:5px;
                                            padding-left:5px;
                                            padding-bottom:5px;
                                            background-color: rgba(128,128,128,0.2);}

                                            QGroupBox#active_loops_main_frame::title {
                                                subcontrol-origin: margin;
                                                subcontrol-position: top left;
                                                left: 30px;
                                                border-radius:5px;
                                                padding-left: 5px;
                                                padding-right: 5px;
                                                background-color: rgba(128,128,128,0.5);
                                            }""")
        loops_main_layout = QVBoxLayout(active_loops_main_frame)

        # Create frames for the content
        loops_frame = QFrame()
        loops_frame.setObjectName("loops_frame")
        loops_frame.setStyleSheet("""QFrame#loops_frame{
                                            border:1px solid rgba(128,128,128,0.8);
                                            border-radius:8px;
                                            padding-top:5px;
                                            margin-top:5px;
                                            padding-right:5px;
                                            padding-left:5px;
                                            padding-bottom:5px;
                                            background-color: rgba(128,128,128,0.1);}""")
        loops_frame.setFixedWidth(400)
        loops_layout = QGridLayout(loops_frame)



        # Add the no of loops section
        no_of_loops_label = QLabel("No. of loops:")
        font_small = QFont("Arial", 10)
        font_small.setBold(True)
        no_of_loops_label.setFont(font_small)
        loops_layout.addWidget(no_of_loops_label, 0, 0, 1, 1, Qt.AlignLeft)

        self.no_of_loops_int_spinbox = IntSpinBox(save_callback=self.save_id_active_config)
        #self.no_of_loops_int_spinbox.setMaximum(100)
        loops_layout.addWidget(self.no_of_loops_int_spinbox, 0, 1, 1, 1, Qt.AlignLeft)

        loops_num_label = QLabel("Num")
        loops_num_label.setFont(font_small)
        loops_layout.addWidget(loops_num_label, 0, 2, 1, 1, Qt.AlignLeft)





        # Add the loops delay section
        loops_delay_label = QLabel("Loops Delay:")
        loops_delay_label.setFont(font_small)
        loops_layout.addWidget(loops_delay_label, 2, 0, 1, 1, Qt.AlignLeft)

        self.loops_delay_int_spinbox = IntSpinBox()
        #self.loops_delay_int_spinbox.setMaximum(100)
        loops_layout.addWidget(self.loops_delay_int_spinbox, 2, 1, 1, 1, Qt.AlignLeft)

        loops_delay_min_label = QLabel("Min")
        loops_delay_min_label.setFont(font_small)
        loops_layout.addWidget(loops_delay_min_label, 2, 2, 1, 1, Qt.AlignLeft)




        # Add the shuffle checkbox 
        self.shuffle_check_box = QCheckBox("Shuffle Activities")
        self.shuffle_check_box.setFont(font_small)
        self.shuffle_check_box.clicked.connect(lambda:self.save_id_active_config())
        loops_layout.addWidget(self.shuffle_check_box, 3, 0, 1, 1,alignment=Qt.AlignLeft)
        loops_layout.setAlignment(Qt.AlignLeft)

        # Add widgets to layouts
        loops_main_layout.addWidget(loops_frame)

        # Add the frame to the main layout
        self.main_layout.addWidget(active_loops_main_frame)
    
        


    def create_vertical_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setFixedWidth(2)
        return line





    def open_scroll_reels_videos_comments_config(self):
        # Create the window instance
        self.reels_comments_window = ReelConfigureWindowComments(self,

            window_title="Reels and videos comments configure",
            label_text="Reels comments configure",
            save_callback=self.save_id_active_config
        )
        
        # Show the window
        self.reels_comments_window.show()
    
    def open_scroll_feed_comments_config(self):
        self.scroll_feed_comments_window = Scroll_feed_ConfigureWindowComments(self,
            window_title="Feed comments configure",
            label_text="Feed comments configure",
            save_callback=self.save_id_active_config
        )
        self.scroll_feed_comments_window.show()

    def open_scroll_reels_videos_groups_config(self):
        self.scroll_reels_videos_groups_config=Scroll_reel_video_group_ConfigureWindow(self,
            window_title="Reels and videos groups configure",
            label_text="Reels groups configure",
            textbox_placeholder_text="Enter Your Group Name. `,` Will Seprate Groups Names.  Somethig Like Group Name1,Group Name2",
            save_callback=self.save_id_active_config
        )
        self.scroll_reels_videos_groups_config.show()

    def open_scroll_feed_groups_config(self):
        self.scroll_feed_groups_config = Scroll_feed_group_ConfigureWindow(
            self,
            window_title="Feed groups configure",
            label_text="Feed groups configure",
            textbox_placeholder_text="Enter Your Group Name. `,` Will Seprate Groups Names.  Somethig Like Group Name1,Group Name2",
            save_callback=self.save_id_active_config
        )
        self.scroll_feed_groups_config.show()




#--------------------------initializing the profile configue loader -------------------------------------

    def open_photo_config_window(self):
            self.photo_config = PhotoPostConfigWindow(
                self, 
                save_callback=self.save_id_active_config,
                main_folder_path=self.main_folder_path,
                current_profile=self.current_profile
            )
            
            self.photo_config.show()
        
    def open_checkin_config_window(self):
            self.checkin_config = CheckinPostConfigWindow(
                self, 
                main_folder_path=self.main_folder_path,
                current_profile=self.current_profile,
                save_callback=self.save_id_active_config
            )
            self.checkin_config.show()

    def open_post_story_config_window(self):
            self.post_story_config = StoryPostConfigWindow(
                self, 
                main_folder_path=self.main_folder_path,
                current_profile=self.current_profile,
                save_callback=self.save_id_active_config
            )
            self.post_story_config.show()








    def run_add_profile_config_ones(self,value=[]):
        
        frist_value = value[0]
        self.add_id_active_config_config()

    def add_id_active_config_config(self):
        try:
            # Define the path to the JSON file
            path = r"User_Data\Page_manager.json"
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            key = f"Id_information.{self.id_frame_idx}"

            # Retrieve the configuration for that ID
            if key not in data:
                raise ValueError(f"Key '{key}' not found in configuration data.")
            id_info = data[key]

            # Check if the id_active key exists
            if "id_active" not in id_info:
                raise ValueError(f"'id_active' key not found under '{key}'.")
            id_active_dict = id_info["id_active"]

            if not id_active_dict:
                print(f"No configuration found for ID {self.id_frame_idx}")
                return

            # **Loops Configuration**
            num_of_loop_l = id_active_dict.get("num_of_loop", 1)
            loop_delay_l = id_active_dict.get("loop_delay", 5)
            shuffel_l = id_active_dict.get("shuffel", True)

            # **Scroll Reels and Video**
            scroll_reels_and_video = id_active_dict.get("scroll_reels_and_vid", {})
            is_scroll_reels_enable = scroll_reels_and_video.get("scroll_reels_enable", False)
            is_scroll_vid_enable = scroll_reels_and_video.get("scroll_vid_enable", False)
            scroll_reels_min_min = scroll_reels_and_video.get("scroll_reels_min_min", 1)
            scroll_reels_max_min = scroll_reels_and_video.get("scroll_reels_min_max", 2)
            scroll_vid_min_min = scroll_reels_and_video.get("scroll_vid_min_min", 1)
            scroll_vid_max_min = scroll_reels_and_video.get("scroll_vid_min_max", 2)

            # **Scroll Reels and Video Activities**
            scroll_reels_and_video_activity = scroll_reels_and_video.get("activity", {})
            
            # Like Post
            scroll_reels_vid_like_post_dict = scroll_reels_and_video_activity.get("like_post", {})
            scroll_reels_vid_is_like_post_enable = scroll_reels_vid_like_post_dict.get("like_post_enable", False)
            scroll_reels_vid_like_post_prob = scroll_reels_vid_like_post_dict.get("like_post_prob", 0)
            
            # React Post
            scroll_reels_vid_react_post_dict = scroll_reels_and_video_activity.get("react_post", {})
            scroll_reels_vid_is_react_post_enable = scroll_reels_vid_react_post_dict.get("react_post_enable", False)
            scroll_reels_vid_react_post_prob = scroll_reels_vid_react_post_dict.get("react_post_prob", 0)
            
            # Comment Post
            scroll_reels_vid_comment_post_dict = scroll_reels_and_video_activity.get("comment_post", {})
            scroll_reels_vid_is_comment_post_enable = scroll_reels_vid_comment_post_dict.get("comment_post_enable", False)
            scroll_reels_vid_comment_post_prob = scroll_reels_vid_comment_post_dict.get("comment_post_prob", 0)
            scroll_reels_vid_comment_config_dict = scroll_reels_vid_comment_post_dict.get("comment_config", {})
            scroll_reels_vid_comment_from = scroll_reels_vid_comment_config_dict.get("comment_from", "From Text Box")
            scroll_reels_vid_comment_text_box = scroll_reels_vid_comment_config_dict.get("comment_text_box", "hello")
            scroll_reels_vid_comment_txt_path = scroll_reels_vid_comment_config_dict.get("comment_txt_path", "")
            scroll_reels_vid_comment_random = scroll_reels_vid_comment_config_dict.get("comment_random", False)
            
            # Share Post to Group
            scroll_reels_vid_share_post_to_group_dict = scroll_reels_and_video_activity.get("share_post_to_group", {})
            scroll_reels_vid_is_share_post_to_group_enable = scroll_reels_vid_share_post_to_group_dict.get("share_post_to_group_enable", False)
            scroll_reels_vid_share_post_to_group_prob = scroll_reels_vid_share_post_to_group_dict.get("share_post_to_group_prob", 0)
            scroll_reels_vid_share_post_to_group_config = scroll_reels_vid_share_post_to_group_dict.get("share_post_to_group_config", {})
            scroll_reels_vid_share_post_to_group_from = scroll_reels_vid_share_post_to_group_config.get("share_post_to_group_from", "From Text Box")
            scroll_reels_vid_share_post_to_group_text_box = scroll_reels_vid_share_post_to_group_config.get("share_post_to_group_text_box", "hello")
            scroll_reels_vid_share_post_to_group_txt_path = scroll_reels_vid_share_post_to_group_config.get("share_post_to_group_txt_path", "")
            scroll_reels_vid_share_post_to_group_txt_random = scroll_reels_vid_share_post_to_group_config.get("share_post_to_group_random", False)
            
            # Share Post to Story
            scroll_reels_vid_share_post_to_story_dict = scroll_reels_and_video_activity.get("share_post_to_story", {})
            scroll_reels_vid_is_share_post_to_story_enable = scroll_reels_vid_share_post_to_story_dict.get("share_post_to_story_enable", False)  
            scroll_reels_vid_share_post_to_story_prob = scroll_reels_vid_share_post_to_story_dict.get("share_post_to_story_prob", 0)

            # **Scroll Feed**
            scroll_feed = id_active_dict.get("scroll_feed", {})
            is_scroll_feed_enable = scroll_feed.get("scroll_feed_enable", False)
            scroll_feed_min_min = scroll_feed.get("scroll_feed_min_min", 1)
            scroll_feed_max_min = scroll_feed.get("scroll_feed_max_min", 2)

            # **Scroll Feed Activities**
            scroll_feed_activity = scroll_feed.get("activity", {})
            
            # Like Post
            scroll_feed_like_post_dict = scroll_feed_activity.get("like_post", {})
            scroll_feed_is_like_post_enable = scroll_feed_like_post_dict.get("like_post_enable", False)
            scroll_feed_like_post_prob = scroll_feed_like_post_dict.get("like_post_prob", 0)
            
            # React Post
            scroll_feed_react_post_dict = scroll_feed_activity.get("react_post", {})
            scroll_feed_is_react_post_enable = scroll_feed_react_post_dict.get("react_post_enable", False)
            scroll_feed_react_post_prob = scroll_feed_react_post_dict.get("react_post_prob", 0)
            
            # Comment Post
            scroll_feed_comment_post_dict = scroll_feed_activity.get("comment_post", {})
            scroll_feed_is_comment_post_enable = scroll_feed_comment_post_dict.get("comment_post_enable", False)
            scroll_feed_comment_post_prob = scroll_feed_comment_post_dict.get("comment_post_prob", 0)
            scroll_feed_comment_config_dict = scroll_feed_comment_post_dict.get("comment_config", {})
            scroll_feed_comment_from = scroll_feed_comment_config_dict.get("comment_from", "From Text Box")
            scroll_feed_comment_text_box = scroll_feed_comment_config_dict.get("comment_text_box", "hello")
            scroll_feed_comment_txt_path = scroll_feed_comment_config_dict.get("comment_txt_path", "")
            scroll_feed_comment_random = scroll_feed_comment_config_dict.get("comment_random", False)
            
            # Share Post to Group
            scroll_feed_share_post_to_group_dict = scroll_feed_activity.get("share_post_to_group", {})
            scroll_feed_is_share_post_to_group_enable = scroll_feed_share_post_to_group_dict.get("share_post_to_group_enable", False)
            scroll_feed_share_post_to_group_prob = scroll_feed_share_post_to_group_dict.get("share_post_to_group_prob", 0)
            scroll_feed_share_post_to_group_config = scroll_feed_share_post_to_group_dict.get("share_post_to_group_config", {})
            scroll_feed_share_post_to_group_from = scroll_feed_share_post_to_group_config.get("share_post_to_group_from", "From Text Box")
            scroll_feed_share_post_to_group_text_box = scroll_feed_share_post_to_group_config.get("share_post_to_group_text_box", "hello")
            scroll_feed_share_post_to_group_txt_path = scroll_feed_share_post_to_group_config.get("share_post_to_group_txt_path", "")
            scroll_feed_share_post_to_group_txt_random = scroll_feed_share_post_to_group_config.get("share_post_to_group_random", False)
            
            # Share Post to Story
            scroll_feed_share_post_to_story_dict = scroll_feed_activity.get("share_post_to_story", {})
            scroll_feed_is_share_post_to_story_enable = scroll_feed_share_post_to_story_dict.get("share_post_to_story_enable", False)  
            scroll_feed_share_post_to_story_prob = scroll_feed_share_post_to_story_dict.get("share_post_to_story_prob", 0)

            # **Check Messages**
            check_msg_dict = id_active_dict.get("check_msg", {})
            is_check_msg_enable_dic = check_msg_dict.get("check_msg_enable", False)
            check_msg_min_min = check_msg_dict.get("check_msg_min_min", 0)
            check_msg_max_min = check_msg_dict.get("check_msg_max_min", 1)
            reply_msg_enable = check_msg_dict.get("reply_msg_enable", False)
            reply_msg_min_chat = check_msg_dict.get("reply_msg_min_chat", 0)
            reply_msg_max_chat = check_msg_dict.get("reply_msg_max_chat", 1)

            # **Add and Confirm Friends**
            add_and_confirm_friends = id_active_dict.get("add_and_confirm_friends", {})
            add_friend_enable = add_and_confirm_friends.get("add_friend_enable", False)
            add_friend_min_frid = add_and_confirm_friends.get("add_friend_min_frid", 0)
            add_friend_max_frid = add_and_confirm_friends.get("add_friend_max_frid", 1)
            confirm_friend_enable = add_and_confirm_friends.get("confirm_friend_enable", False)
            confirm_friend_min_frid = add_and_confirm_friends.get("confirm_friend_min_frid", 1)
            confirm_friend_max_frid = add_and_confirm_friends.get("confirm_friend_max_frid", 2)

            # **Post Photo**
            post_photo_dict = id_active_dict.get("post_photo", {})
            is_post_photo_enable = post_photo_dict.get("post_photo_enable", False)
            post_photo_num = post_photo_dict.get("post_photo_num", 1)
            post_photo_config_dict = post_photo_dict.get("post_photo_config", {})
            post_photo_download_folder = post_photo_config_dict.get("post_photo_download_folder", "")
            post_photo_ld_folder = post_photo_config_dict.get("post_photo_ld_folder", "")
            post_photo_caption_from = post_photo_config_dict.get("post_photo_caption_from", "From Original Photo")
            post_photo_caption_text_box = post_photo_config_dict.get("post_photo_caption_text_box", "hello")
            post_photo_caption_txt_path = post_photo_config_dict.get("post_photo_caption_txt_path", "")
            post_photo_caption_txt_random = post_photo_config_dict.get("post_photo_caption_txt_random", False)

            # **Post Checkin**
            post_checkin = id_active_dict.get("post_checkin", {})
            post_checkin_enable = post_checkin.get("post_checkin_enable", False)
            post_checkin_loacation = post_checkin.get("post_checkin_location","")
            post_checkin_num = post_checkin.get("post_checkin_num", 1)
            post_checkin_config_dict = post_checkin.get("post_checkin_config", {})
            post_checkin_photo_download_folder = post_checkin_config_dict.get("post_checkin_photo_download_folder", "")
            add_photo_to_checkin = post_checkin_config_dict.get("add_photo_to_checkin_post", False)  
            post_checkin_ld_photo_folder = post_checkin_config_dict.get("post_checkin_ld_photo_folder", "")
            post_checkin_caption_from = post_checkin_config_dict.get("post_checkin_caption_from", "From Original Photo")
            post_checkin_caption_text_box = post_checkin_config_dict.get("post_checkin_caption_text_box", "hello")
            post_checkin_caption_txt_path = post_checkin_config_dict.get("post_checkin_caption_txt_path", "")
            post_checkin_caption_txt_random = post_checkin_config_dict.get("post_checkin_caption_txt_random", False)

            # **Create Story**
            create_story_dict = id_active_dict.get("create_story", {})
            create_story_enable = create_story_dict.get("create_story_enable", False)
            create_story_num = create_story_dict.get("create_story_num", 1)
            create_story_config_dict = create_story_dict.get("create_story_config", {})
            create_story_video_download_folder = create_story_config_dict.get("create_story_video_download_folder", "")
            create_story_video_folder = create_story_config_dict.get("create_story_video_folder", "")
            create_story_caption_from = create_story_config_dict.get("create_story_caption_from", "From Original Photo")
            create_story_caption_text_box = create_story_config_dict.get("create_story_caption_text_box", "hello")
            create_story_caption_txt_path = create_story_config_dict.get("create_story_caption_txt_path", "")
            create_story_caption_txt_random = create_story_config_dict.get("create_story_caption_txt_random", False)

            # **Check Notification**
            check_notification_dict = id_active_dict.get("check_notification", {})
            check_notification_enable = check_notification_dict.get("check_notification_enable", False)
            check_notification_min_min = check_notification_dict.get("check_notification_min_min", 1)
            check_notification_max_min = check_notification_dict.get("check_notification_max_min", 2)

            # **Set UI Elements**
            # Loops Configuration
            self.no_of_loops_int_spinbox.set_value(num_of_loop_l)
            self.loops_delay_int_spinbox.set_value(loop_delay_l)
            self.shuffle_check_box.setChecked(shuffel_l)
            self.shuffle_check_box_enable = shuffel_l

            # Scroll Reels and Video
            self.scroll_reels_feed_check_box_btn.setChecked(is_scroll_reels_enable)
            self.is_scroll_reels_enable_var = is_scroll_reels_enable
            self.scroll_video_feed_combo_btn.setChecked(is_scroll_vid_enable)
            self.is_scroll_video_enable_var = is_scroll_vid_enable
            self.scroll_reels_feed_min_intspain_box.set_value(scroll_reels_min_min)
            self.scroll_reels_max_min_intspain_box.set_value(scroll_reels_max_min)
            self.scroll_video_feed_min_min_intspain_box.set_value(scroll_vid_min_min)
            self.scroll_video_feed_max_min_intspain_box.set_value(scroll_vid_max_min)

            # Scroll Reels and Video Activities
            self.scroll_video_feed_like_post_check_box.setChecked(scroll_reels_vid_is_like_post_enable)
            self.scroll_reels_video_is_like_post_enable_var = scroll_reels_vid_is_like_post_enable
            self.scroll_video_feed_like_prob_intspain_box.set_value(scroll_reels_vid_like_post_prob)
            self.scroll_reels_video_like_post_prob_var = scroll_reels_vid_like_post_prob

            self.scroll_video_feed_react_post_check_box.setChecked(scroll_reels_vid_is_react_post_enable)
            self.scroll_reels_video_is_react_post_enable_var = scroll_reels_vid_is_react_post_enable
            self.scroll_video_feed_react_prob_intspain_box.set_value(scroll_reels_vid_react_post_prob)
            self.scroll_reels_video_react_post_prob_var = scroll_reels_vid_react_post_prob

            self.scroll_video_feed_comment_on_post_check_box.setChecked(scroll_reels_vid_is_comment_post_enable)
            self.scroll_reels_video_comments_is_enable_var = scroll_reels_vid_is_comment_post_enable
            self.scroll_video_feed_comment_on_post_prob_intspain_box.set_value(scroll_reels_vid_comment_post_prob)
            self.scroll_reels_video_comments_prob_var = scroll_reels_vid_comment_post_prob
            self.scroll_reels_video_comments_txt_box_var = scroll_reels_vid_comment_text_box
            self.scroll_reels_video_comments_from_var = scroll_reels_vid_comment_from
            self.scroll_reels_video_comments_txt_file_random_var = scroll_reels_vid_comment_random
            self.scroll_reels_video_comments_txt_file_path_var = scroll_reels_vid_comment_txt_path

            self.scroll_video_feed_share_post_to_groups_check_box.setChecked(scroll_reels_vid_is_share_post_to_group_enable)
            self.scroll_reels_video_groups_is_enable_var = scroll_reels_vid_is_share_post_to_group_enable
            self.scroll_video_feed_share_random_post_to_groups_prob_intspain_box.set_value(scroll_reels_vid_share_post_to_group_prob)
            self.scroll_reels_video_groups_prob_var = scroll_reels_vid_share_post_to_group_prob
            self.scroll_reels_video_groups_txt_box_var = scroll_reels_vid_share_post_to_group_text_box
            self.scroll_reels_video_groups_from_var = scroll_reels_vid_share_post_to_group_from
            self.scroll_reels_video_groups_txt_file_random = scroll_reels_vid_share_post_to_group_txt_random
            self.scroll_reels_video_groups_txt_file_path_var = scroll_reels_vid_share_post_to_group_txt_path

            self.scroll_video_feed_share_post_to_story_check_box.setChecked(scroll_reels_vid_is_share_post_to_story_enable)
            self.scroll_reels_video_share_post_to_story_is_enable_var = scroll_reels_vid_is_share_post_to_story_enable
            self.scroll_video_feed_share_random_post_to_story_prob_intspain_box.set_value(scroll_reels_vid_share_post_to_story_prob)
            self.scroll_reels_video_share_post_to_story_prob_var = scroll_reels_vid_share_post_to_story_prob

            # Scroll Feed
            self.scroll_feed_checkbox_btn.setChecked(is_scroll_feed_enable)
            self.is_scroll_feed_enable_var = is_scroll_feed_enable
            self.scroll_feed_min_min_intspain_box.set_value(scroll_feed_min_min)
            self.scroll_feed_max_min_intspain_box.set_value(scroll_feed_max_min)

            # Scroll Feed Activities
            self.scroll_feed_like_post_check_box.setChecked(scroll_feed_is_like_post_enable)
            self.scroll_feed_is_like_post_enable_var = scroll_feed_is_like_post_enable
            self.scroll_feed_like_prob_intspain_box.set_value(scroll_feed_like_post_prob)
            self.scroll_feed_like_post_prob_var = scroll_feed_like_post_prob

            self.scroll_feed_react_post_check_box.setChecked(scroll_feed_is_react_post_enable)
            self.scroll_feed_is_react_post_enable_var = scroll_feed_is_react_post_enable
            self.scroll_feed_react_prob_intspain_box.set_value(scroll_feed_react_post_prob)
            self.scroll_feed_react_post_prob_var = scroll_feed_react_post_prob

            self.scroll_feed_comment_on_post_check_box.setChecked(scroll_feed_is_comment_post_enable)
            self.scroll_feed_comments_is_enable_var = scroll_feed_is_comment_post_enable
            self.scroll_feed_comment_on_post_prob_intspain_box.set_value(scroll_feed_comment_post_prob)
            self.scroll_feed_comments_prob_var = scroll_feed_comment_post_prob
            self.scroll_feed_comments_txt_box_var = scroll_feed_comment_text_box
            self.scroll_feed_comments_from_var = scroll_feed_comment_from
            self.scroll_feed_comments_txt_file_random = scroll_feed_comment_random
            self.scroll_feed_comments_txt_file_path_var = scroll_feed_comment_txt_path

            self.scroll_feed_share_post_to_groups_check_box.setChecked(scroll_feed_is_share_post_to_group_enable)
            self.scroll_feed_groups_is_enable_var = scroll_feed_is_share_post_to_group_enable
            self.scroll_feed_share_random_post_to_groups_prob_intspain_box.set_value(scroll_feed_share_post_to_group_prob)
            self.scroll_feed_groups_prob_var = scroll_feed_share_post_to_group_prob
            self.scroll_feed_groups_txt_box_var = scroll_feed_share_post_to_group_text_box
            self.scroll_feed_groups_from_var = scroll_feed_share_post_to_group_from
            self.scroll_feed_groups_txt_file_random = scroll_feed_share_post_to_group_txt_random
            self.scroll_feed_groups_txt_file_path_var = scroll_feed_share_post_to_group_txt_path

            self.scroll_feed_share_post_to_story_check_box.setChecked(scroll_feed_is_share_post_to_story_enable)
            self.scroll_feed_share_post_to_story_is_enable_var = scroll_feed_is_share_post_to_story_enable
            self.scroll_feed_share_random_post_to_story_prob_intspain_box.set_value(scroll_feed_share_post_to_story_prob)
            self.scroll_feed_share_post_to_story_prob_var = scroll_feed_share_post_to_story_prob

            # Check Messages
            self.check_msg_check_box.setChecked(is_check_msg_enable_dic)
            self.is_check_msg_enable = is_check_msg_enable_dic
            self.check_msg_min_min_int_spinbox.set_value(check_msg_min_min)
            self.check_msg_max_min_intspain_box.set_value(check_msg_max_min)
            self.reply_msg_check_box.setChecked(reply_msg_enable)
            self.reply_msg_enable = reply_msg_enable
            self.reply_msgmin_chats_int_spinbox.set_value(reply_msg_min_chat)
            self.reply_msg_max_chats_intspain_box.set_value(reply_msg_max_chat)

            # Add and Confirm Friends
            self.add_friends_box.setChecked(add_friend_enable)
            self.add_friend_enable = add_friend_enable
            self.add_friends_min_int_spinbox.set_value(add_friend_min_frid)
            self.add_friends_max_intspain_box.set_value(add_friend_max_frid)
            self.confirm_friends_check_box.setChecked(confirm_friend_enable)
            self.confirm_friend_enable = confirm_friend_enable
            self.confirm_friends_min_int_spinbox.set_value(confirm_friend_min_frid)
            self.confirm_friends_max_intspain_box.set_value(confirm_friend_max_frid)

            # Post Photo
            self.post_photos_check_box.setChecked(is_post_photo_enable)
            self.post_photo_enable = is_post_photo_enable
            self.post_photos_int_spinbox.set_value(post_photo_num)
            self.photo_post_download_image_folder = post_photo_download_folder 
            self.photo_post_image_folder = post_photo_ld_folder
            self.photo_captions_from_var = post_photo_caption_from
            self.photo_captions_txt_file_path_var = post_photo_caption_txt_path
            self.photo_captions_text_box_var = post_photo_caption_text_box
            self.photo_Random_var = post_photo_caption_txt_random

            # Post Checkin
            self.create_post_checkin_check_box.setChecked(post_checkin_enable)
            self.is_post_checkin_enable_var = post_checkin_enable
            self.create_post_checkin_num_int_spinbox.set_value(post_checkin_num)
            self.post_checkin_Download_photo_Folder = post_checkin_photo_download_folder
            self.post_checkin_ld_photo_folder = post_checkin_ld_photo_folder
            self.add_photo_to_checkin_post_var = add_photo_to_checkin
            self.location_of_checkin_post_var = post_checkin_loacation
            self.post_checkin_captions_from_var = post_checkin_caption_from
            self.post_checkin_captions_txt_file_path_var = post_checkin_caption_txt_path
            self.post_checkin_captions_text_box_var = post_checkin_caption_text_box
            self.post_checkin_text_caption_Random_var = post_checkin_caption_txt_random
            # Create Story
            self.create_story_check_box.setChecked(create_story_enable)
            self.is_create_stroy_enable_var = create_story_enable  # Typo in variable name
            self.create_story_num_int_spinbox.set_value(create_story_num)
            self.story_video_Download_Folder = create_story_video_download_folder
            self.story_video_Folder = create_story_video_folder
            self.story_video_captions_from_var = create_story_caption_from
            self.story_video_captions_txt_file_path_var = create_story_caption_txt_path
            self.story_video_captions_text_box_var = create_story_caption_text_box
            self.story_video_text_caption_Random_var = create_story_caption_txt_random

            # Check Notification
            self.check_notification_check_box.setChecked(check_notification_enable)
            self.check_notification_enable = check_notification_enable
            self.check_notification_min_min_int_spinbox.set_value(check_notification_min_min)
            self.check_notification_max_min_intspain_box.set_value(check_notification_max_min)

        except Exception as e:
            print(f"Error in add_id_active_config_config: {e}")

    def save_id_active_config(self):
        """
        Save the current ID active configuration to the JSON file.
        """
        try:
            # Load existing JSON data
            with open(self.json_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
    
            # Define the key for this ID
            key = f"Id_information.{self.id_frame_idx}"
            if key not in data:
                print(f"{key} not found in JSON data. Creating new entry.")
                data[key] = {}
    
            id_data = data[key]
    
            # Create the id_active dictionary
            id_active_dict = {}
    
            # **Loops Configuration**
            id_active_dict["num_of_loop"] = self.no_of_loops_int_spinbox.get_value()
            id_active_dict["loop_delay"] = self.loops_delay_int_spinbox.get_value()
            id_active_dict["shuffel"] = self.shuffle_check_box.isChecked()
    
            # **Scroll Reels and Video**
            scroll_reels_and_vid = {
                "scroll_reels_enable": self.scroll_reels_feed_check_box_btn.isChecked(),
                "scroll_vid_enable": self.scroll_video_feed_combo_btn.isChecked(),
                "scroll_reels_min_min": self.scroll_reels_feed_min_intspain_box.get_value(),
                "scroll_reels_min_max": self.scroll_reels_max_min_intspain_box.get_value(),
                "scroll_vid_min_min": self.scroll_video_feed_min_min_intspain_box.get_value(),
                "scroll_vid_min_max": self.scroll_video_feed_max_min_intspain_box.get_value(),
                "activity": {}
            }
    
            activity = scroll_reels_and_vid["activity"]
            # Like Post
            activity["like_post"] = {
                "like_post_enable": self.scroll_video_feed_like_post_check_box.isChecked(),
                "like_post_prob": self.scroll_video_feed_like_prob_intspain_box.get_value()
            }
            # React Post
            activity["react_post"] = {
                "react_post_enable": self.scroll_video_feed_react_post_check_box.isChecked(),
                "react_post_prob": self.scroll_video_feed_react_prob_intspain_box.get_value()
            }
            # Comment Post
            activity["comment_post"] = {
                "comment_post_enable": self.scroll_video_feed_comment_on_post_check_box.isChecked(),
                "comment_post_prob": self.scroll_video_feed_comment_on_post_prob_intspain_box.get_value(),
                "comment_config": {
                    "comment_from": self.scroll_reels_video_comments_from_var,
                    "comment_text_box": self.scroll_reels_video_comments_txt_box_var,
                    "comment_txt_path": self.scroll_reels_video_comments_txt_file_path_var,
                    "comment_random": self.scroll_reels_video_comments_txt_file_random_var
                }
            }
            # Share Post to Group
            activity["share_post_to_group"] = {
                "share_post_to_group_enable": self.scroll_video_feed_share_post_to_groups_check_box.isChecked(),
                "share_post_to_group_prob": self.scroll_video_feed_share_random_post_to_groups_prob_intspain_box.get_value(),
                "share_post_to_group_config": {
                    "share_post_to_group_from": self.scroll_reels_video_groups_from_var,
                    "share_post_to_group_text_box": self.scroll_reels_video_groups_txt_box_var,
                    "share_post_to_group_txt_path": self.scroll_reels_video_groups_txt_file_path_var,
                    "share_post_to_group_random": self.scroll_reels_video_groups_txt_file_random
                }
            }
            # Share Post to Story
            activity["share_post_to_story"] = {
                "share_post_to_story_enable": self.scroll_video_feed_share_post_to_story_check_box.isChecked(),
                "share_post_to_story_prob": self.scroll_video_feed_share_random_post_to_story_prob_intspain_box.get_value()
            }
            id_active_dict["scroll_reels_and_vid"] = scroll_reels_and_vid
    
            # **Scroll Feed**
            scroll_feed = {
                "scroll_feed_enable": self.scroll_feed_checkbox_btn.isChecked(),
                "scroll_feed_min_min": self.scroll_feed_min_min_intspain_box.get_value(),
                "scroll_feed_max_min": self.scroll_feed_max_min_intspain_box.get_value(),
                "activity": {}
            }
    
            feed_activity = scroll_feed["activity"]
            # Like Post
            feed_activity["like_post"] = {
                "like_post_enable": self.scroll_feed_like_post_check_box.isChecked(),
                "like_post_prob": self.scroll_feed_like_prob_intspain_box.get_value()
            }
            # React Post
            feed_activity["react_post"] = {
                "react_post_enable": self.scroll_feed_react_post_check_box.isChecked(),
                "react_post_prob": self.scroll_feed_react_prob_intspain_box.get_value()
            }
            # Comment Post
            feed_activity["comment_post"] = {
                "comment_post_enable": self.scroll_feed_comment_on_post_check_box.isChecked(),
                "comment_post_prob": self.scroll_feed_comment_on_post_prob_intspain_box.get_value(),
                "comment_config": {
                    "comment_from": self.scroll_feed_comments_from_var,
                    "comment_text_box": self.scroll_feed_comments_txt_box_var,
                    "comment_txt_path": self.scroll_feed_comments_txt_file_path_var,
                    "comment_random": self.scroll_feed_comments_txt_file_random
                }
            }
            # Share Post to Group
            feed_activity["share_post_to_group"] = {
                "share_post_to_group_enable": self.scroll_feed_share_post_to_groups_check_box.isChecked(),
                "share_post_to_group_prob": self.scroll_feed_share_random_post_to_groups_prob_intspain_box.get_value(),
                "share_post_to_group_config": {
                    "share_post_to_group_from": self.scroll_feed_groups_from_var,
                    "share_post_to_group_text_box": self.scroll_feed_groups_txt_box_var,
                    "share_post_to_group_txt_path": self.scroll_feed_groups_txt_file_path_var,
                    "share_post_to_group_random": self.scroll_feed_groups_txt_file_random
                }
            }
            # Share Post to Story
            feed_activity["share_post_to_story"] = {
                "share_post_to_story_enable": self.scroll_feed_share_post_to_story_check_box.isChecked(),
                "share_post_to_story_prob": self.scroll_feed_share_random_post_to_story_prob_intspain_box.get_value()
            }
            id_active_dict["scroll_feed"] = scroll_feed
    
            # **Check Messages**
            id_active_dict["check_msg"] = {
                "check_msg_enable": self.check_msg_check_box.isChecked(),
                "check_msg_min_min": self.check_msg_min_min_int_spinbox.get_value(),
                "check_msg_max_min": self.check_msg_max_min_intspain_box.get_value(),
                "reply_msg_enable": self.reply_msg_check_box.isChecked(),
                "reply_msg_min_chat": self.reply_msgmin_chats_int_spinbox.get_value(),
                "reply_msg_max_chat": self.reply_msg_max_chats_intspain_box.get_value()
            }
    
            # **Add and Confirm Friends**
            id_active_dict["add_and_confirm_friends"] = {
                "add_friend_enable": self.add_friends_box.isChecked(),
                "add_friend_min_frid": self.add_friends_min_int_spinbox.get_value(),
                "add_friend_max_frid": self.add_friends_max_intspain_box.get_value(),
                "confirm_friend_enable": self.confirm_friends_check_box.isChecked(),
                "confirm_friend_min_frid": self.confirm_friends_min_int_spinbox.get_value(),
                "confirm_friend_max_frid": self.confirm_friends_max_intspain_box.get_value()
            }
    
            # **Post Photo**
            id_active_dict["post_photo"] = {
                "post_photo_enable": self.post_photos_check_box.isChecked(),
                "post_photo_num": self.post_photos_int_spinbox.get_value(),
                "post_photo_config": {
                    "post_photo_download_folder": self.photo_post_download_image_folder,
                    "post_photo_ld_folder": self.photo_post_image_folder,
                    "post_photo_caption_from": self.photo_captions_from_var,
                    "post_photo_caption_text_box": self.photo_captions_text_box_var,
                    "post_photo_caption_txt_path": self.photo_captions_txt_file_path_var,
                    "post_photo_caption_txt_random": self.photo_Random_var
                }
            }
    
            # **Post Checkin**
            id_active_dict["post_checkin"] = {
                "post_checkin_enable": self.create_post_checkin_check_box.isChecked(),
                "post_checkin_num": self.create_post_checkin_num_int_spinbox.get_value(),
                "post_checkin_location":str(self.location_of_checkin_post_var),
                "post_checkin_config": {
                    "post_checkin_photo_download_folder": self.post_checkin_Download_photo_Folder,
                    "post_checkin_ld_photo_folder": self.post_checkin_ld_photo_folder,
                    "add_photo_to_checkin_post": self.add_photo_to_checkin_post_var,
                    "post_checkin_caption_from": self.post_checkin_captions_from_var,
                    "post_checkin_caption_text_box": self.post_checkin_captions_text_box_var,
                    "post_checkin_caption_txt_path": self.post_checkin_captions_txt_file_path_var,
                    "post_checkin_caption_txt_random": self.post_checkin_text_caption_Random_var
                }
            }
    
            # **Create Story**
            id_active_dict["create_story"] = {
                "create_story_enable": self.create_story_check_box.isChecked(),
                "create_story_num": self.create_story_num_int_spinbox.get_value(),
                "create_story_config": {
                    "create_story_video_download_folder": self.story_video_Download_Folder,
                    "create_story_video_folder": self.story_video_Folder,
                    "create_story_caption_from": self.story_video_captions_from_var,
                    "create_story_caption_text_box": self.story_video_captions_text_box_var,
                    "create_story_caption_txt_path": self.story_video_captions_txt_file_path_var,
                    "create_story_caption_txt_random": self.story_video_text_caption_Random_var
                }
            }
    
            # **Check Notification**
            id_active_dict["check_notification"] = {
                "check_notification_enable": self.check_notification_check_box.isChecked(),
                "check_notification_min_min": self.check_notification_min_min_int_spinbox.get_value(),
                "check_notification_max_min": self.check_notification_max_min_intspain_box.get_value()
            }
    
            # Update the JSON data
            id_data["id_active"] = id_active_dict
    
            # Write back to the JSON file with proper indentation
            with open(self.json_file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
    
            print(f"Configuration saved successfully for ID {self.id_frame_idx}")
    
        except Exception as e:
            print(f"Error saving configuration: {e}")

    def get_config_by_combo_value(self, page_or_Id_data, id_frame_idx, search_value):
        """
        Given a JSON file, an id index (id_frame_idx), and a search value,
        first check the id_information at that index to see if its "id_name" equals search_value.
        If yes, return the entire id_information dictionary.
        Otherwise, loop through its "pages_information" entries and return the page dictionary
        whose "Page_Name" matches search_value.

        :param page_or_Id_data: Dictionary containing the JSON data.
        :param id_frame_idx: The id index (e.g. 1 for "Id_information.1").
        :param search_value: The value from the combo box to search for.
        :return: Tuple of (matching_data, is_id_data) or None if not found.
        """
        try:
            data = page_or_Id_data
            id_key = f"Id_information.{id_frame_idx}"
            if id_key not in data:
                print(f"{id_key} not found in JSON data.")
                return None

            id_data = data[id_key]
            main_folder_path = id_data.get("Main_folder_path","")
            # Normalize the search value for case-insensitive matching
            search_normalized = search_value.strip().lower()

            # First, check the top-level id_name
            id_name = id_data.get("id_name", "").strip().lower()
            if id_name == search_normalized:
                return (id_data, True,main_folder_path)

            # Otherwise, loop through the pages under "pages_information"
            page_info = id_data.get("pages_information", {})
            for key, page_dict in page_info.items():
                page_name = page_dict.get("Page_Name", "").strip().lower()
                if page_name == search_normalized:
                    return (page_dict, False,main_folder_path)

            print(f"No configuration matching '{search_value}' found in {id_key}.")
            return None
        except Exception as e:
            print(f"Error reading JSON: {e}")
            return None
        





#-----------------------configure window for photo post button --------------------------------------



class FolderCreationMixin:
    """Mixin class for common folder creation functionality"""
    
    def create_folder(self, main_folder, folder_name,profile_name_folder=None):
        """Generic folder creation method"""
        if not main_folder:
            QMessageBox.critical(self, "Main folder", "Please select main folder first")
            return None, False
        
        folder_path = os.path.join(main_folder, folder_name)
        folder_path = os.path.normpath(folder_path)
        folder_created = False
        
        if os.path.exists(folder_path):
            folder_created = False
        else:
            os.makedirs(folder_path, exist_ok=True)
            folder_created = True
            
        return os.path.abspath(folder_path), folder_created
        
    def show_folder_creation_result(self, folder_created):
        """Show appropriate message based on folder creation result"""
        if folder_created:
            QMessageBox.information(self, "Folder Created", "Folder created successfully")
        else:
            QMessageBox.information(self, "Folder exists", "Folder already exists")


class CaptionsConfigFrame(QGroupBox):
    """Reusable frame for caption configuration"""
    
    def __init__(self, parent=None, caption_source_var=None, text_box_var=None, 
                 file_path_var=None, random_var=None):
        super().__init__(parent)
        
        self.caption_source_var = caption_source_var
        self.text_box_var = text_box_var
        self.file_path_var = file_path_var
        self.random_var = random_var
        self.setObjectName("caption_configure_frame")
        self.setTitle("Configure Captions")
        self.setStyleSheet("""QGroupBox#caption_configure_frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.1);}
                                            QGroupBox#caption_configure_frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        # Main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        
        # Create the main frame
        self.frame = QFrame()
        self.frame.setObjectName("main_frame")
        #self.frame.setStyleSheet("QFrame#main_frame{border:2px solid green}")
        self.frame.setLineWidth(2)
        frame_layout = QVBoxLayout(self.frame)
        main_layout.addWidget(self.frame)
        
        # Title from section
        title_from_frame = QFrame()
        title_from_frame.setObjectName("title_from_frame")
        title_from_layout = QHBoxLayout(title_from_frame)
        title_from_frame.setLayout(title_from_layout)
        
        title_from_label = QLabel("Captions From")
        title_from_layout.addWidget(title_from_label)
        
        self.title_from_combobox = QComboBox()
        self.title_from_combobox.addItems(["From Original Photo", "From Text Box", "From text file"])
        if caption_source_var:
            self.title_from_combobox.setCurrentText(caption_source_var)
        self.title_from_combobox.currentTextChanged.connect(self.update_options_panel)
        title_from_layout.addWidget(self.title_from_combobox)
        title_from_layout.setAlignment(Qt.AlignLeft)
        frame_layout.addWidget(title_from_frame)
        
        # Options frame 
        self.options_frame = QFrame()
        self.options_frame.setObjectName("QFrame")
        self.options_frame.setStyleSheet("""QFrame#QFrame{border:1px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.1);}""")


        self.options_layout = QVBoxLayout(self.options_frame)
        frame_layout.addWidget(self.options_frame)
        
        # Initialize the options panel
        self.update_options_panel(self.title_from_combobox.currentText())
    
    def update_options_panel(self, value):
        """Update the options panel based on the selected caption source"""
        # Clear existing widgets
        while self.options_layout.count():
            child = self.options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if value == "From Original Photo":
            label = QLabel("Now captions of photo will be taken from original photo")
            self.options_layout.addWidget(label)
            
        elif value == "From Text Box":
            text_box_frame = QFrame()
            text_box_layout = QHBoxLayout(text_box_frame)
            
            label = QLabel("Text Box:")
            text_box_layout.addWidget(label)
            
            self.text_box = QTextEdit()
            self.text_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                                /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;           /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QTextEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QTextEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QTextEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            if self.text_box_var:
                self.text_box.setText(self.text_box_var)
            self.text_box.setMaximumHeight(200)
            text_box_layout.addWidget(self.text_box)
            
            self.options_layout.addWidget(text_box_frame)
            
        elif value == "From text file":
            file_frame = QFrame()
            file_layout = QHBoxLayout(file_frame)
            
            label = QLabel("Text File Path:")
            file_layout.addWidget(label)
            
            self.file_path_entry = QLineEdit()
            self.file_path_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);          
                color: #eeeeee;                     
                border: 1px solid rgba(128,128,128,1);           
                border-radius: 8px;                 
                padding: 2px 2px 2px 10px;           
                selection-background-color: #555555;
            }
            QLineEdit::placeholder {
                color: #888888;                    
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);      
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);         
            }
        """)
            if self.file_path_var:
                self.file_path_entry.setText(self.file_path_var)
            file_layout.addWidget(self.file_path_entry)
            
            browse_button = AnimatedHoverButton(text="Browse")
            browse_button.clicked.connect(self.browse_captions_file)
            file_layout.addWidget(browse_button)
            
            self.random_checkbox = QCheckBox("Random")
            if self.random_var:
                self.random_checkbox.setChecked(self.random_var)
            file_layout.addWidget(self.random_checkbox)
            
            self.options_layout.addWidget(file_frame)
    
    def browse_captions_file(self):
        """Browse for a captions file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select a Text File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            self.file_path_entry.setText(file_path)
            self.file_path_var = file_path
    
    def get_caption_source(self):
        """Get the current caption source"""
        return self.title_from_combobox.currentText()
    
    def get_text_box_content(self):
        """Get the text box content if it exists"""
        if hasattr(self, 'text_box'):
            return self.text_box.toPlainText()
        return ""
    
    def get_file_path(self):
        """Get the file path if it exists"""
        if hasattr(self, 'file_path_entry'):
            return self.file_path_entry.text()
        return ""
    
    def get_random_state(self):
        """Get the random checkbox state if it exists"""
        if hasattr(self, 'random_checkbox'):
            return self.random_checkbox.isChecked()
        return False


class FolderConfigFrame(QGroupBox):
    """Reusable frame for folder configuration"""
    
    def __init__(self, parent=None, title="", folder_label="", folder_var="", 
                 browse_callback=None, create_callback=None, browse_enabled=True):
        super().__init__(parent)
        self.setObjectName("folder_config_frame")
        self.setTitle(title)
        self.setStyleSheet("""QGroupBox#folder_config_frame{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.1);}
                                            QGroupBox#folder_config_frame::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")
        
        
        # Set up grid layout
        layout = QGridLayout(self)
        self.setLayout(layout)
        
        # Add the folder entry section
        folder_frame = QFrame()
        
        folder_layout = QHBoxLayout(folder_frame)
        folder_layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(folder_label)
        label.setFont(QFont("Arial", 10))
        folder_layout.addWidget(label)
        
        self.folder_entry = QLineEdit()
        self.folder_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                color: #eeeeee;                      /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
        if folder_var:
            self.folder_entry.setText(folder_var)
        folder_layout.addWidget(self.folder_entry)
        
        self.browse_button = AnimatedHoverButton(text="Browse")
        if browse_callback:
            self.browse_button.clicked.connect(browse_callback)
        if not browse_enabled:
            self.browse_button.setEnabled(False)
        folder_layout.addWidget(self.browse_button)
        
        # Add folder section to main layout
        layout.addWidget(folder_frame, 0, 0)
        
        # Add create folder button
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        create_button = AnimatedHoverButton(text="Create Folders")
        if create_callback:
            create_button.clicked.connect(create_callback)
        button_layout.addWidget(create_button)
        
        # Add button section to main layout
        layout.addWidget(button_frame, 0, 1)
    
    def get_folder_path(self):
        """Get the folder path from the entry field"""
        return self.folder_entry.text()
    
    def set_folder_path(self, path):
        """Set the folder path in the entry field"""
        self.folder_entry.setText(path)


class PhotoConfigWindow(QDialog, FolderCreationMixin):
    """Base class for photo configuration windows"""
    
    def __init__(self, parent=None, main_folder_path="", current_profile="", window_title=""):
        super().__init__(parent, Qt.Window)
        self.setWindowTitle(window_title)
        self.setFixedSize(700, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.main_folder_path = main_folder_path
        self.current_profile = current_profile
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)
        

        self.init_ui(main_layout)
        
        main_layout.setAlignment(Qt.AlignTop)
    def init_ui(self, layout):
        """Initialize UI components - to be implemented by subclasses"""
        pass
    
    def browse_folder(self):
        """Generic folder browsing method"""
       
        current_flags = self.windowFlags()

        
        self.setWindowFlags(current_flags & ~Qt.WindowStaysOnTopHint)
        self.show()

        folder = QFileDialog.getExistingDirectory(self, "Select Folder")

        
        self.setWindowFlags(current_flags)
        self.show()

        return folder


class PhotoPostConfigWindow(PhotoConfigWindow):
    """Window for configuring photo posts"""
    def __init__(self, parent=None,save_callback=None, main_folder_path="", current_profile=""):
       
        self._parent = parent  
        
        
        self.save_callback=save_callback
        self.photo_post_download_image_folder = parent.photo_post_download_image_folder if parent else ""
        self.photo_post_image_folder = parent.photo_post_image_folder if parent else ""
        self.photo_captions_from_var = parent.photo_captions_from_var if parent else ""
        self.photo_captions_text_box_var = parent.photo_captions_text_box_var if parent else ""
        self.photo_captions_txt_file_path_var = parent.photo_captions_txt_file_path_var if parent else ""
        self.photo_random_var = parent.photo_Random_var if parent else False
        
        
        super().__init__(
            parent, 
            main_folder_path, 
            current_profile, 
            "Photos Configure Window"
        )
    
    def init_ui(self, layout):
        """Initialize UI components for photo post configuration"""
        # Download folder section
        """         download_label = QLabel("download_folder_configure")
        download_label.setFont(QFont("Arial", 13, QFont.Bold))
        #download_label.setObjectName("download_label")
        download_label.setAlignment(Qt.AlignCenter)
        download_label.setStyleSheet("border:1px solid rgba(128,128,128,1);background-color:rgba(128,128,128,0.3);font-weight: bold; font-size: 9pt;border-radius:8px;padding:5px 5px 5px 5px;text-align:center;")
        download_label.setFixedHeight(25)
        download_label.setFixedWidth(300)
        layout.addWidget(download_label) """
        
        self.download_folder_frame = FolderConfigFrame(
            self,
            "Download Folder",
            "Download Photo Folder:",
            self.photo_post_download_image_folder,
            self.photo_download_browse,
            self.create_photo_download_folder
        )
        layout.addWidget(self.download_folder_frame)
        


        # Captions section
        self.captions_frame = CaptionsConfigFrame(
            self,
            self.photo_captions_from_var,
            self.photo_captions_text_box_var,
            self.photo_captions_txt_file_path_var,
            self.photo_random_var
        )
        layout.addWidget(self.captions_frame)
        
        
    def photo_download_browse(self):
        """Browse for photo download folder"""
        folder = self.browse_folder()
        if folder:
            self.photo_post_download_image_folder = folder
            self.download_folder_frame.set_folder_path(folder)
            self._parent.photo_post_download_image_folder = folder
            self.photos_create_folder()
    def create_photo_download_folder(self):
        """Create folder for downloaded photos"""
        if not self.main_folder_path:
            QMessageBox.critical(self, "Main folder", "Please select main folder first")
            return
            
        main_folder_for_download = os.path.dirname(self.main_folder_path)
        download_image_folder_name = f"{self.current_profile}_donwload_id_act_photo"
        
        folder_path = os.path.join(main_folder_for_download,self.current_profile, download_image_folder_name)
        folder_path = os.path.normpath(folder_path)
        folder_created = False
        
        if os.path.exists(folder_path):
            folder_created = False
        else:
            os.makedirs(folder_path, exist_ok=True)
            folder_created = True
        
        
        if folder_path:
            self.photo_post_download_image_folder = folder_path
            self.download_folder_frame.set_folder_path(folder_path)
            self._parent.photo_post_download_image_folder = folder_path
            self.show_folder_creation_result(folder_created)

        self.photos_create_folder()
    def photos_create_folder(self):
        """Create folder for photos"""
        if not self.main_folder_path:
            QMessageBox.critical(self, "Main folder", "Please select main folder first")
            return
            
        image_folder_name = f"{self.current_profile}_id_act_photo"
        folder_path = os.path.join(self.main_folder_path,image_folder_name)
        folder_path = os.path.normpath(folder_path)

        if os.path.exists(folder_path):
            folder_created = False
        else:
            os.makedirs(folder_path, exist_ok=True)
            folder_created = True
        
        if folder_path:
            self.photo_post_image_folder = folder_path
            self._parent.photo_post_image_folder = folder_path
            #self.show_folder_creation_result(folder_created)

    def closeEvent(self, event):
        if self._parent and hasattr(self, 'captions_frame') and self.captions_frame:
            # Get methods safely, returns None if method doesn't exist
            caption_source = getattr(self.captions_frame, 'get_caption_source', lambda: None)()
            text_box_content = getattr(self.captions_frame, 'get_text_box_content', lambda: None)()
            file_path = getattr(self.captions_frame, 'get_file_path', lambda: None)()
            random_state = getattr(self.captions_frame, 'get_random_state', lambda: None)()

            # Only assign if values are not None
            if caption_source is not None:
                self._parent.photo_captions_from_var = caption_source
            if text_box_content is not None:
                self._parent.photo_captions_text_box_var = text_box_content
            if file_path is not None:
                self._parent.photo_captions_txt_file_path_var = file_path
            if random_state is not None:
                self._parent.photo_Random_var = random_state
                
        if self.save_callback is not None:
            self.save_callback()
        super().closeEvent(event)





class CheckinPostConfigWindow(PhotoConfigWindow):
    def __init__(self, parent=None, main_folder_path="", current_profile="", save_callback=None):
        self._parent = parent
        self.save_callback = save_callback
        self.post_checkin_Download_photo_Folder = parent.post_checkin_Download_photo_Folder if parent else ""
        self.post_checkin_ld_photo_folder = parent.post_checkin_ld_photo_folder if parent else ""
        self.post_checkin_captions_from_var = parent.post_checkin_captions_from_var if parent else ""
        self.post_checkin_captions_text_box_var = parent.post_checkin_captions_text_box_var if parent else ""
        self.add_photo_to_checkin_post_var = parent.add_photo_to_checkin_post_var if parent else False
        self.location_of_checkin_post_var = parent.location_of_checkin_post_var if parent else ""
        self.checkin_photo_captions_txt_file_path_var = parent.checkin_photo_captions_txt_file_path_var if parent else ""
        self.post_checkin_text_caption_random_var = parent.post_checkin_text_caption_Random_var if parent else False 
        
        super().__init__(
            parent, 
            main_folder_path, 
            current_profile, 
            "CheckIN Post Configure Window"
        )
    
    def init_ui(self, layout):
        add_photo_to_checkin_groupbox = QGroupBox()
        add_photo_to_checkin_groupbox.setObjectName("add_photo_to_checkin_groupbox")
        add_photo_to_checkin_groupbox.setTitle("Check if add photo")
        add_photo_to_checkin_groupbox.setStyleSheet("""QGroupBox#add_photo_to_checkin_groupbox{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.1);}
                                            QGroupBox#add_photo_to_checkin_groupbox::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")  
        
        add_photo_to_checkin_layout = QHBoxLayout(add_photo_to_checkin_groupbox)

        self.add_photo_to_checkin_checkbox = QCheckBox(text="Add Photo with checkIN")
        self.add_photo_to_checkin_checkbox.setChecked(self.add_photo_to_checkin_post_var)
        add_photo_to_checkin_layout.addWidget(self.add_photo_to_checkin_checkbox)

        #add cheackin_loaction entry 

        location_of_checkin_groupbox = QGroupBox()
        location_of_checkin_groupbox.setObjectName("location_checkin_groupbox")
        location_of_checkin_groupbox.setTitle("Enter CheackIN Location")
        location_of_checkin_groupbox.setStyleSheet("""QGroupBox#location_checkin_groupbox{border:2px solid rgba(128,128,128,0.8);
                                    border-radius:8px;
                                    padding-top:5px;
                                    margin-top:10px;
                                    padding-right:10px;
                                    padding-left:10px;
                                    padding-bottom:5px;
                                    background-color: rgba(128,128,128,0.1);}
                                            QGroupBox#location_checkin_groupbox::title {
                                                            subcontrol-origin: margin;
                                                            subcontrol-position: top left;
                                                            left: 30px;
                                                            border-radius:5px;
                                                            padding-left: 5px;
                                                            padding-right: 5px;
                                                            background-color: rgba(128,128,128,0.5);
                                                        }""")  
        
        location_of_checkin_layout = QHBoxLayout(location_of_checkin_groupbox)

        self.location_of_checkin_label = QLabel("checkIN Location:")
        
        location_of_checkin_layout.addWidget(self.location_of_checkin_label)

        self.loaction_of_cheackin_entry = QLineEdit()
        self.loaction_of_cheackin_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
               
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
        self.loaction_of_cheackin_entry.setText(self.location_of_checkin_post_var)
        location_of_checkin_layout.addWidget(self.loaction_of_cheackin_entry)


        layout.addWidget(add_photo_to_checkin_groupbox)
        layout.addWidget(location_of_checkin_groupbox)

        self.download_folder_frame = FolderConfigFrame(
            self,
            "Photos Download Folder",
            "Download Photo Folder:",
            self.post_checkin_Download_photo_Folder,
            self.checkin_photo_download_browse,
            self.create_checkin_photo_download_folder
        )
        layout.addWidget(self.download_folder_frame)
        
        self.captions_frame = CaptionsConfigFrame(
            self,
            self.post_checkin_captions_from_var,
            self.post_checkin_captions_text_box_var,
            self.checkin_photo_captions_txt_file_path_var,
            self.post_checkin_text_caption_random_var
        )
        layout.addWidget(self.captions_frame)

    def checkin_photo_download_browse(self):
        folder = self.browse_folder()
        if folder:
            self.post_checkin_Download_photo_Folder = folder
            self.download_folder_frame.set_folder_path(folder)
            self._parent.post_checkin_Download_photo_Folder = folder
            self.checkin_photos_create_folder()

    def create_checkin_photo_download_folder(self):
        if not self.main_folder_path:
            QMessageBox.critical(self, "Main folder", "Please select main folder first")
            return
            
        main_folder_for_download = os.path.dirname(self.main_folder_path)
        download_image_folder_name = f"{self.current_profile}_download_id_act_checkin_photo"  
        folder_path = os.path.join(main_folder_for_download, self.current_profile, download_image_folder_name)
        folder_path = os.path.normpath(folder_path)
        folder_created = False

        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            folder_created = True

        if folder_path:
            self.post_checkin_Download_photo_Folder = folder_path
            self.download_folder_frame.set_folder_path(folder_path)
            self._parent.post_checkin_Download_photo_Folder = folder_path
            self.show_folder_creation_result(folder_created)
            self.checkin_photos_create_folder()

    def checkin_photos_create_folder(self):
        """Create folder for check-in photos"""
        if not self.main_folder_path:
            QMessageBox.critical(self, "Main folder", "Please select main folder first")
            return
            
        image_folder_name = f"{self.current_profile}_id_act_checkin_photo"
        folder_path = os.path.join(self.main_folder_path, image_folder_name)
        folder_path = os.path.normpath(folder_path)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            folder_created = True
        else:
            folder_created = False
        
        if folder_path:
            self.post_checkin_ld_photo_folder = folder_path
            self._parent.post_checkin_ld_photo_folder = folder_path
            #  Uncomment to show
            # self.show_folder_creation_result(folder_created)

    def closeEvent(self, event):
        if self._parent:
            # Safely get checkbox state
            if hasattr(self, 'add_photo_to_checkin_checkbox') and self.add_photo_to_checkin_checkbox:
                self._parent.add_photo_to_checkin_post_var = self.add_photo_to_checkin_checkbox.isChecked()
            
            # Safely get captions frame data
            if hasattr(self, 'captions_frame') and self.captions_frame:
                if hasattr(self.captions_frame, 'get_caption_source'):
                    self._parent.post_checkin_captions_from_var = self.captions_frame.get_caption_source()
                
                if hasattr(self.captions_frame, 'get_text_box_content'):
                    self._parent.post_checkin_captions_text_box_var = self.captions_frame.get_text_box_content()
                
                if hasattr(self.captions_frame, 'get_file_path'):
                    self._parent.checkin_photo_captions_txt_file_path_var = self.captions_frame.get_file_path()
                
                if hasattr(self.captions_frame, 'get_random_state'):
                    self._parent.post_checkin_text_caption_Random_var = self.captions_frame.get_random_state()
            
            # Safely get location text
            if hasattr(self, 'loaction_of_cheackin_entry') and self.loaction_of_cheackin_entry:
                self._parent.location_of_checkin_post_var = self.loaction_of_cheackin_entry.text()
        
        # Safely call save callback
        if hasattr(self, 'save_callback') and self.save_callback is not None:
            self.save_callback()
        
        super().closeEvent(event)
    


class StoryPostConfigWindow(PhotoConfigWindow):
    def __init__(self, parent=None, save_callback=None, main_folder_path="", current_profile=""):
        self._parent = parent
        self.save_callback = save_callback
        self.story_video_Download_Folder = parent.story_video_Download_Folder if parent else ""
        self.story_video_Folder = parent.story_video_Folder if parent else ""
        self.story_video_captions_from_var = parent.story_video_captions_from_var if parent else ""
        self.story_video_captions_text_box_var = parent.story_video_captions_text_box_var if parent else ""
        self.story_video_captions_txt_file_path_var = parent.story_video_captions_txt_file_path_var if parent else ""
        self.story_video_text_caption_Random_var = parent.story_video_text_caption_Random_var if parent else False
        
        super().__init__(
            parent, 
            main_folder_path, 
            current_profile, 
            "Story Configure Window"
        )
    
    def init_ui(self, layout):
        self.download_folder_frame = FolderConfigFrame(
            self,
            "Download Folder",
            "Download Video Folder:",
            self.story_video_Download_Folder,
            self.video_download_browse,
            self.create_video_download_folder
        )
        layout.addWidget(self.download_folder_frame)
        
        self.captions_frame = CaptionsConfigFrame(
            self,
            self.story_video_captions_from_var,
            self.story_video_captions_text_box_var,
            self.story_video_captions_txt_file_path_var,
            self.story_video_text_caption_Random_var
        )
        layout.addWidget(self.captions_frame)
        
    def video_download_browse(self):
        folder = self.browse_folder()
        if folder:
            self.story_video_Download_Folder = folder
            self.download_folder_frame.set_folder_path(folder)
            self._parent.story_video_Download_Folder = folder
            self.video_create_folder()  

    def create_video_download_folder(self):
        if not self.main_folder_path:
            QMessageBox.critical(self, "Main folder", "Please select main folder first")
            return
            
        main_folder_for_download = os.path.dirname(self.main_folder_path)
        download_video_folder_name = f"{self.current_profile}_download_id_act_story_video"  
        folder_path = os.path.join(main_folder_for_download, self.current_profile, download_video_folder_name)
        folder_path = os.path.normpath(folder_path)
        folder_created = False
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            folder_created = True
        
        if folder_path:
            self.story_video_Download_Folder = folder_path
            self.download_folder_frame.set_folder_path(folder_path)
            self._parent.story_video_Download_Folder = folder_path
            self.show_folder_creation_result(folder_created)
            self.video_create_folder() 
    
    def video_create_folder(self):
        """Create folder for story videos"""
        if not self.main_folder_path:
            QMessageBox.critical(self, "Main folder", "Please select main folder first")
            return
            
        video_folder_name = f"{self.current_profile}_id_act_story_video"  
        folder_path = os.path.join(self.main_folder_path, video_folder_name)
        folder_path = os.path.normpath(folder_path)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            folder_created = True
        else:
            folder_created = False

        if folder_path:
            self.story_video_Folder = folder_path
            self._parent.story_video_Folder = folder_path
            # Optional: Uncomment to show feedback
            # self.show_folder_creation_result(folder_created)

    def closeEvent(self, event):
        if self._parent:
            # Safely get captions frame data for story video
            if hasattr(self, 'captions_frame') and self.captions_frame:
                if hasattr(self.captions_frame, 'get_caption_source'):
                    self._parent.story_video_captions_from_var = self.captions_frame.get_caption_source()

                if hasattr(self.captions_frame, 'get_text_box_content'):
                    self._parent.story_video_captions_text_box_var = self.captions_frame.get_text_box_content()

                if hasattr(self.captions_frame, 'get_file_path'):
                    self._parent.story_video_captions_txt_file_path_var = self.captions_frame.get_file_path()

                if hasattr(self.captions_frame, 'get_random_state'):
                    self._parent.story_video_text_caption_Random_var = self.captions_frame.get_random_state()

        # Safely call save callback
        if hasattr(self, 'save_callback') and self.save_callback is not None:
            self.save_callback()

        super().closeEvent(event)


class ReelConfigureWindowComments(QDialog):
    
    def __init__(self,parent,save_callback,
        window_title="Configure Window", label_text="Comments",textbox_placeholder_text = "Enter some comments"):
        super().__init__()

        self._parent = parent
        self.setWindowTitle(window_title)
        self.setFixedSize(700, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.textbox_placeholder_text = textbox_placeholder_text
        self.label_text = label_text
        
        # Store variables - in PySide6 we'll need to handle these differently than in ctk
        self.from_where_comments_var = parent.scroll_reels_video_comments_from_var
        self.comments_txt_file_path_var = parent.scroll_reels_video_comments_txt_file_path_var
        self.txt_file_comments_random_var = parent.scroll_reels_video_comments_txt_file_random_var
        self.comments_text_box_var = parent.scroll_reels_video_comments_txt_box_var
        self.on_close_callback = save_callback
        # Setup the UI
        self._create_widget()

    def _create_widget(self):
        main_layout = QVBoxLayout(self)
        auto_edits = self.comments_frame()
        main_layout.addWidget(auto_edits)
        self.setLayout(main_layout)

    def comments_frame(self):
        # Create the main frame
        frame = QFrame()
        #frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("QFrame { border:none; }")
        
        # Main vertical layout for the frame
        main_layout = QVBoxLayout(frame)
        
        # Add the header label
        header_label = QLabel(self.label_text)
        header_label.setFixedWidth(250)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("border:1px solid rgba(128,128,128,1);background-color:rgba(128,128,128,0.3);font-weight: bold; font-size: 9pt;border-radius:8px;padding:5px 5px 5px 5px;text-align:center;")
        main_layout.addWidget(header_label)
        
        
        # Frame for the combobox and label
        title_from_frame = QFrame()
        title_from_layout = QHBoxLayout(title_from_frame)
        title_from_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add label and combobox
        from_label = QLabel("Captions From")
        from_label.setStyleSheet("border:none;")
        title_from_layout.addWidget(from_label)
        
        self.title_from_combobox = QComboBox()
        self.title_from_combobox.addItems(["From Text Box", "From text file"])
        self.title_from_combobox.setCurrentText(self.from_where_comments_var)
        self.title_from_combobox.currentTextChanged.connect(self.option_comment_text_config)
        title_from_layout.addWidget(self.title_from_combobox)
        title_from_layout.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(title_from_frame)
        
        # Create a 
        self.title_from_msg_frame = QFrame()
        self.title_from_msg_frame.setObjectName("title_from_msg_frame")
        self.title_from_msg_frame.setStyleSheet("""QFrame#title_from_msg_frame{border:2px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    background-color: rgba(128,128,128,0.2);}""")
        
        self.title_from_msg_layout = QHBoxLayout(self.title_from_msg_frame)
        
        main_layout.addWidget(self.title_from_msg_frame)
        main_layout.setAlignment(Qt.AlignTop)
        # Initialize 
        self.option_comment_text_config(self.from_where_comments_var)
        
        return frame

    def option_comment_text_config(self, value):
       
        while self.title_from_msg_layout.count():
            item = self.title_from_msg_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if value == "From Text Box":
          
            text_container = QWidget()
            text_container_layout = QHBoxLayout(text_container)
            text_container_layout.setContentsMargins(0, 0, 0, 0)

            text_label = QLabel("Text Box: ")
            text_label.setStyleSheet("border:none;")
            text_container_layout.addWidget(text_label)

            self.title_text_box = QTextEdit()
            self.title_text_box.setPlaceholderText(self.textbox_placeholder_text)
            self.title_text_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                           /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;           /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QTextEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QTextEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QTextEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            self.title_text_box.setFixedSize(400, 200)
            self.title_text_box.setText(self.comments_text_box_var)
            text_container_layout.addWidget(self.title_text_box)

   
            self.title_from_msg_layout.addWidget(text_container, 0, Qt.AlignLeft)

            self.title_from_msg_layout.addStretch(1)

        elif value == "From text file":
       
            file_label = QLabel("Text File Path: ")
            file_label.setStyleSheet("border:none;")
            self.title_from_msg_layout.addWidget(file_label)

            self.file_path_entry = QLineEdit()
            self.file_path_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                               /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            self.file_path_entry.setText(self.comments_txt_file_path_var)
            self.file_path_entry.setFixedSize(300, 20)
            self.title_from_msg_layout.addWidget(self.file_path_entry)

            browse_button = AnimatedHoverButton(text="Browse")
            browse_button.setFixedSize(80, 30)
            browse_button.clicked.connect(self.browse_commnets_txt_file)
            self.title_from_msg_layout.addWidget(browse_button)

            random_checkbox = QCheckBox("Random")
            random_checkbox.setFixedSize(80, 30)

       
            is_checked = False
            if isinstance(self.txt_file_comments_random_var, str):
                is_checked = self.txt_file_comments_random_var.lower() == 'true'
            elif isinstance(self.txt_file_comments_random_var, bool):
                is_checked = self.txt_file_comments_random_var

            random_checkbox.setChecked(is_checked)
            self.random_checkbox = random_checkbox  
            self.title_from_msg_layout.addWidget(random_checkbox)
            self.title_from_msg_layout.setContentsMargins(10, 10, 10, 10)
            self.title_from_msg_layout.addStretch(1)
        else:
            none_label = QLabel("None")
            none_label.setStyleSheet("border:none;")
            self.title_from_msg_layout.addWidget(none_label)



    def browse_commnets_txt_file(self):
   
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Text File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.file_path_entry.setText(file_path)
            self.comments_txt_file_path_var = file_path
      
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
    
  
    def get_comments_text_box_var(self):
        if hasattr(self, 'title_text_box'):
            return self.title_text_box.toPlainText()
        return self.comments_text_box_var
    
    def get_from_where_comments_var(self):
        return self.title_from_combobox.currentText()
    
    def get_comments_txt_file_path_var(self):
        if hasattr(self, 'file_path_entry'):
            return self.file_path_entry.text()
        return self.comments_txt_file_path_var
    
    def get_txt_file_comments_random_var(self):
        if hasattr(self, 'random_checkbox'):
            return self.random_checkbox.isChecked()
        return self.txt_file_comments_random_var
    
    def closeEvent(self, event):
        """Override the close event to run our callback"""
        if self._parent:
            # Safely get comments data
            if hasattr(self, 'get_comments_text_box_var'):
                self._parent.scroll_reels_video_comments_txt_box_var = self.get_comments_text_box_var()

            if hasattr(self, 'get_from_where_comments_var'):
                self._parent.scroll_reels_video_comments_from_var = self.get_from_where_comments_var()

            if hasattr(self, 'get_comments_txt_file_path_var'):
                self._parent.scroll_reels_video_comments_txt_file_path_var = self.get_comments_txt_file_path_var()

            if hasattr(self, 'get_txt_file_comments_random_var'):
                self._parent.scroll_reels_video_comments_txt_file_random_var = self.get_txt_file_comments_random_var()

        # Run the callback function if one was provided
        if hasattr(self, 'on_close_callback') and self.on_close_callback:
            self.on_close_callback()

        super().closeEvent(event)

class Scroll_feed_ConfigureWindowComments(QDialog):
    
    def __init__(self,parent,save_callback,
        window_title="Configure Window", label_text="Comments",textbox_placeholder_text = "Enter some comments"):
        super().__init__()

        self._parent = parent
        self.setWindowTitle(window_title)
        self.setFixedSize(700, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.textbox_placeholder_text = textbox_placeholder_text
        self.label_text = label_text
        
        # Store variables - in PySide6 we'll need to handle these differently than in ctk
        self.from_where_comments_var = parent.scroll_feed_comments_from_var
        self.comments_txt_file_path_var = parent.scroll_feed_comments_txt_file_path_var
        self.txt_file_comments_random_var = parent.scroll_feed_comments_txt_file_random
        self.comments_text_box_var = parent.scroll_feed_comments_txt_box_var
        self.on_close_callback = save_callback
        # Setup the UI
        self._create_widget()

    def _create_widget(self):
        main_layout = QVBoxLayout(self)
        auto_edits = self.comments_frame()
        main_layout.addWidget(auto_edits)
        self.setLayout(main_layout)

    def comments_frame(self):
        # Create the main frame
        frame = QFrame()
        #frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("QFrame { border:none; }")
        
        # Main vertical layout for the frame
        main_layout = QVBoxLayout(frame)
        
        # Add the header label
        header_label = QLabel(self.label_text)
        header_label.setFixedWidth(250)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("border:1px solid rgba(128,128,128,1);background-color:rgba(128,128,128,0.3);font-weight: bold; font-size: 9pt;border-radius:8px;padding:5px 5px 5px 5px;text-align:center;")
        main_layout.addWidget(header_label)
        
        
        # Frame for the combobox and label
        title_from_frame = QFrame()
        title_from_layout = QHBoxLayout(title_from_frame)
        #title_from_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add label and combobox
        from_label = QLabel("Captions From")
        from_label.setStyleSheet("border:none;")
        title_from_layout.addWidget(from_label)
        
        self.title_from_combobox = QComboBox()
        self.title_from_combobox.addItems(["From Text Box", "From text file"])
        self.title_from_combobox.setCurrentText(self.from_where_comments_var)
        self.title_from_combobox.currentTextChanged.connect(self.option_comment_text_config)
        title_from_layout.addWidget(self.title_from_combobox)
        title_from_layout.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(title_from_frame)
        
        # Create a 
        self.title_from_msg_frame = QFrame()
        self.title_from_msg_frame.setObjectName("title_from_msg_frame")
        self.title_from_msg_frame.setStyleSheet("""QFrame#title_from_msg_frame{border:2px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    background-color: rgba(128,128,128,0.2);}""")
        
        self.title_from_msg_layout = QHBoxLayout(self.title_from_msg_frame)
        
        main_layout.addWidget(self.title_from_msg_frame)
        main_layout.setAlignment(Qt.AlignTop)
        # Initialize 
        self.option_comment_text_config(self.from_where_comments_var)
        
        return frame

    def option_comment_text_config(self, value):
       
        while self.title_from_msg_layout.count():
            item = self.title_from_msg_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if value == "From Text Box":
          
            text_container = QWidget()
            text_container_layout = QHBoxLayout(text_container)
            text_container_layout.setContentsMargins(0, 0, 0, 0)

            text_label = QLabel("Text Box: ")
            text_label.setStyleSheet("border:none;")
            text_container_layout.addWidget(text_label)

            self.title_text_box = QTextEdit()
            self.title_text_box.setPlaceholderText(self.textbox_placeholder_text)
            self.title_text_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                          /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;           /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QTextEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QTextEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QTextEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            self.title_text_box.setFixedSize(400, 200)
            self.title_text_box.setText(self.comments_text_box_var)
            text_container_layout.addWidget(self.title_text_box)

   
            self.title_from_msg_layout.addWidget(text_container, 0, Qt.AlignLeft)

            self.title_from_msg_layout.addStretch(1)

        elif value == "From text file":
       
            file_label = QLabel("Text File Path: ")
            file_label.setStyleSheet("border:none;")
            self.title_from_msg_layout.addWidget(file_label)

            self.file_path_entry = QLineEdit()
            self.file_path_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
               
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            self.file_path_entry.setText(self.comments_txt_file_path_var)
            self.file_path_entry.setFixedSize(300, 20)
            self.title_from_msg_layout.addWidget(self.file_path_entry)

            browse_button = AnimatedHoverButton(text="Browse")
            browse_button.setFixedSize(80, 30)
            browse_button.clicked.connect(self.browse_commnets_txt_file)
            self.title_from_msg_layout.addWidget(browse_button)

            random_checkbox = QCheckBox("Random")
            random_checkbox.setFixedSize(80, 30)

       
            is_checked = False
            if isinstance(self.txt_file_comments_random_var, str):
                is_checked = self.txt_file_comments_random_var.lower() == 'true'
            elif isinstance(self.txt_file_comments_random_var, bool):
                is_checked = self.txt_file_comments_random_var

            random_checkbox.setChecked(is_checked)
            self.random_checkbox = random_checkbox  
            self.title_from_msg_layout.addWidget(random_checkbox)
            self.title_from_msg_layout.setContentsMargins(10, 10, 10, 10)
            self.title_from_msg_layout.addStretch(1)
        else:
            none_label = QLabel("None")
            none_label.setStyleSheet("border:none;")
            self.title_from_msg_layout.addWidget(none_label)



    def browse_commnets_txt_file(self):
   
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Text File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.file_path_entry.setText(file_path)
            self.comments_txt_file_path_var = file_path
      
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
    
  
    def get_comments_text_box_var(self):
        if hasattr(self, 'title_text_box'):
            return self.title_text_box.toPlainText()
        return self.comments_text_box_var
    
    def get_from_where_comments_var(self):
        return self.title_from_combobox.currentText()
    
    def get_comments_txt_file_path_var(self):
        if hasattr(self, 'file_path_entry'):
            return self.file_path_entry.text()
        return self.comments_txt_file_path_var
    
    def get_txt_file_comments_random_var(self):
        if hasattr(self, 'random_checkbox'):
            return self.random_checkbox.isChecked()
        return self.txt_file_comments_random_var
    
    def closeEvent(self, event):
        """Override the close event to run our callback"""
        parent = self._parent

        if parent:
            # Safely get comments data
            if hasattr(self, 'get_comments_text_box_var'):
                parent.scroll_feed_comments_txt_box_var = self.get_comments_text_box_var()

            if hasattr(self, 'get_from_where_comments_var'):
                parent.scroll_feed_comments_from_var = self.get_from_where_comments_var()

            if hasattr(self, 'get_comments_txt_file_path_var'):
                parent.scroll_feed_comments_txt_file_path_var = self.get_comments_txt_file_path_var()

            if hasattr(self, 'get_txt_file_comments_random_var'):
                parent.scroll_feed_comments_txt_file_random = self.get_txt_file_comments_random_var()

        # Run the callback function if one was provided
        if hasattr(self, 'on_close_callback') and self.on_close_callback:
            self.on_close_callback()

        super().closeEvent(event)

class Scroll_reel_video_group_ConfigureWindow(QDialog):
    
    def __init__(self,parent,save_callback,
        window_title="Configure Window", label_text="Comments",textbox_placeholder_text = "Enter some comments"):
        super().__init__()

        self._parent = parent
        self.setWindowTitle(window_title)
        self.setFixedSize(700, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.textbox_placeholder_text = textbox_placeholder_text
        self.label_text = label_text
        
        # Store variables - in PySide6 we'll need to handle these differently than in ctk
        self.from_where_comments_var = parent.scroll_reels_video_groups_from_var
        self.comments_txt_file_path_var = parent.scroll_reels_video_groups_txt_file_path_var
        self.txt_file_comments_random_var = parent.scroll_reels_video_groups_txt_file_random
        self.comments_text_box_var = parent.scroll_reels_video_groups_txt_box_var
        self.on_close_callback = save_callback
        # Setup the UI
        self._create_widget()

    def _create_widget(self):
        main_layout = QVBoxLayout(self)
        auto_edits = self.comments_frame()
        main_layout.addWidget(auto_edits)
        self.setLayout(main_layout)

    def comments_frame(self):
        # Create the main frame
        frame = QFrame()
        #frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("QFrame { border:none; }")
        
        # Main vertical layout for the frame
        main_layout = QVBoxLayout(frame)
        
        # Add the header label
        header_label = QLabel(self.label_text)
        header_label.setFixedWidth(250)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("border:1px solid rgba(128,128,128,1);background-color:rgba(128,128,128,0.3);font-weight: bold; font-size: 9pt;border-radius:8px;padding:5px 5px 5px 5px;text-align:center;")
        main_layout.addWidget(header_label)
        
        
        # Frame for the combobox and label
        title_from_frame = QFrame()
        title_from_layout = QHBoxLayout(title_from_frame)
        title_from_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add label and combobox
        from_label = QLabel("Captions From")
        from_label.setStyleSheet("border:none;")
        title_from_layout.addWidget(from_label)
        
        self.title_from_combobox = QComboBox()
        self.title_from_combobox.addItems(["From Text Box", "From text file"])
        self.title_from_combobox.setCurrentText(self.from_where_comments_var)
        self.title_from_combobox.currentTextChanged.connect(self.option_comment_text_config)
        title_from_layout.addWidget(self.title_from_combobox)
        title_from_layout.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(title_from_frame)
        
        # Create a 
        self.title_from_msg_frame = QFrame()
        self.title_from_msg_frame.setObjectName("title_from_msg_frame")
        self.title_from_msg_frame.setStyleSheet("""QFrame#title_from_msg_frame{border:2px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    background-color: rgba(128,128,128,0.2);}""")
        
        self.title_from_msg_layout = QHBoxLayout(self.title_from_msg_frame)
        
        main_layout.addWidget(self.title_from_msg_frame)
        main_layout.setAlignment(Qt.AlignTop)
        # Initialize 
        self.option_comment_text_config(self.from_where_comments_var)
        
        return frame

    def option_comment_text_config(self, value):
       
        while self.title_from_msg_layout.count():
            item = self.title_from_msg_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if value == "From Text Box":
          
            text_container = QWidget()
            text_container_layout = QHBoxLayout(text_container)
            text_container_layout.setContentsMargins(0, 0, 0, 0)

            text_label = QLabel("Text Box: ")
            text_label.setStyleSheet("border:none;")
            text_container_layout.addWidget(text_label)

            self.title_text_box = QTextEdit()
            self.title_text_box.setPlaceholderText(self.textbox_placeholder_text)
            self.title_text_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                                 /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;           /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QTextEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QTextEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QTextEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            self.title_text_box.setFixedSize(400, 200)
            self.title_text_box.setText(self.comments_text_box_var)
            text_container_layout.addWidget(self.title_text_box)

   
            self.title_from_msg_layout.addWidget(text_container, 0, Qt.AlignLeft)

            self.title_from_msg_layout.addStretch(1)

        elif value == "From text file":
       
            file_label = QLabel("Text File Path: ")
            file_label.setStyleSheet("border:none;")
            self.title_from_msg_layout.addWidget(file_label)

            self.file_path_entry = QLineEdit()
            self.file_path_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                              /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            self.file_path_entry.setText(self.comments_txt_file_path_var)
            self.file_path_entry.setFixedSize(300, 20)
            self.title_from_msg_layout.addWidget(self.file_path_entry)

            browse_button = AnimatedHoverButton(text="Browse")
            browse_button.setFixedSize(80, 30)
            browse_button.clicked.connect(self.browse_commnets_txt_file)
            self.title_from_msg_layout.addWidget(browse_button)

            random_checkbox = QCheckBox("Random")
            random_checkbox.setFixedSize(80, 30)

       
            is_checked = False
            if isinstance(self.txt_file_comments_random_var, str):
                is_checked = self.txt_file_comments_random_var.lower() == 'true'
            elif isinstance(self.txt_file_comments_random_var, bool):
                is_checked = self.txt_file_comments_random_var

            random_checkbox.setChecked(is_checked)
            self.random_checkbox = random_checkbox  
            self.title_from_msg_layout.addWidget(random_checkbox)
            self.title_from_msg_layout.setContentsMargins(10, 10, 10, 10)
            self.title_from_msg_layout.addStretch(1)
        else:
            none_label = QLabel("None")
            none_label.setStyleSheet("border:none;")
            self.title_from_msg_layout.addWidget(none_label)



    def browse_commnets_txt_file(self):
   
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Text File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.file_path_entry.setText(file_path)
            self.comments_txt_file_path_var = file_path
      
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
    
  
    def get_comments_text_box_var(self):
        if hasattr(self, 'title_text_box'):
            return self.title_text_box.toPlainText()
        return self.comments_text_box_var
    
    def get_from_where_comments_var(self):
        return self.title_from_combobox.currentText()
    
    def get_comments_txt_file_path_var(self):
        if hasattr(self, 'file_path_entry'):
            return self.file_path_entry.text()
        return self.comments_txt_file_path_var
    
    def get_txt_file_comments_random_var(self):
        if hasattr(self, 'random_checkbox'):
            return self.random_checkbox.isChecked()
        return self.txt_file_comments_random_var
    
    def closeEvent(self, event):
        """Override the close event to run our callback"""
        parent = self._parent

        if parent:
            # Safely get comments data for reels video groups
            if hasattr(self, 'get_comments_text_box_var'):
                parent.scroll_reels_video_groups_txt_box_var = self.get_comments_text_box_var()

            if hasattr(self, 'get_from_where_comments_var'):
                parent.scroll_reels_video_groups_from_var = self.get_from_where_comments_var()

            if hasattr(self, 'get_comments_txt_file_path_var'):
                parent.scroll_reels_video_groups_txt_file_path_var = self.get_comments_txt_file_path_var()

            if hasattr(self, 'get_txt_file_comments_random_var'):
                parent.scroll_reels_video_groups_txt_file_random = self.get_txt_file_comments_random_var()

        # Run the callback function if one was provided
        if hasattr(self, 'on_close_callback') and self.on_close_callback:
            self.on_close_callback()

        super().closeEvent(event)


class Scroll_feed_group_ConfigureWindow(QDialog):
    
    def __init__(self,parent,save_callback,
        window_title="Configure Window", label_text="Comments",textbox_placeholder_text = "Enter some comments"):
        super().__init__()

        self._parent = parent
        self.setWindowTitle(window_title)
        self.setFixedSize(700, 400)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.textbox_placeholder_text = textbox_placeholder_text
        self.label_text = label_text
        
        # Store variables - in PySide6 we'll need to handle these differently than in ctk
        self.from_where_comments_var = parent.scroll_feed_groups_from_var
        self.comments_txt_file_path_var = parent.scroll_feed_groups_txt_file_path_var
        self.txt_file_comments_random_var = parent.scroll_feed_groups_txt_file_random
        self.comments_text_box_var = parent.scroll_feed_groups_txt_box_var
        self.on_close_callback = save_callback
        # Setup the UI
        self._create_widget()

    def _create_widget(self):
        main_layout = QVBoxLayout(self)
        auto_edits = self.comments_frame()
        main_layout.addWidget(auto_edits)
        self.setLayout(main_layout)

    def comments_frame(self):
        # Create the main frame
        frame = QFrame()
        #frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("QFrame { border:none; }")
        
        # Main vertical layout for the frame
        main_layout = QVBoxLayout(frame)
        
        # Add the header label
        header_label = QLabel(self.label_text)
        header_label.setFixedWidth(250)
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("border:1px solid rgba(128,128,128,1);background-color:rgba(128,128,128,0.3);font-weight: bold; font-size: 9pt;border-radius:8px;padding:5px 5px 5px 5px;text-align:center;")
        main_layout.addWidget(header_label)
        
        
        # Frame for the combobox and label
        title_from_frame = QFrame()
        title_from_layout = QHBoxLayout(title_from_frame)
        title_from_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add label and combobox
        from_label = QLabel("Captions From")
        from_label.setStyleSheet("border:none;")
        title_from_layout.addWidget(from_label)
        
        self.title_from_combobox = QComboBox()
        self.title_from_combobox.addItems(["From Text Box", "From text file"])
        self.title_from_combobox.setCurrentText(self.from_where_comments_var)
        self.title_from_combobox.currentTextChanged.connect(self.option_comment_text_config)
        title_from_layout.addWidget(self.title_from_combobox)
        title_from_layout.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(title_from_frame)
        
        # Create a 
        self.title_from_msg_frame = QFrame()
        self.title_from_msg_frame.setObjectName("title_from_msg_frame")
        self.title_from_msg_frame.setStyleSheet("""QFrame#title_from_msg_frame{border:2px solid rgba(128,128,128,0.5);
                                    border-radius:8px;
                                    background-color: rgba(128,128,128,0.2);}""")
        
        self.title_from_msg_layout = QHBoxLayout(self.title_from_msg_frame)
        
        main_layout.addWidget(self.title_from_msg_frame)
        main_layout.setAlignment(Qt.AlignTop)
        # Initialize 
        self.option_comment_text_config(self.from_where_comments_var)
        
        return frame

    def option_comment_text_config(self, value):
       
        while self.title_from_msg_layout.count():
            item = self.title_from_msg_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if value == "From Text Box":
          
            text_container = QWidget()
            text_container_layout = QHBoxLayout(text_container)
            text_container_layout.setContentsMargins(0, 0, 0, 0)

            text_label = QLabel("Text Box: ")
            text_label.setStyleSheet("border:none;")
            text_container_layout.addWidget(text_label)

            self.title_text_box = QTextEdit()
            self.title_text_box.setPlaceholderText(self.textbox_placeholder_text)
            self.title_text_box.setStyleSheet("""
            QTextEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
                             /* light text */  
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;           /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QTextEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QTextEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QTextEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            self.title_text_box.setFixedSize(400, 200)
            self.title_text_box.setText(self.comments_text_box_var)
            text_container_layout.addWidget(self.title_text_box)

   
            self.title_from_msg_layout.addWidget(text_container, 0, Qt.AlignLeft)

            self.title_from_msg_layout.addStretch(1)

        elif value == "From text file":
       
            file_label = QLabel("Text File Path: ")
            file_label.setStyleSheet("border:none;")
            self.title_from_msg_layout.addWidget(file_label)

            self.file_path_entry = QLineEdit()
            self.file_path_entry.setStyleSheet("""
            QLineEdit {
                background-color: rgba(128,128,128,.3);           /* dark background */  
               
                border: 1px solid rgba(128,128,128,1);           /* subtle border */  
                border-radius: 8px;                  /* rounded corners */  
                padding: 2px 2px 2px 10px;              /* right padding for icon */  
                selection-background-color: #555555; /* selection highlight */  
            }
            QLineEdit::placeholder {
                color: #888888;                      /* muted placeholder */  
            }
            QLineEdit:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */  
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
                                             
            }
            QLineEdit:hover {
                background-color: #323232; 
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */  
            }
        """)
            self.file_path_entry.setText(self.comments_txt_file_path_var)
            self.file_path_entry.setFixedSize(300, 20)
            self.title_from_msg_layout.addWidget(self.file_path_entry)

            browse_button = AnimatedHoverButton(text="Browse")
            browse_button.setFixedSize(80, 30)
            browse_button.clicked.connect(self.browse_commnets_txt_file)
            self.title_from_msg_layout.addWidget(browse_button)

            random_checkbox = QCheckBox("Random")
            random_checkbox.setFixedSize(80, 30)

       
            is_checked = False
            if isinstance(self.txt_file_comments_random_var, str):
                is_checked = self.txt_file_comments_random_var.lower() == 'true'
            elif isinstance(self.txt_file_comments_random_var, bool):
                is_checked = self.txt_file_comments_random_var

            random_checkbox.setChecked(is_checked)
            self.random_checkbox = random_checkbox  
            self.title_from_msg_layout.addWidget(random_checkbox)
            self.title_from_msg_layout.setContentsMargins(10, 10, 10, 10)
            self.title_from_msg_layout.addStretch(1)
        else:
            none_label = QLabel("None")
            none_label.setStyleSheet("border:none;")
            self.title_from_msg_layout.addWidget(none_label)



    def browse_commnets_txt_file(self):
   
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a Text File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.file_path_entry.setText(file_path)
            self.comments_txt_file_path_var = file_path
      
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
    
  
    def get_comments_text_box_var(self):
        if hasattr(self, 'title_text_box'):
            return self.title_text_box.toPlainText()
        return self.comments_text_box_var
    
    def get_from_where_comments_var(self):
        return self.title_from_combobox.currentText()
    
    def get_comments_txt_file_path_var(self):
        if hasattr(self, 'file_path_entry'):
            return self.file_path_entry.text()
        return self.comments_txt_file_path_var
    
    def get_txt_file_comments_random_var(self):
        if hasattr(self, 'random_checkbox'):
            return self.random_checkbox.isChecked()
        return self.txt_file_comments_random_var
    
    def closeEvent(self, event):
        """Override the close event to run our callback"""
        parent = self._parent
        
        if parent:
            # Safely get comments data for feed groups
            if hasattr(self, 'get_comments_text_box_var'):
                parent.scroll_feed_groups_txt_box_var = self.get_comments_text_box_var()
            
            if hasattr(self, 'get_from_where_comments_var'):
                parent.scroll_feed_groups_from_var = self.get_from_where_comments_var()
            
            if hasattr(self, 'get_comments_txt_file_path_var'):
                parent.scroll_feed_groups_txt_file_path_var = self.get_comments_txt_file_path_var()
            
            if hasattr(self, 'get_txt_file_comments_random_var'):
                parent.scroll_feed_groups_txt_file_random = self.get_txt_file_comments_random_var()
    
        # Run the callback function if one was provided
        if hasattr(self, 'on_close_callback') and self.on_close_callback:
            self.on_close_callback()
        
        super().closeEvent(event)


class AnimatedHoverIntSpainButton(QPushButton):
    """QPushButton subclass with smooth color transition on hover."""
    def __init__(self, text, btn_padding=3,border_radius_size = 1, parent=None):
        super().__init__(text, parent)
        
        self._hoverLevel = 0.0
        self.button_border_radius = 1 
        if border_radius_size >=0.8:
            self.button_border_radius = 8 
        else:
            self.button_border_radius = 5

        # Calculate padding based on button size to maintain proportions
        self.btn_padding = btn_padding
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)
        # Animation setup
        self._anim = QPropertyAnimation(self, b"hoverLevel", self)
        self._anim.setDuration(200)  # 200 ms transition
   
        self.update_style()
        
    
        self.setDefault(False)
        self.setAutoDefault(False)

    def update_style(self):
       
        alpha = 0.5 + 0.3 * self._hoverLevel
        color = f"rgba(27,86,253,{alpha:.2f})"
        pressed_style = "rgba(27,86,253,1.0)"
        

        width = self.width() if self.width() > 0 else 30
        height = self.height() if self.height() > 0 else 20
        
   
        adjusted_padding = max(1, int(min(width, height) * 0.15))
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: {self.button_border_radius}px;
                padding: {adjusted_padding}px;
                text-align: center;
            }}
            QPushButton:pressed {{
                background-color: {pressed_style};
            }}
        """)

    def resizeEvent(self, event):
        # Update style when resized to maintain proportions
        self.update_style()
        super().resizeEvent(event)

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


class SmallIntSpinBox(QWidget):
    value_changed = Signal(float)  
    
    def __init__(self, parent=None, save_callback=None, from_=1, to=1000, initial=0, support_float=True, size=0.8):
        super().__init__(parent)
        self.from_ = from_
        self.to = to
        self.size = max(0.1, size)  

        self.save_callback = save_callback
        self.support_float = support_float
        

        self.base_button_height = 20
        self.base_button_width = 30
        self.base_entry_height = 20
        self.base_entry_width = 55
        if support_float is False:
            self.base_entry_width = 45
       
        self.button_height = max(10, int(self.base_button_height * self.size))
        self.button_width = max(15, int(self.base_button_width * self.size))
        self.entry_height = max(10, int(self.base_entry_height * self.size))
        self.entry_width = max(30, int(self.base_entry_width * self.size))
        
        # Set size policies to prevent stretching
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)  
        
        # decrease_button
        self.decrease_button = AnimatedHoverIntSpainButton("-", border_radius_size=self.size)
        self.decrease_button.setFixedSize(self.button_width, self.button_height)
        self.decrease_button.clicked.connect(self.decrease)
        layout.addWidget(self.decrease_button)
        

        if support_float:
            self.spin_box = QDoubleSpinBox()
            self.spin_box.setDecimals(1) 
            self.spin_box.setSingleStep(0.1)  
        else:
            self.spin_box = QSpinBox()
        

        border_radius = max(3, int(8 * self.size))
        
        self.spin_box.setStyleSheet(f"""
            QSpinBox, QDoubleSpinBox {{
                background-color: rgba(128,128,128,.3);
                
                border: 1px solid rgba(128,128,128,1);
                border-radius: {border_radius}px;
                selection-background-color: #555555;
                font-size: {max(8, int(10 * self.size))}pt;
                padding: {max(1, int(2 * self.size))}px;
            }}
            QSpinBox::placeholder, QDoubleSpinBox::placeholder {{
                color: #888888;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border: 1px solid rgba(128,128,128,1);
                border-radius: {border_radius}px;
                background-color: rgba(128,128,128,.2);
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                background-color: rgba(128,128,128,.2);
                border-radius: {border_radius}px;
            }}
        """)
        
        self.spin_box.setRange(from_, to)
        self.spin_box.setValue(initial)
        self.spin_box.setFixedSize(self.entry_width, self.entry_height)
        self.spin_box.setAlignment(Qt.AlignCenter)
        self.spin_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        layout.addWidget(self.spin_box)
        
        # increase button
        self.increase_button = AnimatedHoverIntSpainButton("+", border_radius_size=self.size)
        self.increase_button.setFixedSize(self.button_width, self.button_height)
        self.increase_button.clicked.connect(self.increase)
        layout.addWidget(self.increase_button)
        
        # Calculate total 
        spacing_buffer = 15  
        total_width = self.button_width + self.entry_width + self.button_width + spacing_buffer
        total_height = max(self.button_height, self.entry_height)
        
    
        self.setFixedSize(total_width, total_height)
        
        if self.save_callback:
            self.spin_box.editingFinished.connect(self.save_callback)
            self.decrease_button.clicked.connect(self.save_callback)  
            self.increase_button.clicked.connect(self.save_callback)  
    
    def get_value(self):
        return self.spin_box.value()
    
    def set_value(self, value):
        self.spin_box.setValue(max(self.from_, min(self.to, value)))
    
    def increase(self):
        if self.support_float:
            self.spin_box.setValue(self.spin_box.value() + 0.1)
        else:
            self.spin_box.setValue(self.spin_box.value() + 1)
        self.value_changed.emit(self.spin_box.value())
    
    def decrease(self):
        if self.support_float:
            self.spin_box.setValue(self.spin_box.value() - 0.1)
        else:
            self.spin_box.setValue(self.spin_box.value() - 1)
        self.value_changed.emit(self.spin_box.value())


class IntSpinBox(QWidget):
    value_changed = Signal(int)
    
    def __init__(self, parent=None, from_=1, to=100, initial=0, save_callback=None):
        super().__init__(parent)
        self.from_ = from_
        self.to = to
        self.save_callback = save_callback
        
        # Set size policies to prevent stretching
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # Remove spacing between elements
        
        # decrease_button
        self.decrease_button = AnimatedHoverButton("-", 5)
        self.decrease_button.setFixedSize(30, 20)
        self.decrease_button.clicked.connect(self.decrease)
        layout.addWidget(self.decrease_button)
        
        self.spin_box = QSpinBox()
        self.spin_box.setStyleSheet("""
            QSpinBox {
                background-color: rgba(128,128,128,.3);           /* dark background */
                border: 1px solid rgba(128,128,128,1);           /* subtle border */
                border-radius: 8px;                  /* rounded corners */
                selection-background-color: #555555; /* selection highlight */
            }
            QSpinBox::placeholder {
                color: #888888;                      /* muted placeholder */
            }
            QSpinBox:focus {
                border: 1px solid rgba(128,128,128,1);           /* focus accent */
                border-radius:8px;
                background-color:rgba(128,128,128,.2);
            }
            QSpinBox:hover {
                background-color: #323232;
                border-radius:8px;
                background-color:rgba(128,128,128,.2);          /* hover effect */
            }
        """)
        self.spin_box.setRange(from_, to)
        self.spin_box.setValue(initial)
        self.spin_box.setFixedSize(60, 20)  
        self.spin_box.setAlignment(Qt.AlignCenter)
        self.spin_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        layout.addWidget(self.spin_box)
        
        # increase button
        self.increase_button = AnimatedHoverButton("+", 5)
        self.increase_button.setFixedSize(30, 20)
        self.increase_button.clicked.connect(self.increase)
        layout.addWidget(self.increase_button)
        
        
        total_width = 40 + 60 + 40  
        self.setFixedSize(total_width, 20)
        
        if self.save_callback:
            self.spin_box.editingFinished.connect(self.save_callback)
            self.decrease_button.clicked.connect(self.save_callback)  
            self.increase_button.clicked.connect(self.save_callback)  
    
    def get_value(self):
        return self.spin_box.value()
    
    def set_value(self, value):
        self.spin_box.setValue(max(self.from_, min(self.to, value)))
    
    def increase(self):
        self.spin_box.setValue(self.spin_box.value() + 1)
        self.value_changed.emit(self.spin_box.value())
    
    def decrease(self):
        self.spin_box.setValue(self.spin_box.value() - 1)
        self.value_changed.emit(self.spin_box.value())


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

if __name__ =="__main__":
    
    app = QApplication()

    main_window = QMainWindow()
    id = make_id_active_frame(parent=main_window)
    id.create_frame(id_frame_idx=1,json_path=r"User_Data\Page_manager.json")
    main_window.setCentralWidget(id)
    main_window.show()
    app.exec()
