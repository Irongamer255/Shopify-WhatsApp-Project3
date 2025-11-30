# Project Walkthrough: Shopify + WhatsApp Integration

## Overview
Complete Shopify + WhatsApp Order Confirmation system with **dual WhatsApp providers** (Official API + Selenium automation) and **real-time dashboard updates**.

## Key Features
- **FastAPI Backend**: Robust API with SQLAlchemy ORM
- **MySQL Database**: Persistent storage for orders, configs, and logs
- **Vanilla JS Frontend**: Lightweight dashboard with Bootstrap
- **Shopify Webhook**: Real-time order capture with HMAC verification
- **WhatsApp Integration**: 
  - **Official Cloud API**: Template messages and interactive buttons
  - **Selenium Automation**: Browser-based automation for personal accounts
- **Real-time Updates**: WebSocket-powered dashboard with live order and status updates
- **Security**: HMAC verification, idempotency checks
- **In-App Linking**: Connect WhatsApp directly from the dashboard

## Project Structure
```
/app                  # Backend Logic
  /api/v1/endpoints   # API routes
  /core               # Configuration
  /db                 # Database models
  /services           # WhatsApp, Shopify, Selenium services
  /worker             # Celery background tasks
  main.py             # FastAPI application
/static               # Frontend Assets
  /css, /js
  index.html          # Dashboard UI
/tests                # Test Suite
requirements.txt
trigger_order.py      # Test order script
init_whatsapp_session.py  # QR code scanner (deprecated - use dashboard)
chrome_data/          # Selenium session storage
```

## Setup Guide

### 1. Prerequisites
- Python 3.9+
- MySQL Server
- Chrome/Chromium browser (for Selenium)

### 2. Database Setup
```sql
CREATE DATABASE shopify_whatsapp;
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configuration
Edit `app/core/config.py`:
- Update MySQL credentials if needed
- Set `SHOPIFY_WEBHOOK_SECRET`
- For Official API: Set `WHATSAPP_API_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID`
- For Selenium: Set `WHATSAPP_PROVIDER = "selenium"`

### 5. Run Server
```powershell
uvicorn app.main:app --reload
```

### 6. Access Dashboard
- **Dashboard**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## WhatsApp Provider Configuration

### Option 1: Official WhatsApp Cloud API
1. Set `WHATSAPP_PROVIDER = "official"` in `config.py`
2. Configure API token and phone number ID
3. Restart server

### Option 2: Selenium Automation
1. Go to **Dashboard → Settings**
2. Click **"Connect WhatsApp"** button
3. Scan QR code in the browser window
4. Set `WHATSAPP_PROVIDER = "selenium"` in `config.py`
5. Restart server
6. Messages now sent via headless browser

## Testing

### Manual Testing
1. Use `trigger_order.py` to simulate Shopify webhooks
2. Check dashboard for real-time order updates
3. Watch status change from "pending" to "confirmed" automatically
4. Verify WebSocket connection status
5. Monitor server logs for Selenium activity

### Automated Tests
```powershell
pytest
```

## Features Implemented

### ✅ Core Functionality
- Shopify webhook listener
- HMAC signature verification
- Duplicate order prevention (idempotency)
- Async background processing

### ✅ WhatsApp Integration
- Dual provider support (Official + Selenium)
- In-app device linking
- Session persistence
- Headless browser automation

### ✅ Dashboard
- Real-time order table (WebSocket)
- **Real-time status updates** (NEW)
- Analytics cards
- Settings management
- One-click WhatsApp connection

### ✅ Security & Reliability
- HMAC verification
- Idempotency checks
- MySQL transaction safety
- Error logging

## How Real-time Updates Work

### New Orders
When a new order arrives via Shopify webhook:
1. Order saved to database
2. WebSocket broadcasts `new_order` event
3. Dashboard prepends order to table
4. Row highlights briefly in blue

### Status Changes
When order status changes (e.g., confirmed):
1. Worker task updates database
2. WebSocket broadcasts `status_update` event
3. Dashboard finds the order row
4. Status badge updates (color + text)
5. Row highlights briefly in green

## Verification Results

**System Status**: ✅ Fully Operational

- **Server**: Running on http://127.0.0.1:8000
- **Database**: Connected to MySQL `shopify_whatsapp`
- **WebSocket**: Active for real-time updates
- **Selenium Session**: Saved to `chrome_data/`
- **Provider**: Configured for Selenium automation
- **Status Updates**: Working in real-time

## Next Steps

1. **Production Deployment**:
   - Set up proper environment variables
   - Configure Celery with Redis for production
   - Set up proper logging and monitoring

2. **WhatsApp Templates**:
   - Create approved message templates
   - Test with real phone numbers

3. **Shopify Integration**:
   - Register webhook URL with Shopify
   - Configure webhook secret

## Notes

⚠️ **Selenium Risk**: Browser automation may violate WhatsApp ToS. Use for testing only.

✅ **Session Persistence**: WhatsApp session stored in `chrome_data/` - no need to scan again.

🔄 **Real-time Updates**: Dashboard updates automatically via WebSocket when new orders arrive or status changes.

🎨 **Status Colors**:
- **Yellow (pending)**: Order awaiting confirmation
- **Green (confirmed)**: Order confirmed
- **Red (cancelled)**: Order cancelled
- **Blue (delivered)**: Order delivered
