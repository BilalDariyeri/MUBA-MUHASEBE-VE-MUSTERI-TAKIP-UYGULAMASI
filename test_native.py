"""
Test script for native desktop app
"""
import sys
from desktop_app_native import MainWindow
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

