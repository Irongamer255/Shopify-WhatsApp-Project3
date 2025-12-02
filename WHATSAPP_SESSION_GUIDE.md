# WhatsApp Session Data Storage Guide

## Overview
WhatsApp session data is saved using Chrome's **user data directory** feature. This allows the browser to remember your login between restarts, so you don't have to scan the QR code every time.

## Storage Location

### Directory Structure
```
c:\Users\m\.gemini\antigravity\playground\resonant-radiation\
└── chrome_data/           # Main WhatsApp data directory
    ├── Default/           # Your existing session (from before multi-tenant)
    ├── 1/                 # User ID 1's WhatsApp session (will be created when they link)
    ├── 2/                 # User ID 2's WhatsApp session
    └── 3/                 # User ID 3's WhatsApp session
```

### Current State
Right now, you have a `chrome_data/` folder with 529 items, which is a **complete Chrome browser profile** from your previous WhatsApp linking (before multi-tenant).

## How It Works

### 1. Code Configuration
In `app/services/whatsapp_browser.py` (lines 24-28):

```python
# Persist user data to keep login session
current_dir = os.getcwd()
# Use user-specific directory
user_data_dir = os.path.join(current_dir, "chrome_data", str(user_id))
self.options.add_argument(f"--user-data-dir={user_data_dir}")
```

**What this does:**
- Creates a path like: `chrome_data/1/` for user ID 1
- Tells Chrome: "Store all your data in THIS specific folder"
- When Chrome closes and reopens, it loads data from the same folder

### 2. What Gets Saved

Inside each `chrome_data/{user_id}/` folder:

| Folder/File | What It Contains |
|-------------|------------------|
| **Default/** | Main browser profile with cookies, local storage, cache |
| **Local State** | Browser settings and preferences |
| **Cookies** | WhatsApp Web cookies (keeps you logged in) |
| **Local Storage** | WhatsApp Web's data (messages, contacts, etc.) |
| **IndexedDB** | WhatsApp's encrypted message database |
| **Session Storage** | Temporary session data |
| **Cache** | Cached images, scripts, assets |

### 3. WhatsApp Web Authentication

When you scan the QR code:
1. **Chrome opens** to `web.whatsapp.com`
2. **You scan QR** with your phone
3. **WhatsApp Web** saves authentication data to:
   - Cookies (session tokens)
   - Local Storage (encryption keys)
   - IndexedDB (message data)
4. **Chrome closes** and saves everything to `chrome_data/{user_id}/`

Next time the same user sends a message:
1. Selenium opens Chrome with `--user-data-dir=chrome_data/{user_id}/`
2. Chrome loads saved cookies and session
3. WhatsApp Web recognizes the session → **No QR scan needed!**
4. Message sent successfully

## Multi-tenant Isolation

### Old System (Single User)
```
chrome_data/
└── Default/  # Everyone shared this
```
❌ Problem: All users would share the same WhatsApp account

### New System (Multi-tenant)
```
chrome_data/
├── 1/  # User 1's session
├── 2/  # User 2's session
└── 3/  # User 3's session
```
✅ Solution: Each user has their own isolated WhatsApp session

## Session Lifecycle

### First Time (Linking)
1. User clicks "Connect WhatsApp" in dashboard
2. Backend calls: `SeleniumWhatsApp(user_id=5, headless=False)`
3. Browser opens: `chrome_data/5/` is created
4. User scans QR code
5. WhatsApp session saved to `chrome_data/5/`
6. Browser closes

### Subsequent Messages
1. Customer places order (webhook triggered)
2. Worker task runs: `SeleniumWhatsApp(user_id=5, headless=True)`
3. Browser opens in background using `chrome_data/5/`
4. WhatsApp already logged in (from saved session)
5. Message sent
6. Browser closes

## Data Persistence

### What Happens When...

**User deletes `chrome_data/{user_id}/`?**
- Session is lost
- User must scan QR code again
- No impact on other users

**Server restarts?**
- All sessions remain saved on disk
- No re-authentication needed

**User changes phone?**
- Old session becomes invalid
- User must scan QR again with new phone
- Old data automatically overwritten

**Multiple users try to use same WhatsApp?**
- Impossible! Each user_id has separate directory
- User 1 can't access User 2's session

## File Size

A typical WhatsApp session takes:
- **100-500 MB** per user (includes cache, images, etc.)
- Grows over time as messages are cached
- Can be cleaned by deleting the directory

## Security Considerations

### What's Stored
✅ **Encrypted**: WhatsApp messages (end-to-end encrypted even in local storage)
✅ **Session Tokens**: Cookies that expire after inactivity
✅ **No Passwords**: WhatsApp doesn't store password in session

### Risks
⚠️ **Physical Access**: Someone with access to `chrome_data/{user_id}/` can impersonate that user
⚠️ **Backups**: Don't include `chrome_data/` in public backups

### Recommendations
- Add `chrome_data/` to `.gitignore` (already done)
- Restrict file permissions on production server
- Regular cleanup of inactive sessions
- Encrypt disk in production

## Cleanup

### Manual Cleanup
```bash
# Delete specific user's session
rm -rf chrome_data/5/

# Delete all sessions
rm -rf chrome_data/*/
```

### Automated Cleanup (Future Enhancement)
Add a cleanup script that deletes sessions older than 30 days of inactivity.

## Troubleshooting

### "Session expired" or "Scan QR again"
**Cause**: Session data corrupted or WhatsApp logged out remotely  
**Fix**: Delete `chrome_data/{user_id}/` and re-link

### "Phone not connected"
**Cause**: User's phone is offline  
**Fix**: User must turn on phone and connect to internet

### Messages not sending
**Cause**: Session might be invalid  
**Fix**: Check if `chrome_data/{user_id}/` exists, re-link if needed

## Summary

**Where**: `chrome_data/{user_id}/` in your project directory  
**What**: Complete Chrome profile with WhatsApp Web session  
**Why**: Avoid scanning QR code repeatedly  
**How**: Selenium's `--user-data-dir` parameter  
**Size**: ~200-500 MB per user  
**Security**: Treat like password (don't share, don't commit to git)
