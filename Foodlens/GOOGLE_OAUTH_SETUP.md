# Google OAuth Setup Guide for FoodLens

## 1. Google Cloud Console Setup

### Step 1: Create a Google Cloud Project
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project" or select an existing project
3. Name your project (e.g., "FoodLens")
4. Click "Create"

### Step 2: Enable Google APIs
1. Go to "APIs & Services" > "Library"
2. Search for and enable these APIs:
   - Google+ API (for profile information)
   - Google OAuth2 API
   - People API (recommended for profile data)

### Step 3: Configure OAuth Consent Screen
1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type (or "Internal" if using Google Workspace)
3. Fill in required information:
   - App name: "FoodLens"
   - User support email: Your email
   - Developer contact information: Your email
4. Add scopes:
   - `email`
   - `profile`
   - `openid`
5. Add test users if needed (your email addresses)
6. Submit for verification (if going to production)

### Step 4: Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Configure:
   - Name: "FoodLens Web Client"
   - Authorized JavaScript origins:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
   - Authorized redirect URIs:
     - `http://localhost:3000` (for development)
     - `https://yourdomain.com` (for production)
5. Click "Create"
6. Copy the Client ID and Client Secret

## 2. Update Environment Variables

### Backend (.env file)
```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
```

### Frontend (.env file)
```env
# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
```

## 3. Current Demo Mode

The application currently runs in demo mode when Google credentials are not configured:
- Uses placeholder credentials: `your-google-client-id.apps.googleusercontent.com`
- Demo tokens: `demo-google-token-signin` and `demo-google-token-signup`
- Backend accepts these demo tokens for testing

## 4. Testing Google OAuth

### Demo Mode (Current)
1. Click "Sign In with Google" or "Sign Up with Google"
2. System detects demo mode and shows toast message
3. Uses demo token for authentication
4. Backend processes demo token and creates/authenticates user

### Production Mode (After Setup)
1. Replace placeholder credentials with real ones
2. Google OAuth popup will appear
3. User signs in with their Google account
4. Real Google token is sent to backend
5. Backend verifies token with Google APIs

## 5. Security Considerations

### Development
- Demo mode is only for development/testing
- Demo tokens are hardcoded and not secure

### Production
- Use real Google OAuth credentials
- Enable proper domain restrictions
- Implement proper error handling
- Add rate limiting for auth endpoints

## 6. Troubleshooting

### Common Issues

#### "OAuth client was not found"
- Check that Client ID is correctly set in environment variables
- Verify the Client ID exists in Google Cloud Console

#### "Error 401: invalid_client"
- Client Secret might be incorrect
- Check backend environment variables
- Restart backend server after updating credentials

#### "redirect_uri_mismatch"
- Add your domain to authorized redirect URIs in Google Console
- For development: `http://localhost:3000`
- For production: `https://yourdomain.com`

#### "access_blocked"
- OAuth consent screen needs approval
- Add test users to OAuth consent screen
- Submit app for verification if needed

## 7. Implementation Status

✅ **Completed:**
- Google OAuth backend integration
- Demo token support for testing
- Frontend Google OAuth buttons
- Error handling and fallbacks
- Secure token verification

🔄 **Needs Configuration:**
- Real Google Cloud Console project
- Production OAuth credentials
- Domain verification for production

📝 **Next Steps:**
1. Create Google Cloud project
2. Set up OAuth consent screen
3. Generate real credentials
4. Update environment variables
5. Test with real Google accounts
