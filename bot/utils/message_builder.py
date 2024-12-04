from logging import getLogger

from utils.config import load_config
from database.models import Toilet


config = load_config()
logger = getLogger('bot')


def keywords_message(keywords: list) -> str:
    message = '反応できるキーワードは以下でやんす\n```'
    for k in keywords:
        message += f'⚪︎{k}\n' if k == config.KEYWORDS.days else f'{k}\n'

    return f'{message}```'


def records_message(term: str, records: list[Toilet]) -> str:
    if len(records) == 0:
        return f'{term}はおトイレしていません'

    message = f'{term}のおトイレ結果です\n```'
    for record in records:
        message += f'{record.created_at.strftime('%Y/%m/%d %H:%M:%S')}: {record.category.name}\n'

    return f'{message}```'
