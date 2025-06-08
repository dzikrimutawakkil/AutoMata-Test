from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QTextEdit

class FileHandler:
    def __init__(self):
        self.file_name = None

    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "Open Test File", "", "Test Sample File (*.txt)", options=options)
        return file_name
    
    def open_fileAPK_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(None, "Open App File", "", "Apk File (*.apk)", options=options)
        return file_name