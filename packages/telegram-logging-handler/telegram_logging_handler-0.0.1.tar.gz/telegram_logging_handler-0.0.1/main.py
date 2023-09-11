import logging

from src.telegram_logging_handler import TelegramHandler

logger = logging.getLogger('my_logger')
telegram_handler = TelegramHandler(
    api_token="6037801712:AAH-zIzBnou5PR58TKMgUtcbgfvgTKN_m14",
    chat_id=["864003403"]
)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
telegram_handler.setFormatter(formatter)
logger.addHandler(telegram_handler)

logger.error('Fd')

# async def main():
#     tasks = []
#     for i in range(100):
#         tasks.append(handle(str(i)))
#     await asyncio.gather(*tasks)
#
#
# asyncio.run(main())
