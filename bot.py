from aiogram import Dispatcher, Bot, types
from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message()
async def start(message: types.Message) -> None:
    await bot.send_message(chat_id=message.chat.id, text=message.text)
