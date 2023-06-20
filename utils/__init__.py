import asyncio
import logging

from telegram import Update, User
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

import config
from app.globals import DB
from bot import user_semaphores
from database.models import User as UserTable

logger = logging.getLogger(__name__)


async def register_user_if_not_exists(
    update: Update, context: CallbackContext, user: User
) -> str:
    reply_text = ""
    if not DB.check_if_object_exists(user.id):
        reply_text = "Hi! I'm <b>Maya</b> your personal medical assistant 🤖.\nLet's register your details as a patient, please click on /register."
        DB.add_instance(
            user.id,
            UserTable,
            {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        )
        DB.start_new_dialog(user.id)
    if DB.get_attribute(user.id, "current_dialog_id") is None:
        DB.start_new_dialog(user.id)
    if user.id not in user_semaphores:
        user_semaphores[user.id] = asyncio.Semaphore(1)
    # back compatibility for n_used_tokens field
    n_used_tokens = DB.get_attribute(user.id, "n_used_tokens")
    if isinstance(n_used_tokens, int):
        new_n_used_tokens = {
            config.gpt_model: {"n_input_tokens": 0, "n_output_tokens": n_used_tokens}
        }
        DB.set_attribute(user.id, "n_used_tokens", new_n_used_tokens)
    if reply_text != "":
        await update.message.reply_text(
            reply_text, reply_to_message_id=update.message.id, parse_mode=ParseMode.HTML
        )
        return True
    return False


async def is_previous_message_not_answered_yet(
    update: Update, context: CallbackContext
):
    if await register_user_if_not_exists(update, context, update.message.from_user):
        return True
    user_id = update.message.from_user.id
    if user_semaphores[user_id].locked():
        text = "⏳ Please <b>wait</b> for a reply to the previous message\n"
        text += "Or you can /cancel it"
        await update.message.reply_text(
            text, reply_to_message_id=update.message.id, parse_mode=ParseMode.HTML
        )
        return True
    else:
        return False


async def edited_message_handle(update: Update, context: CallbackContext):
    text = "🥲 Unfortunately, message <b>editing</b> is not supported"
    await update.edited_message.reply_text(text, parse_mode=ParseMode.HTML)
