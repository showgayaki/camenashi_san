from logging import getLogger
from database.models import Toilet


logger = getLogger('bot')


def builder(term: str, records: list[Toilet]) -> str:
    if len(records) == 0:
        return f'{term}はまだおトイレしていません'

    message = f'{term}のおトイレ結果です\n\n'
    for record in records:
        message += f'{record.created_at.strftime('%Y/%m/%d %H:%M:%S')}: {record.category.name}\n'

    return message
