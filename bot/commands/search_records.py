from logging import getLogger
from datetime import datetime
import discord
from discord import app_commands, Interaction
from discord.ext import commands

from utils.config_manager import ConfigManager
from utils.reply_builder import keywords_reply, records_reply
from utils.message_parser import zenkaku_to_int_days, start_datetime, end_datetime
from database.crud.toilet import read_toilet_by_created_at_with_category


config = ConfigManager().config
logger = getLogger('bot')


class SearchRecords(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='today', description='今日のおトイレを検索します')
    async def today(self, interaction: Interaction):
        reply = await self.reply(interaction=interaction)
        await interaction.response.send_message(reply)

    @app_commands.command(name='this_week', description='今週のおトイレを検索します')
    async def this_week(self, interaction: Interaction):
        reply = await self.reply(interaction=interaction)
        await interaction.response.send_message(reply)

    @app_commands.command(name='this_month', description='今月のおトイレを検索します')
    async def this_month(self, interaction: Interaction):
        reply = await self.reply(interaction=interaction)
        await interaction.response.send_message(reply)

    async def reply(self, interaction: Interaction = None, message: discord.Message = None) -> list | str:
        # interactionがNoneじゃなければスラッシュコマンド
        if interaction:
            keyword = getattr(config.KEYWORDS, interaction.command.name)
            logger.info(f'interaction.command.name: {interaction.command.name}')
        else:
            keyword = message.content

        if message is not None and message.content == config.KEYWORDS.keyword:
            reply = keywords_reply(config.KEYWORDS.__dict__.values())
        elif keyword.endswith(config.KEYWORDS.days):  # ⚪︎日前の処理
            days = zenkaku_to_int_days(keyword)
            if isinstance(days, int):
                now = datetime.now()
                start = start_datetime(now, keyword)
                end = end_datetime(now, keyword)

                records = read_toilet_by_created_at_with_category(start, end)
                reply = records_reply(keyword, start, end, records)
            else:
                reply = days
        else:
            now = datetime.now()
            start = start_datetime(now, keyword)
            end = end_datetime(now, keyword)

            records = read_toilet_by_created_at_with_category(start, end)
            reply = records_reply(keyword, start, end, records)

        return reply


async def setup(bot: commands.Bot):
    await bot.add_cog(SearchRecords(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
