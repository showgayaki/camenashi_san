from logging import getLogger
import discord
from discord.ext import commands

from utils.config import ConfigManager
from utils.logger import load_looger


config = ConfigManager().config
load_looger()

logger = getLogger('bot')

# intentsの設定 (必要な権限に応じて調整)
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.members = True

# Botの初期化
bot = commands.Bot(command_prefix='!', intents=intents)

# コグのロード
initial_extensions = [
    'events',
    'commands.search_records',
    'commands.admin',
]


async def main():
    # 拡張機能（コグ）のロード
    logger.info('Loading Bot Extensions.')
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
        except Exception as e:
            logger.error(f'Failed to load extension {extension}. Error: {e}')

    # configの内容を出力(パスワードやトークンは除く)
    app_config = {key: '' if 'PASS' in key or 'TOKEN' in key else value for key, value in vars(config).items()}
    logger.info(f'App Config: {app_config}')

    # Botの起動
    logger.info('Starting Bot.')
    await bot.start(config.DISCORD_TOKEN)


if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt.')
