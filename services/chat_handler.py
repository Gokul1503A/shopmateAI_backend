from llama_cpp import Llama
import json
import os
from services.productfilter import filter_products
import re
import logging
from datetime import datetime

# Load the llama model
llama = Llama(model_path="models/Llama-3.2-3B-Instruct-IQ3_M.gguf", n_ctx=2048, n_batch=512)

# Load products data
with open(os.path.join("data", "items.json"), "r") as f:
    products = json.load(f)

def chat_handler(user_message: str, chat_history: list) -> dict:
    # Use filter_products from product_filter.py to get recommended products
    recommended_products = filter_products(user_message)

    # Format recommended products for prompt readability
    def format_product(p):
        return f"- {p.get('name', 'Unknown')} ({p.get('category', 'No category')}): ${p.get('price', 'N/A')}"
    if recommended_products:
        products_str = "\n".join([format_product(p) for p in recommended_products])
    else:
        products_str = "No matching products found in the catalog."

    # Prepare prompt with chat history and user message, using user/assistant roles consistently
    prompt = (
        "You are a helpful fashion shopkeeper named Laila, 23 F. "
        "Respond politely, include only real products from the catalog below:\n"
        f"{products_str}\n\n"
    )
    for turn in chat_history:
        role = turn.get("role", "user")
        if role not in ("user", "assistant"):
            role = "user"
        prompt += f"{role}: {turn['content']}\n"
    prompt += f"user: {user_message}\nassistant:"

    # Generate reply using llama with low temperature for deterministic output, handle errors
    try:
        response = llama(prompt=prompt, max_tokens=256, temperature=0.1, stop=["user:", "assistant:"])
        reply = response.get("choices", [{}])[0].get("text", "").strip()
    except Exception as e:
        reply = "Sorry, there was an error processing your request. Please try again later."
    
    clean_text = re.sub(r"\([^)]*\)", "", reply)
    clean_text = re.sub(r"\*.*?\*", "", clean_text).strip()

    return {
        "reply": clean_text,
        "recommended_products": recommended_products
    }

def chat_handler_stream(user_message: str, chat_history: list):
    user_id = "user"

    # Use filter_products from product_filter.py to get recommended products
    recommended_products = filter_products(user_message)

    # Format recommended products for prompt readability
    def format_product(p):
        return f"- {p.get('name', 'Unknown')} ({p.get('category', 'No category')}): ${p.get('price', 'N/A')}"
    if recommended_products:
        products_str = "\n".join([format_product(p) for p in recommended_products])
    else:
        products_str = "No matching products found in the catalog."

    # Prepare prompt with chat history and user message, using user/assistant roles consistently
    prompt = (
        "You are a helpful fashion shopkeeper named Laila, 23 F. "
        "Respond naturally and politely to the customer. "
        "ONLY recommend products from the catalog below when the customer is asking to see or explore items. "
        "If they are just greeting, saying thanks, checking out, or not asking for products, do not recommend anything.\n\n"
        f"{products_str}\n\n"
        "you need not recommend products if the user is not asking for them.\n\n"
        "If the user asks for products, recommend them in a friendly way, like 'Here are some options for you:'.\n\n"
        "no need to reply your actoins to the user, just reply but not your actions.\n\n"
        "after purchase you should also ask customer if they want anything matching to the product they wanted"
    )
    for turn in chat_history:
        role = turn.get("role", "user")
        if role not in ("user", "assistant"):
            role = "user"
        prompt += f"{role}: {turn['content']}\n"
    prompt += f"user: {user_message}\nassistant:"

    full_reply = ""
    try:
        response_stream = llama.create_completion(
            prompt=prompt,
            max_tokens=256,
            temperature=0.1,
            stop=["user:", "assistant:"],
            stream=True
        )
        for chunk in response_stream:
            token = chunk.get("choices", [{}])[0].get("text", "")
            if token:
                full_reply += token
                yield json.dumps({"token": token}) + "\n"
        # After streaming completes, check if any recommended product name appears in full_reply
        product_names = [p.get("name", "").lower() for p in recommended_products]
        full_reply_lower = full_reply.lower()
        if any(name and name in full_reply_lower for name in product_names):
            if not recommended_products:
                logging.warning("LLM recommended products but recommended_products list is empty.")
            for p in recommended_products:
                name = p.get("name", "Unknown")
                price = p.get("price", "N/A")
                image_url = p.get("image_url", "")
                yield json.dumps({"recommended": {
                    "name": name,
                    "price": price,
                    "image_url": image_url
                }}) + "\n"
        # Signal done at the end of the stream
        yield json.dumps({"done": True}) + "\n"
    except Exception:
        yield "Sorry, there was an error processing your request. Please try again later."

if __name__ == "__main__":
    # Example usage
    user_message = "I need a red dress"
    chat_history = []
    print("Streaming response:")
    for token in chat_handler_stream(user_message, chat_history):
        print(token, end='', flush=True)
    print()