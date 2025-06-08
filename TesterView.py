from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit, 
    QComboBox, QHBoxLayout, QRadioButton, QButtonGroup, QLineEdit, QLabel, QCheckBox
)
from PyQt5.QtCore import pyqtSignal, QThread, Qt
import subprocess
import sys
from AppiumManager import AppiumManager
from FileHandler import FileHandler
from AppiumHelper import AppiumHelper


class TestRunnerThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, py_file, appium_manager, device_name, app, android_version, has_app, reset_app):
        super().__init__()
        self.helper = AppiumHelper(py_file, appium_manager, device_name, app, android_version, has_app, reset_app)
        self.helper.output_signal.connect(self.output_signal)

    def run(self):
        self.helper.run()

    def stop(self):
        self.terminate()
        self.wait()


class TesterView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.appium_manager = AppiumManager()
        self.file_py_handler = FileHandler()
        self.file_apk_handler = FileHandler()
        self.test_runner_thread = None
        self.reset_app = True
        self.get_device_name()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.upload_button_py = QPushButton('Upload Test File', self)
        self.upload_button_py.clicked.connect(self.upload_py_file)
        self.layout.addWidget(self.upload_button_py)

        self.installation_status_layout = QHBoxLayout()
        self.radio_installed = QRadioButton("App already installed")
        self.radio_not_installed = QRadioButton("App not installed")
        self.radio_installed.setChecked(True)

        self.installation_status_group = QButtonGroup()
        self.installation_status_group.addButton(self.radio_installed)
        self.installation_status_group.addButton(self.radio_not_installed)

        self.installation_status_layout.addWidget(self.radio_installed)
        self.installation_status_layout.addWidget(self.radio_not_installed)
        self.layout.addLayout(self.installation_status_layout)

        self.radio_installed.toggled.connect(self.update_layout)
        self.dynamic_layout = QVBoxLayout()
        self.layout.addLayout(self.dynamic_layout)

        self.device_layout = QHBoxLayout()
        self.device_combo = QComboBox(self)
        self.device_layout.addWidget(self.device_combo)
        self.sync_button = QPushButton('Sync', self)
        self.sync_button.setFixedSize(50, 30)
        self.sync_button.clicked.connect(self.get_device_name)
        self.device_layout.addWidget(self.sync_button)
        self.layout.addLayout(self.device_layout)

        self.button_layout = QHBoxLayout()
        self.run_button = QPushButton('Run Appium Test', self)
        self.run_button.clicked.connect(self.run_test)
        self.button_layout.addWidget(self.run_button)
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_test)
        self.stop_button.setFixedSize(50, 30)
        self.button_layout.addWidget(self.stop_button)
        self.layout.addLayout(self.button_layout)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.layout.addWidget(self.output)

        self.setLayout(self.layout)
        self.setWindowTitle('Appium Tester')
        self.setGeometry(300, 300, 600, 400)
        self.update_layout()

    def handle_reset_checkbox(self, state):
        self.reset_app = state == Qt.Checked

    def update_layout(self):
        while self.dynamic_layout.count():
            item = self.dynamic_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()

        if self.radio_installed.isChecked():
            self.url_layout = QHBoxLayout()
            self.url_label = QLabel("Enter URL (com.appname):", self)
            self.url_layout.addWidget(self.url_label)
            self.url_input = QLineEdit(self)
            self.url_layout.addWidget(self.url_input)
            self.dynamic_layout.addLayout(self.url_layout)
            self.reset_checkbox = QCheckBox("Want to reset app?", self)
            self.reset_checkbox.setChecked(True)
            self.reset_checkbox.stateChanged.connect(self.handle_reset_checkbox)
            self.dynamic_layout.addWidget(self.reset_checkbox)

        elif self.radio_not_installed.isChecked():
            self.upload_button_apk = QPushButton('Upload .Apk File', self)
            self.upload_button_apk.clicked.connect(self.upload_apk_file)
            self.dynamic_layout.addWidget(self.upload_button_apk)

    def upload_py_file(self):
        file_name = self.file_py_handler.open_file_dialog()
        if file_name:
            self.file_py_handler.file_name = file_name
            self.output.append(f"Selected file: {self.file_py_handler.file_name}")

    def upload_apk_file(self):
        file_name = self.file_apk_handler.open_fileAPK_dialog()
        if file_name:
            self.file_apk_handler.file_name = file_name
            self.output.append(f"Selected file: {self.file_apk_handler.file_name}")

    def run_test(self):
        if self.file_py_handler.file_name:
            app = ""
            has_app = True
            if self.radio_installed.isChecked():
                app = self.url_input.text()
            else:
                app = self.file_apk_handler.file_name
                has_app = False

            selected_device = self.device_combo.currentText()
            if selected_device:
                self.output.clear()
                android_version = self.get_device_android_version(self.get_device_id(selected_device))
                self.output.append(f"Running test on device: {selected_device}")

                self.test_runner_thread = TestRunnerThread(
                    self.file_py_handler.file_name, self.appium_manager,
                    selected_device, app, android_version, has_app, self.reset_app
                )
                self.test_runner_thread.output_signal.connect(self.append_output)
                self.test_runner_thread.start()

                self.run_button.setEnabled(False)
                self.stop_button.setEnabled(True)
            else:
                self.output.append("Please select a device first.")
        else:
            self.output.append("Please upload a .py file first.")

    def stop_test(self):
        if self.test_runner_thread:
            self.output.append("Stopping the test...")
            self.appium_manager.stop_appium()
            self.test_runner_thread.stop()
            self.test_runner_thread = None

            self.run_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.output.append("Test stopped.")

    def get_device_name(self):
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            devices = result.stdout.splitlines()[1:]
            device_list = [line.split()[0] for line in devices if line and '\tdevice' in line]

            self.device_combo.clear()

            if device_list:
                for device in device_list:
                    device_name = self.get_device_full_name(device)
                    self.device_combo.addItem(device_name)
            else:
                self.output.append("No devices connected.")
        except Exception as e:
            self.output.append(f"Error getting devices: {str(e)}")

    def get_device_full_name(self, device_id):
        try:
            model_result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
                capture_output=True, text=True
            )
            return model_result.stdout.strip()
        except Exception as e:
            return f"Unknown device (Error: {str(e)})"

    def get_device_id(self, model_name):
        result = subprocess.run(['adb', 'devices', '-l'], stdout=subprocess.PIPE)
        devices_output = result.stdout.decode()
        for line in devices_output.splitlines():
            if model_name in line:
                return line.split()[0]

    def get_device_android_version(self, device_id):
        try:
            version_result = subprocess.run(
                ['adb', '-s', device_id, 'shell', 'getprop', 'ro.build.version.release'],
                capture_output=True, text=True
            )
            return version_result.stdout.strip()
        except Exception as e:
            return f"Unknown version (Error: {str(e)})"

    def append_output(self, text):
        self.output.append(text)

    def closeEvent(self, event):
        self.appium_manager.stop_appium()
        if self.test_runner_thread:
            self.test_runner_thread.stop()
        event.accept()
