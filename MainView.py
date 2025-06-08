from PyQt5.QtWidgets import QApplication, QTabWidget, QMainWindow
from PyQt5.QtGui import QIcon
import sys
from TesterView import TesterView 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a tab widget
        self.tabs = QTabWidget()

        # Create instances of your views
        self.tester_view = TesterView()

        # Add the views to the tabs
        self.tabs.addTab(self.tester_view, "Test Runner")
        # self.tabs.addTab(self.generator_view, "Script Generator")

        # Set the tab widget as the central widget of the main window
        self.setCentralWidget(self.tabs)

        self.setWindowTitle("AutoMata Test App")    
        self.setWindowIcon(QIcon("logo.ico"))
        self.setGeometry(300, 300, 600, 400)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())