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
        guild = self.bot.get_guild(reaction.guild_id)  # サーバー情報を取得
        user_name = 'Unknown' if guild is None else guild.get_member(reaction.user_id).name
        logger.info(f'Reaction removed: {reaction.emoji} from message id[{reaction.message_id}] by {user_name}')

        # devのときは、かめなしチャンネルには反応しない
        if config.ENVIRONMENT == 'dev' and reaction.channel_id == config.NON_MONITORED_CHANNEL_ID:
            logger.info('Not reply channel')
            return

        # emojiをremoveされたメッセージがDBに登録されているか
        toilet = read_toilet_by_message_id(reaction.message_id)
        if toilet is None:
            # 関係ないレコードなら終了
            logger.info('No record found to update.')
            return
        else:
            channel = self.bot.get_channel(reaction.channel_id)
            reactions = []
            try:
                # すでに付けられているリアクションを取るために、メッセージ取得
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

            # メッセージについているリアクションのリスト
            reactions = [r.emoji for r in message.reactions]
            logger.info(f'reactions: {reactions}')
            # カテゴリー取得
            categories = read_category_all()
            # emojiのリスト(ノーリアクションとノー集計は除くので[2:]にしておく)
            category_emojis = [cat.emoji for cat in categories][2:]
            # すでにリアクションされているemojiのうち、DBに登録されているものを抜き出す
            reacted_emojis_in_db = [emoji for emoji in reactions if emoji in category_emojis]
            logger.info(f'reacted_emojis_in_db: {reacted_emojis_in_db}')

            # emojiが０個になったら、ノーリアクション(id:1)に戻す
            if len(reacted_emojis_in_db) == 0:
                reacted_category_id = 1
            elif len(reacted_emojis_in_db) == 1:
                # 1個だけになったら、そのemoji(category)でレコード更新
                reacted_category_id = read_category(emoji=reacted_emojis_in_db[0]).id
            else:
                await thread.send('リアクションするならどれか１つにしてくれでやんす\n'
                                  f'とりあえず後につけられた方({reacted_emojis_in_db[-1]})で更新しておくでやんす')
                reacted_category_id = read_category(emoji=reacted_emojis_in_db[-1]).id

            # category_idに変化なしなら更新しない
            logger.info(f'reacted_category_id == toilet.category_id: {reacted_category_id == toilet.category_id}')
            if reacted_category_id == toilet.category_id:
                logger.info(f'No update required for the record(id: {toilet.id}).')
                return
            else:
                id_before, id_after = update_toilet(reaction.message_id, reacted_category_id)

            reply = category_update_reply(id_before, id_after, categories)
            await thread.send(reply)


# コグのセットアップ
async def setup(bot: commands.Bot):
    await bot.add_cog(OnRawReactionRemove(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
