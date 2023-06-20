import logging
from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from app.globals import DB
from database.models import User
from utils import register_user_if_not_exists


async def start_handler(update: Update, _: CallbackContext):
    if await register_user_if_not_exists(update.message.from_user):
        user_id = update.message.from_user.id
        DB.set_attribute(
            User,
            "last_interaction",
            datetime.now(),
            filters={"user_id": user_id},
        )
        await update.message.reply_text(
            "Hi! I'm <b>Maya</b> your personal medical assistant 🤖.\nLet's start with introductions, please let me know your name, age and gener.\nAlso let me know if you're pregnant if applicable.",
            parse_mode=ParseMode.HTML,
        )
