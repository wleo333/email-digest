import json
from summarizer import summarize_content, summarize_all_new

def main():
    # 1. Read the file with explicit UTF-8 encoding to handle special characters
    try:
        with open('full_email.json', 'r', encoding='utf-8') as file:
            emails = json.load(file)
    except FileNotFoundError:
        print("Error: full_email.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON from full_email.json.")
        return
    except UnicodeDecodeError:
        print("Error: Encoding issue. Ensure the file is read as UTF-8.")
        return

    # 2. Global summary
    global_summary = summarize_all_new(emails)

    # 3. Individual summaries
    individual_summaries_html = ""
    for email in emails:
        content_summary = summarize_content(email['full_body'])
        
        individual_summaries_html += f"""
        <div class="email-entry">
            <h3>{email['subject']}</h3>
            <p><strong>From:</strong> {email['sender']}</p>
            <p><strong>Date:</strong> {email['date']}</p>
            <div class="summary-box">{content_summary}</div>
        </div>
        <hr>
        """

    # 4. HTML Template
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Email Summary Report</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; }}
        .top-half {{ background: #2c3e50; color: white; padding: 30px; height: 35%; overflow-y: auto; }}
        .bottom-half {{ padding: 30px; height: 65%; overflow-y: auto; background: #f4f4f9; }}
        .summary-box {{ background: white; padding: 15px; border-left: 5px solid #3498db; margin-top: 10px; }}
        .email-entry {{ margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="top-half">
        <h1>Global Briefing</h1>
        <p>{global_summary}</p>
    </div>
    <div class="bottom-half">
        <h2>Individual Summaries</h2>
        {individual_summaries_html}
    </div>
</body>
</html>
"""

    # 5. Write to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("Success: index.html has been generated.")

if __name__ == "__main__":
    main()