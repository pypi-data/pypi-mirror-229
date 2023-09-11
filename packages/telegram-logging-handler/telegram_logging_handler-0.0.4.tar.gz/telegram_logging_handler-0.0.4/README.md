## Telegram logging handler for python

Provide your bot credentials to TelegramHandler:

```python
from src.telegram_logging_handler import TelegramHandler

telegram_handler = TelegramHandler(
    api_token="api_token",
    chat_id="000000000"
)
```

For multiple chats you can provide a list of chat ids:

```python
from src.telegram_logging_handler import TelegramHandler

telegram_handler = TelegramHandler(
    api_token="api_token",
    chat_id=["000000000", "11111111", "2222222"]
)
```

Use it with standard logging package:

```python
import logging

from src.telegram_logging_handler import TelegramHandler

logger = logging.getLogger('my_logger')
telegram_handler = TelegramHandler(
    api_token="api_token",
    chat_id=["000000000", "11111111", "2222222"]
)
formatter = logging.Formatter('<b>%(asctime)s - %(levelname)s</b> - %(message)s')
telegram_handler.setFormatter(formatter)
logger.addHandler(telegram_handler)
logger.error('')
```

As you can see, handler also supports HTML tags inside formatter.