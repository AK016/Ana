#!/usr/bin/env python3
# Ana AI Assistant - Startup Script

import os
import sys
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ana.log')
    ]
)

logger = logging.getLogger('Ana.Startup')

def main():
    """Main entry point for Ana AI Assistant"""
    parser = argparse.ArgumentParser(description='Ana AI Assistant')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-gui', action='store_true', help='Run without GUI (console mode)')
    args = parser.parse_args()
    
    # Set log level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Add the current directory to the path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Import Ana modules
    from main import main as run_ana
    
    # Start Ana
    logger.info("Starting Ana...")
    run_ana()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Ana stopped by user")
    except Exception as e:
        logger.exception(f"Error starting Ana: {str(e)}")
        sys.exit(1) 