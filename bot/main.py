import os, logging, asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from commands import cmd_list_users, cmd_add_user, cmd_del_user

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")
logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(Command("list_users"))
async def on_list(m: Message): await cmd_list_users(m)
@dp.message(Command("add_user"))
async def on_add(m: Message): await cmd_add_user(m, m.text.split()[1:])
@dp.message(Command("del_user"))
async def on_del(m: Message): await cmd_del_user(m, m.text.split()[1:])

if __name__ == "__main__":
    logging.info("Starting bot...")
    asyncio.run(dp.start_polling(bot))