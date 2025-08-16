from fastapi import FastAPI, Request
from services.chat_handler import chat_handler

chat_history = []

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_message = data.get("message")
    if not user_message:
        return {"error": "Message cannot be empty."}
    response = chat_handler(user_message, chat_history)
    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": response["reply"]})
    if len(chat_history) > 10:
        chat_history.pop(0)
    return {"reply": response["reply"]}

# to run this app with uvicorn:
# uvicorn main:app --reload