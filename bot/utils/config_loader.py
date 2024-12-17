import os
from types import SimpleNamespace
from dotenv import load_dotenv


def load_config() -> SimpleNamespace:
    load_dotenv(override=True)  # .envファイルの読み込み
    cfg = {
        'ENVIRONMENT': os.getenv('ENVIRONMENT'),
        'NON_MONITORED_CHANNEL_ID': int(os.getenv('NON_MONITORED_CHANNEL_ID', 0)),
        'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
        'DISCORD_ADMIN_CHANNEL_ID': int(os.getenv('DISCORD_ADMIN_CHANNEL_ID')),
        'DISCORD_GUILD_ID': int(os.getenv('DISCORD_GUILD_ID')),
        'MENTION_ID': int(os.getenv('MENTION_ID')),
        'MESSAGE_LIMIT_LENGTH': int(os.getenv('MESSAGE_LIMIT_LENGTH', 2000)),
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASS': os.getenv('DB_PASS'),
        'DB_NAME': os.getenv('DB_NAME'),
        'KEYWORDS': SimpleNamespace(
            keyword='キーワード',
            today='今日',
            this_week='今週',
            this_month='今月',
            yesterday='昨日',
            day_before_yesterday='一昨日',
            last_week='先週',
            last_month='先月',
            days='日前',
        ),
        'EMOJI_EXTERNAL_LINK': os.getenv('EMOJI_EXTERNAL_LINK'),
    }

    return SimpleNamespace(**cfg)
