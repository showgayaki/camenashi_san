from logging import getLogger
import discord
from discord.ext import commands

from utils.config import load_config
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
            # 自分(bot)へのメンションで、WebhookからのメッセージならDBに登録
            if mention.id == config.MENTION_ID and message.author.bot:
                print(message.id)

        if message.author.bot:
            return  # Botのメッセージは無視
        # データベースにログを保存 (例: log_messageはCRUD関数)
        # log_message(message.author.id, message.content)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        リアクションが追加されたときに呼び出されるイベント。
        """
        logger.info(reaction.emoji == ':poop:')
        logger.info(f"Reaction added: {reaction.emoji} by {user.name}")
        if user.bot:
            return  # Botのリアクションは無視

        # データベースにリアクションログを保存 (例: log_reactionはCRUD関数)
        # log_reaction(user.id, reaction.message.id, str(reaction.emoji))


# コグのセットアップ
async def setup(bot):
    await bot.add_cog(EventListeners(bot))
