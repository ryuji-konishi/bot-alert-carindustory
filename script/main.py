
import os
import requests

def send_discord_alert(message):
    webhook_url = os.getenv("DISCORD_WEBHOOK")
    data = {
        "content": message
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(webhook_url, json=data, headers=headers)
    if response.status_code != 204:
        print(f"❌ Failed to send alert: {response.status_code} - {response.text}")
    else:
        print("✅ Alert sent to Discord!")

# Example message
send_discord_alert("🚗 Daily EV alert from bot-alert-carindustory: Everything looks good!")
