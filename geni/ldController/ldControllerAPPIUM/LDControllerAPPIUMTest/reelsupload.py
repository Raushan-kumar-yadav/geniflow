from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from click import option
from numpy import append
from appium.webdriver.extensions.android.nativekey import AndroidKey
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
options.app_package = "com.facebook.katana"
options.app_activity = "com.facebook.katana.LoginActivity"

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)





driver.implicitly_wait(5)
Plus_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Create, Double tap to create a new post, story, or reel")
Plus_button.click()
driver.implicitly_wait(2)

Reels_button = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().description("Reel")')
Reels_button.click()


driver.implicitly_wait(2)

#continue editing popup

try:
    driver.find_element(AppiumBy.ID,'android:id/button3').click()
except:
    print("No such popup")

driver.implicitly_wait(2)

galary_button = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().description("Gallery")')

galary_button.click()

driver.implicitly_wait(2)

# Check available contexts
contexts = driver.contexts
print("Available contexts:", contexts)
# Make sure you're in the native context
driver.switch_to.context("NATIVE_APP") 


try:
    folder_selector_button = driver.find_element(AppiumBy.XPATH,'//android.widget.Button[@content-desc="Select album, Steki"]').click()

except:
    print("cannot find element")

driver.implicitly_wait(2)

videos = driver.find_elements(AppiumBy.XPATH, '//*[@content-desc[contains(., "Video taken on")]]')
video = videos[1]
video.click()
driver.implicitly_wait(2)

next_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID,"Next")
next_button.click()

driver.implicitly_wait(2)

text_box_button = driver.find_element(AppiumBy.CLASS_NAME,'android.widget.EditText')
paste_text = text_box_button.send_keys("How Zoos Bathe Tigers! 🐅")

driver.implicitly_wait(2)

share_now_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID,'Share now').click()

driver.implicitly_wait(5)



driver.press_keycode(AndroidKey.HOME) 

driver.implicitly_wait(5)

driver.quit()