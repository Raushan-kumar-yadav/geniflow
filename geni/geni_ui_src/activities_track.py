import os
import threading
import time
import orjson  



# we have to improve this funciton 








class DevicesJson:
    def __init__(self, filepath):
        self.filepath = self.makedir(os.path.join(filepath, "Devices_Setting.json"))
        self.debounce_delay = 1.0  # seconds; adjust as needed
        self._debounce_timer = None
        self.data = self.load_or_create_json()
    
    def makedir(self, file_path):
        norm_path = os.path.normpath(file_path)
        # Ensure the directory exists
        dir_path = os.path.dirname(norm_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return norm_path

    def Default_data(self):
        default_settings = {
            "Loctions": {
                "LD Location": "",
                "Geni Data": ""
            },
            "Times Setting": {
                "LD Opening Delay": 10,
                "Account Switching Delay": 10,
                "Reels Uploading Delay": 10,
                "Anythings Delay": 10
            },
            "Detalut Apps": [],
            "LDPlayer Settings": {
                "Ld Settings": {
                    "Resolution": 0,
                    "CPU": 0,
                    "RAM": 0,
                    "Display": 0,
                    "LD Per Row": 2,
                    "Run At Startup Time Delay (sec)": 10
                },
                "Settings Enable/Disable": {
                    "Check for internet at startup": True,
                    "Run at startup after time delay": True,
                    "Check and apply ld config": True,
                    "Auto arrange ld player": True,
                    "Auto shutdown after task cornpletion": False
                }
            },
            "LD Instance Settings": {
                "Number of instance at a time": 2,
                "Install defaut apps": True
            },
            "GPU settings": {
                "Hardware accelerated": True,
                "Enable Nvidia GPU": True
            },
            "Devices Into": []
        }
        return default_settings

    def load_or_create_json(self):
        # If file exists, try to load; otherwise, write default data.
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "rb") as file:
                    # Using orjson to deserialize
                    return orjson.loads(file.read())
            except Exception as e:
                print("Error loading JSON, using default data:", e)
        default_data = self.Default_data()
        self._write_file(default_data)
        return default_data

    def _write_file(self, data):
        # Write the JSON data to disk using orjson (which returns bytes)
        try:
            with open(self.filepath, 'wb') as file:
                file.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
            print("Data written to", self.filepath)
        except Exception as e:
            print("Error writing JSON:", e)

    def save_changes(self, new_data):
        """
        Schedule a file save operation using a debounce mechanism to avoid frequent disk writes.
        """
        self.data = new_data

        # Cancel any previously scheduled write
        if self._debounce_timer and self._debounce_timer.is_alive():
            self._debounce_timer.cancel()

        # Schedule a new write after the debounce delay
        self._debounce_timer = threading.Timer(self.debounce_delay, self._write_file, args=(self.data,))
        self._debounce_timer.start()

# Example usage:
if __name__ == "__main__":
    filepath = r"E:\facebook_tool\facebook_tools\User_Data"
    devices_json = DevicesJson(filepath)
    
    # Example change: update "LD Opening Delay"
    devices_json.data["Times Setting"]["LD Opening Delay"] = 15
    devices_json.save_changes(devices_json.data)
    
    # Simulate additional changes in a short time frame:
    for delay in range(16, 20):
        devices_json.data["Times Setting"]["LD Opening Delay"] = delay
        devices_json.save_changes(devices_json.data)
        time.sleep(0.3)  # simulate rapid changes
    
    # Wait enough time for the final save to complete.
    time.sleep(2)
