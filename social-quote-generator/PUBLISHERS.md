# Social Media Publishers Guide

This document provides information about the implemented social media publishers and how to configure them.

## Supported Platforms

- **Twitter/X** - Fully implemented and tested
- **Instagram** - Implemented with session caching
- **Facebook** - Implemented for Facebook Pages
- **LinkedIn** - Implemented with OAuth 2.0

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

**Troubleshooting:**
- If you get "Challenge Required", verify your account through the Instagram app first
- If you get "2FA Required", use an app-specific password or disable 2FA temporarily
- Session files help avoid repeated login attempts

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

**Getting a Page Access Token:**
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app or use existing app
3. Add "Facebook Login" product
4. Generate a User Access Token with `pages_manage_posts` permission
5. Exchange it for a Page Access Token using Graph API Explorer
6. Use the Page Access Token in configuration

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

**Getting a LinkedIn Access Token:**
1. Create a LinkedIn App at [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Add "Share on LinkedIn" product
3. Request `w_member_social` permission
4. Use OAuth 2.0 flow to get access token
5. Note: Access tokens expire (typically 60 days)

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
