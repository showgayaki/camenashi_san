from logging import getLogger
from datetime import datetime, timedelta, time

from utils.config import ConfigManager


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
        # 今日が何曜日かを取得 (月曜=0, 日曜=6)
        today_weekday = now.weekday()
        # 前の日曜日までの日数を計算
        # 日曜(6) = 0, 月曜(0) = 1, 火曜(1) = 2, 水曜(2) = 3, 木曜(3) = 4, 金曜(4) = 5, 土曜(5) = 6
        days_until_last_sunday = 0 if today_weekday == 6 else today_weekday + 1
        last_sunday = now - timedelta(days=days_until_last_sunday)

        return datetime.combine(last_sunday, time.min)
    elif keyword == config.KEYWORDS.this_month:
        return datetime(now.year, now.month, 1)
    elif keyword == config.KEYWORDS.yesterday:
        return datetime.combine(now - timedelta(days=1), time.min)
    elif keyword == config.KEYWORDS.day_before_yesterday:
        return datetime.combine(now - timedelta(days=2), time.min)
    elif keyword == config.KEYWORDS.last_week:
        # 今日が何曜日かを取得 (月曜=0, 日曜=6)
        today_weekday = now.weekday()
        # 先週の日曜日までの日数を計算
        # 日曜(6) = 7, 月曜(0) = 8, 火曜(1) = 9, 水曜(2) = 10, 木曜(3) = 11, 金曜(4) = 12, 土曜(5) = 13
        days_until_last_sunday = 7 if today_weekday == 6 else (today_weekday + 8)
        last_sunday = now - timedelta(days=days_until_last_sunday)

        # 前の日曜日のさらに1週間前が、先週の日曜日
        return datetime.combine(last_sunday, time.min)
    elif keyword == config.KEYWORDS.last_month:
        return datetime(now.year, now.month - 1, 1)
    elif config.KEYWORDS.days in keyword:
        days = zenkaku_to_int_days(keyword)
        return datetime.combine(now - timedelta(days=days), time.min)


def end_datetime(start: datetime, keyword: str) -> datetime:
    if config.KEYWORDS.days in keyword or\
            keyword == config.KEYWORDS.yesterday or\
            keyword == config.KEYWORDS.day_before_yesterday:
        return datetime.combine(start, time.max)
    elif keyword == config.KEYWORDS.last_week:
        return datetime.combine(start + timedelta(days=6), time.max)
    elif keyword == config.KEYWORDS.last_month:
        this_month_1st = datetime(start.year, start.month + 1, 1)
        # 今月の1日から一瞬戻れば先月の最終日時
        return this_month_1st - timedelta(microseconds=1)
    else:
        return datetime.now()
