import unittest
import os
from dotenv import load_dotenv
from telegram_notifier_bot import send


load_dotenv()


class TestSendNotification(unittest.TestCase):
    """
    Send a notification to a Telegram user or group.
    """
    class _TestData:
            
        telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        notification = "We're out of coffe! Please fix ASAP!"

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        pass

    def test(self) -> None:
        response = send(
            self._TestData.telegram_bot_token,
            self._TestData.telegram_chat_id,
            self._TestData.notification
        )
        self.assertTrue(response.status_code == 200)
