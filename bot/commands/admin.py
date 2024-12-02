from logging import getLogger
import sys
import importlib
import discord
from discord.ext import commands

from utils.config import load_config

# 設定の読み込み
config = load_config()
logger = getLogger('bot')


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        """
        すべての拡張機能をホットリロードするコマンド
        """
        self._reload_modules()
        extensions = list(self.bot.extensions.keys())
        logger.info('Starting reload extensions.')

        reload_extensions = []
        for ext in extensions:
            try:
                await self.bot.reload_extension(ext)
                reload_extensions.append(ext)
            except Exception as e:
                logger.error(f'Failed to reload extension: {ext}\nError: {e}')

        logger.info(f'Reloaded extensions: {reload_extensions}')

    def _reload_modules(self):
        logger.info('Starting reload modules.')
        prefixes = [
            'database',
            'utils',
        ]

        reloaded_modules = []
        for prefix in prefixes:
            for name, module in list(sys.modules.items()):
                if name.startswith(prefix) and module is not None:
                    importlib.reload(module)
                    reloaded_modules.append(name)

        logger.info(f'Reloaded modules: {reloaded_modules}')


async def setup(bot):
    await bot.add_cog(AdminCog(bot), guild=discord.Object(id=config.DISCORD_GUILD_ID))
