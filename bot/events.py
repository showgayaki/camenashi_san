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

# from typing import Union
# import discord
# from .bot import config, client


# @client.event
# async def on_ready():
#     print(f'We have logged in as {client.user}')


# @client.event
# async def on_message(message):
#     print('on_message!!!')
#     if message.author == client.user:
#         return

#     if message.content.startswith('$hello'):
#         await message.channel.send('Hello!')


# # リアクションされた時に動作する処理
# @client.event
# async def on_reaction_add(reaction: discord.Reaction, user: Union[discord.Member, discord.User]):
#     # リアクションされたメッセージ
#     message = reaction.message
#     print(message.author)
#     # 自分自身に対するリアクションは通知しない
#     # if (message.author == user):
#     #     return
#     # 左からリアクションされたメッセージの投稿主、リアクション、リアクションしたユーザの表示名、
#     # メッセージの内容、メッセージへのリンク
#     msg = f"{message.author.mention} {reaction}\nFrom:{user.display_name} \
#           \nMessage:{message.content}\n{message.jump_url}"

#     channel = client.get_channel(config.DISCORD_CHANNEL_ID)
#     # メンションを指定のチャンネルに投稿
#     await channel.send(msg)
