from app.core.security import create_access_token
from app.api.v1.endpoints.auth import get_current_user
from app.db.database import SessionLocal
from fastapi import HTTPException

db = SessionLocal()
token = create_access_token(data={"sub": "1"})
print(f"Token: {token}")

try:
    user = get_current_user(token=token, db=db)
    print(f"User: {user.email}")
except HTTPException as e:
    print(f"HTTPException: {e.detail}")
except Exception as e:
    print(f"Exception: {e}")
finally:
    db.close()
