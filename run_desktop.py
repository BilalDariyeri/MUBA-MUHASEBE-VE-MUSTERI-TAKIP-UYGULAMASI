#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Desktop uygulamasını çalıştır
"""
import sys
import os

# Proje kök dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desktop_app import MainWindow
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

