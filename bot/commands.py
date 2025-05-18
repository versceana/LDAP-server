import logging
from aiogram import types
from ldap_client import LdapClient

ldap = LdapClient()

async def cmd_list_users(message: types.Message):
    users = ldap.list_users()
    text = '\n'.join(f"{uid} — {cn}" for uid,cn in users) or 'No users.'
    await message.reply(f"Users:\n{text}")

async def cmd_add_user(message: types.Message, args: list):
    if len(args) < 2:
        return await message.reply('Usage: /add_user <uid> <password> [<cn>]')
    uid, pwd = args[0], args[1]
    cn = args[2] if len(args)>2 else uid
    if ldap.add_user(uid, pwd, cn):
        logging.info(f"Added user {uid}")
        await message.reply(f'User {uid} added.')
    else:
        await message.reply(f'Failed to add {uid}.')

async def cmd_del_user(message: types.Message, args: list):
    if not args:
        return await message.reply('Usage: /del_user <uid>')
    uid = args[0]
    if ldap.delete_user(uid):
        logging.info(f"Deleted user {uid}")
        await message.reply(f'User {uid} deleted.')
    else:
        await message.reply(f'Failed to delete {uid}.')