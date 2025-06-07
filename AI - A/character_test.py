#!/usr/bin/env python3
# Ana AI Assistant - Character Test Entry Point

import os
import sys
import signal
import logging
import argparse
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('character_test.log')
    ]
)
logger = logging.getLogger('CharacterTest')

def main():
    """Launch the character-only window for testing"""
    parser = argparse.ArgumentParser(description='Ana AI Character Test')
    parser.add_argument('--character-path', default='character_test',
                        help='Path to character assets (relative to ana/assets/)')
    args = parser.parse_args()
    
    try:
        # Import necessary modules
        logger.info("Loading modules...")
        from ana.ui.character_only_window import CharacterOnlyWindow
        from ana.config.settings import load_settings
        logger.info("Modules loaded successfully")
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("Ana AI Character Test")
        
        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        # Load settings
        logger.debug("Loading configuration...")
        settings = load_settings()
        
        # Override character assets path if specified
        if args.character_path:
            character_path = args.character_path
            logger.info(f"Using custom character path: {character_path}")
            
            # Check if the path exists
            full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                     'ana', 'assets', character_path)
            if not os.path.exists(full_path):
                logger.warning(f"Character path does not exist: {full_path}")
                logger.warning("Will use default character assets instead")
        
        # Create and show character window
        logger.debug("Creating character window...")
        window = CharacterOnlyWindow(settings=settings)
        window.show()
        
        logger.info("Character test window started successfully")
        
        # Run application event loop
        exit_code = app.exec_()
        
        # Clean up
        logger.info("Character test window closed")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 