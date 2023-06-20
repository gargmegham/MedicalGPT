import logging
from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from database.mysql import MySQL
from utils import register_user_if_not_exists

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: CallbackContext):
    try:
        mysql = MySQL()
        if not await register_user_if_not_exists(
            update, context, update.message.from_user
        ):
            user_id = update.message.from_user.id
            mysql.set_attribute(user_id, "last_interaction", datetime.now())
            mysql.start_new_dialog(user_id)
            reply_text = "Hi! I'm <b>Maya</b> your personal medical assistant 🤖.\nPlease click on /new to start a new conversation, or click /register if you've not registered yet."
            await update.message.reply_text(reply_text, parse_mode=ParseMode.HTML)
    finally:
        mysql.close()
