# Social Media Publishers Guide

This document provides information about the implemented social media publishers and how to configure them.

## Supported Platforms

- **Twitter/X** - Fully implemented and tested
- **Instagram** - Implemented with session caching
- **Facebook** - Implemented for Facebook Pages
- **LinkedIn** - Implemented with OAuth 2.0

## Quick Start: API Token Setup

This guide provides step-by-step instructions for obtaining API credentials for each platform. All credentials should be stored in a `.env` file in the project root.

### Prerequisites

1. **Create `.env` file:**
   ```bash
   cd social-quote-generator
   touch .env
   chmod 600 .env  # Secure the file
   ```

2. **Add to `.gitignore`:**
   ```bash
   echo ".env" >> .gitignore
   ```

### Setup Difficulty & Time Estimates

| Platform | Difficulty | Time Required | Token Expiration | Notes |
|----------|-----------|---------------|------------------|-------|
| **Twitter/X** | Medium | 30-60 min | Never | Requires Elevated Access approval |
| **Instagram** | Easy | 5 min | Session-based | Unofficial method, simple but limited |
| **Facebook** | Hard | 30-45 min | 60 days | Complex OAuth flow, requires Page |
| **LinkedIn** | Hard | 30-45 min | 60 days | Complex OAuth flow, requires approval |

### Environment Variables Template

Create a `.env` file with this structure:

```bash
# Twitter/X API Credentials (OAuth 1.0a)
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here

# Instagram Credentials (Username/Password - Unofficial)
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# Facebook API Credentials (OAuth 2.0)
FACEBOOK_ACCESS_TOKEN=your_long_lived_page_token_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here

# LinkedIn API Credentials (OAuth 2.0)
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here
LINKEDIN_PERSON_URN=urn:li:person:your_person_id_here
```

### Platform-Specific Quick Links

