# Complete User Guide: Shopify WhatsApp Multi-tenant System

## Table of Contents
1. [What This System Does](#what-this-system-does)
2. [How It Works (Simple Explanation)](#how-it-works-simple-explanation)
3. [Getting Started](#getting-started)
4. [User Interface Guide](#user-interface-guide)
5. [How Everything Works Together](#how-everything-works-together)
6. [Advanced Topics](#advanced-topics)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## What This System Does

### The Problem
You run a Shopify store and want to:
- Send WhatsApp messages to customers when they place orders
- Confirm order details before shipping
- Allow multiple business owners to use the same system
- See all orders in a dashboard
- Get real-time updates without refreshing

### The Solution
This system automatically:
1. **Receives** order notifications from Shopify
2. **Sends** WhatsApp messages to customers
3. **Tracks** order status in real-time
4. **Isolates** each user's data completely
5. **Updates** dashboard instantly when changes happen

### Who Is This For?
- **E-commerce store owners** using Shopify
- **SaaS companies** offering WhatsApp automation
- **Agencies** managing multiple clients
- **Businesses** wanting automated order confirmations

---

## How It Works (Simple Explanation)

### The Big Picture

```
┌──────────────────────────────────────────────────────────────┐
│                     YOUR SHOPIFY STORE                        │
│  Customer places order → Shopify creates order               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Sends webhook
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                    YOUR SERVER (This App)                     │
│  1. Receives order details                                   │
│  2. Saves to database                                        │
│  3. Updates dashboard (WebSocket)                            │
│  4. Schedules WhatsApp message                               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Sends message
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                  CUSTOMER'S WHATSAPP                          │
│  Receives: "Hi John, your order #1234 is confirmed!"        │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step Flow

**1. User Signs Up**
- You create an account with email/password
- System creates a unique user ID for you (e.g., User #5)
- You get your own isolated space

**2. User Links WhatsApp**
- Click "Connect WhatsApp" button
- Browser window opens showing QR code
- Scan with your phone
- WhatsApp session saved to `chrome_data/5/` (your unique folder)

**3. Customer Places Order**
- Customer buys something on your Shopify store
- Shopify sends notification to: `/webhooks/5/orders/create` (your unique URL)
- System knows this order belongs to YOU (User #5)

**4. Order Processed**
- Order saved to database with your user_id
- Dashboard updates instantly (you see it appear!)
- Background task scheduled to send WhatsApp message

**5. WhatsApp Message Sent**
- System loads YOUR WhatsApp session from `chrome_data/5/`
- Opens Chrome browser (invisible, in background)
- WhatsApp already logged in (from step 2!)
- Sends message to customer
- Updates order status to "confirmed"
- Dashboard shows status change instantly

---

## Getting Started

### Installation (For Developers/Server Admins)

#### Step 1: Install Requirements
```powershell
# Install Python 3.9 or higher
# Install MySQL Server
# Install Chrome browser

# Clone or download the project
cd path/to/project

# Create virtual environment (optional but recommended)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# Install Python packages
pip install -r requirements.txt
```

#### Step 2: Set Up Database
```sql
-- Open MySQL and run:
CREATE DATABASE shopify_whatsapp;
```

```powershell
# Initialize database tables
python reset_db.py
```

#### Step 3: Configure Settings
Edit `app/core/config.py`:
```python
# Database connection
DATABASE_URL = "mysql+pymysql://root:yourpassword@localhost:3306/shopify_whatsapp"

# Shopify webhook secret (get from Shopify admin)
SHOPIFY_WEBHOOK_SECRET = "your-secret-here"

# WhatsApp provider
WHATSAPP_PROVIDER = "selenium"  # Use browser automation
```

#### Step 4: Start Server
```powershell
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Application startup complete.
```

#### Step 5: Open Dashboard
Open browser: http://localhost:8000

---

## User Interface Guide

### 1. Login/Signup Screen

**First Time User:**
```
┌─────────────────────────────────┐
│          SIGN UP                │
│                                 │
│  Email: [your@email.com     ]  │
│  Password: [********        ]  │
│                                 │
│  [ Sign Up Button ]             │
│                                 │
│  Already have account? Login   │
└─────────────────────────────────┘
```

**Returning User:**
```
┌─────────────────────────────────┐
│          LOGIN                  │
│                                 │
│  Email: [your@email.com     ]  │
│  Password: [********        ]  │
│                                 │
│  [ Login Button ]               │
│                                 │
│  Need an account? Sign up      │
└─────────────────────────────────┘
```

After login, you're automatically taken to the dashboard.

### 2. Dashboard - Orders Tab

```
┌────────────────────────────────────────────────────────────┐
│  Shopify WhatsApp Dashboard              [ Logout ]        │
├────────────────────────────────────────────────────────────┤
│  [ Orders ]  [ Settings ]  [ Analytics ]                   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Recent Orders                                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Order #  │ Customer     │ Total  │ Status    │ Slot  │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │ #1234    │ John Doe     │ $99.99 │ confirmed │ -     │ │ ← Updates in real-time!
│  │ #1233    │ Jane Smith   │ $49.99 │ pending   │ -     │ │
│  │ #1232    │ Bob Johnson  │ $149.99│ delivered │ 2pm   │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

**Colors:**
- 🟡 Yellow badge = Pending
- 🟢 Green badge = Confirmed
- 🔴 Red badge = Cancelled
- 🔵 Blue badge = Delivered

**Real-time Updates:**
- New orders appear instantly at the top (no refresh needed!)
- Status changes update automatically (watch it change from yellow to green!)
- Rows briefly highlight when changed

### 3. Settings Tab

```
┌────────────────────────────────────────────────────────────┐
│  [ Orders ]  [ Settings ]  [ Analytics ]                   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Configuration                                              │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Webhook URL:                                         │ │
│  │ http://localhost:8000/api/v1/webhooks/5/orders/create│ │ ← Your unique URL!
│  │                                                       │ │
│  │ Confirmation Delay (minutes): [ 30 ]                 │ │
│  │                                                       │ │
│  │ [ Save Settings ]                                    │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                             │
│  WhatsApp Connection                                        │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ [ 📱 Connect WhatsApp ]                              │ │ ← Click to link!
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

**Important Notes:**
- **Webhook URL**: Copy this and paste into Shopify (see Shopify Setup section)
- **Connect WhatsApp**: Click once to link your WhatsApp account
- **Settings**: Save any changes before leaving this tab

### 4. Analytics Tab

```
┌────────────────────────────────────────────────────────────┐
│  [ Orders ]  [ Settings ]  [ Analytics ]                   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │Total Orders │  │Confirmation │  │Cancellation │        │
│  │     150     │  │    Rate     │  │    Rate     │        │
│  │             │  │   95.5%     │  │    3.2%     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────┐                                           │
│  │ Delivery    │                                           │
│  │  Success    │                                           │
│  │   98.1%     │                                           │
│  └─────────────┘                                           │
└────────────────────────────────────────────────────────────┘
```

---

## How Everything Works Together

### Architecture Explained (For Non-Technical Users)

Think of the system like a restaurant:

**1. The Waiter (Shopify)**
- Takes orders from customers
- Sends order details to the kitchen

**2. The Kitchen (Your Server)**
- Receives orders
- Stores them in the order book (database)
- Tells the messenger (WhatsApp bot)

**3. The Messenger (WhatsApp Bot)**
- Sends confirmation to customer
- Uses YOUR WhatsApp account
- Works automatically in the background

**4. The Display Board (Dashboard)**
- Shows all orders in real-time
- Updates automatically when orders change
- You can check it anytime

### Data Flow

```
Customer Order → Shopify → Webhook → Your Server → Database
                                           ↓
                                    WebSocket Update
                                           ↓
                                    Your Dashboard
                                           ↓
                                    Background Task
                                           ↓
                                    WhatsApp Message
                                           ↓
                                    Customer's Phone
```

### User Isolation (Multi-tenant)

**Why is this important?**
Imagine you're running a SaaS business. You have 3 clients:
- Coffee Shop A
- Clothing Store B
- Electronics Store C

**Without multi-tenant:**
❌ All orders mixed together
❌ Everyone uses the same WhatsApp
❌ Orders get confused

**With multi-tenant:**
✅ Coffee Shop sees only their orders
✅ Clothing Store has their own WhatsApp
✅ Complete isolation and privacy

**How it works:**
```
User 1 (Coffee Shop):
- Database: Only sees orders where user_id = 1
- WhatsApp: Uses chrome_data/1/ session
- Webhook: /webhooks/1/orders/create

User 2 (Clothing Store):
- Database: Only sees orders where user_id = 2
- WhatsApp: Uses chrome_data/2/ session
- Webhook: /webhooks/2/orders/create

User 3 (Electronics):
- Database: Only sees orders where user_id = 3
- WhatsApp: Uses chrome_data/3/ session
- Webhook: /webhooks/3/orders/create
```

**No way for data to mix!**

---

## Advanced Topics

### Authentication Deep Dive

**What is JWT?**
JSON Web Token - a secure way to verify who you are without storing passwords.

**How it works:**
1. You login with email/password
2. Server verifies password (hashed with Argon2)
3. Server creates a token: `eyJhbGc...` (contains your user_id)
4. Token stored in browser (localStorage)
5. Every request includes this token
6. Server decodes token → knows it's you!

**Example:**
```
Login Request:
→ POST /api/v1/auth/login
→ Body: { email: "you@email.com", password: "secret123" }

Response:
← { access_token: "eyJhbGc...", token_type: "bearer" }

Future Requests:
→ GET /api/v1/admin/orders
→ Header: Authorization: Bearer eyJhbGc...
```

### WhatsApp Session Storage

**What is stored?**
When you scan the QR code, WhatsApp Web saves:
- Cookies (session tokens)
- Local Storage (encryption keys)
- IndexedDB (message cache)
- Cache (images, media)

**Where is it stored?**
```
chrome_data/{your_user_id}/
├── Default/
│   ├── Cookies           ← Your login token
│   ├── Local Storage/    ← Encryption keys
│   ├── IndexedDB/        ← Messages, contacts
│   └── Cache/            ← Media files
├── Local State
└── First Run
```

**Size:** Typically 100-500 MB per user

**Security:**
- End-to-end encrypted (even locally!)
- Only accessible on this server
- Not synced to cloud
- Treat like a password (don't share!)

### Real-time Updates (WebSocket)

**Why not just refresh the page?**
- Refreshing is slow
- Misses updates between refreshes
- Uses more server resources

**How WebSocket works:**
```
Normal HTTP:
Browser: "Hey server, give me data" → Server: "Here's data"
[5 seconds later]
Browser: "Hey server, give me data again" → Server: "Here's data"
[Repeat forever]

WebSocket:
Browser: "Hi server, keep me updated" → Server: "Sure, connected!"
[Order arrives]
Server: "Hey browser! New order!" → Browser: "Thanks, updating UI!"
[No need to ask, server pushes updates]
```

**Connection Flow:**
```javascript
// Frontend connects
ws = new WebSocket('ws://localhost:8000/ws/orders');

ws.onopen = () => console.log("Connected!");
ws.onmessage = (event) => {
    // New order or status update!
    updateUI(JSON.parse(event.data));
};
```

---

## Troubleshooting

### Common Issues

#### 1. "Can't login" / "Invalid credentials"
**Causes:**
- Wrong email/password
- User doesn't exist
- Server not running

**Solutions:**
```powershell
# Check if server is running
# Should see: "Uvicorn running on http://127.0.0.1:8000"

# Try signing up again
# Make sure you're using the correct email

# Reset password (not implemented yet - recreate account)
```

#### 2. "WhatsApp session expired"
**Causes:**
- Logged out on phone
- Session data deleted
- Phone disconnected

**Solutions:**
```powershell
# Re-link WhatsApp
1. Dashboard → Settings
2. Click "Connect WhatsApp"
3. Scan QR code again
4. Session saved!
```

#### 3. "Orders not appearing"
**Causes:**
- Wrong webhook URL in Shopify
- HMAC verification failing
- Database connection issue

**Solutions:**
```powershell
# Check webhook URL
Dashboard → Settings → Copy exact URL
Shopify → Webhooks → Verify URL matches

# Check server logs
Look for errors about HMAC or database

# Verify database running
mysql -u root -p
USE shopify_whatsapp;
SHOW TABLES;  # Should see: users, orders, etc.
```

#### 4. "Real-time updates not working"
**Causes:**
- WebSocket disconnected
- Browser blocking WebSocket
- Server restarted

**Solutions:**
```powershell
# Check browser console
F12 → Console tab
Look for: "Connected to WebSocket"

# If disconnected
Refresh page (auto-reconnects)

# Check firewall
Make sure port 8000 is not blocked
```

---

## FAQ

### General Questions

**Q: Can I use this for free?**
A: Yes, the code is yours. You only pay for server hosting and WhatsApp API (if using official).

**Q: How many users can I have?**
A: Unlimited! Each user is completely isolated.

**Q: Is my data secure?**
A: Yes:
- Passwords hashed with Argon2
- JWT authentication
- User data isolated in database
- HTTPS recommended for production

**Q: Can I customize messages?**
A: Yes, edit the message template in `app/worker/tasks.py`:
```python
message = f"Hello {order.customer_name}, your order {order.order_number} of {order.currency} {order.total_price} is confirmed!"
```

### WhatsApp Questions

**Q: Why use Selenium instead of Official API?**
A: 
- **Selenium**: Free, use personal WhatsApp, no approval needed
- **Official API**: Costs money, requires business approval, more features

**Q: Will my WhatsApp get banned?**
A: ⚠️ Using Selenium (browser automation) violates WhatsApp ToS. Risk of ban exists. Use for testing only. For production, use Official API.

**Q: Can I use the same WhatsApp for multiple users?**
A: No! Each user MUST use their own WhatsApp account. That's the point of multi-tenant isolation.

**Q: WhatsApp session keeps expiring?**
A: This happens if:
- You logout on your phone
- WhatsApp detects automation
- Session older than 30 days
Solution: Re-link from dashboard.

### Technical Questions

**Q: What database do I need?**
A: MySQL is recommended. PostgreSQL also works (change `DATABASE_URL`).

**Q: Do I need Redis?**
A: Not for local testing. For production with multiple workers, yes.

**Q: How do I deploy to production?**
A: See "Production Deployment" section in walkthrough.md

**Q: Can I add more features?**
A: Absolutely! The code is modular. Common additions:
- Email notifications
- SMS integration
- Order tracking
- Customer portal

### Shopify Questions

**Q: How do I set up Shopify webhook?**
A: 
1. Login to Shopify Admin
2. Settings → Notifications → Webhooks
3. Create webhook
4. Event: "Order creation"
5. URL: Your webhook URL from dashboard
6. Format: JSON
7. Save

**Q: How do I get webhook secret?**
A: Shopify shows it after creating webhook. Copy and paste into `config.py`.

**Q: Can I test without Shopify?**
A: Yes! Use `trigger_order.py`:
```powershell
python trigger_order.py
```

---

## Summary

### What You've Learned

✅ **Multi-tenant System**: Each user isolated, separate WhatsApp sessions  
✅ **Authentication**: Signup, Login, JWT tokens  
✅ **WhatsApp Integration**: Selenium automation, session persistence  
✅ **Real-time Dashboard**: WebSocket updates, no refresh needed  
✅ **Shopify Integration**: Webhooks, HMAC verification  

### Quick Start Checklist

- [ ] Install Python, MySQL, Chrome
- [ ] Run `pip install -r requirements.txt`
- [ ] Create database: `shopify_whatsapp`
- [ ] Run `python reset_db.py`
- [ ] Configure `app/core/config.py`
- [ ] Start server: `uvicorn app.main:app --reload`
- [ ] Open http://localhost:8000
- [ ] Sign up for account
- [ ] Connect WhatsApp (scan QR)
- [ ] Configure Shopify webhook
- [ ] Test with `python trigger_order.py`
- [ ] 🎉 You're ready!

### Getting Help

**Documentation:**
- `walkthrough.md` - Technical details
- `WHATSAPP_SESSION_GUIDE.md` - WhatsApp storage explained
- `USER_FLOW_DIAGRAM.md` - How users are tracked
- `SHOPIFY_SETUP_GUIDE.txt` - Shopify configuration

**Support:**
- Check server logs for errors
- Review troubleshooting section above
- Read code comments in source files
