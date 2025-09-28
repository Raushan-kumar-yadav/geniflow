import random
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import subprocess
from appium.webdriver.extensions.android.nativekey import AndroidKey
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
options = UiAutomator2Options()
options.platform_name = "Android"
options.device_name = "emulator-5556"
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

wait = WebDriverWait(driver, 30)
class Reels_upload():

    def __init__(self,id_name,Page_name_list):

        self.id_name = id_name
        self.page_name_lists = Page_name_list

    def check_selected(self):
       
        # Tap at x=100, y=100 using the mobile: clickGesture command
        driver.execute_script("mobile: clickGesture", {"x": 1032, "y": 273})
        time.sleep(random.uniform(1.0,2.0))

        driver.execute_script("mobile: clickGesture", {"x": 332, "y": 490})
        time.sleep(random.uniform(1.0,2.0))

        # Give the UI a moment to update.
        time.sleep(5)
        wait.until(EC.visibility_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Open profile switcher")')))
        # Use an explicit wait for the button with a content-desc attribute.
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().description("Open profile switcher")').click()
        
        wait.until(EC.visibility_of_element_located((AppiumBy.CLASS_NAME, 'androidx.recyclerview.widget.RecyclerView')))
        recycler_views = driver.find_elements(AppiumBy.CLASS_NAME, 'androidx.recyclerview.widget.RecyclerView')
        driver.implicitly_wait(100)
        # Iterate over each RecyclerView found
        for recycler in recycler_views:
            wait.until(EC.visibility_of_element_located((AppiumBy.XPATH, ".//*")))
            # Find all child elements (descendants) under the RecyclerView
            child_elements = recycler.find_elements(AppiumBy.XPATH, ".//*")

            # Print the text attribute of each child element
            filtered_lines = [child.text.strip() for child in child_elements if child.text.strip() and "null" not in child.text]
            if filtered_lines:
                current_profile = filtered_lines[0]
                print(current_profile)
                return current_profile
            else:
                print("No valid profile text found.")
                return None




    def switchPage(self,page_name):

        current_page = page_name
        try:
            if current_page == self.check_selected():
                window_size = driver.get_window_size()
                width = window_size['width']
                height = window_size['height']

                # Define the swipe bounding area (e.g., center of the screen)
                left = width * 0.1
                top = height * 0.1
                swipe_width = width * 0.8
                swipe_height = height * 0.8

                # Perform a swipe down gesture within the defined area
                driver.execute_script('mobile: swipeGesture', {
                    'left': left,
                    'top': top,
                    'width': swipe_width,
                    'height': swipe_height,
                    'direction': 'down',
                    'percent': 0.75  # Adjust the swipe length as needed
                })

                driver.implicitly_wait(10)

                try:
                    # Try to click the home tab using the first accessibility id
                    driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Home, tab 1 of 5').click()
                except Exception as e1:
                    print("Home tab '1 of 5' not found; trying 'Home, tab 1 of 6'")
                    try:
                        # Fallback: try the alternative accessibility id
                        driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Home, tab 1 of 6').click()
                    except Exception as e2:
                        print("Both accessibility id attempts failed; using mobile clickGesture fallback")
                        driver.execute_script("mobile: clickGesture", {"x": 63, "y": 150})
                finally:
                    print("run reels upload method")

                return True

            else:
                driver.implicitly_wait(100)


                page_name_xpath = f'//android.view.View[@text="{current_page}"]'
                driver.find_element(AppiumBy.XPATH,page_name_xpath).click()
                driver.implicitly_wait(100)
                print("run reels upload method")
                return True

        except:
            print("Error at page switching")
            return False 



    def find_with_scroll(self,Album_xpath,Max_scroll_Attempts = 10,scroll_duration = 500 ,Scroll_pause = 1):

        for attempt in range(Max_scroll_Attempts):
            try:
                #try to find and click on element
                driver.find_element(AppiumBy.XPATH,Album_xpath).click()
                print("Element found and click ")
                return True
            except NoSuchElementException:
                print("Element not found , Scrolling")

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

                
                try:
                
                
                    
                    driver.find_element(AppiumBy.XPATH,Album_xpath).click()




                except:
                    print("cant find element")

                return False


    def reelsUplode(self,Profile_Name,Title="Hi"):

        #This will click on 'Pluse button'
        Plus_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Create, Double tap to create a new post, story, or reel")
        Plus_button.click()
        driver.implicitly_wait(2)
        #This will click on Reel button
        try:
            driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().description("Reel")').click()
        except:
            print("reel button not working trying another path")
            driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,'new UiSelector().text("Reel")').click()
        


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

        """         # Check available contexts
        contexts = driver.contexts
        print("Available contexts:", contexts)
        # Make sure you're in the native context
        driver.switch_to.context("NATIVE_APP") """ 
        
        Album_xpath = f'//android.widget.Button[@content-desc="Select album, {Profile_Name}"]'

        try:
            folder_selector_button = self.find_with_scroll(Album_xpath=Album_xpath)

        except:
            print("No such element found even after scroll")

        driver.implicitly_wait(2)

        videos = driver.find_elements(AppiumBy.XPATH, '//*[@content-desc[contains(., "Video taken on")]]')
        video = videos[1]
        video.click()
        driver.implicitly_wait(2)

        next_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID,"Next")
        next_button.click()

        driver.implicitly_wait(2)

        text_box_button = driver.find_element(AppiumBy.CLASS_NAME,'android.widget.EditText')
        paste_text = text_box_button.send_keys(Title)

        driver.implicitly_wait(2)

        share_now_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID,'Share now').click()

        driver.implicitly_wait(5)
    def StartApp(self,app_package,app_activity):
        """
        Launch the specified Android application using its package and activity.

        Parameters:
            driver (WebDriver): The Appium driver instance.
            app_package (str): The package name of the app.
            app_activity (str): The activity to launch.
        """
        # start_activity is available in Appium 2 via the driver

        try:
            driver.start_activity(app_package, app_activity)
            print(f"Opened app: {app_package}/{app_activity}")
        except Exception as e:
            print(f"Error opening app: {app_package}/{app_activity}")
            print(e)

    def SwitchApp(self,app_package):
        """
        Switch to an already installed app by bringing it to the foreground.

        Parameters:
            driver (WebDriver): The Appium driver instance.
            app_package (str): The package name of the app to switch to.
        """
        # activate_app is available in Appium 2
        try:
            driver.activate_app(app_package)
            print(f"Switched to app: {app_package}")
        except Exception as e:
            print(f"Error switching to app: {app_package}")
            print(e)

        

        

    def StartReelsUploding(self,Video_Tile):
        Profile_lists = self.page_name_lists
        id_name = self.id_name

        while len(Profile_lists) > 0:

            current_profile = Profile_lists.pop()
            check_profile = self.switchPage(page_name=current_profile)
            if check_profile == True:
                Reel_upload = self.reelsUplode(Profile_Name=current_profile,Title=Video_Tile)

        driver.implicitly_wait(90)

        driver.press_keycode(AndroidKey.HOME)

        print(f"Uploding done on all page of {id_name}")
        print("Closing LDPlayer instance")
        time.sleep(10)

        ldconsole_path = r"E:\LDPlayer\LDPlayer9\ldconsole.exe"
        args = ["quit", "--name", "LDPlayer0"]
        try:
            # Run the command and wait for it to complete
            result = subprocess.run([ldconsole_path] + args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("Command output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("An error occurred:")
            print(e.stderr) 


if __name__ == "__main__":
    q = Reels_upload(id_name="Akshita Kumari",Page_name_list=["Letstrythisagain","Filipph4m"])


    q3 = q.StartReelsUploding(Video_Tile="How this maatchine work")


