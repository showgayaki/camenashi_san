from logging import getLogger
from datetime import datetime, timedelta, time

from utils.config_manager import ConfigManager


config = ConfigManager().config
logger = getLogger('bot')


def extract_file_path(message: str) -> str:
    for line in message.splitlines():
        if line.endswith('.mp4'):
            return line


def zenkaku_to_int_days(zenkaku_str: str):
    zenkaku_number = zenkaku_str.replace(config.KEYWORDS.days, '')
    days_str = zenkaku_number.translate(
        str.maketrans(
            '０１２３４５６７８９一二三四五六七八九',
            '0123456789123456789'
        )
    )
    try:
        return int(days_str)
    except Exception as e:
        logger.error(f'Error: {e}')
        return 'ココハドコ？ワタシハダレ？？'


def start_datetime(now: datetime, keyword: str) -> datetime:
    if keyword == config.KEYWORDS.today:
        return datetime.combine(now.date(), time.min)
    elif keyword == config.KEYWORDS.this_week:
        # 今日が何曜日かを取得 (月曜日=0, 日曜日=6)
        today_weekday = now.weekday()
        # 前の日曜日までの日数を計算
        days_until_last_sunday = 0 if (6 - today_weekday - 7) == -7 else (6 - today_weekday - 7)
        last_sunday = now + timedelta(days=days_until_last_sunday)

        return datetime.combine(last_sunday, time.min)
    elif keyword == config.KEYWORDS.this_month:
        return datetime(now.year, now.month, 1)
    elif keyword == config.KEYWORDS.yesterday:
        return datetime.combine(now - timedelta(days=1), time.min)
    elif keyword == config.KEYWORDS.day_before_yesterday:
        return datetime.combine(now - timedelta(days=2), time.min)
    elif keyword == config.KEYWORDS.last_week:
        # 今日が何曜日かを取得 (月曜日=0, 日曜日=6)
        today_weekday = now.weekday()
        # 前の日曜日までの日数を計算
        days_until_last_sunday = 0 if (6 - today_weekday - 7) == -7 else (6 - today_weekday - 7)
        last_sunday = now + timedelta(days=days_until_last_sunday)

        # 前の日曜日のさらに1週間前が、先週の日曜日
        return datetime.combine(last_sunday - timedelta(weeks=1), time.min)
    elif keyword == config.KEYWORDS.last_month:
        return datetime(now.year, now.month - 1, 1)
    elif config.KEYWORDS.days in keyword:
        days = zenkaku_to_int_days(keyword)
        return datetime.combine(now - timedelta(days=days), time.min)


def end_datetime(now: datetime, keyword: str) -> datetime:
    if config.KEYWORDS.days in keyword:
        days = zenkaku_to_int_days(keyword)
    elif keyword == config.KEYWORDS.yesterday:
        days = 1
    elif keyword == config.KEYWORDS.day_before_yesterday:
        days = 2
    elif keyword == config.KEYWORDS.last_week:
        # 今日が何曜日かを取得 (月曜日=0, 日曜日=6)
        today_weekday = now.weekday()
        # 前の土曜日までの日数を計算
        days_until_last_saturday = 0 if (5 - today_weekday - 7) == -7 else (5 - today_weekday - 7)
        last_saturday = now + timedelta(days=days_until_last_saturday)

        return datetime.combine(last_saturday, time.max)
    elif keyword == config.KEYWORDS.last_month:
        this_month_1st = datetime(now.year, now.month, 1)
        # 今月の1日から一瞬戻れば先月の最終日時
        return this_month_1st + timedelta(microseconds=-1)
    else:
        return now

    return datetime.combine(now - timedelta(days=days), time.max)
