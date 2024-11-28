from logging import getLogger
import discord
from discord.ext import commands

from utils.config import load_config
from utils.message_parser import extract_file_path
from database.crud import create_toilet, read_toilet, update_toilet, read_category


# 設定の読み込み
config = load_config()

logger = getLogger('bot')


class EventListeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Cog ready.')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        ユーザーがメッセージを投稿したときに呼び出されるイベント。
        """
        logger.info(f'Message received: {message.mentions}.')
        mention_ids = [mention.id for mention in message.mentions]
        # 自分(bot)へのメンションで、WebhookからのメッセージならDBに登録
        if config.MENTION_ID in mention_ids:
            if message.author.bot:
                file_path = extract_file_path(message.content)
                logger.info(f'file_path: {file_path}')
                new = create_toilet(
                    message_id=message.id,
                    video_file_path=file_path,
                )
                logger.info(f'New Toilet record: {new.to_dict()}')
            else:
                # 人間にはうんちでやんす
                await message.channel.send('💩')
        else:
            # メンション以外は無視
            return

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        リアクションが追加されたときに呼び出されるイベント。
        """
        logger.info(f'Reaction added: {reaction.emoji} to message id[{reaction.message.id}] by {user.name}')
        if user.bot:
            return  # Botのリアクションは無視

        # リアクションされたメッセージが、
        # DBに登録のあるemojiか、DBに登録されたメッセージか(Webhookから通知されたものか)確認
        category = read_category(emoji=reaction.emoji)

        if category is None:
            logger.info('Emoji NOT found in the database.')
        else:
            logger.info(f'category: {category.to_dict()}')
            toilet = read_toilet(reaction.message.id)
            if toilet is None:
                logger.info('No record found to update.')
            else:
                update_toilet(toilet.message_id, category.id)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.User):
        pass


# コグのセットアップ
async def setup(bot):
    await bot.add_cog(EventListeners(bot))
