from models.classifier import classify_prompt

from models.local_model import local_chat

from models.cloud_model import cloud_chat


# =====================================
# CLEAN MODEL OUTPUT
# =====================================

def clean_patch_output(text):

    cleaned = text.strip()

    # remove markdown fences
    if cleaned.startswith("```"):

        lines = cleaned.splitlines()

        # remove first ```
        lines = lines[1:]

        # remove last ```
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]

        cleaned = "\n".join(lines)

    return cleaned


# =====================================
# PATCH GENERATION
# =====================================

def generate_patch(prompt, file_data):

    edit_prompt = f"""
You are modifying a repository file.

IMPORTANT RULES:
- Return ONLY the final updated file
- Do NOT explain anything
- Do NOT use markdown code fences
- Do NOT wrap output in ```
- Output must be directly writable

USER REQUEST:
{prompt}

FILE PATH:
{file_data['path']}

CURRENT FILE CONTENT:
{file_data['content']}
"""

    decision = classify_prompt(prompt)

    # =====================================
    # SIMPLE → LOCAL
    # =====================================

    if decision == "SIMPLE":

        response = local_chat([
            {
                "role": "user",
                "content": edit_prompt
            }
        ])

        raw_output = response["message"]["content"]

        return clean_patch_output(raw_output)

    # =====================================
    # COMPLEX → CLOUD
    # =====================================

    raw_output = cloud_chat([
        {
            "role": "user",
            "content": edit_prompt
        }
    ])

    return clean_patch_output(raw_output)