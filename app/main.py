from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.api.v1.endpoints import webhooks
from app.core.config import settings
from app.db.database import engine, Base
from app.services.websocket import manager

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(webhooks.router, prefix=f"{settings.API_V1_STR}/webhooks", tags=["webhooks"])
from app.api.v1.endpoints import whatsapp_webhook, admin
app.include_router(whatsapp_webhook.router, prefix=f"{settings.API_V1_STR}/webhooks", tags=["whatsapp"])
app.include_router(admin.router, prefix=f"{settings.API_V1_STR}/admin", tags=["admin"])

@app.websocket("/ws/orders")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
def read_root():
    return FileResponse('static/index.html')
