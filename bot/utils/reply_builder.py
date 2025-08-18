from logging import getLogger
from datetime import datetime
from pathlib import Path
import re

from utils.config import ConfigManager
from database.models import Toilet, Category, ToiletCategory
from database.crud.category import read_category


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
    admin_message = f'Newおﾄｲﾚｺｰﾄﾞ(ID: {new_record.id})が登録されました'
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
    # 文末の「か[? | ？]」「なの[? | ？]」「でしょう[? | ？]」を`！`に変換
    reply = re.sub(r'(か|なの|でしょう)([?？]?)$', '！', message)
    return reply


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
        category_links = []
        for cat in record.categories:
            # name = f'[{cat.name}]({record.message_url})' if record.message_url else cat.name
            category_links.append(cat.name)

        # - リンクあり
        # `2025/01/01 00:00:00: `[しーしー・うんち](https://hoge):external_link:
        # - リンクなし
        # `2025/01/01 00:00:00: `しーしー・うんち
        category_name = f'[{'・'.join(category_links)}]({record.message_url}) {config.EMOJI_EXTERNAL_LINK}'\
            if record.message_url else f'{'・'.join(category_links)}'
        results += f'`{record.created_at.strftime("%Y/%m/%d %H:%M:%S")}:` {category_name}\n'

        for cat in record.categories:
            if cat.emoji is None:
                continue
            total[cat.emoji] += 1

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


def category_update_reply(toilet_categories: list[ToiletCategory] | None) -> str:
    logger.debug(
        f'toilet_categories: {
            [t for t in toilet_categories]
            if toilet_categories is not None
            else toilet_categories
        }'
    )

    reply = 'おトイレの種別が'
    if toilet_categories is None:
        reply += 'うまいこと取得できなかったでやんす'
    elif len(toilet_categories) == 1:
        category = read_category(id=toilet_categories[0].category_id)
        reply += f'「{category.name}」になったでやんす'
    elif len(toilet_categories) > 1:
        for i, record in enumerate(toilet_categories):
            category = read_category(id=record.category_id)
            reply += f'「{category.name}」' if i == 0 else f'と「{category.name}」'

        reply += 'になったでやんす'
    else:
        reply = 'おトイレの種別の変更に失敗したでやんす'

    return reply


def graph_reply(period: str, start: datetime, end: datetime) -> str:
    period = _period(period, start, end)
    return f'{period}のおトイレグラフでやんす'
