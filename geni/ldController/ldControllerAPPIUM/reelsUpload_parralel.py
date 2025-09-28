from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.appium_service import AppiumService
import multiprocessing
import time

# Device configurations
DEVICES = [
    {
        "device_name": "Pixel 6",
        "udid": "emulator-5554",
        "platform_version": "13.0",
        "app": "/path/to/app.apk",
        "appium_port": 4723,
        "system_port": 8200,
        "driver_args": {
            "autoGrantPermissions": True,
            "enforceAppInstall": True
        }
    },
    {
        "device_name": "Galaxy S23",
        "udid": "emulator-5556",
        "platform_version": "13.0",
        "app": "/path/to/app.apk",
        "appium_port": 4724,
        "system_port": 8201,
        "driver_args": {
            "autoGrantPermissions": True,
            "enforceAppInstall": True
        }
    }
]

def start_appium_server(port):
    """Start Appium server with specified port"""
    appium_service = AppiumService()
    appium_service.start(
        args=[
            '--port', str(port),
            '--base-path', '/',
            '--relaxed-security',
            '--use-drivers', 'uiautomator2'
        ]
    )
    return appium_service

def run_test(device_config):
    """Execute test on a single device"""
    appium_service = None
    driver = None
    
    try:
        # Start Appium server
        appium_service = start_appium_server(device_config["appium_port"])
        time.sleep(5)  # Wait for server initialization

        # Configure capabilities for Appium 2
        options = UiAutomator2Options().load_capabilities({
            "platformName": "Android",
            "appium:automationName": "UiAutomator2",
            "appium:deviceName": device_config["device_name"],
            "appium:udid": device_config["udid"],
            "appium:platformVersion": device_config["platform_version"],
            "appium:app": device_config["app"],
            "appium:systemPort": device_config["system_port"],
            **device_config["driver_args"]
        })

        # Initialize driver
        driver = webdriver.Remote(
            command_executor=f'http://localhost:{device_config["appium_port"]}/',
            options=options
        )

        # Your test logic here
        print(f"Running test on {device_config['device_name']}")
        # Example interaction:
        driver.find_element("id", "com.example.button").click()
        time.sleep(2)

    except Exception as e:
        print(f"Error on {device_config['device_name']}: {str(e)}")
    finally:
        if driver:
            driver.quit()
        if appium_service and appium_service.is_running:
            appium_service.stop()
        print(f"Completed test on {device_config['device_name']}")

if __name__ == "__main__":
    # Create process pool
    with multiprocessing.Pool(processes=len(DEVICES)) as pool:
        pool.map(run_test, DEVICES)
    
    print("All parallel tests completed!")