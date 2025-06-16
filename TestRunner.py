from datetime import timedelta
import subprocess
import sys
import unittest
import time
from appium import webdriver
from appium.options.common import AppiumOptions
from appium_flutter_finder import FlutterFinder, FlutterElement
from selenium.common.exceptions import TimeoutException

class AppTest(unittest.TestCase):
    def setUp(self):
        # Get arguments
        deviceName = sys.argv[1]
        self.app_identifier = sys.argv[2]
        platformV = sys.argv[3]
        hasApp = sys.argv[4]
        fileDir = sys.argv[5]
        
        with open(fileDir, 'r', encoding='utf-8') as file:
            self.lines = file.readlines()

        # Define capabilities
        if hasApp == 'True':
            cap = {
                'platformName': 'Android',
                'platformVersion': platformV,
                'deviceName': deviceName,
                'automationName': 'Flutter',
                'appPackage': self.app_identifier,
                'appActivity': self.app_identifier + '.MainActivity',
                'noReset': True # Let AppiumHelper handle resets
            }
        else:
            cap = {
                'platformName': 'Android',
                'platformVersion': platformV,
                'deviceName': deviceName,
                'automationName': 'Flutter',
                'appium:app': self.app_identifier
            }

        url = 'http://localhost:4723'
        self.driver = webdriver.Remote(url, options=AppiumOptions().load_capabilities(cap))
        self.finder = FlutterFinder()
        self.driver.execute_script("flutter:waitForFirstFrame")

    def tearDown(self):
        print("--- Starting Teardown ---")
        
        # 1. Terminate the application on the device
        try:
            # We can only terminate if we have a package name, not a file path.
            # self.app_identifier will be the package name in both hasApp=true and hasApp=false modes now.
            if self.app_identifier and 'com.' in self.app_identifier:
                 print(f"Closing application with package name: {self.app_identifier}...")
                 self.driver.terminate_app(self.app_identifier)
                 print("Application closed.")
        except Exception as e:
            print(f"Note: Could not terminate the app. It may have already closed. Error: {e}")

        # 2. End the Appium session
        if self.driver:
            print("Quitting driver session...")
            self.driver.quit()
            
        print("--- Teardown Complete ---")
            
    def wait_for_element(self, key):
        try:
            self.driver.execute_script('flutter:waitFor', self.finder.by_value_key(key), 30000)
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
                    if len(parts) < 3:
                        continue  
                    component_id = parts[1]
                    text = parts[2].strip()

                    try:
                        if component_id == "":
                            self.clear_text(text)
                        else:
                            self.input_text(text, component_id)
                        # if i + 1 < len(self.lines):
                        #     nextLine = self.lines[i + 1].strip()

                        #     if 'Text input:' in nextLine:
                        #         next_parts = nextLine.split(': ')
                        #         if len(next_parts) >= 3:
                        #             next_component_id = next_parts[1]
                        #             next_text = next_parts[2].strip()

                        #             if (next_text == text) and ((component_id not in next_component_id) and (next_component_id not in component_id)):
                        #                 if component_id == "":
                        #                     self.clear_text(text)
                        #                 else:
                        #                     self.input_text(text, component_id)
                        #             elif (next_text != text):
                        #                 if component_id == "":
                        #                     self.clear_text(text)
                        #                 else:
                        #                     self.input_text(text, component_id)
                        #             else:
                        #                 pass  # bisa gunakan `continue` jika perlu
                        #         else:
                        #             # Format salah, tetap input baris saat ini
                        #             if component_id == "":
                        #                 self.clear_text(text)
                        #             else:
                        #                 self.input_text(text, component_id)
                        #     else:
                        #         # nextLine bukan input text, tetap proses baris saat ini
                        #         if component_id == "":
                        #             self.clear_text(text)
                        #         else:
                        #             self.input_text(text, component_id)
                        # else:
                        #     # Tidak ada nextLine, langsung proses baris saat ini
                        #     if component_id == "":
                        #         self.clear_text(text)
                        #     else:
                        #         self.input_text(text, component_id)

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