from logging import getLogger
import discord
from discord.ext import commands

from utils.config import load_config
from utils.message_parser import extract_file_path
from database.crud import create_toilet, update_toilet, read_category

# 設定の読み込み
config = load_config()

logger = getLogger(__name__)


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
        logger.info('Message received.')
        for mention in message.mentions:
            logger.info(f'mention.id: {mention.id}')
            # 自分(bot)へのメンションで、WebhookからのメッセージならDBに登録
            if mention.id == config.MENTION_ID:
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
        logger.info(reaction.emoji == ':poop:')
        logger.info(f"Reaction added: {reaction.emoji} by {user.name}")
        if user.bot:
            return  # Botのリアクションは無視


# コグのセットアップ
async def setup(bot):
    await bot.add_cog(EventListeners(bot))
