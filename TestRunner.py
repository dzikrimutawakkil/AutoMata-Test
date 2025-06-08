from datetime import timedelta
import sys
import unittest
import time
from appium import webdriver
from appium.options.common import AppiumOptions
from appium_flutter_finder import FlutterFinder, FlutterElement
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.interaction import Interaction
from selenium.webdriver.common.actions.key_input import KeyInput



class AppTest(unittest.TestCase):
    def setUp(self):
        # Parse command-line arguments
        deviceName = sys.argv[1]
        app = sys.argv[2]
        platformV = sys.argv[3]
        hasApp = sys.argv[4]
        fileDir = sys.argv[5]
        resetApp = sys.argv[6]
        
        # Read test instructions
        with open(fileDir, 'r', encoding='utf-8') as file:
            self.lines = file.readlines()

        appResetSetting = 'true'
        appNoResetSetting = 'false'
        resetApp = True
        if (not resetApp) :
            appResetSetting = 'false'
            appNoResetSetting = 'true'

        if hasApp == 'True':
            cap = {
                'platformName': 'Android',
                'platformVersion': platformV,
                'deviceName': deviceName,
                'automationName': 'Flutter',
                'appPackage': app,
                'appActivity': app+'.MainActivity',
                'noReset' : appResetSetting,
                'fastReset' : appNoResetSetting
            }
        else:
            cap = {
                'platformName': 'Android',
                'platformVersion': platformV,
                'deviceName': deviceName,
                'automationName': 'Flutter',
                'appium:app': app
            }

        url = 'http://localhost:4723'
        self.driver = webdriver.Remote(url, options=AppiumOptions().load_capabilities(cap))
        self.finder = FlutterFinder()

        # Wait until Flutter app is ready
        self.driver.execute_script("flutter:waitForFirstFrame")

    def tearDown(self):
        self.driver.quit()

    def wait_for_element(self, key):
        try:
            self.driver.execute_script('flutter:waitFor', self.finder.by_value_key(key), 3000)
            return True
        except TimeoutException:
            return False

    def click_element(self, key):
        try:
            if self.wait_for_element(key):
                FlutterElement(self.driver, self.finder.by_value_key(key)).click()
            else:
                raise Exception(f'Element {key} not found')
        except Exception as e:
            self.fail(str(e))
    
    def input_text(self, key, text):
        try:
            if self.wait_for_element(key):
                FlutterElement(self.driver, self.finder.by_value_key(key)).send_keys(text)
            else:
                raise Exception(f'Text field {key} not found')
        except Exception as e:
            self.fail(str(e))

    def clear_text(self, key):
        try:
            if self.wait_for_element(key):
                FlutterElement(self.driver, self.finder.by_value_key(key)).clear()
            else:
                raise Exception(f'Text field {key} not found')
        except Exception as e:
            self.fail(str(e))

    def pop_back(self):
        try:
            self.driver.back()
        except Exception as e:
            self.fail(f'Failed to pop back: {str(e)}')
    
    def long_press_element(self, key, duration=1000):
        try:
            if self.wait_for_element(key):
                element = self.finder.by_value_key(key)
                self.driver.execute_script(
                    "flutter:longTap",
                    element,
                    {
                        "durationMilliseconds": duration,
                        "frequency": 60
                    }
                )
            else:
                raise Exception(f'Element {key} not found for long press')
        except Exception as e:
            self.fail(str(e))

    def input_quill_text(self, key, text):
        """ Inputs text into the Flutter Quill editor using flutter:enterText """
        try:
            if self.wait_for_element(key):
                element = FlutterElement(self.driver, self.finder.by_value_key(key))
                element.click()  # Tap to focus on Quill editor
                # time.sleep(1)  # Ensure editor is ready

                # Use flutter:enterText to input text
                self.driver.execute_script("flutter:enterText", text)

            else:
                raise Exception(f'Quill editor {key} not found')
        except Exception as e:
            self.fail(str(e))

    
    def format_quill_text(self, key):
        """ Clicks a toolbar button to format Quill editor text """
        try:
            self.click_element(key)
        except Exception as e:
            self.fail(str(e))

    def test_find_and_interact_elements(self):
        for i, line in enumerate(self.lines):
            try:
                line = line.strip()
                if 'Tap on screen' in line:
                    time.sleep(1)
                    self.driver.tap([(100, 100)])

                elif 'Text input:' in line:
                    parts = line.split(': ')
                    component_id = parts[1]
                    text = parts[2].strip()
                    try:
                        # element = self.find_element_with_retry(self.driver, self.finder, text, timeout=3)
                        nextLine = self.lines[i+1]
                        if 'Text input' in nextLine:
                            next_parts = nextLine.split(': ')
                            next_component_id = next_parts[1]
                            next_text = next_parts[2].strip()
                            if (next_text == text) and ((component_id not in next_component_id) and (next_component_id not in component_id)):
                                if component_id == "":
                                    self.clear_text(text)
                                else:
                                    self.input_text(text, component_id)
                            elif (next_text != text):
                                if component_id == "":
                                    self.clear_text(text)
                                else:
                                    self.input_text(text, component_id)
                            else:
                                continue
                        else:
                            if component_id == "":
                                self.clear_text(text)
                            else:
                                self.input_text(text, component_id)
                    except TimeoutException:
                        self.fail(f"Element with key '{text}' not found within the timeout.")                

                elif 'Button clicked:' in line:
                    component_id = line.split(': ')[1].strip()
                    self.click_element(component_id)

                elif 'Long press:' in line:
                    component_id = line.split(': ')[1].strip()
                    self.long_press_element(component_id)

                elif 'Quill input:' in line:
                    parts = line.split(': ')
                    component_id = parts[1]
                    text = parts[2].strip()
                    try:
                        # element = self.find_element_with_retry(self.driver, self.finder, text, timeout=3)
                        nextLine = self.lines[i+1]
                        if 'Quill input' in nextLine:
                            next_parts = nextLine.split(': ')
                            next_component_id = next_parts[1]
                            next_text = next_parts[2].strip()
                            if (next_text == text) and ((component_id not in next_component_id) and (next_component_id not in component_id)):
                                if component_id == "":
                                    self.clear_text(text)
                                else:
                                    self.input_quill_text(text, component_id)
                            elif (next_text != text):
                                if component_id == "":
                                    self.clear_text(text)
                                else:
                                    self.input_quill_text(text, component_id)
                            else:
                                continue
                        else:
                            if component_id == "":
                                self.clear_text(text)
                            else:
                                self.input_quill_text(text, component_id)
                    except TimeoutException:
                        self.fail(f"Element with key '{text}' not found within the timeout.")  

            except Exception as e:
                self.fail(f'Test failed with exception: {str(e)}')

if __name__ == '__main__':
    unittest_args = sys.argv[:1]
    unittest.main(argv=unittest_args)