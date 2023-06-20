from telegram.ext import (
    AIORateLimiter,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from app import config
from app.filters import get_user_filter
from handlers.command import start_handler
from handlers.error import error_handler
from handlers.message import message_handler


def consumer() -> None:
    application = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=5))
        .build()
    )
    user_filter = get_user_filter()
    application.add_handler(CommandHandler("start", start_handler, filters=user_filter))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, message_handler)
    )
    # add error handler
    application.add_error_handler(error_handler)
    # start the bot
    application.run_polling()
