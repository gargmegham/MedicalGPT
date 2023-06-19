from app.filters import get_user_filter
from telegram.ext import (
    AIORateLimiter,
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

from app import config
import handlers

user_semaphores = {}
user_tasks = {}


def consumer() -> None:
    application = (
        ApplicationBuilder()
        .token(config.telegram_token)
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=5))
        .build()
    )
    user_filter = get_user_filter()
    application.add_handler(
        CommandHandler(
            "start", handlers.commands.CommandHandler.start_handle, filters=user_filter
        )
    )
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND & user_filter, handlers.message_handler
        )
    )
    # add error handler
    application.add_error_handler(handlers.error_handler)
    # start the bot
    application.run_polling()
