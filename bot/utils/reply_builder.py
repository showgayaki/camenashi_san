from logging import getLogger
from datetime import datetime

from utils.config_manager import ConfigManager
from database.models import Toilet, Category


config = ConfigManager().config
logger = getLogger('bot')


def parrot_reply(message: str) -> str:
    return (message.translate(str.maketrans('?？', '！！'))
            .replace('か', '').replace('なの', '').replace('でしょう', ''))


def keywords_reply(keywords: list) -> str:
    message = '反応できるキーワードは以下でやんす\n```'
    for k in keywords:
        message += f'⚪︎{k}(一〜九の漢数字もいけるでやんす)\n' if k == config.KEYWORDS.days else f'{k}\n'

    return f'{message}```'


def records_reply(term: str, start: datetime, end: datetime, records: list[Toilet]) -> str:
    if len(records) == 0:
        return f'{term}はおトイレしていません'

    # ⚪︎日前と昨日・一昨日のときは、日にちをかっこ書きで入れておく
    if config.KEYWORDS.days in term or\
            term == config.KEYWORDS.yesterday or\
            term == config.KEYWORDS.day_before_yesterday:
        term = f'{term}（{start.strftime("%m/%d")}）'
    elif term == config.KEYWORDS.last_week or\
            term == config.KEYWORDS.last_month:
        # 先週と先月の場合は期間を入れておく
        term = f'{term}（{start.strftime("%m/%d")}〜{end.strftime("%m/%d")}）'
    else:
        term = term

    total = {}
    results = '```\n'
    for record in records:
        results += f'{record.created_at.strftime('%Y/%m/%d %H:%M:%S')}: {record.category.name}\n'

        if record.category.emoji is None:
            continue
        else:
            if record.category.emoji not in total:
                total[record.category.emoji] = 1
            else:
                total[record.category.emoji] += 1

    results += '\n```'
    total_str = '    '.join([f'{key}`: {value}回`' for key, value in total.items()])

    return (f'{term}のおトイレ結果です\n'
            f'{total_str}\n'
            f'{results}\n')


def category_update_reply(id_before: int, id_after: int, categories: list[Category]) -> str:
    logger.info(f'len(categories): {len(categories)}')
    if id_before and id_after:
        emoji_before = ''.join([cat.name for cat in categories if cat.id == id_before])
        emoji_after = ''.join([cat.name for cat in categories if cat.id == id_after])

        return f'おトイレの種別が「{emoji_before}」から「{emoji_after}」に変更されたでやんす'
    else:
        return 'おトイレの種別の変更に失敗したでやんす'
