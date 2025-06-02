#!/usr/bin/env python3
# Ana AI Assistant - Full Screen Character Demo

import sys
import os
import time
from PyQt5.QtWidgets import QApplication

# Add the project to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ana.ui.full_screen_character import FullScreenCharacter, BackgroundType

def main():
    """Run a demo of the full screen character view"""
    app = QApplication(sys.argv)
    
    # Create and show full screen window
    window = FullScreenCharacter()
    window.show()
    
    # Set initial message
    window.set_message("Welcome to Ana in full screen mode. Press Escape to exit.")
    
    # Demo various background types
    # Start with default gradient
    
    # Wait 3 seconds then switch to cyberpunk city
    QApplication.processEvents()
    time.sleep(3)
    window.set_message("This is the cyberpunk city background.")
    window.set_background(BackgroundType.CYBERPUNK_CITY)
    
    # Wait 3 seconds then switch to matrix
    QApplication.processEvents()
    time.sleep(3)
    window.set_message("This is the matrix background.")
    window.set_background(BackgroundType.MATRIX)
    
    # Wait 3 seconds then switch to weather (rain)
    QApplication.processEvents()
    time.sleep(3)
    window.set_message("This is a rainy weather background.")
    window.set_background(BackgroundType.WEATHER, weather="rain", time_of_day="night")
    
    # Wait 3 seconds then switch to weather (snow)
    QApplication.processEvents()
    time.sleep(3)
    window.set_message("This is a snowy weather background.")
    window.set_background(BackgroundType.WEATHER, weather="snow", time_of_day="day")
    
    # Wait 3 seconds then demonstrate speaking animation
    QApplication.processEvents()
    time.sleep(3)
    window.set_message("Ana can animate speaking and listening in full screen mode too.")
    window.animate_speaking(3000)  # 3 second speaking animation
    
    # Wait 4 seconds (for speaking to complete) then show listening
    QApplication.processEvents()
    time.sleep(4)
    window.set_message("Ana is listening...")
    window.animate_listening(True)
    
    # Wait 3 seconds then stop listening
    QApplication.processEvents()
    time.sleep(3)
    window.animate_listening(False)
    
    # Final message
    window.set_message("Press Escape to exit or use the Close button at the bottom.")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main()) 