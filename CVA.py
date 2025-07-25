#!/usr/bin/env python3
import os
import sys

# Add source folder to import path
source_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source')
if source_path not in sys.path:
    sys.path.append(source_path)

# Import ColorVisionAid class directly from source package
from source import ColorVisionAid
from PyQt5.QtWidgets import QApplication

def main():
    """Main function to start the application"""
    app = QApplication(sys.argv)
    window = ColorVisionAid()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
