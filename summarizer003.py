import re

def clean_text(text):
    """Removes extra whitespace and basic artifacts."""
    if not text: return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def summarize_content(text, max_length=180):
    """Distills the email body into a concise summary."""
    cleaned = clean_text(text).upper()
    if len(cleaned) <= max_length:
        return cleaned
    summary = cleaned[:max_length].rsplit(' ', 1)[0]
    return f"{summary}..."

def summarize_all_new(new_emails):
    """Creates a high-level overview of all emails fetched in the current run."""
    if not new_emails:
        return "No new emails were fetched in this run."
    
    # Group by sender to see who is most active
    senders = {}
    for e in new_emails:
        name = e['sender'].split('<')[0].strip()
        senders[name] = senders.get(name, 0) + 1
    
    sender_str = ", ".join([f"{name} ({count})" for name, count in list(senders.items())[:5]])
    
    # Pick out the top 3-4 subjects as 'Highlights'
    highlights = [e['subject'] for e in new_emails[:4]]
    highlight_str = " | ".join(highlights)
    
    return f"RUN BRIEFING: Received {len(new_emails)} new updates. Primary sources: {sender_str}. Highlights include: {highlight_str}."