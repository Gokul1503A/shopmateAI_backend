from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from services.chat_handler import chat_handler_stream
import json
from services import crm_logger
from datetime import datetime

app = FastAPI()
chat_history = []

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message")
    user_id = data.get("user_id", "user")
    if not user_message:
        return {"error": "Message cannot be empty."}

    chat_history.append({"role": "user", "content": user_message})

    def event_stream():
        crm_logger.increment_visit(user_id)
        response_text = ""
        for chunk in chat_handler_stream(user_message, chat_history):
            data_json = json.loads(chunk)
            if "token" in data_json:
                response_text += data_json.get("token", "")
            if data_json.get("event") == "checkout_intent":
                crm_logger.log_transaction({
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "source": "ai",
                    "details": data_json.get("details", {})
                })
            # Pass through all event types including "event", "recommended", and "done"
            yield chunk.encode("utf-8")
        chat_history.append({"role": "assistant", "content": response_text})

    return StreamingResponse(event_stream(), media_type="text/event-stream")