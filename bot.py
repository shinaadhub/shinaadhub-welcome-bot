
import os
import logging
import requests
from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
CHANNEL_USERNAME = "@official_shinaadhub"

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route("/", methods=["GET"])
def home():
    return "ShinaAdHub Welcome Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json(silent=True) or {}
    member_update = update.get("chat_member")

    if not member_update:
        return "OK", 200

    chat = member_update.get("chat", {})
    old_member = member_update.get("old_chat_member", {})
    new_member = member_update.get("new_chat_member", {})

    old_status = old_member.get("status")
    new_status = new_member.get("status")

    if (
        chat.get("username", "").lower() == "official_shinaadhub"
        and old_status in ("left", "kicked")
        and new_status in ("member", "administrator")
    ):
        new_user = new_member.get("user", {})
        username = new_user.get("username")

        if username:
            welcome_text = (
                f"🎉 @{username}, welcome to ShinaAdHub!\n\n"
                "We're happy to have you here. "
                "Stay connected for updates, announcements and more. ❤️"
            )
        else:
            first_name = new_user.get("first_name", "there")
            welcome_text = (
                f"🎉 {first_name}, welcome to ShinaAdHub!\n\n"
                "We're happy to have you here. "
                "Stay connected for updates, announcements and more. ❤️"
            )

        keyboard = {
            "inline_keyboard": [[
                {
                    "text": "📢 Visit ShinaAdHub",
                    "url": "https://t.me/official_shinaadhub"
                }
            ]]
        }

        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={
                "chat_id": CHANNEL_USERNAME,
                "text": welcome_text,
                "reply_markup": keyboard
            },
            timeout=20
        )
        response.raise_for_status()

    return "OK", 200


if __name__ == "__main__":
    response = requests.post(
        f"{TELEGRAM_API}/setWebhook",
        json={
            "url": WEBHOOK_URL,
            "allowed_updates": ["chat_member"]
        },
        timeout=20
    )
    response.raise_for_status()
    logging.info("Telegram webhook registered successfully")

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )
