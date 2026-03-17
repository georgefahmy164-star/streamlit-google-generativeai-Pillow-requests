messages_db = {}

def save_message(user_id, role, content):
    if user_id not in messages_db:
        messages_db[user_id] = []
    messages_db[user_id].append({"role": role, "content": content})

def get_last_messages(user_id, limit=5):
    if user_id in messages_db:
        return messages_db[user_id][-limit:]
    return []
