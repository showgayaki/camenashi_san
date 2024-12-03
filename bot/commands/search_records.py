from logging import getLogger
from datetime import datetime, time, timedelta
import discord
from discord import app_commands, Interaction
from discord.ext import commands

from utils.config import load_config
from utils.message_builder import builder
from database.crud.toilet import read_toilet_by_created_at_with_category


config = load_config()
logger = getLogger('bot')


class SearchRecords(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='today', description='今日のおトイレを検索します')
    async def today(self, interaction: Interaction):
        await self.reply(interaction=interaction)

    @app_commands.command(name='week', description='今週のおトイレを検索します')
    async def week(self, interaction: Interaction):
        await self.reply(interaction=interaction)

    @app_commands.command(name='month', description='今月のおトイレを検索します')
    async def month(self, interaction: Interaction):
        await self.reply(interaction=interaction)

    async def reply(self, interaction: Interaction = None, message: discord.Message = None) -> None:
        # interactionがNoneじゃなければスラッシュコマンド
        if interaction:
            term = getattr(config.KEYWORDS, interaction.command.name)
            logger.info(f'interaction.command.name: {interaction.command.name}')
        else:
            term = message.content

        start = self._start_datetime(term)
        # start = datetime(2024, 12, 1, 0, 0, 0)

        records = read_toilet_by_created_at_with_category(start)
        logger.info(f'Records ids: {[record.id for record in records]}')

        reply = builder(term, records)
        if interaction:
            await interaction.response.send_message(reply)
        elif message:
            await message.channel.send(reply)

    def _start_datetime(self, keyword) -> datetime:
        now = datetime.now()
        if keyword == '今日':
            return datetime.combine(now.date(), time.min)
        elif keyword == '今週':
            # 今日が何曜日かを取得 (月曜日=0, 日曜日=6)
            today_weekday = now.weekday()
            # 前の日曜日までの日数を計算
            days_until_last_sunday = 0 if (6 - today_weekday - 7) == -7 else (6 - today_weekday - 7)
            last_sunday = now + timedelta(days=days_until_last_sunday)

            return datetime.combine(last_sunday, time.min)
        elif keyword == '今月':
            return datetime(now.year, now.month, 1)


async def setup(bot: commands.Bot):
    await bot.add_cog(SearchRecords(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
