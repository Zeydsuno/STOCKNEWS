"""
LINE Bot Push Message Handler
Sends messages to LINE users via LINE Messaging API
No webhook required - only uses Push API
"""

import logging
import os
from typing import List, Dict, Optional
import requests

logger = logging.getLogger(__name__)

class LINEPusher:
    """Push messages to LINE users"""

    def __init__(self, channel_access_token: str = None):
        """
        Initialize LINE Pusher

        Args:
            channel_access_token: LINE Channel Access Token
        """
        self.channel_access_token = channel_access_token or os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.api_url = "https://api.line.biz/v3/bot"

        if not self.channel_access_token:
            logger.warning("[WARN] LINE Channel Access Token not set")
            self.available = False
        else:
            self.available = True
            logger.info("[OK] LINE Pusher initialized")

    def push_message(self, user_id: str, message: Dict) -> bool:
        """
        Push a single message to a user

        Args:
            user_id: LINE User ID
            message: Message object (JSON format)

        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            logger.error("[FAIL] LINE Pusher not available")
            return False

        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.channel_access_token}'
            }

            payload = {
                'to': user_id,
                'messages': [message]
            }

            response = requests.post(
                f"{self.api_url}/message/push",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"[OK] Message pushed to {user_id}")
                return True
            else:
                logger.error(f"[FAIL] Failed to push message: {response.status_code} {response.text}")
                return False

        except Exception as e:
            logger.error(f"[FAIL] Error pushing message: {e}")
            return False

    def broadcast_message(self, message: Dict) -> bool:
        """
        Broadcast message to all users who added the bot

        Args:
            message: Message object (JSON format)

        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            logger.error("[FAIL] LINE Pusher not available")
            return False

        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.channel_access_token}'
            }

            payload = {
                'messages': [message]
            }

            response = requests.post(
                f"{self.api_url}/message/broadcast",
                headers=headers,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("[OK] Broadcast message sent to all users")
                return True
            else:
                logger.error(f"[FAIL] Failed to broadcast: {response.status_code} {response.text}")
                return False

        except Exception as e:
            logger.error(f"[FAIL] Error broadcasting message: {e}")
            return False

    def push_flex_message(self, user_id: str, flex_message: Dict) -> bool:
        """
        Push a flex message (rich format)

        Args:
            user_id: LINE User ID
            flex_message: Flex message object

        Returns:
            True if successful
        """
        message = {
            'type': 'flex',
            'altText': flex_message.get('altText', 'Stock News'),
            'contents': flex_message.get('contents', {})
        }

        return self.push_message(user_id, message)

    def broadcast_flex_message(self, flex_message: Dict) -> bool:
        """
        Broadcast flex message to all users

        Args:
            flex_message: Flex message object

        Returns:
            True if successful
        """
        message = {
            'type': 'flex',
            'altText': flex_message.get('altText', 'Stock News'),
            'contents': flex_message.get('contents', {})
        }

        return self.broadcast_message(message)

    def get_status(self) -> Dict:
        """Get LINE Pusher status"""
        return {
            'available': self.available,
            'api_url': self.api_url,
            'token_configured': bool(self.channel_access_token),
            'api_type': 'Push Only (No Webhook)'
        }


def test_line_pusher():
    """Test LINE Pusher"""
    print("Testing LINE Pusher...")
    print("=" * 60)

    pusher = LINEPusher()
    status = pusher.get_status()

    print(f"Available: {status['available']}")
    print(f"API URL: {status['api_url']}")
    print(f"Token Configured: {status['token_configured']}")
    print(f"API Type: {status['api_type']}")

    if status['available']:
        print("\n[OK] LINE Pusher is ready!")
        print("Setup Instructions:")
        print("1. Set LINE_CHANNEL_ACCESS_TOKEN in .env")
        print("2. Get user ID from LINE Messaging API webhook")
        print("3. Call push_message(user_id, message)")
    else:
        print("\n[FAIL] LINE Pusher not available")
        print("Make sure to set LINE_CHANNEL_ACCESS_TOKEN in .env")

    print("=" * 60)


if __name__ == "__main__":
    test_line_pusher()
