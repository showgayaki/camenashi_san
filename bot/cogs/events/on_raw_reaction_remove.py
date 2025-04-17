from logging import getLogger
import discord
from discord.ext import commands

from utils.config import ConfigManager
from utils.reply_builder import category_update_reply
from database.crud.toilet import read_toilet_by_message_id_with_categories
from database.crud.category import read_category
from database.crud.toilet_category import (
    update_toilet_category,
    delete_toilet_category,
    read_toilet_categories_by_tolet_id_all,
)


# 設定の読み込み
config = ConfigManager().config
logger = getLogger('bot')


class OnRawReactionRemove(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction: discord.RawReactionActionEvent):
        """
        リアクションが削除されたときに呼び出されるイベント。

        ・user_nameの取得
        reaction.memberは追加イベントのときだけなので、guild.get_member()で取る。
        Discord Developer PortalのBotの設定で
        Privileged Gateway Intents
          - Server Members Intent: 有効
        にする。
        んでbot.pyで、intents.members = Trueする
        """
        if reaction.guild_id is None:
            logger.error('reaction.guild_id is None')
            return
        # devのときは、かめなしチャンネルには反応しない
        if config.ENVIRONMENT == 'dev' and reaction.channel_id == config.NON_MONITORED_CHANNEL_ID:
            logger.info('Not reply channel')
            return

        guild = self.bot.get_guild(reaction.guild_id)
        member = guild.get_member(reaction.user_id) if guild else None
        logger.info(
            f"Reaction removed: {reaction.emoji} to message id[{reaction.message_id}] by {member.name if member else 'Unknown User'}"
        )

        # emojiをremoveされたメッセージがDBに登録されているか
        toilet_record = read_toilet_by_message_id_with_categories(reaction.message_id)
        if toilet_record is None:
            # 関係ないメッセージなら終了
            logger.info('No record found to update.')
            return
        else:
            category = read_category(emoji=str(reaction.emoji))
            if category is None:
                # 関係ない絵文字なら終了
                logger.info('Removed emoji NOT found in the database.')
                return
            else:
                logger.info(f'Removed emoji: {category.to_dict()}')

            # サーバー・チャンネル情報を取得
            channel = guild.get_channel(reaction.channel_id)
            # リアクションが削除されたメッセージを取得
            try:
                if isinstance(channel, discord.TextChannel):
                    message = await channel.fetch_message(reaction.message_id)
            except Exception as e:
                logger.error(f'Error occurred: {e}')
                return

            if message.thread:
                # 既存のスレッドがある場合
                thread = message.thread
            else:
                # スレッドがない場合、新しいスレッドを作成
                thread = await message.create_thread(
                    name=f'{config.THREAD_PREFIX} {toilet_record.video_file_path.split("/")[-1]}',
                    auto_archive_duration=config.AUTO_ARCHIVE_DURATION,  # アーカイブまでの時間（分単位で設定）
                )

            # category_idを更新、または削除
            toilet_category_records = read_toilet_categories_by_tolet_id_all(toilet_record.id)
            if len(toilet_category_records) == 1:
                # おトイレカテゴリーが1つのときは、「ノーリアクション」に戻したいので
                # 「ノーリアクション(id: 1)」に書き換える
                update_toilet_category(toilet_record.id, 1)
            else:
                # 削除されたemojiのtoilet_categoryレコードを削除
                delete_toilet_category(toilet_record.id, category.id)

            # 削除後のtoilet_categoryのレコードを取得してリプライ作成
            updated_toilet_category_record = read_toilet_categories_by_tolet_id_all(toilet_record.id)
            reply = category_update_reply(updated_toilet_category_record)

            await thread.send(reply)


# コグのセットアップ
async def setup(bot: commands.Bot):
    await bot.add_cog(OnRawReactionRemove(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
