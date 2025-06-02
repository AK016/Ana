#!/usr/bin/env python3
# Ana AI Assistant - Main Entry Point

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Ana')

# Import core modules
from core.assistant import AnaAssistant
from ui.main_window import MainWindow
from config.settings import load_settings

def main():
    """Main entry point for Ana AI Assistant"""
    logger.info("Starting Ana AI Assistant...")
    
    # Load configuration
    settings = load_settings()
    
    # Initialize Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Ana AI")
    app.setQuitOnLastWindowClosed(False)  # Allow running in background
    
    # Initialize assistant core
    assistant = AnaAssistant(settings)
    
    # Initialize UI
    window = MainWindow(assistant, settings)
    window.show()
    
    # Start assistant services
    QTimer.singleShot(500, assistant.start_services)
    
    # Execute application
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 