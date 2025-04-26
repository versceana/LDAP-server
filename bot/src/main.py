import os, asyncio
from aiogram import Bot, Dispatcher, types
from ldap3 import Server, Connection, ALL
from dotenv import load_dotenv

load_dotenv()
TOKEN    = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_CHAT_ID")
LDAP_URL = "ldap://openldap:389"
BASE_DN  = os.getenv("LDAP_ROOT")
ADMIN_DN = f"cn={os.getenv('LDAP_ADMIN_USERNAME')},{BASE_DN}"
ADMIN_PW = os.getenv("LDAP_ADMIN_PASSWORD")

bot = Bot(token=TOKEN)
dp  = Dispatcher(bot)

async def get_conn():
    srv  = Server(LDAP_URL, get_info=ALL)
    conn = Connection(srv, ADMIN_DN, ADMIN_PW, auto_bind=True)
    return conn

@dp.message_handler(commands=["start"])
async def cmd_start(msg: types.Message):
    if str(msg.chat.id) != ADMIN_ID:
        return await msg.reply("🚫 Access denied")
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("👁 list", callback_data="list"),
        types.InlineKeyboardButton("➕ add",  callback_data="add"),
        types.InlineKeyboardButton("➖ del",  callback_data="del")
    )
    await msg.reply("Choose:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data=="list")
async def cb_list(cb: types.CallbackQuery):
    conn = await get_conn()
    conn.search(BASE_DN, "(objectClass=inetOrgPerson)", attributes=["cn"])
    users = [e.cn.value for e in conn.entries]
    await cb.message.reply("Users:\n" + "\n".join(users))

# TODO: реализовать add/del по аналогии: запрос имени, вызов conn.add/delete()

if __name__ == "__main__":
    asyncio.run(dp.start_polling())