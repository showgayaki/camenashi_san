from logging import getLogger
from datetime import datetime, time, timedelta
import discord
from discord import app_commands, Interaction
from discord.ext import commands

from utils.config import load_config
from utils.message_builder import keywords_message, records_message
from utils.message_parser import zenkaku_to_int_days
from database.crud.toilet import read_toilet_by_created_at_with_category


config = load_config()
logger = getLogger('bot')


class SearchRecords(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='today', description='今日のおトイレを検索します')
    async def today(self, interaction: Interaction):
        await self.reply(interaction=interaction)

    @app_commands.command(name='this_week', description='今週のおトイレを検索します')
    async def this_week(self, interaction: Interaction):
        await self.reply(interaction=interaction)

    @app_commands.command(name='this_month', description='今月のおトイレを検索します')
    async def this_month(self, interaction: Interaction):
        await self.reply(interaction=interaction)

    async def reply(self, interaction: Interaction = None, message: discord.Message = None) -> None:
        # interactionがNoneじゃなければスラッシュコマンド
        if interaction:
            keyword = getattr(config.KEYWORDS, interaction.command.name)
            logger.info(f'interaction.command.name: {interaction.command.name}')
        else:
            keyword = message.content

        if message.content == config.KEYWORDS.keyword:
            reply = keywords_message(config.KEYWORDS.__dict__.values())
        else:
            now = datetime.now()
            start = self._start_datetime(now, keyword)
            end = self._end_datetime(now, keyword)

            records = read_toilet_by_created_at_with_category(start, end)
            logger.info(f'Records ids: {[record.id for record in records]}')

            # ⚪︎日前のときは、日にちをかっこ書きで入れておく
            if config.KEYWORDS.days in keyword:
                keyword = f'{keyword}（{start.strftime("%m/%d")}）'
            elif config.KEYWORDS.last_week in keyword or\
                    config.KEYWORDS.last_month in keyword:
                # 先週と先月の場合は期間を入れておく
                keyword = f'{keyword}（{start.strftime("%m/%d")}〜{end.strftime("%m/%d")}）'

            reply = records_message(keyword, records)

        if interaction:
            await interaction.response.send_message(reply)
        elif message:
            await message.channel.send(reply)

    def _start_datetime(self, now: datetime, keyword: str) -> datetime:
        if keyword == config.KEYWORDS.today:
            return datetime.combine(now.date(), time.min)
        elif keyword == config.KEYWORDS.this_week:
            # 今日が何曜日かを取得 (月曜日=0, 日曜日=6)
            today_weekday = now.weekday()
            # 前の日曜日までの日数を計算
            days_until_last_sunday = 0 if (6 - today_weekday - 7) == -7 else (6 - today_weekday - 7)
            last_sunday = now + timedelta(days=days_until_last_sunday)

            return datetime.combine(last_sunday, time.min)
        elif keyword == config.KEYWORDS.this_month:
            return datetime(now.year, now.month, 1)
        elif keyword == config.KEYWORDS.yesterday:
            return datetime.combine(now - timedelta(days=1), time.min)
        elif keyword == config.KEYWORDS.last_week:
            # 今日が何曜日かを取得 (月曜日=0, 日曜日=6)
            today_weekday = now.weekday()
            # 前の日曜日までの日数を計算
            days_until_last_sunday = 0 if (6 - today_weekday - 7) == -7 else (6 - today_weekday - 7)
            last_sunday = now + timedelta(days=days_until_last_sunday)

            # 前の日曜日のさらに1週間前が、先週の日曜日
            return datetime.combine(last_sunday - timedelta(weeks=1), time.min)
        elif keyword == config.KEYWORDS.last_month:
            return datetime(now.year, now.month - 1, 1)
        elif config.KEYWORDS.days in keyword:
            days = zenkaku_to_int_days(keyword)
            return datetime.combine(now - timedelta(days=days), time.min)

    def _end_datetime(self, now: datetime, keyword: str) -> datetime:
        if config.KEYWORDS.days in keyword:
            days = zenkaku_to_int_days(keyword)
        elif keyword == config.KEYWORDS.yesterday:
            days = 1
        elif keyword == config.KEYWORDS.last_week:
            # 今日が何曜日かを取得 (月曜日=0, 日曜日=6)
            today_weekday = now.weekday()
            # 前の土曜日までの日数を計算
            days_until_last_saturday = 0 if (5 - today_weekday - 7) == -7 else (5 - today_weekday - 7)
            last_saturday = now + timedelta(days=days_until_last_saturday)

            return datetime.combine(last_saturday, time.max)
        elif keyword == config.KEYWORDS.last_month:
            this_month_1st = datetime(now.year, now.month, 1)
            # 今月の1日から一瞬戻れば先月の最終日時
            return this_month_1st + timedelta(microseconds=-1)
        else:
            return now

        return datetime.combine(now - timedelta(days=days), time.max)


async def setup(bot: commands.Bot):
    await bot.add_cog(SearchRecords(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
