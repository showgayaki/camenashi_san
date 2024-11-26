import os
from types import SimpleNamespace
from dotenv import load_dotenv


def load_config() -> SimpleNamespace:
    load_dotenv(override=True)  # .envファイルの読み込み
    cfg = {
        'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
        'DISCORD_CHANNEL_ID': int(os.getenv('DISCORD_CHANNEL_ID')),
        'MENTION_ID': int(os.getenv('MENTION_ID')),
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASS': os.getenv('DB_PASS'),
        'DB_NAME': os.getenv('DB_NAME'),
    }

    return SimpleNamespace(**cfg)
