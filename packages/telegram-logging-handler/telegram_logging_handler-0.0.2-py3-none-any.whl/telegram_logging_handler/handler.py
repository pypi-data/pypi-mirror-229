import logging
from typing import Union, List
import requests


class TelegramHandler(logging.Handler):
    def __init__(self, api_token: str, chat_id: Union[str, List[str]]):
        self.api_token = api_token
        self.chat_id = chat_id
        super().__init__()

    def emit(self, record):
        messages = self.format(record)
        for message in messages:
            if isinstance(self.chat_id, str):
                self._emit(self.chat_id, message)
            elif isinstance(self.chat_id, list):
                for chat_id in self.chat_id:
                    self._emit(chat_id, message)

    def _emit(self, chat_id: str, message: str):
        api_url = f'https://api.telegram.org/bot{self.api_token}/sendMessage'
        try:
            requests.post(api_url, json={'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'})
        except Exception as e:
            print(e)

    def format(self, record: logging.LogRecord) -> list:
        text = super().format(record)
        messages = []
        for i in range(0, len(text), 4096):
            messages.append(text[i:i + 4000])
        return messages
