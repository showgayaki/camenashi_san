import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Keywords:
    keyword: str = 'キーワード'
    today: str = '今日'
    this_week: str = '今週'
    this_month: str = '今月'
    yesterday: str = '昨日'
    day_before_yesterday: str = '一昨日'
    last_week: str = '先週'
    last_month: str = '先月'
    days: str = '日前'
    gragh: str = 'グラフ'

    def periods(self) -> list:
        exclude_keys = ['keyword', 'today', 'yesterday', 'day_before_yesterday', 'days', 'gragh']
        return [key for key in self.__dict__.keys() if key not in exclude_keys]


@dataclass
class Config:
    ENVIRONMENT: str
    NON_MONITORED_CHANNEL_ID: int
    DISCORD_TOKEN: str
    DISCORD_ADMIN_CHANNEL_ID: int
    DISCORD_GUILD_ID: int
    MENTION_ID: int
    MESSAGE_LIMIT_LENGTH: int
    THREAD_PREFIX: str
    AUTO_ARCHIVE_DURATION: int
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    KEYWORDS: Keywords
    EMOJI_EXTERNAL_LINK: str = ''


def load_config() -> Config:
    load_dotenv(override=True)  # .envファイルの読み込み
    return Config(
        ENVIRONMENT=os.getenv('ENVIRONMENT', 'dev'),
        NON_MONITORED_CHANNEL_ID=int(os.getenv('NON_MONITORED_CHANNEL_ID', 0)),
        DISCORD_TOKEN=os.getenv('DISCORD_TOKEN', ''),
        DISCORD_ADMIN_CHANNEL_ID=int(os.getenv('DISCORD_ADMIN_CHANNEL_ID', 0)),
        DISCORD_GUILD_ID=int(os.getenv('DISCORD_GUILD_ID', 0)),
        MENTION_ID=int(os.getenv('MENTION_ID', 0)),
        MESSAGE_LIMIT_LENGTH=int(os.getenv('MESSAGE_LIMIT_LENGTH', 2000)),
        THREAD_PREFIX=os.getenv('THREAD_PREFIX', 'Thread-'),
        AUTO_ARCHIVE_DURATION=int(os.getenv('AUTO_ARCHIVE_DURATION', 60)),
        DB_HOST=os.getenv('DB_HOST', 'localhost'),
        DB_PORT=os.getenv('DB_PORT', '3306'),
        DB_USER=os.getenv('DB_USER', 'root'),
        DB_PASS=os.getenv('DB_PASS', ''),
        DB_NAME=os.getenv('DB_NAME', 'database'),
        KEYWORDS=Keywords(),
        EMOJI_EXTERNAL_LINK=os.getenv('EMOJI_EXTERNAL_LINK', ''),
    )
