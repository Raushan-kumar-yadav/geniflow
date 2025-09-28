import json

class DeviceSettingsFlatten:
    def __init__(self, device_setting_json_path):
        self.device_setting_json_path = device_setting_json_path

    def flatten_json(self, data=None):
        """
        Recursively flatten nested dictionaries by merging their keys
        into the top level.
        """
        # If no data provided, load it from the JSON file.
        if data is None:
            with open(self.device_setting_json_path, mode="r", encoding="utf-8") as file:
                data = json.load(file)
                
        result = {}
        if isinstance(data, dict):
            for key, value in data.items():
                # Skip the "Devices Info" key entirely
                if key == "Devices Info":
                    continue
                if isinstance(value, dict):
                    # Recursively flatten nested dictionary and merge its keys
                    result.update(self.flatten_json(value))
                elif isinstance(value, list):
                    # If list elements are not dictionaries, keep them as is.
                    if all(not isinstance(item, dict) for item in value):
                        result[key] = value
                    else:
                        # For each dictionary in the list, merge its keys.
                        for item in value:
                            if isinstance(item, dict):
                                result.update(self.flatten_json(item))
                            else:
                                # Append non-dictionary items if needed.
                                result.setdefault(key, []).append(item)
                else:
                    result[key] = value
        return result


# Example usage:

if __name__ == "__main__":

    device_settings_flatten_obj = DeviceSettingsFlatten(r"User_Data\Devices_Setting.json")
    flatten_data = device_settings_flatten_obj.flatten_json()
    # Get delay (in days) and last update time from the flattened JSON
    insight_update_delay_day = flatten_data["Auto arrange ld player"]
    last_time_insight_updated = flatten_data["last_insights_updated"]
    print(insight_update_delay_day)
    print(last_time_insight_updated)