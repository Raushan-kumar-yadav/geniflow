import json
import os


class DevicesJson:
    def __init__(self, base_path="User_Data"):
        self.base_path = base_path
        self.filename = "Devices_Setting.json"

    def makedir(self, dir_path=""):
        new_dir = os.path.normpath(dir_path)
        return new_dir

    def get_filepath(self, filepath=None):
        """Get the consistent filepath for the JSON file"""
        if filepath:
            return self.makedir(os.path.join(filepath, self.filename))
        return self.makedir(os.path.join(self.base_path, self.filename))

    def Default_data(self):
        Devices_settings = {
            "Locations": {  # Fixed typo from "Loctions"
                "LD Location": "",
                "Geni Data": ""
            },
            "Times Setting": {
                "LD Opening Delay": 20,
                "video_uploading_delay":50,
                "Account Switching Delay": 4,
                "Reels Uploading Delay": 10,
                "Anythings Delay": 1,
                "Update_insights_delay": 2,
                "last_insights_updated": 0,
                "before_any_task_delay":1
            },
            "Default Apps": [],
            "LDPlayer Settings": {
                "Ld Settings": {
                    "Resolution": "1080x1920",
                    "CPU": "2 Cores  (Recommended)",
                    "RAM": "1024MB  (Recommended)",
                    "Display": "Display1 [1920x1080]",
                    "LD Per Row": 2,
                    "Run At Startup Time Delay (sec)": 10
                },
                "Settings Enable/Disable": {
                    "Check for internet at startup": False,
                    "check_vpn_connnection": False,
                    "Check and apply ld config": False,
                    "Auto arrange ld player": False,
                    "Auto shutdown after task completion": False  # Fixed typo
                }
            },
            "LD Instance Settings": {
                "Number of instance at a time": 2,
                "Number of chrome instance at a time": 5,
                "Install default apps": False  # Fixed typo
            },
            "GPU settings": {
                "Hardware accelerated": False,
                "Enable Nvidia GPU": False
            },
            "global_settings": {
                "is_auto_upload_enabled": False,
                "is_id_active_enabled": False
            },
            "vpn":{"vpn_app_name":""},
            "Devices Info": []
        }
        return Devices_settings

    def load_or_create_json(self, filepath=None):
        """Load JSON file or create with default data if it doesn't exist"""
        path = self.get_filepath(filepath)
        
        # Try to load existing file
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    
                # Validate that loaded data has required structure
                if isinstance(data, dict) and data:
                    # Merge with default data to ensure all keys exist
                    default_data = self.Default_data()
                    self.deep_update(default_data, data)
                    
                    # Save the merged data back to ensure consistency
                    self._write_json_file(path, default_data)
                    return default_data
                else:
                    print(f"Warning: Invalid data structure in {path}, recreating with defaults")
                    
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"Error reading {path}: {e}. Creating new file with defaults.")
        
        # Create new file with default data
        default_data = self.Default_data()
        self._ensure_directory_exists(path)
        self._write_json_file(path, default_data)
        print(f"Created new settings file: {path}")
        return default_data

    def _ensure_directory_exists(self, filepath):
        """Ensure the directory for the file exists"""
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

    def _write_json_file(self, filepath, data):
        """Write JSON data to file with error handling"""
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
        except (IOError, OSError) as e:
            print(f"Error writing to {filepath}: {e}")
            raise

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

    def save_changes(self, data, filepath=None):
        """
        Load existing JSON, merge with new data, and save changes back.
        Now uses consistent filepath handling.
        """
        path = self.get_filepath(filepath)
        
        try:
            # Load current data
            current_data = {}
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        current_data = json.load(file)
                        if not isinstance(current_data, dict):
                            current_data = {}
                except (json.JSONDecodeError, IOError) as e:
                    print(f"Warning: Could not read existing file {path}: {e}")
                    current_data = {}
            
            # Ensure directory exists
            self._ensure_directory_exists(path)
            
            # Merge data
            self.deep_update(current_data, data)
            
            # Save updated data
            self._write_json_file(path, current_data)
            print(f"Changes saved successfully to {path}")
            
        except Exception as e:
            print(f"Error saving changes to {path}: {e}")
            raise

    def get_current_data(self, filepath=None):
        """Get current data from JSON file"""
        path = self.get_filepath(filepath)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading {path}: {e}")
                return self.Default_data()
        return self.Default_data()


# Example usage:
if __name__ == "__main__":
    # Initialize the class
    devices = DevicesJson()
    
    # Load or create the JSON file
    data = devices.load_or_create_json()
    print("Loaded data keys:", list(data.keys()))
    
    # Example of saving changes
    new_settings = {
        "Times Setting": {
            "LD Opening Delay": 25,
            "Account Switching Delay": 8
        },
        "global_settings": {
            "is_auto_upload_enabled": True
        }
    }
    
    devices.save_changes(new_settings)
    
    # Verify the changes
    updated_data = devices.get_current_data()
    print("LD Opening Delay:", updated_data["Times Setting"]["LD Opening Delay"])
    print("Auto upload enabled:", updated_data["global_settings"]["is_auto_upload_enabled"])