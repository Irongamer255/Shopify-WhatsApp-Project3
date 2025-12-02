# How The System Knows Which User & WhatsApp Session to Load

## The Complete Flow

### Scenario 1: User Links WhatsApp (First Time)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER CLICKS "CONNECT WHATSAPP" IN DASHBOARD                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND SENDS REQUEST                                        │
│    POST /api/v1/admin/whatsapp/link                             │
│    Headers: Authorization: Bearer eyJhbGc...  (JWT token)       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. BACKEND EXTRACTS USER FROM JWT                               │
│    get_current_user(token) → decodes JWT → user_id = 5         │
│    File: app/api/v1/endpoints/auth.py                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. BACKEND CREATES SELENIUM WITH USER_ID                        │
│    bot = SeleniumWhatsApp(user_id=5, headless=False)           │
│    File: app/api/v1/endpoints/admin.py                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. SELENIUM CONFIGURES CHROME SESSION                           │
│    user_data_dir = "chrome_data/5/"  ← USER 5's FOLDER         │
│    File: app/services/whatsapp_browser.py                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. CHROME OPENS & USER SCANS QR                                 │
│    WhatsApp session saved to chrome_data/5/                     │
└─────────────────────────────────────────────────────────────────┘
```

### Scenario 2: Shopify Order Arrives (Sending Message)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. SHOPIFY SENDS WEBHOOK                                         │
│    POST /api/v1/webhooks/5/orders/create  ← USER_ID IN URL!    │
│    Body: { order_number: "#1234", customer_phone: "+1..." }    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. WEBHOOK HANDLER EXTRACTS USER_ID FROM URL                    │
│    @router.post("/{user_id}/orders/create")                    │
│    def handle_order_create(user_id: int, ...)                  │
│    user_id = 5  ← From URL path parameter!                     │
│    File: app/api/v1/endpoints/webhooks.py                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. CREATE ORDER WITH USER_ID                                    │
│    order = Order(                                               │
│        user_id = 5,  ← Linked to User 5!                       │
│        order_number = "#1234",                                  │
│        customer_phone = "+1234567890"                           │
│    )                                                             │
│    db.add(order)  → Saved to database                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. TRIGGER BACKGROUND TASK                                      │
│    send_order_confirmation.apply_async(                         │
│        args=[order.id]  ← Only pass ORDER ID                   │
│    )                                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. WORKER LOADS ORDER FROM DATABASE                             │
│    order = db.query(Order).filter(Order.id == order_id).first()│
│    order.user_id = 5  ← Retrieved from database!               │
│    File: app/worker/tasks.py                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. WORKER CREATES SELENIUM WITH ORDER'S USER_ID                 │
│    bot = SeleniumWhatsApp(                                      │
│        user_id=order.user_id,  ← USER 5!                       │
│        headless=True                                            │
│    )                                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. SELENIUM LOADS CORRECT SESSION                               │
│    user_data_dir = "chrome_data/5/"  ← USER 5's SESSION!       │
│    Chrome loads saved cookies, local storage, etc.             │
│    WhatsApp Web: "Hey, I know this session!" ✓                 │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. MESSAGE SENT VIA USER 5's WHATSAPP                           │
│    bot.send_message(customer_phone, message)                   │
│    Message sent from User 5's WhatsApp account!                │
└─────────────────────────────────────────────────────────────────┘
```

## Key Code Sections

### 1. Webhook Handler (webhooks.py)
```python
@router.post("/{user_id}/orders/create")  # ← user_id from URL path
async def handle_order_create(
    user_id: int,  # ← FastAPI automatically extracts this!
    request: Request,
    db: Session = Depends(get_db)
):
    # Create order linked to this user
    new_order = Order(
        user_id=user.id,  # ← Saved to database
        shopify_order_id=shopify_order_id,
        customer_phone=customer_phone,
        # ...
    )
    db.add(new_order)
    db.commit()
```

**How it knows**: User ID is **in the webhook URL** that Shopify calls!

### 2. Worker Task (tasks.py)
```python
@celery_app.task(bind=True)
def send_order_confirmation(self, order_id: int):
    db = SessionLocal()
    
    # Load the order from database
    order = db.query(Order).filter(Order.id == order_id).first()
    
    # Get user_id from the order
    user_id = order.user_id  # ← Retrieved from database!
    
    # Create Selenium with the correct user_id
    bot = SeleniumWhatsApp(user_id=user_id, headless=True)
    bot.start()
    bot.send_message(order.customer_phone, message)
```

**How it knows**: Order has `user_id` stored in database!

### 3. Admin Endpoint (admin.py)
```python
@router.post("/whatsapp/link")
def link_whatsapp_device(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)  # ← From JWT!
):
    def run_linking():
        bot = SeleniumWhatsApp(
            user_id=current_user.id,  # ← From authenticated user!
            headless=False
        )
        bot.link_device()
    
    background_tasks.add_task(run_linking)
```

**How it knows**: JWT token decoded to get `current_user.id`!

### 4. Selenium Service (whatsapp_browser.py)
```python
class SeleniumWhatsApp:
    def __init__(self, user_id: int, headless=True):
        # Create user-specific directory path
        current_dir = os.getcwd()
        user_data_dir = os.path.join(current_dir, "chrome_data", str(user_id))
        # ↑ If user_id=5, this becomes "chrome_data/5/"
        
        # Tell Chrome to use this directory
        self.options.add_argument(f"--user-data-dir={user_data_dir}")
        # ↑ Chrome will load/save everything from chrome_data/5/
```

**How it knows**: User ID passed as parameter, used to build folder path!

## The Magic: URL Path Parameter

The key insight is the webhook URL structure:

```
User 1: /api/v1/webhooks/1/orders/create
User 2: /api/v1/webhooks/2/orders/create
User 5: /api/v1/webhooks/5/orders/create
```

**Each user gets their own unique webhook URL!**

When they configure Shopify, they use **their specific URL**, so:
- User 1's Shopify → calls `/webhooks/1/...` → orders linked to User 1
- User 2's Shopify → calls `/webhooks/2/...` → orders linked to User 2

## Multi-user Example

```
┌──────────────────────────────────────────────────────────────────┐
│ COMPANY A (User ID: 1)                                            │
│ - Shopify webhook: /webhooks/1/orders/create                     │
│ - WhatsApp session: chrome_data/1/                               │
│ - WhatsApp number: +1-555-0001                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ COMPANY B (User ID: 2)                                            │
│ - Shopify webhook: /webhooks/2/orders/create                     │
│ - WhatsApp session: chrome_data/2/                               │
│ - WhatsApp number: +1-555-0002                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ COMPANY C (User ID: 3)                                            │
│ - Shopify webhook: /webhooks/3/orders/create                     │
│ - WhatsApp session: chrome_data/3/                               │
│ - WhatsApp number: +1-555-0003                                   │
└──────────────────────────────────────────────────────────────────┘
```

**Complete isolation!** Each company has:
- Their own Shopify webhook URL
- Their own WhatsApp session
- Their own order database records

## Summary

**The system knows which user through a chain of identifiers:**

1. **Webhook URL** contains `user_id` → Order created with `user_id`
2. **Order** stored in DB with `user_id` → Worker retrieves it
3. **Worker** uses `order.user_id` → Selenium gets user_id
4. **Selenium** uses `user_id` → Loads `chrome_data/{user_id}/`
5. **Chrome** loads session → WhatsApp recognizes login ✓

**No confusion possible!** Each step passes the user_id along like a relay race. 🏃‍♂️→🏃‍♀️→🏃‍♂️
