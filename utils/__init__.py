import asyncio
import logging

from telegram import Update, User
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from app.globals import DB, USER_SEMAPHORES
from database.models import User as UserTable


async def register_user_if_not_exists(user: User) -> str:
    if user.id not in USER_SEMAPHORES:
        USER_SEMAPHORES[user.id] = asyncio.Semaphore(1)
    if not DB.check_if_object_exists(UserTable, filters={"user_id": user.id}):
        DB.add_instance(
            UserTable,
            {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_id": user.id,
            },
        )
        return True
    return False


async def is_previous_message_not_answered_yet(update: Update):
    user_id = update.message.from_user.id
    if USER_SEMAPHORES[user_id].locked():
        await update.message.reply_text(
            "⏳ Please <b>wait</b> for a reply to the previous message.",
            reply_to_message_id=update.message.id,
            parse_mode=ParseMode.HTML,
        )
        return True
    else:
        return False


async def edited_message_handle(update: Update):
    text = "🥲 Unfortunately, message <b>editing</b> is not supported"
    await update.edited_message.reply_text(text, parse_mode=ParseMode.HTML)
