import os
import requests
from openai import OpenAI
from datetime import datetime
from data_sources import (
    fetch_latest_news,
    fetch_next_earnings,
    fetch_stock_summary,
)

# Load secrets from GitHub Actions
webhook_url = os.getenv("DISCORD_WEBHOOK")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Generate GPT-powered message
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
        model="gpt-4",  # Or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You summarize given information."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7
    )

    return response.choices[0].message.content

# Send message to Discord
def send_discord_alert(message):
    data = {"content": message}
    headers = {"Content-Type": "application/json"}
    res = requests.post(webhook_url, json=data, headers=headers)
    if res.status_code != 204:
        print(f"❌ Failed to send alert: {res.status_code} - {res.text}")
    else:
        print("✅ Alert sent to Discord!")

# Run
message = generate_update()
# Limit message length for Discord
if len(message) > 2000:
    slice_length = 2000 - len("\n...[truncated]")
    message = message[:slice_length] + "\n...[truncated]"

today = datetime.now().strftime("%Y-%m-%d")
send_discord_alert(f"📅 {today} – Today's Tesla Update [OpenAI version]\n")
send_discord_alert(message)
