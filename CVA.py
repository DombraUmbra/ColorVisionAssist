#!/usr/bin/env python3
import os
import sys

# Source klasörünü import path'ine ekle
source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source')
if source_path not in sys.path:
    sys.path.append(source_path)

# Direkt source paketinden ColorVisionAid sınıfını import et
from source import ColorVisionAid
from PyQt5.QtWidgets import QApplication

def main():
    """Ana uygulamayı başlatan fonksiyon"""
    app = QApplication(sys.argv)
    window = ColorVisionAid()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
