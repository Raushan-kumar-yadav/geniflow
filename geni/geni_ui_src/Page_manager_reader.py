import json
import os
import copy

class DevicesJson:
    def __init__(self):
        pass

    def makedir(self, dir_path=""):
      
        return os.path.normpath(dir_path)

    def Default_data(self,idx):
       
        str_idx = str(idx)
        data = {
            f"Id_information.{str_idx}": {
                "id_name": "",
                "package_name": "",
                "Ld_name": "",
                "Upload": False,
                "id_active_enable":False,
                "Main_folder_path": "",
                "chrome_instance_path":"",
                "upload_method":"Without Apps Switch",
                "id_active":{
                    "num_of_loop":1,
                    "loop_delay":60,
                    "shuffel":False,
                    "scroll_reels_and_vid":{
                        "scroll_reels_enable": False,
                        "scroll_vid_enable":False,
                        "scroll_reels_min_min":1,
                        "scroll_reels_min_max":2,
                        "scroll_vid_min_min":1,
                        "scroll_vid_min_max":2,
                        "activity":{
                            "like_post":{
                                "like_post_enable":False,
                                "like_post_prob":0
                            },
                            "react_post":{
                                "react_post_enable":False,
                                "react_post_prob":0
                            },
                            "comment_post":{
                                "comment_post_enable":False,
                                "comment_post_prob":0,
                                "comment_config":{
                                    "comment_from":"From Text Box", 
                                    "comment_text_box":"",
                                    "comment_txt_path":"",
                                    "comment_random":False
                                }
                            },
                            "share_post_to_group":{
                                "share_post_to_group_enable":False,
                                "share_post_to_group_prob":0,
                                "share_post_to_group_config":{
                                    "share_post_to_group_from":"From Text Box",
                                    "share_post_to_group_text_box":"",
                                    "share_post_to_group_txt_path":"",
                                    "share_post_to_group_random":False
                                }
                            },
                            "share_post_to_story":{
                                "share_post_to_stroy_enable":False,
                                "share_post_to_story_prob":0
                            }
                        }
                    },
                    "scroll_feed":{
                        "scroll_feed_enable": False,
                        "scroll_feed_min_min":1,
                        "scroll_feed_max_min":2,
                        "activity":{
                            "like_post":{
                                "like_post_enable":False,
                                "like_post_prob":0,
                            },
                            "react_post":{
                                "react_post_enable":False,
                                "react_post_prob":0
                            },
                            "comment_post":{
                                "comment_post_enable":False,
                                "comment_post_prob":0,
                                "comment_config":{
                                    "comment_from":"From Text Box",
                                    "comment_text_box":"",
                                    "comment_txt_path":"",
                                    "comment_random":False
                                }
                            },
                            "share_post_to_group":{
                                "share_post_to_group_enable":False,
                                "share_post_to_group_prob":0,
                                "share_post_to_group_config":{
                                    "share_post_to_group_from":"From Text Box",
                                    "share_post_to_group_text_box":"group name1,group name2,......",
                                    "share_post_to_group_txt_path":"",
                                    "share_post_to_group_random":False
                                }
                            },
                            "share_post_to_story":{
                                "share_post_to_stroy_enable":False,
                                "share_post_to_story_prob":0
                            }
                        }
                    },
                    "check_msg":{
                        "check_msg_enable":False,
                        "check_msg_min_min":0,
                        "check_msg_max_min":1,
                        "reply_msg_enable":False,
                        "reply_msg_min_chat":0,
                        "reply_msg_max_chat":1
                    },
                    "add_and_confirm_friends":{

                        "add_friend_enable":False,
                        "add_friend_min_frid":0,
                        "add_friend_max_frid":1,
                        "confirm_friend_enable":False,
                        "confirm_friend_min_frid":0,
                        "confirm_friend_max_frid":1
                    },
                    "post_photo":{
                        "post_photo_enable":False,
                        "post_photo_num":1,
                        "post_photo_config":{
                            "post_photo_download_folder":"",
                            "post_photo_folder":"",
                            "post_photo_caption_from":"From Original Photo",
                            "post_photo_caption_text_box":"hello",
                            "post_photo_caption_txt_path":"",
                            "post_photo_caption_txt_random":False
                        }
                    },
                    "post_checkin":{

                        "post_checkin_enable":False,
                        "post_checkin_num":1,
                        "post_checkin_location":"",
                        "post_checkin_config":{
                            "post_checkin_photo_download_folder":"",
                            "post_checkin_photo_folder":"",
                            "post_checkin_caption_from":"From Original Photo",
                            "post_checkin_caption_text_box":"hello",
                            "post_checkin_caption_txt_path":"",
                            "post_checkin_caption_txt_random":False,
                            "add_photo_to_checkin_post":False
                        }
                    },
                    "create_story":{
                        "create_story_enable":False,
                        "create_story_num":1,
                        "create_story_config":{
                            "create_story_video_download_folder":"",
                            "create_story_video_folder":"",
                            "create_story_caption_from":"From Original Photo",
                            "create_story_caption_text_box":"hello",
                            "create_story_caption_txt_path":"",
                            "create_story_caption_txt_random":False
                        }
                    },
                    "check_notification":{
                        "check_notification_enable":False,
                        "check_notification_min_min":0,
                        "check_notification_max_min":1,
                    }
                },
                "ID_info": {
                    "download_folder_config": {
                        "download_video_folder": "",
                        "download_Image_folder": ""
                    },
                    "reels_config":{
                        "download_folder":"",
                        "ld_folder":"",
                        "num":1,
                        "download_configuration":{
                            "auto_download": True,
                            "download_from":"YouTube",
                            "channel_link":"",
                            "download_qulity":"best",
                            "num_of_content_download":1,
                            "save_download_history":""
                        },
                        "captions":{
                            "caption_from":"From Original Video",
                            "caption_text_box":"",
                            "txt_file_path":"",
                            "txt_random":False
                        },
                        "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},
                        "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },
                        "auto_edit_preset":{},
                    },
                    "videos_config":{
                        "download_folder":"",
                        "ld_folder":"",
                        "num":1,
                        "download_configuration":{
                            "auto_download": True,
                            "download_from":"YouTube",
                            "channel_link":"",
                            "download_qulity":"best",
                            "num_of_content_download":1,
                            "save_download_history":""
                        },
                        "captions":{
                            "caption_from":"From Original Video",
                            "caption_text_box":"",
                            "txt_file_path":"",
                            "txt_random":False
                        },
                        "schedule_enable":False,
                        "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},
                        "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },
                        "auto_edit_preset":{}
                        },

                    "image_config":{
                        "download_folder":"",
                        "ld_folder":"",
                        "num":1,
                        "download_configuration":{
                            "auto_download": True,
                            "download_from":"YouTube",
                            "channel_link":"",
                            "download_qulity":"best",
                            "num_of_content_download":1,
                            "save_download_history":""
                        },
                        "captions":{
                            "caption_from":"From Original Video",
                            "caption_text_box":"",
                            "txt_file_path":"",
                            "txt_random":False
                        },
                        "schedule_enable":False,
                        "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},

                        "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },

                        "auto_edit_preset":{}
                        },

                    "story_config":{
                        "download_folder":"",
                        "ld_folder":"",
                        "num":1,
                        "story_type":"video",
                        "download_configuration":{
                            "auto_download": True,
                            "download_from":"YouTube",
                            "channel_link":"",
                            "download_qulity":"best",
                            "num_of_content_download":1,
                            "save_download_history":""
                        },
                        "captions":{
                            "caption_from":"From Original Video",
                            "caption_text_box":"",
                            "txt_file_path":"",
                            "txt_random":False
                        },
                        "auto_edit_preset":{}
                        },

                    "Folder config": {
                        "Video Folder": "",
                        "Image Folder": ""
                    },
                    "configure_download_bonus_edits_video_edits": {
                        "auto_download": False,
                        "auto_video_edits": False,
                        "auto_reels_edits": False,
                        "auto_image_edits": False,
                        "auto_story_video_edits":False,
                        "Download Configurations": {
                            "Download From": "YouTube",
                            "Channel link": "",
                            "Download Quality": "720p",
                            "No of video to Download": 1,
                            "Save downloaded video history": ""
                        },
                    },
                    "Auto Video Edits": {
                        "Title": {
                            "Title From": "From Original Video",
                            "Title Text Box ": "",
                            "Text File Path": "",
                            "txt_random":False
                        },
                    },
                    "set_upload_types": {
                        "reels_upload": False,
                        "image_upload": False,
                        "video_upload": False,
                        "story_upload": False,
                    },
                    "Insights": {
                        "Followers": 0,
                        "Views": 0,
                        "Engagement": 0,
                        "is_setup_available":False,
                        "Screenshot Images": []
                    }
                },
                "page_information": {
                    
                }
            },
        }
        return data
    
    def create_id_frame(self,idx,id_name,Package_name,ld_name,upload = False):
        # Your given default dictionary.
        data = {
            f"Id_information.{str(idx)}": {
                "id_name": "",
                "package_name": "",
                "Ld_name": "",
                "Upload": False,
                "id_active_enable":False,
                "Main_folder_path": "",
                "chrome_instance_path":"",
                "upload_method":"Without Apps Switch",
                "id_active":{
                    "num_of_loop":1,
                    "loop_delay":60,
                    "shuffel":False,
                    "scroll_reels_and_vid":{
                        "scroll_reels_enable": False,
                        "scroll_vid_enable":False,
                        "scroll_reels_min_min":1,
                        "scroll_reels_min_max":2,
                        "scroll_vid_min_min":1,
                        "scroll_vid_min_max":2,
                        "activity":{
                            "like_post":{
                                "like_post_enable":False,
                                "like_post_prob":0,
                            },
                            "react_post":{
                                "react_post_enable":False,
                                "react_post_prob":0
                            },
                            "comment_post":{
                                "comment_post_enable":False,
                                "comment_post_prob":0,
                                "comment_config":{
                                    "comment_from":"From Text Box",
                                    "comment_text_box":"",
                                    "comment_txt_path":"",
                                    "comment_random":False
                                }
                            },
                            "share_post_to_group":{
                                "share_post_to_group_enable":False,
                                "share_post_to_group_prob":0,
                                "share_post_to_group_config":{
                                    "share_post_to_group_from":"From Text Box",
                                    "share_post_to_group_text_box":"",
                                    "share_post_to_group_txt_path":"",
                                    "share_post_to_group_random":False
                                }
                            },
                            "share_post_to_story":{
                                "share_post_to_stroy_enable":False,
                                "share_post_to_story_prob":0,
                            }
                        }
                    },
                    "scroll_feed":{
                        "scroll_feed_enable": False,
                        "activity":{
                            "like_post":{
                                "like_post_enable":False,
                                "like_post_prob":0,
                            },
                            "react_post":{
                                "react_post_enable":False,
                                "react_post_prob":0
                            },
                            "comment_post":{
                                "comment_post_enable":False,
                                "comment_post_prob":0,
                                "comment_config":{
                                    "comment_from":"From Text Box",
                                    "comment_text_box":"",
                                    "comment_txt_path":"",
                                    "comment_random":False
                                }
                            },
                            "share_post_to_group":{
                                "share_post_to_group_enable":False,
                                "share_post_to_group_prob":0,
                                "share_post_to_group_config":{
                                    "share_post_to_group_from":"From Text Box",
                                    "share_post_to_group_text_box":"group name1,group name2,......",
                                    "share_post_to_group_txt_path":"",
                                    "share_post_to_group_random":False
                                }
                            },
                            "share_post_to_story":{
                                "share_post_to_stroy_enable":False,
                                "share_post_to_story_prob":0,
                            }
                        }
                    },
                    "check_msg":{
                        "check_msg_enable":False,
                        "check_msg_min_min":0,
                        "check_msg_max_min":1,
                        "reply_msg_enable":False,
                        "reply_msg_min_chat":0,
                        "reply_msg_max_chat":1
                    },
                    "add_and_confirm_friends":{

                        "add_friend_enable":False,
                        "add_friend_min_frid":0,
                        "add_friend_max_frid":1,
                        "confirm_friend_enable":False,
                        "confirm_friend_min_frid":0,
                        "confirm_friend_max_frid":1
                    },
                    "post_photo":{
                        "post_photo_enable":False,
                        "post_photo_num":1,
                        "post_photo_config":{
                            "post_photo_download_folder":"",
                            "post_photo_folder":"",
                            "post_photo_caption_from":"From Original Photo",
                            "post_photo_caption_text_box":"hello",
                            "post_photo_caption_txt_path":"",
                            "post_photo_caption_txt_random":False
                        }
                    },
                    "post_checkin":{

                        "post_checkin_enable":False,
                        "post_checkin_num":1,
                        "post_checkin_location":"",
                        "post_checkin_config":{
                            "post_checkin_photo_download_folder":"",
                            "post_checkin_photo_folder":"",
                            "post_checkin_caption_from":"From Original Photo",
                            "post_checkin_caption_text_box":"hello",
                            "post_checkin_caption_txt_path":"",
                            "post_checkin_caption_txt_random":False,
                            "add_photo_to_checkin_post":False
                        }
                    },
                    "create_story":{
                        "create_story_enable":False,
                        "create_story_num":1,
                        "create_story_config":{
                            "create_story_video_download_folder":"",
                            "create_story_video_folder":"",
                            "create_story_caption_from":"From Original Photo",
                            "create_story_caption_text_box":"hello",
                            "create_story_caption_txt_path":"",
                            "create_story_caption_txt_random":False
                        }
                    },
                    "check_notification":{
                        "check_notification_enable":False,
                        "check_notification_min_min":0,
                        "check_notification_max_min":1,
                    }
                },
                "ID_info": {
                    
                    "reels_config":{
                        "download_folder":"",
                        "ld_folder":"",
                        "num":1,
                        "download_configuration":{
                            "auto_download":True,
                            "download_from":"YouTube",
                            "channel_link":"",
                            "download_qulity":"best",
                            "num_of_content_download":1,
                            "save_download_history":""
                        },
                        "captions":{
                            "caption_from":"From Original Video",
                            "caption_text_box":"",
                            "txt_file_path":"",
                            "txt_random":False
                        },
                        "schedule_enable":False,
                        "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},
                        
                        "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },

                        "auto_edit_preset":{},
                    },
                    "videos_config":{
                        "download_folder":"",
                        "ld_folder":"",
                        "num":1,
                        "download_configuration":{
                            "auto_download":True,
                            "download_from":"YouTube",
                            "channel_link":"",
                            "download_qulity":"best",
                            "num_of_content_download":1,
                            "save_download_history":""
                        },
                        "captions":{
                            "caption_from":"From Original Video",
                            "caption_text_box":"",
                            "txt_file_path":"",
                            "txt_random":False
                        },
                        "schedule_enable":False,
                        "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},

                        "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },

                        "auto_edit_preset":{}
                        },

                    "image_config":{
                        "download_folder":"",
                        "ld_folder":"",
                        "num":1,
                        "download_configuration":{
                            "auto_download":True,
                            "download_from":"YouTube",
                            "channel_link":"",
                            "download_qulity":"best",
                            "num_of_content_download":1,
                            "save_download_history":""
                        },
                        "captions":{
                            "caption_from":"From Original Video",
                            "caption_text_box":"",
                            "txt_file_path":"",
                            "txt_random":False
                        },
                        "schedule_enable":False,
                        "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},
                                            
                        "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },

                        "auto_edit_preset":{}
                        },

                    "story_config":{
                        "download_folder":"",
                        "ld_folder":"",
                        "num":1,
                        "story_type":"video",
                        "download_configuration":{
                            "auto_download":True,
                            "download_from":"YouTube",
                            "channel_link":"",
                            "download_qulity":"best",
                            "num_of_content_download":1,
                            "save_download_history":""
                        },
                        "captions":{
                            "caption_from":"From Original Video",
                            "caption_text_box":"",
                            "txt_file_path":"",
                            "txt_random":False
                        },
                        "auto_edit_preset":{}
                        },


                    "download_folder_config": {
                        "download_video_folder": "",
                        "download_image_folder": ""
                    },
                    "Folder config": {
                        "Video Folder": "",
                        "Image Folder": ""
                    },
                    "configure_download_bonus_edits_video_edits": {
                        "auto_download": False,
                        "auto_video_edits": False,
                        "auto_reels_edits": False,
                        "auto_image_edits": False,
                        "auto_story_video_edits":False,
                        "Download Configurations": {
                            "Download From": "YouTube",
                            "Channel link": "",
                            "Download Quality": "720p",
                            "No of video to Download": 1,
                            "Save downloaded video history": ""
                        },
                    },
                    "Auto Video Edits": {
                        "Title": {
                            "Title From": "From Original Video",
                            "Title Text Box ": "",
                            "Text File Path": "",
                        },
                    },
                    "set_upload_types": {
                        "reels_upload": False,
                        "image_upload": False,
                        "video_upload": False,
                        "story_upload": False,
                    },
                    "Insights": {
                        "Followers": 0,
                        "Views": 0,
                        "Engagement": 0,
                        "is_setup_available":False,
                        "Screenshot Images": []
                    }
                },
                "pages_information": {
                    
                }
            },
        }
        return data

    def add_page_data(self, idx, page_name):
        # Builds the default structure for a page and sets its name.
        str_idx = str(idx)
        page_name_srt = str(page_name)
        data = {f"Page.{str_idx}": {
            "Page_Name": page_name_srt,

            "reels_config":{
                "download_folder":"",
                "ld_folder":"",
                "num":1,
                "download_configuration":{
                    "auto_download":True,
                    "download_from":"YouTube",
                    "channel_link":"",
                    "download_qulity":"best",
                    "num_of_content_download":1,
                    "save_download_history":""
                    },
                "captions":{
                    "caption_from":"From Original Video",
                    "caption_text_box":"",
                    "txt_file_path":""
                    },
                "schedule_enable":False,
                "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},

                "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },


                "auto_edit_preset":{},
            },

            "videos_config":{
                "download_folder":"",
                "ld_folder":"",
                "num":1,
                "download_configuration":{
                    "auto_download":True,
                    "download_from":"YouTube",
                    "channel_link":"",
                    "download_qulity":"best",
                    "num_of_content_download":1,
                    "save_download_history":""
                },
                "captions":{
                    "caption_from":"From Original Video",
                    "caption_text_box":"",
                    "txt_file_path":"",
                    "txt_random":False
                },
                "schedule_enable":False,
                "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},

                "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },

                "auto_edit_preset":{}
            },

            "image_config":{
                "download_folder":"",
                "ld_folder":"",
                "num":1,
                "download_configuration":{
                    "auto_download":True,
                    "download_from":"YouTube",
                    "channel_link":"",
                    "download_qulity":"best",
                    "num_of_content_download":1,
                    "save_download_history":""
                },
                "captions":{
                    "caption_from":"From Original Video",
                    "caption_text_box":"",
                    "txt_file_path":"",
                    "txt_random":False
                },
                
                "schedule_config":{"schedule_enable":False,
                                            "schedule_time":{}},

                "group_sharing_config":{
                            "enable_sharing":False,
                            "ignore_name":False,
                            "num_of_share":1,
                            "groups_name":""
                        },


                "auto_edit_preset":{}
            },

            "story_config":{
                "download_folder":"",
                "ld_folder":"",
                "num":1,
                "story_type":"video",
                "download_configuration":{
                    "auto_download":True,
                    "download_from":"YouTube",
                    "channel_link":"",
                    "download_qulity":"best",
                    "num_of_content_download":1,
                    "save_download_history":""
                },
                "captions":{
                    "caption_from":"From Original Video",
                    "caption_text_box":"",
                    "txt_file_path":"",
                    "txt_random":False
                },
            "auto_edit_preset":{}
            },


            "download_folder_config": {
                "download_video_folder": "",
                "download_image_folder": ""
            },
            "Folder config": {
                "Video Folder": "",
                "Image Folder": ""
            },
            "configure_download_bonus_edits_video_edits": {
                "auto_download": False,
                "auto_video_edits": False,
                "auto_reels_edits": False,
                "auto_image_edits": False,
                "auto_story_video_edits":False,
                "Download Configurations": {
                    "Download From": "YouTube",
                    "Channel link": "",
                    "Download Quality": "720p",
                    "No of video to Download": 1,
                    "Save downloaded video history": ""
                },
            },
            "Auto Video Edits": {
                "Title": {
                    "Title From": "From Original Video",
                    "Title Text Box ": "",
                    "Text File Path": "",
                },
            },
            "set_upload_types": {
                "reels_upload": False,
                "image_upload": False,
                "video_upload": False,
                "story_upload": False,
            },
            "Insights": {
                "Followers": 0,
                "Views": 0,
                "Engagement": 0,
                "is_setup_available":False,
                "Screenshot Images": []
            }
        }}
        return data

    def load_or_create_json(self, filepath):
        default_data = self.Default_data(idx=1)
        path = self.makedir(os.path.join(filepath, "Page_manager.json"))
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    return data
            except json.JSONDecodeError:
                # Fall back to default data if JSON is invalid.
                pass
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=4)
        return default_data
    
    def recalc_id_information_idx(self,data):
        """
        Recalculate the idx part of keys that start with 'Id_information_'.
        All other keys are left unchanged.
        """
        new_data = {}
        new_idx = 1
        for key, value in data.items():
            if key.startswith("Id_information_"):
                # Create a new key with the recalculated index.
                new_key = f"Id_information_{new_idx}"
                new_idx += 1
            else:
                new_key = key
            new_data[new_key] = value
        return new_data
    
    def recalc_pages_idx(self,pages_dict):
        """
        Recalculate the keys for a dictionary with keys formatted as 'number.Page'.
        Returns a new dictionary with sequential keys.
        """
        # Sort the keys by their numeric prefix.
        sorted_keys = sorted(pages_dict.keys(), key=lambda k: int(k.split('.')[0]))

        new_pages = {}
        for i, old_key in enumerate(sorted_keys):
            new_key = f"{i+1}.Page"  # New sequential key.
            new_pages[new_key] = pages_dict[old_key]
        return new_pages

    def save_changes(self, data, filepath):
        path = self.makedir(os.path.join(filepath, "Page_manager.json"))
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print("Changes saved successfully to", path)


