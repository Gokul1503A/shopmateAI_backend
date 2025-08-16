

import json
import os
import re

def filter_products(user_message: str):
    """
    Filters products from shop_items.json based on keywords in user_message.
    Matches are performed against 'tags', 'name', and 'category'.
    Returns up to 5 matching products.
    """
    # Load the product data
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'items.json')
    with open(data_path, 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Extract keywords from user_message (simple split on non-word chars, lowercase)
    keywords = set(
        word.lower()
        for word in re.findall(r'\w+', user_message)
        if len(word) > 1
    )

    def matches(product):
        # Check name
        name = product.get('name', '').lower()
        category = product.get('category', '').lower()
        tags = [tag.lower() for tag in product.get('tags', [])]
        # Check if any keyword is in name, category, or tags
        for kw in keywords:
            if kw in name or kw in category or any(kw in tag for tag in tags):
                return True
        return False

    # Filter products, return up to 5 matches
    filtered = [prod for prod in products if matches(prod)]
    return filtered[:5]

if __name__ == "__main__":
    # Example usage
    user_message = "I need a red dress"
    matching_products = filter_products(user_message)
    print("Matching products:", matching_products)  