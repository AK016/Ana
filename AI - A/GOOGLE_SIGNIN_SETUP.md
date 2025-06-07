# Setting Up Google Sign-In for Ana AI Assistant

This guide provides step-by-step instructions for setting up Google OAuth authentication for the Ana AI Assistant application to avoid the "OAuth client was not found" (Error 401: invalid_client) error.

## Prerequisites

- Google account
- Ana AI Assistant codebase
- Access to edit configuration files

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "Ana AI Assistant")
5. Click "Create"
6. Once created, select your new project from the dropdown

## Step 2: Enable the Google OAuth APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google OAuth2 API" and enable it
3. Also search for and enable "People API" (for user profile information)

## Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (unless you have Google Workspace)
3. Click "Create"
4. Fill in the required fields:
   - App name: "Ana AI Assistant"
   - User support email: Your email
   - Developer contact information: Your email
5. Click "Save and Continue"
6. On the Scopes page, add these scopes:
   - `userinfo.email`
   - `userinfo.profile`
   - `openid`
7. Click "Save and Continue"
8. Add test users (including your own email)
9. Click "Save and Continue", then "Back to Dashboard"

## Step 4: Create OAuth Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click on "Create Credentials" and select "OAuth client ID"
3. For Application type, select "Desktop app"
4. Name: "Ana AI Assistant Desktop"
5. Click "Create"
6. You'll receive a client ID and client secret - **save these values**

## Step 5: Update Ana AI Configuration

1. Navigate to the Ana AI config directory
2. Edit the `client_secrets.json` file in the `ana/config/` directory:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "ana-ai-assistant",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": [
      "http://localhost:8085/",
      "http://localhost"
    ]
  }
}
```

3. Replace `YOUR_CLIENT_ID.apps.googleusercontent.com` with your actual client ID
4. Replace `YOUR_CLIENT_SECRET` with your actual client secret
5. Make sure the "installed" key is used (not "web") since this is a desktop application

## Step 6: Enable Google Sign-In in Ana AI Settings

1. Edit the `settings.json` file in the `ana/config/` directory
2. Make sure the security section has `require_google_login` set to `true`:

```json
"security": {
  "require_google_login": true,
  "allowed_domains": [],
  "local_authentication": true
}
```

## Step 7: Disable Test Mode

1. Edit the `test_mode.json` file in the `ana/config/` directory
2. Make sure `enabled` and `skip_google_login` are both set to `false`:

```json
{
  "enabled": false,
  "skip_google_login": false,
  "test_user": {
    "name": "Test User",
    "email": "test@example.com",
    "picture": ""
  },
  "mock_services": {
    "weather": true,
    "voice": true,
    "facial_recognition": true
  },
  "debug_logging": true
}
```

## Step 8: Run Ana AI Assistant

1. Start the application with `python3 -m ana.main`
2. The Google sign-in screen should appear
3. When you click "Sign in with Google," it will open a browser window
4. Sign in with your Google account
5. Grant the requested permissions
6. The application should now log you in successfully

## Troubleshooting

### Error: "The OAuth client was not found"
- Check that you've properly replaced the placeholders in `client_secrets.json` with your actual client ID and secret
- Verify that you're using the "installed" key (not "web") in the JSON structure
- Make sure the file is properly formatted JSON with no syntax errors

### Error: "Redirect URI Mismatch"
- Make sure your `client_secrets.json` file includes the exact redirect URIs that match what the application is using
- The default is `http://localhost:8085/` and `http://localhost`

### Authorization Code Flow Issues
- The Ana AI application uses port 8085 by default for the OAuth callback
- If you're experiencing issues, make sure this port is available and not blocked by a firewall

### Google Developer Console Issues
- If you can't see your project or credentials, make sure you're logged into the correct Google account
- Sometimes browser caching can cause issues - try clearing your browser cache or using incognito mode

## Additional Resources

- [Google OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Setting up OAuth 2.0](https://support.google.com/cloud/answer/6158849)
- [Using OAuth 2.0 for Installed Applications](https://developers.google.com/identity/protocols/oauth2/native-app) 