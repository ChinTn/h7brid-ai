import ollama

from config import LOCAL_MODEL

from tracing.debug import trace

# =====================================
# LOCAL CHAT
# =====================================

def local_chat(messages, stream=False):

    trace("Running local model")

    response = ollama.chat(
        model=LOCAL_MODEL,
        messages=messages,
        stream=stream
    )

    return response