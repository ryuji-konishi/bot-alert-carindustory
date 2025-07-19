import os
import requests
from openai import OpenAI
from datetime import datetime

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
    prompt = (
        "You are an expert automotive industry analyst. Generate a brief, concise and informative summary "
        "about the very latest developments and daily trends in the automotive sector, especially related to Tesla. "
        "Focus on:\n"
        "- The most recent and notable daily news involving Tesla or the broader EV industry\n"
        "- Tesla’s vehicle business\n"
        "- Tesla’s non-automotive ventures such as Optimus (robotics), energy/solar business\n"
        "- Any major updates about Elon Musk, and its impact to Tesla\n"
        "- A quick note on Tesla’s current stock price trend and its reason, especially if it changed significantly\n"
        "- If any, date the imminent major events that are related to EV industry and business like Tesla's Quarterly Earnings Call\n\n"
        "If possible, include the source link next to the statement — but only if the link is known or provided. "
        "Do not make up links. If no URL is given, just skip it. No need to say like source link not provided.\n\n"
        "Assume this will be posted in a Discord server for car enthusiasts and developers in Japan. "
        "Keep it under 5 sentences, and make it sound fresh and insightful. Include emojis where helpful. "
        "If nothing major changed, still write a brief note saying so.\n"
    )

    response = client.chat.completions.create(
        model="grok-4",  # Use Grok 4 (Grok 3 not available for API as of July 19, 2025)
        messages=[
            {"role": "system", "content": "You are a helpful assistant providing real-time information."},
            {"role": "user", "content": prompt}
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
