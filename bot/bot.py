from logging import getLogger
import discord
from discord.ext import commands

from utils.config import load_config
from utils.logger import load_looger

config = load_config()
load_looger()

logger = getLogger(__name__)

# intentsの設定 (必要な権限に応じて調整)
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True

# Botの初期化
bot = commands.Bot(command_prefix='!', intents=intents)

# コグのロード
initial_extensions = [
    'admin',
    'events',  # イベント処理
    # 'commands.example',  # コマンド例
]


async def main():
    # 拡張機能（コグ）のロード
    logger.info('Loading Bot Extensions.')
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)  # 非同期でロード
        except Exception as e:
            logger.error(f'Failed to load extension {extension}. Error: {e}')

    # Botの起動
    logger.info('Starting Bot.')
    await bot.start(config.DISCORD_TOKEN)


if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('KeyboardInterrupt.')
