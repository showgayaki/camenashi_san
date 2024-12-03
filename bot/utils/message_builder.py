from logging import getLogger
from database.models import Toilet


logger = getLogger('bot')


def builder(term: str, records: list[Toilet]) -> str:
    if len(records) == 0:
        return f'{term}はおトイレしていません'

    message = f'{term}のおトイレ結果です\n```'
    for record in records:
        message += f'{record.created_at.strftime('%Y/%m/%d %H:%M:%S')}: {record.category.name}\n'

    return f'{message}```'
