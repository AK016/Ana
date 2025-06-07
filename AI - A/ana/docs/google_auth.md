# Google Authentication for Ana AI Assistant

This document explains how to set up and use Google Sign-In for Ana AI Assistant.

## Overview

Ana AI Assistant uses Google Sign-In to authenticate users before granting access to the application. This provides several benefits:

1. Secure authentication using industry standards (OAuth 2.0)
2. No need to manage user credentials
3. Integration with existing Google accounts
4. User profile information

## Setup Instructions

### 1. Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth client ID"
5. Select "Desktop application" as the application type
6. Enter a name for your OAuth client
7. Add `http://localhost:8085` as an authorized redirect URI
8. Click "Create" to generate your credentials
9. Download the JSON file containing your credentials

### 2. Configure Ana AI Assistant

1. Rename the downloaded JSON file to `google_credentials.json`
2. Place the file in the `ana/config/` directory
3. Install required dependencies:
   ```
   pip install google-auth google-auth-oauthlib google-auth-httplib2 requests
   ```

## Usage

### Sign-In Process

When Ana AI Assistant starts, it will:

1. Check if Google Sign-In is required (default: yes)
2. Look for previously saved credentials if "Remember Me" was enabled
3. If valid credentials are found, skip the sign-in screen
4. Otherwise, display the Google Sign-In screen
5. Open a browser window for Google authentication
6. After successful authentication, proceed to the main application

### Remember Me Feature

The "Remember Me" feature allows users to avoid signing in each time they start the application:

- When checked (default), credentials are saved and reused for future sessions
- When unchecked, credentials are used only for the current session
- You can clear saved credentials in Settings > APIs & Security > "Clear Remembered Login"

### Domain Restrictions

You can restrict which email domains are allowed to sign in:

1. Go to Settings > APIs & Security
2. Enter comma-separated domains in the "Allowed Email Domains" field
3. Leave empty to allow all domains

### Disabling Google Sign-In

To disable the Google Sign-In requirement:

1. Go to Settings > APIs & Security
2. Uncheck "Require Google Sign-In at startup"
3. Save settings

## For Developers

### Test Mode

For development and testing, you can use test mode to bypass Google authentication:

1. Edit `ana/config/test_mode.json`
2. Set `"enabled": true`
3. Configure `test_user` with the test account details
4. Set `"skip_google_login": true` to bypass the sign-in requirement

### OAuth Callback Server

The application runs a local server on port 8085 to handle the OAuth callback from Google. Ensure this port is available on your system. 