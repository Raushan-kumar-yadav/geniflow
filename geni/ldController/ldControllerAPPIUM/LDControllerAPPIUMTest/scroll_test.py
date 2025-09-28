from calendar import prmonth
from locale import currency
import profile
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from click import option
from requests_toolbelt import ImproperBodyPartContentException
import subprocess
from numpy import append
from appium.webdriver.extensions.android.nativekey import AndroidKey
import xml.etree.ElementTree as ET
import time
from selenium.common.exceptions import NoSuchElementException
from regex import F
from selenium.webdriver.support.ui import WebDriverWait
from sympy import false, root
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5554"
#options.app_package = "com.facebook.katana"
#options.app_activity = "*"  # Key change!
options.automation_name = "UiAutomator2"
options.no_reset = True  # Critical for retaining sessions
options.set_capability("appium:enableMultiWindows", True)
options.set_capability("appium:forceAppLaunch", True)
options.set_capability("App","com.facebook.katana")

options.auto_grant_permissions = True  # Auto-accept permissions
# First App (Facebook)
#options.app_package = "com.facebook.katana"
#options.app_activity = "com.facebook.katana.LoginActivity"

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
# Set up Appium options
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5554"
options.automation_name = "UiAutomator2"
options.no_reset = True
options.set_capability("appium:enableMultiWindows", True)
options.auto_grant_permissions = True
options.app_package = "com.facebook.katana"
options.app_activity = "com.facebook.katana.LoginActivity"

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
driver.update_settings({"enableMultiWindows": True})
# Get current screen dimensions
window_size = driver.get_window_size()
start_x = window_size['width'] // 3
start_y = int(window_size['height'] * 0.7)
end_y = int(window_size['height'] * 0.3)

# Create an ActionChains object and use its w3c_actions for pointer actions
actions = ActionChains(driver)
pointer = actions.w3c_actions.pointer_action

# Build the swipe gesture:
# 1. Move to the start location
pointer.move_to_location(start_x, start_y)
# 2. Press down (simulate touch)
pointer.pointer_down()
# 3. Pause for 1 second (adjust as needed)
pointer.pause(1)
# 4. Move to the end location over 1 second (this duration is implicit in the pause/move)
pointer.move_to_location(start_x, end_y)
# 5. Release (simulate lift finger)
pointer.pointer_up()

# Perform the action
actions.perform()

driver.implicitly_wait(10)

Profile_Name = "Vibes videos"
try:


    Album_xpath = f'//android.widget.Button[@content-desc="Select album, {Profile_Name}"]'
    driver.find_element(AppiumBy.XPATH,Album_xpath).click()


    

except:
    print("cant find element")