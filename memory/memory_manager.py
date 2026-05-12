from config import MAX_RECENT_MESSAGES

recent_messages = []

conversation_summary = ""

CURRENT_MODE = "CHAT"

def add_message(role, content):

    global recent_messages

    recent_messages.append({
        "role": role,
        "content": content
    })

    if len(recent_messages) > MAX_RECENT_MESSAGES:
        recent_messages.pop(0)



def get_recent_messages():

    return recent_messages

# =====================================
# MODE MANAGEMENT
# =====================================

def get_current_mode():

    global CURRENT_MODE

    return CURRENT_MODE


def set_current_mode(mode):

    global CURRENT_MODE

    CURRENT_MODE = mode