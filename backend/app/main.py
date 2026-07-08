import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.agent import process_message
from app.schemas import InteractionCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="HCP CRM - AI Interaction Logger", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "HCP CRM Agent"}


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    conversation_id = None

    while True:
        try:
            data = await websocket.receive_text()
            payload = json.loads(data)
            message = payload.get("message", "")
            cid = payload.get("conversation_id", conversation_id)

            reply, interaction, conversation_id = process_message(message, cid)

            response = {
                "reply": reply,
                "interaction": interaction,
                "conversation_id": conversation_id,
                "tool_called": "detected_automatically",
            }

            await websocket.send_text(json.dumps(response))

        except WebSocketDisconnect:
            break
        except Exception as e:
            await websocket.send_text(json.dumps({"error": str(e)}))
