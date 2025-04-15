from logging import getLogger
import discord
from discord.ext import commands

from utils.config import ConfigManager
from utils.message_parser import zenkaku_to_int_days, start_datetime, end_datetime, extract_file_path
from utils.reply_builder import registered_new_record_reply, parrot_reply, keywords_reply, records_reply
from database.crud.category import read_category_all
from database.crud.toilet import create_toilet, read_toilet_by_created_at_with_category
from views.period_buttons import PeriodButtons


# 設定の読み込み
config = ConfigManager().config
logger = getLogger('bot')


class OnMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.period_buttons = PeriodButtons()
        self.bot.add_view(self.period_buttons)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        ユーザーがメッセージを投稿したときに呼び出されるイベント。
        """
        # ログに出すのは1行目だけ
        message.content = f'{message.content.splitlines()[0]}...' if '\n' in message.content else message.content
        logger.info(f"Message received: {{'id': {message.id}, 'type': {message.type}, 'message.author.name': {message.author.name}, 'message.content': {message.content}}}")
        mention_ids = [mention.id for mention in message.mentions]

        # devのときは、かめなしチャンネルには反応しない
        if config.ENVIRONMENT == 'dev' and message.channel.id == config.NON_MONITORED_CHANNEL_ID:
            channel_name: str = getattr(message.channel, 'name', 'Unknown')
            logger.info(f'Not reply channel: {channel_name}(id: {message.channel.id})')
            return

        # スレッド作成メッセージはジャマくさいので削除
        if message.type == discord.MessageType.thread_created and\
            message.content.startswith(config.THREAD_PREFIX) and\
                message.content.endswith('.mp4'):
            logger.info('Received a "thread_created" message: Deleting it.')
            try:
                await message.delete()
            except Exception as e:
                logger.error(f'Error occurred: {e}')
            finally:
                return

        # 自分(bot)へのメンションで、WebhookからのメッセージならDBに登録
        if config.MENTION_ID in mention_ids:
            if message.author.bot:
                file_path = extract_file_path(message.content)
                logger.info(f'file_path: {file_path}')
                new = create_toilet(
                    message_id=message.id,
                    video_file_path=file_path,
                    message_url=message.jump_url,
                )

                registered_message = registered_new_record_reply(new, file_path)
                admin_channel = self.bot.get_channel(config.DISCORD_ADMIN_CHANNEL_ID)
                if admin_channel and isinstance(admin_channel, discord.TextChannel):
                    await admin_channel.send(registered_message)
                else:
                    logger.error('Admin channel is not a TextChannel or is None')
            else:
                # 人間にはうんちでやんす
                await message.channel.send('💩')
        else:
            if message.content == config.KEYWORDS.gragh:
                await message.channel.send('どの期間のグラフを出すでやんすか？', view=self.period_buttons)
                return

            # キーワードに合致するか、「⚪︎日前」ならDBからレコードを検索してリプライする
            if message.content in config.KEYWORDS.__dict__.values() or\
                    message.content.endswith(config.KEYWORDS.days):
                reply = await self.reply(message=message)

                if isinstance(reply, list):
                    for r in reply:
                        await message.channel.send(r)
                else:
                    await message.channel.send(reply)
            else:  # キーワードに合致せず
                # ユーザーからの質問なら元気にオウム返し
                if not message.author.bot and\
                        (message.content.endswith('?') or message.content.endswith('？')):
                    await message.channel.send(parrot_reply(message.content))
                else:  # Botの投稿なら無視
                    return

    async def reply(self, message: discord.Message) -> list | str:
        if message is not None and message.content == config.KEYWORDS.keyword:
            reply = keywords_reply(list(config.KEYWORDS.__dict__.values()))
        elif message.content.endswith(config.KEYWORDS.days):  # ⚪︎日前の処理
            days = zenkaku_to_int_days(message.content)
            if isinstance(days, int):
                start = start_datetime(message.content)
                end = end_datetime(start, message.content)

                records = read_toilet_by_created_at_with_category(start, end)
                categories = read_category_all()
                reply = records_reply(message.content, start, end, records, categories)
            else:
                reply = days
        else:
            start = start_datetime(message.content)
            end = end_datetime(start, message.content)

            records = read_toilet_by_created_at_with_category(start, end)
            categories = read_category_all()
            reply = records_reply(message.content, start, end, records, categories)

        return reply


# コグのセットアップ
async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessage(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
