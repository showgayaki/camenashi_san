from logging import getLogger
import discord
from discord.ext import commands

from utils.config import ConfigManager
from views.period_buttons import PeriodButtons


# 設定の読み込み
config = ConfigManager().config
logger = getLogger('bot')


class OnReady(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.period_buttons = PeriodButtons()
        self.bot.add_view(self.period_buttons)

    @commands.Cog.listener()
    async def on_ready(self):
        # スラッシュコマンドの同期
        try:
            synced = await self.bot.tree.sync(guild=discord.Object(id=config.DISCORD_GUILD_ID))
            logger.info(f'Synced {len(synced)} command(s) successfully.')
        except Exception as e:
            logger.error(f'Failed to sync commands: {e}')

        logger.info('Cog ready.')


# コグのセットアップ
async def setup(bot: commands.Bot):
    await bot.add_cog(OnReady(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
