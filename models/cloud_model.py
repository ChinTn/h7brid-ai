from openai import OpenAI

from config import (
    OPENROUTER_API_KEY,
    CLOUD_MODEL
)

from tracing.debug import trace

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# =====================================
# NORMAL CLOUD CHAT
# =====================================

def cloud_chat(messages):

    trace("Starting cloud streaming")

    stream = client.chat.completions.create(
        model=CLOUD_MODEL,
        messages=messages,
        max_tokens=2000,
        stream=True
    )

    full_response = ""

    for chunk in stream:

        try:

            content = chunk.choices[0].delta.content

            if content:

                print(content, end="", flush=True)

                full_response += content

        except:
            pass

    print()

    trace("Cloud streaming completed")

    return full_response