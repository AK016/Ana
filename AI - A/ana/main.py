#!/usr/bin/env python3
# Ana AI Assistant - Main Entry Point

import os
import sys
import signal
import logging
import traceback
import json
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ana_debug.log')
    ]
)
logger = logging.getLogger('Ana')

# Import modules
try:
    logger.info("Loading modules...")
    from ana.ui.main_window import MainWindow
    from ana.ui.google_login import GoogleLoginDialog, GOOGLE_AVAILABLE
    from ana.core.assistant import AnaAssistant
    from ana.config.settings import load_settings
    logger.info("Modules loaded successfully")
except ImportError as e:
    logger.error(f"Error importing modules: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

def main():
    """Main entry point for Ana AI Assistant"""
    logger.info("Starting Ana AI Assistant...")
    
    try:
        # Load settings
        logger.debug("Loading configuration...")
        settings = load_settings()
        
        # Check for test mode (for development)
        test_mode_enabled = False
        test_user = None
        test_mode_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config", "test_mode.json")
        if os.path.exists(test_mode_path):
            try:
                with open(test_mode_path, 'r') as f:
                    test_mode_config = json.load(f)
                    test_mode_enabled = test_mode_config.get('enabled', False)
                    if test_mode_enabled:
                        test_user = test_mode_config.get('test_user')
                        skip_google_login = test_mode_config.get('skip_google_login', False)
                        logger.warning("TEST MODE ENABLED - Using test configuration!")
                        
                        # If test mode is configured to skip Google login, update settings
                        if skip_google_login:
                            if 'security' not in settings:
                                settings['security'] = {}
                            settings['security']['require_google_login'] = False
                            logger.warning("TEST MODE - Google login requirement disabled")
                            
                        # If test user is defined, use it
                        if test_user:
                            if 'user' not in settings:
                                settings['user'] = {}
                            settings['user']['email'] = test_user.get('email', 'test@example.com')
                            settings['user']['name'] = test_user.get('name', 'Test User')
                            settings['user']['picture'] = test_user.get('picture', '')
                            logger.warning(f"TEST MODE - Using test user: {settings['user']['name']} ({settings['user']['email']})")
            except Exception as e:
                logger.error(f"Error reading test mode configuration: {str(e)}")
        
        # Check if Google Sign-In is required
        if settings.get("security", {}).get("require_google_login", True):
            logger.info("Google Sign-In required, showing login screen")
            
            # Check if Google auth libraries are available
            if not GOOGLE_AVAILABLE:
                QMessageBox.critical(
                    None, 
                    "Missing Dependencies",
                    "Google authentication libraries are required but not installed.\n\n"
                    "Please install them with:\n"
                    "pip install google-auth google-auth-oauthlib google-auth-httplib2 requests"
                )
                sys.exit(1)
            
            # Show login dialog
            login_dialog = GoogleLoginDialog()
            
            # Check if auto-proceed is possible (remember me is enabled and has valid credentials)
            auto_proceed = False
            if login_dialog.credentials and login_dialog.user_info:
                # We have valid credentials and user info from the "Remember Me" feature
                remember_me_path = login_dialog._get_remember_me_path()
                if os.path.exists(remember_me_path):
                    try:
                        with open(remember_me_path, 'r') as f:
                            remember_me_data = json.load(f)
                            if remember_me_data.get('enabled', False):
                                auto_proceed = True
                                logger.info("Auto-proceeding with remembered Google credentials")
                    except Exception as e:
                        logger.error(f"Error reading remember me file: {str(e)}")
            
            # Only show dialog if we can't auto-proceed
            if not auto_proceed:
                login_result = login_dialog.exec_()
                
                # If login was cancelled or failed, exit
                if login_result != GoogleLoginDialog.Accepted:
                    logger.info("Google Sign-In cancelled, exiting")
                    sys.exit(0)
            
            # Store user info in settings
            if login_dialog.user_info:
                user_email = login_dialog.user_info.get('email')
                user_name = login_dialog.user_info.get('name')
                logger.info(f"User authenticated: {user_name} ({user_email})")
                
                # Check allowed domains if configured
                allowed_domains = settings.get("security", {}).get("allowed_domains", [])
                if allowed_domains:
                    # If we have restricted domains, verify the email domain
                    email_domain = user_email.split('@')[-1] if '@' in user_email else ''
                    if email_domain and email_domain not in allowed_domains:
                        error_msg = f"Email domain {email_domain} is not allowed. Allowed domains: {', '.join(allowed_domains)}"
                        logger.error(error_msg)
                        QMessageBox.critical(None, "Authentication Error", error_msg)
                        sys.exit(1)
                
                # Update settings with user info
                if 'user' not in settings:
                    settings['user'] = {}
                settings['user']['email'] = user_email
                settings['user']['name'] = user_name
                settings['user']['picture'] = login_dialog.user_info.get('picture', '')
            else:
                logger.warning("User authenticated but no user info available")
        
        # Initialize assistant
        logger.debug("Initializing assistant...")
        assistant = AnaAssistant(settings)
        
        # Create and show GUI
        logger.debug("Creating main window...")
        window = MainWindow(assistant, settings)
        window.show()
        
        # Start assistant services in the background
        logger.debug("Starting assistant services...")
        QTimer.singleShot(1000, lambda: assistant.start_services())
        
        logger.info("Ana AI Assistant started successfully")
        return window, assistant
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Ana AI Assistant")
    app.setWindowIcon(QIcon("assets/icons/ana_icon.png"))
    
    # Handle Ctrl+C gracefully
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    try:
        # Start Ana
        window, assistant = main()
        
        # Run application event loop
        exit_code = app.exec_()
        
        # Clean up
        logger.info("Shutting down Ana AI Assistant...")
        assistant.stop_services()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1) 