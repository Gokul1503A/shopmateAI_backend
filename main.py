from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from services.chat_handler import chat_handler_stream
import json

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
    if not user_message:
        return {"error": "Message cannot be empty."}

    chat_history.append({"role": "user", "content": user_message})

    def event_stream():
        response_text = ""
        for chunk in chat_handler_stream(user_message, chat_history):
            response_text += chunk
            data_json = json.dumps({"token": chunk})
            yield f"{data_json}\n".encode("utf-8")
        chat_history.append({"role": "assistant", "content": response_text})

    return StreamingResponse(event_stream(), media_type="text/event-stream")