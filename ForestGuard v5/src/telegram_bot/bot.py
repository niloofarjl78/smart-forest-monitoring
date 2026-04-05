"""Telegram bot for sending alerts and notifications."""

import requests, json
from datetime import datetime
from src.common.rest_helper import get_catalog_config, register_service
from src.common.mongodb_client import MongoDBClient

class TelegramBot:
    """Manages Telegram bot operations."""
    def __init__(self):
        """Initialize the bot with configuration."""
        register_service({"name": "telegram_bot", "port": 5003, "host": "localhost", "status": "running", "endpoints": ["/api/health"]})
        config = get_catalog_config("telegram")
        self.bot_token = config.get('bot_token', '') or config.get('token', '')
        self.chat_ids = config.get('authorized_chat_ids', [])
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.mongo_client = MongoDBClient()
        print(f"[TelegramBot] {'Connected' if self.bot_token else 'ERROR: No bot token'}")

    def send_message(self, message, chat_id=None):
        """Send a message to authorized chat IDs."""
        if not self.bot_token:
            return False
        try:
            chat_ids = [chat_id] if chat_id else self.chat_ids
            for cid in chat_ids:
                response = requests.post(f"{self.base_url}/sendMessage", 
                                       {'chat_id': cid, 'text': message, 'parse_mode': 'HTML'})
                if response.status_code == 200:
                    print(f"[TelegramBot] Alert sent to {cid}")
                else:
                    print(f"[TelegramBot] Failed to send to {cid}: {response.status_code}")
            return True
        except Exception as e:
            print(f"[TelegramBot] Send error: {e}")
            return False

    def get_system_status(self):
        try:
            status = "IoT Forest Fire Monitor V4\n\n"
            for sensor_type in ['temperature', 'humidity', 'smoke']:
                result = self.mongo_client.find_latest(f"{sensor_type}_sensor", {})
                status += f"{sensor_type.title()}: {result.get('value', 0) if result else 'No data'}\n"
            return status + f"\nUpdated: {datetime.now().strftime('%H:%M:%S')}"
        except:
            return "Error getting status"

def main():
    bot = TelegramBot()
    if bot.bot_token:
        bot.send_message("IoT Forest Fire Monitor V4 Bot Started\nUse /status for current readings")
        print("[TelegramBot] Bot running. Waiting for alerts...")
    else:
        print("[TelegramBot] ERROR: Bot token missing")

if __name__ == '__main__':
    main()
