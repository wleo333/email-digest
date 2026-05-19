import os
import re
from anthropic import Anthropic

API_KEY = "<KEY>"

MODEL = "claude-opus-4-7"

def _load_prompt():
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        return f.read().strip()

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def summarize_content(text):
    """Uses AI to create a concise summary of a single email body."""
    cleaned = clean_text(text)
    if not cleaned:
        return "No content to summarize."

    client = Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model=MODEL,
        max_tokens=300,
        system=_load_prompt(),
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following email in 2-3 sentences:\n\n{cleaned}"
            }
        ]
    )
    return message.content[0].text

def summarize_all_new(new_emails):
    """Uses AI to produce a thematic synthesis across all emails."""
    if not new_emails:
        return "No new emails were fetched in this run."

    emails_text = ""
    for i, email in enumerate(new_emails, 1):
        emails_text += (
            f"Email {i}: {email['subject']}\n"
            f"From: {email['sender']}\n"
            f"{clean_text(email['full_body'])}\n"
            "---\n"
        )

    client = Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model=MODEL,
        max_tokens=600,
        system=_load_prompt(),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Below are {len(new_emails)} emails. "
                    "Identify the common themes, key insights, and interesting patterns across all of them. "
                    "Write a thematic synthesis in 3-5 sentences.\n\n"
                    f"{emails_text}"
                )
            }
        ]
    )
    return message.content[0].text
