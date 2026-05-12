from models.local_model import local_chat
from models.cloud_model import cloud_chat

# =====================================
# CLEAN RESPONSE
# =====================================

def clean_response(text):

    text = text.strip()

    if "```" in text:

        parts = text.split("```")

        for part in parts:

            part = part.strip()

            if "===FILE:" in part:

                return part

    return text


# =====================================
# PARSE MULTI FILE BLOCKS
# =====================================

def parse_file_blocks(text):

    files = []

    chunks = text.split(
        "===FILE:"
    )

    for chunk in chunks:

        chunk = chunk.strip()

        if not chunk:
            continue

        try:

            header, rest = chunk.split(
                "===",
                1
            )

            path = header.strip()

            content = rest.split(
                "===END===",
                1
            )[0].strip()

            files.append({
                "path": path,
                "content": content
            })

        except:
            pass

    return files


# =====================================
# PATCH GENERATION
# =====================================

def generate_patch(
    prompt,
    relevant_files,
    use_cloud=False
):

    files_context = ""

    for file in relevant_files:

        files_context += f"""

FILE PATH:
{file['path']}

FILE CONTENT:
{file['content']}

====================================
"""

    edit_prompt = f"""
You are modifying a repository.

USER REQUEST:
{prompt}

You may modify MULTIPLE files.

IMPORTANT:
- Only modify files that truly need changes
- Preserve formatting
- Preserve unrelated code

DO NOT RETURN JSON.

RETURN FORMAT:

===FILE: relative/path===
FULL UPDATED FILE CONTENT
===END===

You may return MULTIPLE file blocks.

FILES:

{files_context}
"""

    # =====================================
    # MODEL SELECTION
    # =====================================

    if use_cloud:

        raw_output = cloud_chat([
            {
                "role": "user",
                "content": edit_prompt
            }
        ])

    else:

        response = local_chat([
            {
                "role": "user",
                "content": edit_prompt
            }
        ])

        raw_output = response[
            "message"
        ][
            "content"
        ]

    # =====================================
    # CLEAN
    # =====================================

    cleaned = clean_response(
        raw_output
    )

    # =====================================
    # PARSE
    # =====================================

    parsed = parse_file_blocks(
        cleaned
    )

    if not parsed:

        print(
            "\n❌ PATCH PARSE FAILED\n"
        )

    return parsed