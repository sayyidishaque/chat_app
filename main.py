from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI()

# Store active WebSocket connections
active_connections = []

# WebSocket endpoint
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Receive message from the client
            data = await websocket.receive_text()
            # Broadcast the message to all connected clients except the sender
            for connection in active_connections:
                if connection != websocket:  # Exclude the sender
                    await connection.send_text(f"Client {client_id}: {data}")
    except WebSocketDisconnect:
        # Remove the connection when the client disconnects
        active_connections.remove(websocket)
        await broadcast_message(f"Client {client_id} left the chat", websocket)

# Helper function to broadcast messages
async def broadcast_message(message: str, exclude_websocket: WebSocket = None):
    for connection in active_connections:
        if connection != exclude_websocket:  # Exclude the specified WebSocket
            await connection.send_text(message)

# Serve a simple HTML page for testing
@app.get("/")
async def get():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())