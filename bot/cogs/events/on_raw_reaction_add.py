from logging import getLogger
import discord
from discord.ext import commands

from utils.config import ConfigManager
from utils.reply_builder import category_update_reply
from database.crud.toilet import read_toilet_by_message_id, update_toilet
from database.crud.category import read_category, read_category_all


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
        if reaction.member.bot:
            return  # Botのリアクションは無視

        # devのときは、かめなしチャンネルには反応しない
        if config.ENVIRONMENT == 'dev' and reaction.channel_id == config.NON_MONITORED_CHANNEL_ID:
            logger.info('Not reply channel')
            return

        # リアクションされたメッセージが、
        # DBに登録されたメッセージか(Webhookから通知されたものか)、DBに登録のあるemojiか確認
        toilet = read_toilet_by_message_id(reaction.message_id)

        if toilet is None:
            logger.info('No record found to update.')
            return
        else:
            category = read_category(emoji=reaction.emoji)

            if category is None:
                logger.info('Reacted emoji NOT found in the database.')
                # DBに登録のないemojiの場合は、集計対象から外すcategoryを付与する
                category = read_category(include_in_summary=False)
            else:
                logger.info(f'Reacted emoji: {category.to_dict()}')

            # DBに登録されているメッセージに、DBに登録されているemojiがリアクションされたら
            # スレッドを開始して返信する
            guild = self.bot.get_guild(reaction.guild_id)
            channel = guild.get_channel(reaction.channel_id)
            try:
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
                    name=f'{config.THREAD_PREFIX} {toilet.video_file_path.split('/')[-1]}',
                    auto_archive_duration=config.AUTO_ARCHIVE_DURATION,  # アーカイブまでの時間（分単位で設定）
                )

            # category_idを更新
            id_before, id_after = update_toilet(toilet.message_id, category.id)
            reply = category_update_reply(id_before, id_after, read_category_all())
            await thread.send(reply)


# コグのセットアップ
async def setup(bot: commands.Bot):
    await bot.add_cog(OnRawReactionAdd(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
