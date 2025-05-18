import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from .commands import cmd_list_users, cmd_add_user, cmd_del_user, cmd_set_role
import sys

log_dir = os.getenv('LOG_DIR', '/logs')
log_file = os.path.join(log_dir, 'bot.log')

logging.basicConfig(
    level=logging.INFO,
    filename=log_file,
    format='%(asctime)s %(levelname)s %(message)s'
)

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=['list_users']))
async def handle_list(message: Message):
    await cmd_list_users(message)

@dp.message(Command(commands=['add_user']))
async def handle_add(message: Message):
    args = message.text.split()[1:]
    await cmd_add_user(message, args)

@dp.message(Command(commands=['del_user']))
async def handle_del(message: Message):
    args = message.text.split()[1:]
    await cmd_del_user(message, args)

async def main():
    logging.info('Starting bot...')
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())