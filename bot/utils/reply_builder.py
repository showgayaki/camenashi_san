from logging import getLogger
from datetime import datetime
from pathlib import Path

from utils.config import ConfigManager
from database.models import Toilet, Category


config = ConfigManager().config
logger = getLogger('bot')


def _period(period: str, start: datetime, end: datetime) -> str:
    # ⚪︎日前と昨日・一昨日のときは、日にちをかっこ書きで入れておく
    if config.KEYWORDS.days in period or\
            period == config.KEYWORDS.yesterday or\
            period == config.KEYWORDS.day_before_yesterday:
        period = f'{period}（{start.strftime("%m/%d")}）'
    elif period == config.KEYWORDS.last_week or\
            period == config.KEYWORDS.last_month:
        # 先週と先月の場合は期間を入れておく
        period = f'{period}（{start.strftime("%m/%d")}〜{end.strftime("%m/%d")}）'

    return period


def registered_new_record_reply(new_record: Toilet, file_path: str) -> str:
    admin_message = f'新しいおトイレコード(ID: {new_record.id})が登録されました'
    file_created_at = Path(file_path).name.split('_')[0]
    record_created_at = new_record.created_at.strftime('%Y%m%d-%H%M%S')
    logger.info(f'file_created_at: {file_created_at}, record_created_at: {record_created_at}')

    if file_created_at != record_created_at:
        admin_message += ('\n'
                          'ファイル名の作成日時と新しいレコードのcreated_atが一致しません\n'
                          f'ID: {new_record.id} のcreated_atを確認してください\n'
                          '```\n'
                          f'from file : {file_created_at}\n'
                          f'new record: {record_created_at}\n'
                          '```')

    return admin_message


def parrot_reply(message: str) -> str:
    return (message.translate(str.maketrans('?？', '！！'))
            .replace('か', '').replace('なの', '').replace('でしょう', ''))


def keywords_reply(keywords: list) -> str:
    message = '反応できるキーワードは以下でやんす\n```'
    for k in keywords:
        message += f'⚪︎{k}(一〜九の漢数字もいけるでやんす)\n' if k == config.KEYWORDS.days else f'{k}\n'

    return f'{message}```'


def records_reply(period: str, start: datetime, end: datetime, records: list[Toilet], categories: list[Category]) -> list | str:
    if len(records) == 0:
        return f'{period}はおトイレしていません'

    period = _period(period, start, end)
    total = {category.emoji: 0 for category in categories if category.emoji is not None}

    results = ''
    for record in records:
        # message_urlがあればリンクをつける
        category_name = f'[{record.category.name}]({record.message_url}) {config.EMOJI_EXTERNAL_LINK}'\
            if record.message_url else record.category.name
        results += f'`{record.created_at.strftime('%Y/%m/%d %H:%M:%S')}:` {category_name}\n'

        if record.category.emoji is None:
            continue
        else:
            total[record.category.emoji] += 1

    total_str = '    '.join([f'{key}`: {value}回`' for key, value in total.items() if value > 0])

    reply_str = (f'{period}のおトイレ結果です\n'
                 f'{total_str}\n'
                 f'{results}')

    # メッセージ1回あたりの文字数制限があるので、検証
    if len(reply_str) < config.MESSAGE_LIMIT_LENGTH:
        return reply_str

    logger.info(f'The message length exceeds {config.MESSAGE_LIMIT_LENGTH} characters.')
    reply_tmp = ''
    reply = []
    for line in reply_str.splitlines():
        # 文字数制限超えた？
        if len(reply_tmp + line) > config.MESSAGE_LIMIT_LENGTH:
            reply.append(f'{reply_tmp}\n')
            reply_tmp = f'{line}\n'
        else:
            reply_tmp += f'{line}\n'
    reply.append(reply_tmp)

    return reply


def category_update_reply(id_before: int, id_after: int, categories: list[Category]) -> str:
    logger.info(f'len(categories): {len(categories)}')
    if id_before and id_after:
        emoji_before = ''.join([cat.name for cat in categories if cat.id == id_before])
        emoji_after = ''.join([cat.name for cat in categories if cat.id == id_after])

        return f'おトイレの種別が「{emoji_before}」から「{emoji_after}」に変更されたでやんす'
    else:
        return 'おトイレの種別の変更に失敗したでやんす'


def graph_reply(period: str, start: datetime, end: datetime) -> str:
    period = _period(period, start, end)
    return f'{period}のおトイレグラフでやんす'
