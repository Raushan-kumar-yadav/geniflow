import json
import os


class user_settings_json:
    def __init__(self):
        pass

    def makedir(self, dir_path=""):
        new_dir = os.path.normpath(dir_path)
        return new_dir

    def Default_user_settings(self):
        user_settings = {
            "user_name":"User Name",
            "saved_serial_number":"",
            "theme_mode":"dark",
            "theme_color":"dark-blue",
            "user_api":{}
            }
            
        return user_settings

    def load_or_create_json(self, filepath):

        Default_user_settings = self.Default_user_settings()
        path = self.makedir(os.path.join(filepath, "user_setting.json"))
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
            json.dump(Default_user_settings, file, indent=4)
        return Default_user_settings
    
    def deep_update(self, source, overrides):
        """
        Recursively update nested dictionaries in source with values from overrides.
        This preserves keys that are not being updated.
        """
        for key, value in overrides.items():
            if isinstance(value, dict) and key in source and isinstance(source[key], dict):
                self.deep_update(source[key], value)
            else:
                source[key] = value

    def save_changes(self, data):
        """
        Opens the JSON file at a constructed file path ("User_Data/Devices_Setting.json"),
        updates its keys with the new data (merging nested dictionaries), and saves the changes back.
        """
        # Build the full file path (this is included inside the method)
        filepath = os.path.join("User_Data", "user_setting.json")
        
        # If the file does not exist, create the directory and initialize the file with an empty dict.
        if not os.path.isfile(filepath):
            dir_path = os.path.dirname(filepath)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump({}, file)
        
        # Open the file in read mode and load its content.
        with open(filepath, "r", encoding="utf-8") as file:
            try:
                current_data = json.load(file)
            except json.JSONDecodeError:
                current_data = {}
        
        # Recursively update the current JSON data with new key-value pairs from 'data'
        self.deep_update(current_data, data)
        
        # Open the same file in write mode and save the updated JSON data.
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(current_data, file, indent=4)
        
        print("Changes saved successfully to", filepath)

