# AppiumHelper.py
import sys
import re
import json
import asyncio
import unittest
import threading
from PyQt5.QtCore import QThread, pyqtSignal
from TestRunner import AppTest  # Custom test class


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
        self.result = None

    def stop(self):
        self.appium_manager.stop_appium()

    def run_tests_with_timeout(self, suite, timeout=60):
        """
        Run test suite in a separate thread with timeout.
        """
        def run_tests():
            runner = unittest.TextTestRunner()
            self.result = runner.run(suite)

        test_thread = threading.Thread(target=run_tests)
        test_thread.start()
        test_thread.join(timeout)

        if test_thread.is_alive():
            self.output_signal.emit("⚠️ Test timed out. Stopping Appium...")
            self.appium_manager.stop_appium()
            raise TimeoutError("Test execution timed out.")

    def override_sys_argv(self):
        """
        Sets sys.argv for AppTest class (used inside unittest).
        """
        sys.argv = [
            "test",  # dummy script name
            self.selected_device,
            self.file_apk_name,
            self.android_version,
            str(self.hasApp),
            self.fileTest,
            self.reset_app
        ]

    def emit_failure_messages(self):
        """
        Emits cleaned up failure/error messages from the test result.
        """
        total_failures = len(self.result.failures)
        total_errors = len(self.result.errors)

        for test, err in self.result.failures + self.result.errors:
            response_match = re.search(r'"response":\s*"(.+?)"', err)
            if response_match:
                message = response_match.group(1)
            else:
                lines = err.strip().splitlines()
                message = lines[-1] if lines else "Unknown error"
            self.output_signal.emit(f"⚠️ {test.id()}: {message}")

        self.output_signal.emit(f"❌ Total Failures: {total_failures}, Errors: {total_errors}")
        self.output_signal.emit("⛔ Test failed.")

    def run(self):
        try:
            self.output_signal.emit("🚀 Starting Appium server...")
            appium_started = asyncio.run(self.appium_manager.start_appium())

            if not appium_started:
                self.output_signal.emit("❌ Failed to start Appium server.")
                return

            self.output_signal.emit("✅ Appium server started successfully.")
            self.output_signal.emit("🧪 Running test...")

            self.override_sys_argv()

            suite = unittest.TestSuite()
            suite.addTest(unittest.TestLoader().loadTestsFromTestCase(AppTest))

            self.run_tests_with_timeout(suite, timeout=60)

            if self.result.wasSuccessful():
                self.output_signal.emit("✅ Test completed successfully.")
            else:
                self.emit_failure_messages()

        except Exception as e:
            self.output_signal.emit(f"❌ Exception occurred: {e}")

        finally:
            self.output_signal.emit("🛑 Stopping Appium server...")
            self.appium_manager.stop_appium()
            self.output_signal.emit("✅ Appium server stopped.")
