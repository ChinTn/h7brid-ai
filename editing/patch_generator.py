from models.classifier import classify_prompt

from models.local_model import local_chat

from models.cloud_model import cloud_chat



def generate_patch(prompt, file_data):

    edit_prompt = f"""
Modify this file.

USER REQUEST:
{prompt}

FILE CONTENT:
{file_data['content']}

Return ONLY updated file.
"""

    decision = classify_prompt(prompt)

    if decision == "SIMPLE":

        response = local_chat([
            {
                "role": "user",
                "content": edit_prompt
            }
        ])

        return response["message"]["content"]

    return cloud_chat([
        {
            "role": "user",
            "content": edit_prompt
        }
    ])