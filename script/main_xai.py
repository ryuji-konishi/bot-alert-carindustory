import os
import requests
from openai import OpenAI
from datetime import datetime
from data_sources import (
    fetch_latest_news,
    fetch_next_earnings,
    fetch_stock_summary,
)

# Load secrets
webhook_url = os.getenv("DISCORD_WEBHOOK")
xai_api_key = os.getenv("XAI_API_KEY")

# Initialize xAI client
client = OpenAI(
    api_key=xai_api_key,
    base_url="https://api.x.ai/v1"
)

# Generate Grok-powered message
def generate_update():
    news = fetch_latest_news()
    stock = fetch_stock_summary()
    earnings = fetch_next_earnings()

    lines = []
    if news:
        lines.append("Recent News:")
        lines.extend(f"- {n}" for n in news)
    if stock:
        lines.append(f"Stock: {stock}")
    if earnings:
        lines.append(f"Next earnings: {earnings}")

    prompt = (
        "Summarize the following Tesla-related information for a Discord post. "
        "Limit the summary to about five sentences and include emojis if they help readability.\n\n"
        + "\n".join(lines)
    )

    response = client.chat.completions.create(
        model="grok-4",  # Use Grok 4 (Grok 3 not available for API as of July 19, 2025)
        messages=[
            {"role": "system", "content": "You summarize given information."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
        extra_body={
            "search_parameters": {
                "mode": "off"  # Disable Live Search to test if it’s the issue
            }
        }
        # extra_body={
        #     "search_parameters": {
        #         "mode": "auto",  # Grok decides when to search
        #         "max_search_results": 10  # Limit sources
        #     }
        # }
    )
    # Log full response for debugging
    print(f"Full API response: {response}")
    content = response.choices[0].message.content
    if content is None or content.strip() == "":
        print(f"⚠️ xAI API returned empty or None content: {content}")
        raise ValueError(f"xAI API returned empty or None content: {content}")
    content = content.strip()
    print(f"API response content: {content[:100]}...")  # Log first 100 chars
    return content

# Send message to Discord
def send_discord_alert(message):
    if not message or message.strip() == "":
        print("⚠️ Attempted to send empty message; raising error")
        raise ValueError("Cannot send empty message to Discord")
    
    data = {"content": message}
    headers = {"Content-Type": "application/json"}
    res = requests.post(webhook_url, json=data, headers=headers)
    if res.status_code != 204:
        print(f"❌ Failed to send alert: {res.status_code} - {res.text}")
        raise RuntimeError(f"Discord webhook failed: {res.status_code} - {res.text}")
    print("✅ Alert sent to Discord!")

# Run
message = generate_update()
# Limit message length for Discord
if len(message) > 2000:
    message = message[:1990] + "\n...[truncated]"

today = datetime.now().strftime("%Y-%m-%d")
send_discord_alert(f"📅 {today} – Today's Tesla Update [xAI version]\n")
send_discord_alert(message)
