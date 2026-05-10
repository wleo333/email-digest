import ezgmail
import json
import re
import os
import time
import argparse  # Added for CLI arguments
import summarizer 

PREVIOUS_FILE = 'previous.json'
INCLUDE_LABELS = {"Inbox", "AI", "Cybersecurity", "Development", "Philosophy", "Ignites", "Investing", "Podcasts"}

DISPLAY_NAMES = {
    'INBOX': 'Inbox', 'STARRED': 'Starred', 'IMPORTANT': 'Important',
    'CATEGORY_PERSONAL': 'Personal', 'CATEGORY_SOCIAL': 'Social',
    'CATEGORY_PROMOTIONS': 'Promotions', 'CATEGORY_UPDATES': 'Updates', 'CATEGORY_FORUMS': 'Forums'
}

# --- Command Line Argument Handling ---
parser = argparse.ArgumentParser(description="Gmail Summary Viewer Reader")
parser.add_argument('--reset', action='store_true', help="Ignore cache and re-process all historical emails from scratch.")
args = parser.parse_args()

# 1. Load existing data or start fresh
if os.path.exists(PREVIOUS_FILE) and not args.reset:
    print(f"Loading existing data from {PREVIOUS_FILE}...")
    with open(PREVIOUS_FILE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
        last_run_time = cache.get('last_run', 0)
        cached_labels = cache.get('labels_data', {})
else:
    if args.reset:
        print("Reset flag detected. Re-processing ALL emails from scratch...")
    else:
        print("No previous data found. Starting fresh...")
    last_run_time = 0
    cached_labels = {}

current_run_time = int(time.time())

print("Initializing Gmail...")
ezgmail.init()

# 2. Sync unread status
print("Syncing unread status...")
all_unread = ezgmail.search('is:unread', maxResults=500)
unread_thread_ids = {t.id for t in all_unread}

print("Fetching labels...")
resp = ezgmail.SERVICE_GMAIL.users().labels().list(userId='me').execute()
all_labels = resp.get('labels', [])

final_labels_data = {}
all_processed_emails = [] # To feed the global summary

for label in all_labels:
    lid = label['id']
    raw_name = label['name']
    ltype = label.get('type', 'user')

    if raw_name not in INCLUDE_LABELS and lid not in INCLUDE_LABELS:
        continue

    display_name = DISPLAY_NAMES.get(lid, raw_name)
    
    # 3. Query Logic: if reset, search everything. Otherwise, incremental.
    base_query = f'label:{lid}' if ltype == 'system' else 'label:' + raw_name.replace(' ', '-')
    
    if last_run_time == 0:
        search_query = base_query
    else:
        search_query = f"{base_query} after:{last_run_time}"

    print(f"Processing {display_name}...")
    try:
        # Increase maxResults if re-processing everything to catch older history
        limit = 500 if args.reset else 100
        new_threads = ezgmail.search(search_query, maxResults=limit)
    except Exception as e:
        print(f"  Skipped {display_name} ({e})")
        continue

    new_emails = []
    for thread in new_threads:
        msg = thread.messages[0]
        ts = msg.timestamp
        date_str = f"{ts.month}/{ts.day}/{ts.year % 100:02d}" if ts else ''
        
        raw_body = msg.body or ''
        email_obj = {
            'id': thread.id,
            'subject': (msg.subject or '(no subject)').strip(),
            'date': date_str,
            'preview': summarizer.clean_text(raw_body)[:250],
            'summary': summarizer.summarize_content(raw_body),
            'sender': msg.sender or 'Unknown',
            'timestamp': ts.timestamp() if ts else 0
        }
        new_emails.append(email_obj)
        all_processed_emails.append(email_obj)

    # 4. Merge New with Cached (If reset, cached_labels is already empty)
    existing_emails = cached_labels.get(lid, {}).get('emails', [])
    if isinstance(cached_labels.get(lid), dict) and 'emails' not in cached_labels[lid]:
        existing_emails = cached_labels[lid] if isinstance(cached_labels[lid], list) else []

    combined_dict = {e['id']: e for e in existing_emails if 'id' in e}
    for e in new_emails:
        combined_dict[e['id']] = e
    
    merged_emails = sorted(combined_dict.values(), key=lambda x: x.get('timestamp', 0), reverse=True)

    # 5. Update unread status and count
    unread_count = 0
    for e in merged_emails:
        e['isUnread'] = e['id'] in unread_thread_ids
        if e['isUnread']:
            unread_count += 1

    final_labels_data[lid] = {
        'id': lid, 
        'name': display_name, 
        'emails': merged_emails,
        'unread_count': unread_count
    }

# Generate the Global Summary for the index.html
global_run_summary = summarizer.summarize_all_new(all_processed_emails)

# Save updated data
with open(PREVIOUS_FILE, 'w', encoding='utf-8') as f:
    json.dump({'last_run': current_run_time, 'labels_data': final_labels_data}, f, ensure_ascii=False, indent=2)

# Generate HTML...
# (The rest of your HTML generation code remains the same as previously established)
# ...