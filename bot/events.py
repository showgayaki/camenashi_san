from logging import getLogger
import discord
from discord.ext import commands

from utils.config_manager import ConfigManager
from utils.message_parser import extract_file_path
from utils.reply_builder import parrot_reply, category_update_reply
from database.crud.toilet import create_toilet, read_toilet_by_message_id, update_toilet
from database.crud.category import read_category, read_category_all
from commands.search_records import SearchRecords


# 設定の読み込み
config = ConfigManager().config
logger = getLogger('bot')


class EventListeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # スラッシュコマンドの同期
        try:
            synced = await self.bot.tree.sync(guild=discord.Object(id=config.DISCORD_GUILD_ID))
            logger.info(f'Synced {len(synced)} command(s) successfully.')
        except Exception as e:
            logger.error(f'Failed to sync commands: {e}')

        logger.info('Cog ready.')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        ユーザーがメッセージを投稿したときに呼び出されるイベント。
        """
        # ログに出すのは1行目だけ
        message_content = f'{message.content.splitlines()[0]}...' if '\n' in message.content else message.content
        logger.info(f'Message received from {message.author.name}: {message_content}')
        mention_ids = [mention.id for mention in message.mentions]

        # devのときは、かめなしチャンネルには反応しない
        if config.ENVIRONMENT == 'dev' and message.channel.id == config.NON_MONITORED_CHANNEL_ID:
            logger.info(f'Not reply channel: {message.channel.name}(id: {message.channel.id})')
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

                admin_channel = self.bot.get_channel(config.DISCORD_ADMIN_CHANNEL_ID)
                await admin_channel.send(f'新しいおトイレコード(ID: {new.id})が登録されました')
            else:
                # 人間にはうんちでやんす
                await message.channel.send('💩')
        else:
            # キーワードに合致するか、「⚪︎日前」ならDBからレコードを検索してリプライする
            if message.content in config.KEYWORDS.__dict__.values() or\
                    message.content.endswith(config.KEYWORDS.days):
                search_records_cog: SearchRecords = self.bot.get_cog('SearchRecords')
                reply = await search_records_cog.reply(message=message)

                if isinstance(reply, list):
                    for r in reply:
                        await message.channel.send(r)
                else:
                    await message.channel.send(reply)

            else:  # キーワードに合致せず
                # Botの投稿なら無視
                if message.author.bot:
                    return
                elif '?' in message.content or '？' in message.content:
                    # ユーザーからの質問なら元気にオウム返し
                    await message.channel.send(parrot_reply(message.content))
                else:
                    return

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
                    name=f'スッドレ {toilet.video_file_path.split('/')[-1]}',
                    auto_archive_duration=1440,  # アーカイブまでの時間（分単位で設定）
                )

            # category_idを更新
            id_before, id_after = update_toilet(toilet.message_id, category.id)
            reply = category_update_reply(id_before, id_after, read_category_all())
            await thread.send(reply)

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
                    name=f'スッドレ {toilet.video_file_path.split('/')[-1]}',
                    auto_archive_duration=1440,  # アーカイブまでの時間（分単位で設定）
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
    await bot.add_cog(EventListeners(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
