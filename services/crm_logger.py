_db = {
    "logs": [],
    "visit_count": {},
    "transaction_id_counter": 0,
    "addresses": {}
}

def increment_visit(user_id: str):
    if user_id in _db["visit_count"]:
        _db["visit_count"][user_id] += 1
    else:
        _db["visit_count"][user_id] = 1

def get_visit_count(user_id: str):
    return _db["visit_count"].get(user_id, 0)

def log_transaction(user_id, transaction):
    _db["transaction_id_counter"] += 1
    transaction_id = _db["transaction_id_counter"]
    products = transaction.get("products", [])
    enriched_products = []
    for idx, product in enumerate(products):
        if "id" not in product:
            product = product.copy()
            product["id"] = idx + 1
        enriched_products.append(product)
    log_entry = {
        "transaction_id": transaction_id,
        "user_id": user_id,
        "timestamp": transaction.get("timestamp"),
        "products": enriched_products,
        "total_amount": transaction.get("total_amount"),
        "delivery_address": transaction.get("delivery_address"),
        "source": transaction.get("source")
    }
    _db["logs"].append(log_entry)

def get_transactions(user_id: str):
    return [log for log in _db["logs"] if log["user_id"] == user_id]

def get_all_logs():
    return _db["logs"]

def save_delivery_address(user_id: str, address: str):
    _db["addresses"][user_id] = address

def get_delivery_address(user_id: str):
    return _db["addresses"].get(user_id)
