from llama_cpp import Llama
import json
import os
from services.productfilter import filter_products
import re

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
if __name__ == "__main__":
    # Example usage
    user_message = "I need a red dress"
    chat_history = []
    response = chat_handler(user_message, chat_history)
    print("Response:", response["reply"])
    