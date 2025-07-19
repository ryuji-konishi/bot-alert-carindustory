import os
import requests
from openai import OpenAI

# Load secrets from GitHub Actions
webhook_url = os.getenv("DISCORD_WEBHOOK")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Generate GPT-powered message
def generate_update():
    prompt = (
        "You are an expert automotive industry analyst. Generate a brief, concise and informative summary "
        "about the very latest developments and trends in the automotive sector, especially related to Tesla. "
        "Focus on:\n"
        "- The most recent and notable daily news involving Tesla or the broader EV industry\n"
        "- Tesla’s vehicle business\n"
        "- Tesla’s non-automotive ventures such as Optimus (robotics), energy/solar business\n"
        "- Any major updates about Elon Musk, but only if related to Tesla\n"
        "- A quick note on Tesla’s current stock price trend, especially if it changed significantly\n"
        "- Global EV sales comparison (e.g., Tesla vs. BYD, Volkswagen, Toyota)\n"
        "- Date the upcoming major events that are related to EV industry and business like Tesla's Quarterly Earnings Call\n\n"
        "If possible, include the source link next to the statement — but only if the link is known or provided. "
        "Do not make up links. If no URL is given, just skip it.\n\n"
        "Assume this will be posted in a Discord server for car enthusiasts and developers in Japan. "
        "Keep it under 5 sentences, and make it sound fresh and insightful. Include emojis where helpful. "
        "If nothing major changed, still write a brief note saying so.\n"
        "No need of any disclaimer or preamble, just the content.\n"
    )

    response = client.chat.completions.create(
        model="gpt-4",  # Or "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
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
    message = message[:1990] + "\n...[truncated]"

send_discord_alert(message)