**Twitter/X:**
- [Developer Portal](https://developer.twitter.com/en/portal/dashboard)
- [Apply for Elevated Access](https://developer.twitter.com/en/portal/products/elevated)
- Detailed instructions: See "Twitter/X Publisher" section below

**Instagram:**
- Simple username/password setup
- No developer account required (unofficial method)
- Detailed instructions: See "Instagram Publisher" section below

**Facebook:**
- [Developers Console](https://developers.facebook.com/)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
- Detailed instructions: See "Facebook Publisher" section below

**LinkedIn:**
- [Developer Portal](https://www.linkedin.com/developers/)
- Requires LinkedIn Page
- Detailed instructions: See "LinkedIn Publisher" section below

### Testing Your Setup

After configuring credentials, test each platform:

```bash
# Test Twitter
bge-quote-gen --episode 1 --platform twitter --dry-run --verbose

# Test Instagram
bge-quote-gen --episode 1 --platform instagram --dry-run --verbose

# Test Facebook
bge-quote-gen --episode 1 --platform facebook --dry-run --verbose

# Test LinkedIn
bge-quote-gen --episode 1 --platform linkedin --dry-run --verbose
```

### Common Setup Issues

**All Platforms:**
- Ensure `.env` file is in the correct location (project root or social-quote-generator/)
- Check for typos in environment variable names (must match exactly)
- Verify no extra spaces or quotes around token values
- Confirm `.env` file has Unix line endings (LF, not CRLF)

**Token Expiration:**
- Twitter: Tokens don't expire
- Instagram: Session expires after weeks/months of inactivity
- Facebook: Page tokens expire after 60 days
- LinkedIn: Access tokens expire after 60 days

**Refresh Strategy:**
- Set calendar reminders for token expiration
- Implement automated token refresh (advanced)
- Keep refresh tokens saved securely for Facebook/LinkedIn

---

## Publisher Architecture

All publishers inherit from `BasePublisher` and implement:
- `authenticate()` - Authenticate with platform API
- `publish()` - Publish image with caption
- `_generate_caption()` - Generate caption from template (inherited)
- `_generate_hashtags()` - Generate hashtags (inherited)

## Platform-Specific Details

### Twitter/X Publisher

**Library:** tweepy (v4.14.0+)

**Authentication:** OAuth 1.0a with API keys and access tokens

**Required Credentials:**
- API Key (Consumer Key)
- API Secret (Consumer Secret)
- Access Token
- Access Token Secret

**Configuration Example:**
```yaml
twitter:
  enabled: true
  api_key: "${TWITTER_API_KEY}"
  api_secret: "${TWITTER_API_SECRET}"
  access_token: "${TWITTER_ACCESS_TOKEN}"
  access_token_secret: "${TWITTER_ACCESS_TOKEN_SECRET}"
  caption_template: "🎙️ BGE Episodio {episode_number}: {title}\n\n{quote}\n\n{hashtags}"
  hashtags: ["#BGE", "#DevOps", "#IT"]
```

**Character Limit:** 280 characters (automatically truncated)

**Getting Twitter/X API Credentials (Detailed):**

1. **Apply for Twitter Developer Account**
   - Visit [Twitter Developer Portal](https://developer.twitter.com/)
   - Sign in with your Twitter/X account
   - Click "Sign up" for a developer account
   - Fill out the application form:
     - Select account type: "Hobbyist" or "Professional"
     - Choose use case: "Making a bot" or "Exploring the API"
     - Describe your intended use (be specific about posting quotes)
   - Accept terms and conditions
   - Verify your email address

2. **Apply for Elevated Access (Required for Posting)**
   - After developer account approval, go to [Developer Portal Dashboard](https://developer.twitter.com/en/portal/dashboard)
   - You'll start with Essential Access (read-only)
   - Click "Elevated" under your account name
   - Click "Apply for Elevated"
   - Fill out the detailed form:
     - Describe your use case in detail
     - Confirm you're not violating Twitter Rules
     - Explain tweet/retweet behavior (automated quote posting)
     - Mention approximate posting frequency
   - Wait for approval (usually 1-2 days, can be instant)

3. **Create a Project and App**
   - In Developer Portal, click "Projects & Apps"
   - Click "Create Project"
   - Name your project (e.g., "BGE Social Quote Bot")
   - Select use case: "Making a bot" or "Enabling programmatic access"
   - Provide project description
   - Click "Next" and create an App within the project
   - Name your app (e.g., "BGE Quote Generator")

4. **Configure App Settings**
   - Go to your App settings
   - Navigate to "Settings" tab
   - Configure "User authentication settings":
     - App permissions: **"Read and Write"** (required for posting)
     - Type of App: "Web App, Automated App or Bot"
     - Callback URI: `http://localhost/callback` (can be anything for automated apps)
     - Website URL: Your website or GitHub repo
   - Save settings

5. **Generate API Keys and Tokens**
   - Go to "Keys and tokens" tab
   - **API Key and Secret (Consumer Keys):**
     - Click "Regenerate" under "Consumer Keys"
     - Copy `API Key` → Save as `TWITTER_API_KEY`
     - Copy `API Key Secret` → Save as `TWITTER_API_SECRET`
     - **Important:** Store these immediately - secret is shown only once!

   - **Access Token and Secret:**
     - Scroll to "Authentication Tokens"
     - Click "Generate" under "Access Token and Secret"
     - Ensure permissions show "Read and Write"
     - Copy `Access Token` → Save as `TWITTER_ACCESS_TOKEN`
     - Copy `Access Token Secret` → Save as `TWITTER_ACCESS_TOKEN_SECRET`
     - **Important:** Store these immediately - secret is shown only once!

6. **Add to Configuration**
   ```bash
   # In .env file
   TWITTER_API_KEY=xxxxxxxxxxxxxxxxxxx
   TWITTER_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWITTER_ACCESS_TOKEN=1234567890-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWITTER_ACCESS_TOKEN_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

7. **Verify Permissions**
   - Test credentials with: `bge-quote-gen --episode 1 --platform twitter --dry-run --verbose`
   - Check that App Settings show "Read and Write" permissions
   - Confirm Elevated Access is granted (required for v2 API posting)

**Rate Limits (Elevated Access):**
- **Tweets:** 300 posts per 3 hours (per app)
- **Media uploads:** 300 per 15 minutes
- **Essential Access:** Cannot create tweets (read-only)

**Common Issues:**
- **"403 Forbidden"** → Likely have Essential Access only, need Elevated
- **"Read-only application"** → Change App permissions to "Read and Write" in User authentication settings
- **"Could not authenticate"** → Regenerate tokens, ensure copied correctly with no extra spaces
- **"Rate limit exceeded"** → Wait for rate limit window to reset (automatic retry implemented)

**Important Notes:**
- Requires **Elevated Access** to post tweets
- App must have **"Read and Write"** permissions
- Access tokens don't expire unless regenerated or revoked
- Always use OAuth 1.0a (API Key + Access Token), not OAuth 2.0
- The code uses API v1.1 for media upload and v2 for tweet creation

**Documentation:**
- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Authentication Guide](https://developer.twitter.com/en/docs/authentication/oauth-1-0a)
- [Elevated Access](https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api#v2-access-level)

**Notes:**
- Uses both API v1.1 (media upload) and v2 (tweet creation)
- Implements retry logic for rate limits
- Verifies credentials on authentication

---

### Instagram Publisher

**Library:** instagrapi (v2.0.0+)

**Authentication:** Username and password

**Required Credentials:**
- Username
- Password
- Session File (optional, recommended)

**Configuration Example:**
```yaml
instagram:
  enabled: true
  username: "${INSTAGRAM_USERNAME}"
  password: "${INSTAGRAM_PASSWORD}"
  session_file: "output/.instagram_session"
  caption_template: "🎙️ BGE Episodio {episode_number}\n\n{quote}\n\n{hashtags}"
  hashtags: ["#BGE", "#DevOps", "#IT", "#Podcast"]
```

**Character Limit:** 2,200 characters (automatically truncated)

**Notes:**
- Session file caching reduces login frequency and avoids rate limits
- May require manual verification for new accounts
- Instagram has aggressive anti-bot measures
- 2FA and challenge verification are detected with helpful error messages

**Getting Instagram Credentials (Detailed):**

The code currently uses the **unofficial method** (instagrapi library) which is simpler but has limitations. The official Instagram Graph API is more complex but more reliable for production use.

**Method 1: Username/Password (Currently Implemented - Unofficial)**

This method uses the `instagrapi` library which mimics the Instagram mobile app.

1. **Prepare Instagram Account**
   - Use an Instagram account (personal or business)
   - Consider creating a dedicated account for automation
   - **Recommended:** Convert to Business or Creator account for better reliability

2. **Handle Two-Factor Authentication (2FA)**
   - **Option A:** Temporarily disable 2FA during setup
     - Go to Instagram Settings → Security → Two-Factor Authentication
     - Disable temporarily, then re-enable after session is established
   - **Option B:** Use backup codes
     - Save backup codes from Instagram 2FA settings
     - You may be prompted to enter one during first login
   - **Option C:** Handle challenges programmatically (advanced)
     - The code may prompt for verification codes
     - Check your email/SMS for Instagram verification codes

3. **Configure Credentials**
   ```bash
   # In .env file
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_secure_password
   ```

4. **Session File Management**
   - First run will create `.instagram_session` file in output directory
   - This file stores login session to avoid repeated logins
   - Session files can last weeks to months
   - **Security:** Add to `.gitignore` and set file permissions to 600
   ```bash
   chmod 600 output/.instagram_session
   ```

5. **Test Login**
   ```bash
   # First run may require verification
   bge-quote-gen --episode 1 --platform instagram --dry-run --verbose
   ```

**Method 1 Limitations:**
- Instagram may flag automated activity
- Account can be temporarily blocked for suspicious activity
- Session files may expire requiring re-login
- Violates Instagram's Terms of Service (use at your own risk)
- May require manual verification challenges

**Method 2: Facebook Graph API (Official - Not Implemented)**

For production use, consider implementing the official Instagram Graph API.

**Requirements:**
- Instagram Business or Creator account
- Facebook Page connected to Instagram account
- Facebook Developer App with Instagram Graph API

**Steps:**
1. **Convert Instagram to Business Account**
   - Open Instagram app
   - Go to Settings → Account → Switch to Professional Account
   - Choose "Business" or "Creator"

2. **Connect to Facebook Page**
   - Go to Settings → Account → Linked Accounts → Facebook
   - Connect to a Facebook Page (create one if needed)
   - This links your Instagram Business account to the Facebook Page

3. **Create Facebook Developer App**
   - Follow Facebook setup instructions (see Facebook section above)
   - Add "Instagram Graph API" product
   - Request permissions: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`

4. **Get Access Token**
   - Use Graph API Explorer: https://developers.facebook.com/tools/explorer/
   - Generate token with Instagram permissions
   - Exchange for Long-Lived Token (60 days)

5. **Get Instagram Business Account ID**
   ```bash
   curl -X GET "https://graph.facebook.com/v21.0/me/accounts?access_token={ACCESS_TOKEN}"
   # Get page access token and page ID
   curl -X GET "https://graph.facebook.com/v21.0/{PAGE_ID}?fields=instagram_business_account&access_token={PAGE_ACCESS_TOKEN}"
   ```

6. **Publishing with Graph API** (requires code changes)
   ```bash
   # Create media container
   curl -X POST "https://graph.facebook.com/v21.0/{IG_ACCOUNT_ID}/media" \
     -d "image_url={IMAGE_URL}" \
     -d "caption={CAPTION}" \
     -d "access_token={ACCESS_TOKEN}"

   # Publish media
   curl -X POST "https://graph.facebook.com/v21.0/{IG_ACCOUNT_ID}/media_publish" \
     -d "creation_id={CREATION_ID}" \
     -d "access_token={ACCESS_TOKEN}"
   ```

**Method 2 Benefits:**
- Official API, complies with Instagram Terms of Service
- More reliable for production use
- Better rate limits and error handling
- Supports scheduling and insights

**Method 2 Limitations:**
- Requires Business/Creator account
- Requires Facebook Page connection
- More complex setup process
- Token expires every 60 days (needs refresh)

**Current Recommendation:**
- For personal/testing: Use Method 1 (username/password)
- For production: Consider implementing Method 2 (Graph API)

**Troubleshooting:**
- **"Challenge Required"** → Instagram wants you to verify it's you
  - Open Instagram app and complete verification
  - Try disabling 2FA temporarily
  - Wait 24 hours and try again
- **"Two-Factor Authentication Required"** →
  - Disable 2FA temporarily, or
  - Save session file after successful login with 2FA
- **"Feedback Required"** → Account has been flagged
  - Reduce posting frequency
  - Use Instagram app normally to appear less automated
  - Wait 24-48 hours before retrying
- **"Login Required" / Session Expired** →
  - Delete `.instagram_session` file
  - Re-authenticate (may require verification)
- **"Too Many Requests"** → Rate limited
  - Wait 15-30 minutes
  - Reduce posting frequency
  - Consider using official API

**Session File Best Practices:**
- Store in secure location (not in git)
- Set file permissions: `chmod 600 .instagram_session`
- Backup session files to avoid repeated logins
- Session typically valid for weeks/months
- If suspicious activity detected, delete and re-authenticate

---

### Facebook Publisher

**Library:** facebook-sdk (v3.1.0+)

**Authentication:** Page Access Token

**Required Credentials:**
- Page Access Token (not User Access Token)
- Page ID (optional, can be retrieved from token)

**Configuration Example:**
```yaml
facebook:
  enabled: true
  access_token: "${FACEBOOK_ACCESS_TOKEN}"
  page_id: "${FACEBOOK_PAGE_ID}"
  caption_template: "🎙️ BGE Episodio {episode_number}: {title}\n\n{quote}\n\n{hashtags}"
  hashtags: ["#BGE", "#DevOps", "#IT"]
```

**Character Limit:** 63,206 characters (warning at 5,000+)

**Notes:**
- Requires a **Page Access Token**, not a User Access Token
- Token must have `pages_manage_posts` permission
- Posts to Facebook Pages, not personal profiles
- Page ID can be auto-retrieved if token includes it

**Getting a Page Access Token (Detailed):**

1. **Create a Facebook Developer App**
   - Visit [Facebook Developers](https://developers.facebook.com/)
   - Click "My Apps" → "Create App"
   - Choose app type: "Business" or "Consumer"
   - Provide app name, contact email, and optional Business Manager account
   - Click "Create App"

2. **Add Required Products**
   - In the App Dashboard, find "Add Products to Your App"
   - Add "Facebook Login for Business" or "Facebook Login"
   - Configure OAuth redirect URIs (can use `https://localhost/` for testing)

3. **Configure App Permissions**
   - Go to "App Review" → "Permissions and Features"
   - Request advanced access for: `pages_read_engagement`, `pages_manage_posts`
   - For personal use, standard access is sufficient

4. **Generate Access Token**
   - Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - Select your app from the dropdown
   - Click "Generate Access Token"
   - Select permissions: `pages_read_engagement`, `pages_manage_posts`, `pages_read_user_content`
   - Click "Generate Access Token" and authorize
   - Copy the User Access Token (short-lived, ~1 hour)

5. **Get Page ID**
   - In Graph API Explorer, with your token selected
   - Make a GET request to: `/me/accounts`
   - Find your page in the results
   - Copy the `id` field (this is your Page ID)
   - Copy the `access_token` for that page (this is your Page Access Token)

6. **Convert to Long-Lived Token (Optional but Recommended)**
   - Short-lived User tokens expire in ~1 hour
   - Page tokens from step 5 are typically long-lived (60 days) already
   - To manually extend a User token to 60 days, use:
   ```bash
   curl "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}"
   ```
   - Use [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/) to check expiration

7. **Add to Configuration**
   ```bash
   # In .env file
   FACEBOOK_ACCESS_TOKEN=EAABsbCS1iHgBO...  # Page Access Token from step 5
   FACEBOOK_PAGE_ID=123456789012345          # Page ID from step 5
   ```

**Important Notes:**
- Use the **Page Access Token** (from `/me/accounts`), not the User Access Token
- Page Access Tokens are typically long-lived (60 days) by default
- Tokens need `pages_manage_posts` permission to create posts
- For production apps, implement token refresh flow to avoid expiration

**Troubleshooting:**
- "Permissions error" → Check token has `pages_manage_posts` permission
- "Token expired" → Generate a new Page Access Token
- "Invalid page ID" → Verify page ID or let it auto-retrieve

---

### LinkedIn Publisher

**Library:** requests (direct API calls to LinkedIn API v2)

**Authentication:** OAuth 2.0 Access Token

**Required Credentials:**
- Access Token with `w_member_social` permission

**Configuration Example:**
```yaml
linkedin:
  enabled: true
  access_token: "${LINKEDIN_ACCESS_TOKEN}"
  caption_template: "🎙️ BGE Episodio {episode_number}: {title}\n\n{quote}\n\n{hashtags}"
  hashtags: ["#BGE", "#DevOps", "#IT"]
```

**Character Limit:** 3,000 characters (automatically truncated)

**Notes:**
- Uses LinkedIn API v2 with three-step upload process:
  1. Register image upload
  2. Upload image binary
  3. Create UGC post with image
- Requires OAuth 2.0 access token with `w_member_social` permission
- Posts are public by default
- Person URN is automatically retrieved

**Getting a LinkedIn Access Token (Detailed):**

1. **Create LinkedIn Developer App**
   - Visit [LinkedIn Developers](https://www.linkedin.com/developers/)
   - Sign in with your LinkedIn account
   - Click "Create app"
   - Fill in required information:
     - App name (e.g., "BGE Quote Generator")
     - LinkedIn Page: **Required** - select or create a LinkedIn Page
     - App logo: Upload a logo image (min 300x300px)
     - Privacy policy URL (can use your website or GitHub repo)
     - Legal agreement
   - Click "Create app"

2. **Request API Products**
   - In your app dashboard, go to "Products" tab
   - Request access to:
     - **"Share on LinkedIn"** (required for posting)
     - **"Sign In with LinkedIn using OpenID Connect"** (required for authentication)
   - Click "Request access" for each product
   - Wait for approval (can be instant or take a few days)
   - **Note:** Some products require LinkedIn Page verification

3. **Configure OAuth 2.0 Settings**
   - Go to "Auth" tab in your app
   - Under "OAuth 2.0 settings":
     - Note your **Client ID**
     - Note your **Client Secret** (click "Show" to reveal)
   - Add **Redirect URLs**:
     - For testing: `https://localhost/auth/callback` or `http://127.0.0.1/callback`
     - For production: Your actual OAuth callback URL
   - Save settings

4. **Get Authorization Code (OAuth 2.0 Flow)**

   **Step A: Authorize Your App**
   - Build authorization URL (replace placeholders):
   ```
   https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id={YOUR_CLIENT_ID}&redirect_uri=https://localhost/auth/callback&scope=openid%20profile%20w_member_social
   ```
   - Open this URL in a web browser while logged into LinkedIn
   - Review permissions and click "Allow"
   - You'll be redirected to: `https://localhost/auth/callback?code=AUTHORIZATION_CODE&state=...`
   - Copy the `code` parameter value (the authorization code)
   - **Important:** Code expires in 30 seconds, use immediately

5. **Exchange Code for Access Token**

   Use curl or Postman to exchange the authorization code:
   ```bash
   curl -X POST 'https://www.linkedin.com/oauth/v2/accessToken' \
     -H 'Content-Type: application/x-www-form-urlencoded' \
     -d 'grant_type=authorization_code' \
     -d 'code={AUTHORIZATION_CODE}' \
     -d 'client_id={YOUR_CLIENT_ID}' \
     -d 'client_secret={YOUR_CLIENT_SECRET}' \
     -d 'redirect_uri=https://localhost/auth/callback'
   ```

   Response will contain:
   ```json
   {
     "access_token": "AQXdSP_W0...",
     "expires_in": 5184000,
     "refresh_token": "AQVbOTc...",
     "refresh_token_expires_in": 31536000
   }
   ```
   - Copy `access_token` → Save as `LINKEDIN_ACCESS_TOKEN`
   - Optionally save `refresh_token` for automated token renewal

6. **Get Person URN**

   Use the access token to get your LinkedIn URN:
   ```bash
   curl -X GET 'https://api.linkedin.com/v2/userinfo' \
     -H 'Authorization: Bearer {ACCESS_TOKEN}'
   ```

   Response:
   ```json
   {
     "sub": "urn:li:person:abc123xyz",
     "name": "Your Name",
     "email": "your@email.com"
   }
   ```
   - Copy the `sub` field → Save as `LINKEDIN_PERSON_URN`

7. **Add to Configuration**
   ```bash
   # In .env file
   LINKEDIN_ACCESS_TOKEN=AQXdSP_W0KLxZpGtQk...
   LINKEDIN_PERSON_URN=urn:li:person:abc123xyz
   ```

**Token Refresh (Optional but Recommended):**

Access tokens expire after 60 days by default. To refresh:
```bash
curl -X POST 'https://www.linkedin.com/oauth/v2/accessToken' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=refresh_token' \
  -d 'refresh_token={REFRESH_TOKEN}' \
  -d 'client_id={YOUR_CLIENT_ID}' \
  -d 'client_secret={YOUR_CLIENT_SECRET}'
```

**Testing:**
```bash
# Test token validity
curl -X GET 'https://api.linkedin.com/v2/userinfo' \
  -H 'Authorization: Bearer {ACCESS_TOKEN}'

# Test with bge-quote-gen
bge-quote-gen --episode 1 --platform linkedin --dry-run --verbose
```

**Rate Limits:**
- **Posts:** 100 per day per person
- **API Calls:** 500 per day per application
- **Media Uploads:** Included in API call limit

**Common Issues:**
- **"401 Unauthorized"** → Access token expired (60 days), regenerate or use refresh token
- **"403 Forbidden"** → Missing `w_member_social` permission or "Share on LinkedIn" product not approved
- **"429 Too Many Requests"** → Rate limit exceeded, wait before retrying
- **"The token used in the request has expired"** → Get a new access token using refresh token or OAuth flow
- **"Invalid redirect_uri"** → Ensure redirect URI matches exactly what's configured in app settings

**Important Notes:**
- Access tokens expire after **60 days** (5,184,000 seconds)
- Refresh tokens expire after **1 year**
- Use refresh tokens to avoid manual re-authentication
- Person URN format: `urn:li:person:{alphanumeric-id}`
- Requires approval of "Share on LinkedIn" product
- Must have a LinkedIn Page associated with the app

**OAuth 2.0 Scopes Required:**
- `openid` - Required for authentication
- `profile` - Get user profile information
- `w_member_social` - Post content on behalf of user

**Documentation:**
- [LinkedIn OAuth 2.0](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Share on LinkedIn API](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [UGC Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api)

**Troubleshooting:**
- "401 Unauthorized" → Access token expired, generate new one
- "403 Forbidden" → Token missing `w_member_social` permission
- "429 Rate Limit" → Wait before retrying, implements exponential backoff

---

## Common Features

### Retry Logic

All publishers implement retry logic with exponential backoff:
- **Attempts:** 3 retries
- **Wait times:** 1s, 2s, 4s, 8s (exponential)
- **Retries on:** Rate limits, server errors, transient network issues
- **Logs:** Warning level before each retry

### Dry-Run Mode

All publishers support dry-run mode:
```python
result = publisher.publish(image_path, quote_data, dry_run=True)
```

In dry-run mode:
- Caption is generated and logged
- No actual API calls are made
- Returns success with `[DRY RUN - not published]` URL

### Error Handling

All publishers handle common errors:
- **FileNotFoundError:** Image file doesn't exist
- **ValueError:** Configuration or validation errors
- **Platform-specific exceptions:** API errors with helpful messages
- **Unexpected errors:** Logged with full stack trace

### Caption Generation

Captions are generated from templates with variable substitution:

**Available variables:**
- `{episode_number}` - Episode number
- `{title}` - Episode title
- `{quote}` - Selected quote
- `{guests}` - Comma-separated guest names
- `{date}` - Publication date
- `{youtube_url}` - Full YouTube URL
- `{youtube_id}` - YouTube video ID
- `{host}` - Host name
- `{hashtags}` - Generated hashtags

### Hashtag Generation

Hashtags are generated from:
1. Platform default hashtags (from config)
2. Episode-specific tags (from episode metadata)

Format: `#Tag` (spaces removed, # prefix added)

---

## Security Best Practices

1. **Never commit credentials to version control**
   - Use environment variables
   - Add `.env` to `.gitignore`

2. **Use read-only permissions where possible**
   - Twitter: Read and write permissions only
   - Facebook: `pages_manage_posts` only
   - LinkedIn: `w_member_social` only

3. **Rotate tokens regularly**
   - Set expiration reminders
   - Use short-lived tokens when possible

4. **Store session files securely**
   - Instagram session files contain sensitive data
   - Add to `.gitignore`
   - Set appropriate file permissions

5. **Monitor API usage**
   - Check for unusual activity
   - Set up rate limit alerts
   - Review published posts regularly

---

## Testing

### Unit Tests

Mock API calls to test:
- Authentication with valid/invalid credentials
- Caption generation and length validation
- Retry logic with simulated failures
- Error handling

### Integration Tests

Test with actual credentials:
- Image upload and post creation
- Dry-run mode
- Error recovery
- Post URL generation

### Manual Testing

Verify with real posts:
- Check image quality
- Verify caption formatting
- Test with various quote lengths
- Confirm hashtags appear correctly

---

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**"Invalid credentials" errors:**
- Check environment variables are set
- Verify credentials haven't expired
- Ensure correct credential type (e.g., Page Token for Facebook)

**"Permission denied" errors:**
- Check token permissions
- Verify app has required products enabled
- Review platform-specific permission requirements

**"Rate limit exceeded" errors:**
- Wait before retrying (automatic with retry logic)
- Reduce posting frequency
- Check if you're hitting daily/hourly limits

**"Image upload failed" errors:**
- Verify image file exists and is readable
- Check image format (PNG, JPEG supported)
- Ensure image size is within platform limits

---

## Future Enhancements

Potential improvements:
- Video support
- Carousel posts (multiple images)
- Scheduled posting
- Analytics integration
- Story/Reels support (Instagram)
- Thread support (Twitter)
- Company page support (LinkedIn)
