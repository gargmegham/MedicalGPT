from telegram.ext import filters

from app import config


def get_user_filter():
    filter = filters.ALL
    if len(config.allowed_telegram_usernames) > 0:
        usernames = config.allowed_telegram_usernames
        user_ids = [x for x in config.allowed_telegram_usernames if isinstance(x, int)]
        if config.developer_telegram_username is not None:
            usernames.append(config.developer_telegram_username)
        filter = filters.User(username=usernames) | filters.User(user_id=user_ids)
    return filter
