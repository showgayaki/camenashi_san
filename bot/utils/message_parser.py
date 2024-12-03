from logging import getLogger

from utils.config import load_config


config = load_config()
logger = getLogger('bot')


def extract_file_path(message: str) -> str:
    for line in message.splitlines():
        if line.endswith('.mp4'):
            return line


def zenkaku_to_int_days(zenkaku_str: str):
    zenkaku_number = zenkaku_str.replace(config.KEYWORDS.days, '')
    days_str = zenkaku_number.translate(str.maketrans('０１２３４５６７８９', '0123456789'))
    return int(days_str)
