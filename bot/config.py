from pathlib import Path

import dotenv
import yaml

config_dir = Path(__file__).parent.parent.resolve() / "config"

# load yaml config
with open(config_dir / "config.yml", "r") as f:
    config_yaml = yaml.safe_load(f)

# load .env config
config_env = dotenv.dotenv_values(config_dir / "config.env")

# config parameters
telegram_token = config_yaml["telegram_token"]
openai_api_key = config_yaml["openai_api_key"]
use_chatgpt_api = config_yaml.get("use_chatgpt_api", True)
allowed_telegram_usernames = config_yaml["allowed_telegram_usernames"]
developer_telegram_chatid = config_yaml["developer_telegram_chatid"]
admin_telegram_username = config_yaml["admin_telegram_username"]
new_dialog_timeout = config_yaml["new_dialog_timeout"]
mysql_uri = f"mysql+pymysql://{config_env['MYSQL_USER']}:{config_env['MYSQL_PASSWORD']}@{config_env['MYSQL_HOST']}:{config_env['MYSQL_PORT']}/{config_env['MYSQL_DATABASE']}"

# chat_modes
with open(config_dir / "chat_modes.yml", "r") as f:
    chat_modes = yaml.safe_load(f)
