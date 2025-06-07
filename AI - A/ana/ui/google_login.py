#!/usr/bin/env python3
# Ana AI Assistant - Google Login Screen

import os
import sys
import json
import logging
import webbrowser
import http.server
import socketserver
import threading
import urllib.parse
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QMessageBox, QProgressBar, QApplication, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont, QDesktopServices

# Google Auth libraries
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    
logger = logging.getLogger('Ana.GoogleLogin')

# Google OAuth scopes
SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

# OAuth callback server
class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Handle OAuth callback from Google"""
    
    def do_GET(self):
        """Process GET request with authorization code"""
        # Parse query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            # Store the authorization code
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Show success page
            success_html = """
            <html>
            <head>
                <title>Ana AI - Authentication Successful</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        text-align: center;
                        background-color: #121212;
                        color: #FFFFFF;
                        margin: 50px;
                    }
                    .container {
                        background-color: #1e1e1e;
                        border-radius: 10px;
                        padding: 30px;
                        max-width: 600px;
                        margin: 0 auto;
                        border: 1px solid #00E5FF;
                        box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
                    }
                    h1 {
                        color: #00E5FF;
                    }
                    p {
                        font-size: 16px;
                        line-height: 1.5;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Authentication Successful!</h1>
                    <p>You have successfully authenticated with Google.</p>
                    <p>You can now close this window and return to Ana AI Assistant.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            # Show error page
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            error_html = """
            <html>
            <head>
                <title>Ana AI - Authentication Failed</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        text-align: center;
                        background-color: #121212;
                        color: #FFFFFF;
                        margin: 50px;
                    }
                    .container {
                        background-color: #1e1e1e;
                        border-radius: 10px;
                        padding: 30px;
                        max-width: 600px;
                        margin: 0 auto;
                        border: 1px solid #FF3C78;
                        box-shadow: 0 0 20px rgba(255, 60, 120, 0.3);
                    }
                    h1 {
                        color: #FF3C78;
                    }
                    p {
                        font-size: 16px;
                        line-height: 1.5;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Authentication Failed</h1>
                    <p>There was a problem authenticating with Google.</p>
                    <p>Please close this window and try again.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Override to prevent console logging"""
        return

class GoogleLoginDialog(QDialog):
    """Google login dialog for Ana AI Assistant"""
    
    # Signal emitted when login is successful
    login_successful = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ana AI - Google Sign In")
        self.setMinimumSize(500, 600)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Auth state
        self.credentials = None
        self.user_info = None
        self.auth_thread = None
        self.oauth_port = 8085
        self.oauth_server = None
        
        self._setup_ui()
        
        # Check for existing credentials
        self._check_saved_credentials()
    
    def _setup_ui(self):
        """Set up the UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("ANA AI")
            logo_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #00E5FF;")
        
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)
        
        # Welcome text
        welcome_label = QLabel("Welcome to Ana AI Assistant")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)
        
        info_label = QLabel("Please sign in with your Google account to continue.")
        info_label.setStyleSheet("font-size: 14px; color: #AAAAAA;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # User info area (hidden initially)
        self.user_info_frame = QLabel()
        self.user_info_frame.setStyleSheet("background-color: #1e1e1e; border-radius: 10px; padding: 20px;")
        self.user_info_frame.setMinimumHeight(100)
        self.user_info_frame.setAlignment(Qt.AlignCenter)
        self.user_info_frame.setText("Not signed in")
        self.user_info_frame.hide()
        layout.addWidget(self.user_info_frame)
        
        # Google Sign In button
        self.sign_in_button = QPushButton("Sign in with Google")
        self.sign_in_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #757575;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #F5F5F5;
            }
            QPushButton:pressed {
                background-color: #EEEEEE;
            }
        """)
        
        # Add Google icon if available
        google_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                       "assets", "icons", "google_icon.png")
        if os.path.exists(google_icon_path):
            self.sign_in_button.setIcon(QIcon(google_icon_path))
            self.sign_in_button.setIconSize(QSize(24, 24))
        
        self.sign_in_button.clicked.connect(self._start_google_auth)
        
        # Progress bar for auth
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 5px;
                text-align: center;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #00E5FF;
                width: 10px;
            }
        """)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.hide()
        
        # Continue button (disabled until logged in)
        self.continue_button = QPushButton("Continue to Ana AI")
        self.continue_button.setStyleSheet("""
            QPushButton {
                background-color: #00E5FF;
                color: #000000;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 20px;
            }
            QPushButton:hover {
                background-color: #00D0F0;
            }
            QPushButton:pressed {
                background-color: #00C0E0;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """)
        self.continue_button.setEnabled(False)
        self.continue_button.clicked.connect(self.accept)
        
        # Remember me checkbox
        self.remember_me = QCheckBox("Remember me")
        self.remember_me.setStyleSheet("""
            QCheckBox {
                color: #AAAAAA;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #444444;
                border-radius: 3px;
                background-color: #1a1a1a;
            }
            QCheckBox::indicator:checked {
                background-color: #00E5FF;
                border: 1px solid #00E5FF;
            }
        """)
        self.remember_me.setChecked(True)  # Checked by default
        
        # Button layout
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        button_layout.addWidget(self.sign_in_button)
        button_layout.addWidget(self.progress_bar)
        button_layout.addWidget(self.remember_me)
        button_layout.addWidget(self.continue_button)
        
        layout.addStretch()
        layout.addLayout(button_layout)
    
    def _check_saved_credentials(self):
        """Check for previously saved credentials"""
        if not GOOGLE_AVAILABLE:
            QMessageBox.warning(
                self, 
                "Google Authentication Not Available", 
                "Google authentication libraries are not installed. Please install them to enable Google Sign-In."
            )
            return
        
        # Check for remember me setting
        remember_me_path = self._get_remember_me_path()
        remember_me_enabled = False
        
        if os.path.exists(remember_me_path):
            try:
                with open(remember_me_path, 'r') as f:
                    remember_me_data = json.load(f)
                    remember_me_enabled = remember_me_data.get('enabled', False)
            except Exception as e:
                logger.error(f"Error reading remember me file: {str(e)}")
        
        # Only try to use saved credentials if remember me is enabled
        if not remember_me_enabled:
            logger.info("Remember me is disabled, not using saved credentials")
            return
            
        # Try to load saved credentials
        token_path = self._get_token_path()
        
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_info(
                    json.loads(token_path.read_text()), SCOPES)
                
                if creds and creds.valid:
                    logger.info("Found valid saved credentials")
                    self.credentials = creds
                    self._fetch_user_info()
                    return
                
                if creds and creds.expired and creds.refresh_token:
                    logger.info("Refreshing expired credentials")
                    creds.refresh(Request())
                    self.credentials = creds
                    self._save_credentials()
                    self._fetch_user_info()
                    return
            except (RefreshError, Exception) as e:
                logger.error(f"Error loading saved credentials: {str(e)}")
                # Invalid token, will need to reauthenticate
                if os.path.exists(token_path):
                    os.remove(token_path)
    
    def _get_token_path(self):
        """Get the path to the token file"""
        # Create data directory if it doesn't exist
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(app_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        return Path(os.path.join(data_dir, "google_token.json"))
    
    def _get_remember_me_path(self):
        """Get the path to the remember me file"""
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(app_dir, "data")
        return Path(os.path.join(data_dir, "remember_me.json"))
    
    def _get_credentials_path(self):
        """Get the path to the credentials file"""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config", 
            "google_credentials.json"
        )
    
    def _start_google_auth(self):
        """Start the Google authentication flow"""
        if not GOOGLE_AVAILABLE:
            QMessageBox.warning(
                self, 
                "Google Authentication Not Available", 
                "Google authentication libraries are not installed. Please install them to enable Google Sign-In."
            )
            return
        
        # Check if credentials file exists
        credentials_path = self._get_credentials_path()
        if not os.path.exists(credentials_path):
            QMessageBox.critical(
                self,
                "Missing OAuth Credentials",
                "Google OAuth credentials file is missing. Please add a valid 'google_credentials.json' file to the config directory."
            )
            return
        
        # Show progress and disable button
        self.sign_in_button.setEnabled(False)
        self.progress_bar.show()
        
        # Start authentication in a thread to avoid blocking UI
        self.auth_thread = threading.Thread(target=self._authenticate)
        self.auth_thread.daemon = True
        self.auth_thread.start()
    
    def _authenticate(self):
        """Authenticate with Google (run in thread)"""
        try:
            # Start a local server to handle the OAuth callback
            self.oauth_server = socketserver.TCPServer(
                ("localhost", self.oauth_port), 
                OAuthCallbackHandler
            )
            self.oauth_server.auth_code = None
            
            # Start server in a thread
            server_thread = threading.Thread(target=self.oauth_server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            # Set up OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                self._get_credentials_path(),
                SCOPES,
                redirect_uri=f'http://localhost:{self.oauth_port}'
            )
            
            # Open browser for authentication
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            QDesktopServices.openUrl(QUrl(auth_url))
            
            # Wait for the callback to receive the authorization code
            while self.oauth_server.auth_code is None:
                if not getattr(self, 'auth_thread', None) or not self.auth_thread.is_alive():
                    # Authentication was cancelled
                    self.oauth_server.shutdown()
                    return
                # Don't hog the CPU
                import time
                time.sleep(0.1)
            
            # Exchange the authorization code for credentials
            flow.fetch_token(code=self.oauth_server.auth_code)
            self.credentials = flow.credentials
            
            # Save credentials
            self._save_credentials()
            
            # Get user info
            self._fetch_user_info()
            
            # Shut down the server
            self.oauth_server.shutdown()
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            # Update UI from the main thread
            QApplication.instance().callLater(0, self._on_auth_error, str(e))
    
    def _save_credentials(self):
        """Save credentials to token file"""
        if self.credentials:
            token_path = self._get_token_path()
            token_path.write_text(
                self.credentials.to_json()
            )
            logger.info(f"Credentials saved to {token_path}")
            
            # Save remember me setting
            if hasattr(self, 'remember_me'):
                remember_me_path = self._get_remember_me_path()
                with open(remember_me_path, 'w') as f:
                    json.dump({'enabled': self.remember_me.isChecked()}, f)
                logger.info(f"Remember me setting saved: {self.remember_me.isChecked()}")
    
    def _fetch_user_info(self):
        """Fetch user info from Google API"""
        if not self.credentials:
            return
            
        try:
            import requests
            # Call the Google userinfo API
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers={'Authorization': f'Bearer {self.credentials.token}'}
            )
            
            if response.status_code == 200:
                self.user_info = response.json()
                logger.info(f"Got user info: {self.user_info.get('email')}")
                
                # Update UI from the main thread
                QApplication.instance().callLater(0, self._on_auth_success)
            else:
                logger.error(f"Failed to get user info: {response.text}")
                # Update UI from the main thread
                QApplication.instance().callLater(0, self._on_auth_error, "Failed to get user info")
                
        except Exception as e:
            logger.error(f"Error fetching user info: {str(e)}")
            # Update UI from the main thread
            QApplication.instance().callLater(0, self._on_auth_error, str(e))
    
    def _on_auth_success(self):
        """Handle successful authentication"""
        # Hide progress and re-enable button
        self.progress_bar.hide()
        self.sign_in_button.setEnabled(True)
        
        # Update user info display
        if self.user_info:
            self.user_info_frame.show()
            
            # Create user info HTML
            email = self.user_info.get('email', 'Unknown')
            name = self.user_info.get('name', 'Unknown User')
            picture = self.user_info.get('picture', '')
            
            user_html = f"""
            <div style="text-align: center;">
                <div style="margin-bottom: 10px;">
                    <img src="{picture}" width="64" height="64" style="border-radius: 32px;">
                </div>
                <div style="font-size: 18px; font-weight: bold; color: #FFFFFF;">{name}</div>
                <div style="font-size: 14px; color: #AAAAAA;">{email}</div>
                <div style="margin-top: 10px; color: #00E5FF;">Successfully signed in</div>
            </div>
            """
            
            self.user_info_frame.setText(user_html)
        
        # Enable continue button
        self.continue_button.setEnabled(True)
        
        # Emit signal with user info
        self.login_successful.emit(self.user_info or {})
    
    def _on_auth_error(self, error_message):
        """Handle authentication error"""
        # Hide progress and re-enable button
        self.progress_bar.hide()
        self.sign_in_button.setEnabled(True)
        
        # Show error message
        QMessageBox.critical(
            self,
            "Authentication Error",
            f"Failed to authenticate with Google: {error_message}"
        )

# For testing directly
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    login = GoogleLoginDialog()
    result = login.exec_()
    
    if result == QDialog.Accepted:
        print("Login successful!")
        if login.user_info:
            print(f"User: {login.user_info.get('name')} ({login.user_info.get('email')})")
    else:
        print("Login cancelled.")
    
    sys.exit(0) 