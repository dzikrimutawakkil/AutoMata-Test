# AppiumHelper.py
import sys
from PyQt5.QtCore import QThread, pyqtSignal
import asyncio
import unittest
import threading
from TestRunner import AppTest  # Import AppTest from TestRunner
import re
import json

class AppiumHelper(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, file_py_name, appium_manager, selected_device, file_apk_name, android_version, hasApp, reset_app):
        super().__init__()
        self.file_apk_name = file_apk_name
        self.appium_manager = appium_manager
        self.selected_device = selected_device
        self.android_version = android_version
        self.fileTest = file_py_name
        self.hasApp = hasApp
        self.reset_app = reset_app
        self.result = None  # Store test result

    def stop(self):
        self.appium_manager.stop_appium()

    def run_tests_with_timeout(self, suite, timeout=60):
        """
        Runs the test suite and stops execution if it hangs.
        """
        def run_tests():
            runner = unittest.TextTestRunner()
            self.result = runner.run(suite)

        test_thread = threading.Thread(target=run_tests)
        test_thread.start()
        test_thread.join(timeout)

        if test_thread.is_alive():
            self.output_signal.emit("⚠️ Test timed out! Stopping Appium...")
            self.appium_manager.stop_appium()
            raise Exception("Test execution timed out and was forcefully stopped.")

    def run(self):
        try:
            self.output_signal.emit("🚀 Starting Appium server...")

            # Start the Appium server
            appium_started = asyncio.run(self.appium_manager.start_appium())

            if not appium_started:
                self.output_signal.emit("❌ Failed to start Appium server.")
                return

            self.output_signal.emit("✅ Appium server started successfully.")
            self.output_signal.emit("🪄 Running test...")

            # Override sys.argv values to match expected inputs for AppTest
            sys.argv = ["test", self.selected_device, self.file_apk_name, self.android_version, str(self.hasApp), self.fileTest, self.reset_app]

            # Load and run AppTest directly
            suite = unittest.TestSuite()
            suite.addTest(unittest.TestLoader().loadTestsFromTestCase(AppTest))

            # Run the test suite with a timeout
            self.run_tests_with_timeout(suite, timeout=60)  

            # Handle test results
            if len(self.result.failures) == 0 or self.result.wasSuccessful():
                self.output_signal.emit("✅ Test finished successfully.")
            else:
                failures = len(self.result.failures)
                errors = len(self.result.errors)
                self.output_signal.emit(f"❌ Test encountered {failures + errors} failures/errors.")

                # Log specific failures with extracted "response" value
                for test, err in self.result.failures + self.result.errors:
                    response_match = re.search(r'"response":\s*"(.+?)"', err)  # Extract response field
                    error_message = response_match.group(1) if response_match else err.split("\n")[-2]
                    self.output_signal.emit(f"⚠️ {test}: {error_message}")

                # Stop Appium on failure
                self.output_signal.emit("⛔ Test failed!")
                self.appium_manager.stop_appium()

            # Stop the Appium server after test completion
            self.output_signal.emit("🛑 Stopping Appium server...")
            self.appium_manager.stop_appium()
            self.output_signal.emit("✅ Appium server stopped.")

        except Exception as e:
            self.output_signal.emit(f"❌ Test execution failed: {e}")
            self.appium_manager.stop_appium()
            self.output_signal.emit("⚠️ Appium server stopped due to an error.")
            raise  # Re-raise exception for proper error handling
