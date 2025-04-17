from logging import getLogger
import discord
from discord.ext import commands

from utils.config import ConfigManager
from utils.reply_builder import category_update_reply
from database.crud.toilet import read_toilet_by_message_id_with_categories
from database.crud.category import read_category
from database.crud.toilet_category import (
    read_toilet_categories_by_tolet_id_all,
    update_toilet_category,
    create_toilet_category,
)


# 設定の読み込み
config = ConfigManager().config
logger = getLogger('bot')


class OnRawReactionAdd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction: discord.RawReactionActionEvent):
        """
        リアクションが追加されたときに呼び出されるイベント。
        """
        logger.info(f'Reaction added: {reaction.emoji} to message id[{reaction.message_id}] by {reaction.member.name}')

        if reaction.guild_id is None:
            logger.error('reaction.guild_id is None')
            return
        # devのときは、かめなしチャンネルには反応しない
        if config.ENVIRONMENT == 'dev' and reaction.channel_id == config.NON_MONITORED_CHANNEL_ID:
            logger.info('Not reply channel')
            return

        if reaction.member is not None and reaction.member.bot:
            return  # Botのリアクションは無視

        # リアクションされたメッセージが、
        # DBに登録されたメッセージか(Webhookから通知されたものか)、DBに登録のあるemojiか確認
        toilet_record = read_toilet_by_message_id_with_categories(reaction.message_id)

        if toilet_record is None:
            logger.info('No record found to update.')
            return
        else:
            category = read_category(emoji=str(reaction.emoji))
            if category is None:
                # 関係ない絵文字なら終了
                logger.info('Reacted emoji NOT found in the database.')
                return
            else:
                logger.info(f'Reacted emoji: {category.to_dict()}')

            # サーバー・チャンネル情報を取得
            guild = self.bot.get_guild(reaction.guild_id)
            channel = guild.get_channel(reaction.channel_id)
            # リアクションされたメッセージを取得
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

            # 「ノー集計」emojiがリアクションされたら、そのemoji以外を削除する
            if category.include_in_summary is False:
                await self.remove_reactions(message, reaction)

            # category_idを更新、または追加
            toilet_category_records = read_toilet_categories_by_tolet_id_all(toilet_record.id)
            if toilet_category_records[0].category_id == 1:
                # おトイレカテゴリーが「1」のときは、「ノーリアクション」だけのはずなので
                # 「ノーリアクション」のレコードを書き換える
                update_toilet_category(toilet_record.id, category.id)
            else:
                create_toilet_category(toilet_record.id, category.id)

            # 削除後のtoilet_categoryのレコードを取得してリプライ作成
            updated_toilet_category_record = read_toilet_categories_by_tolet_id_all(toilet_record.id)
            reply = category_update_reply(updated_toilet_category_record)

            await thread.send(reply)

    async def remove_reactions(self, message: discord.Message, reaction: discord.RawReactionActionEvent) -> None:
        for reaction_obj in message.reactions:
            # ❌ は残す
            if str(reaction_obj.emoji) == str(reaction.emoji):
                continue

            async for user in reaction_obj.users():
                if user.id == reaction.user_id:
                    await message.remove_reaction(reaction_obj.emoji, user)


# コグのセットアップ
async def setup(bot: commands.Bot):
    await bot.add_cog(OnRawReactionAdd(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
