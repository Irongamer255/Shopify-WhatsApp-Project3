import asyncio
import websockets
import json

async def listen():
    uri = "ws://127.0.0.1:8000/ws/orders"
    print(f"Connecting to {uri}...", flush=True)
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected! Waiting for messages...", flush=True)
            while True:
                message = await websocket.recv()
                print(f"Received: {message}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(listen())
