from logging import getLogger
import discord

from database.crud.toilet import read_toilet_by_created_at_with_category
from database.crud.category import read_category_all
from utils.config import ConfigManager
from utils.message_parser import start_datetime, end_datetime
from utils.graph import draw_toilet_records
from utils.reply_builder import graph_reply


config = ConfigManager().config
logger = getLogger('bot')


class PeriodButtons(discord.ui.View):
    def __init__(self, timeout=None) -> None:
        super().__init__(timeout=timeout)

        periods = config.KEYWORDS.periods()
        for period in periods:
            label = getattr(config.KEYWORDS, period)
            self.add_item(PeriodButton(label, period))


class PeriodButton(discord.ui.Button):
    def __init__(self, label: str, period: str) -> None:
        super().__init__(label=label, custom_id=period, style=discord.ButtonStyle.secondary)

    async def callback(self, interaction: discord.Interaction) -> None:
        logger.info(f'{interaction.user.display_name} pushed {self.label} button.')

        start = start_datetime(self.label)
        end = end_datetime(start, self.label)
        records = read_toilet_by_created_at_with_category(start, end)

        if not records:
            logger.info(f'The records for the specified period({self.custom_id}) were not found.')
            reply = f'{self.label}はおトイレしていません'
            await interaction.response.send_message(reply)
            return

        logger.info(f'Found {len(records)} records for the specified period({self.custom_id}).')
        categories = read_category_all(include_in_summary=True)
        graph_image_path = draw_toilet_records(self.label, self.custom_id, records, categories)
        logger.info(f'Graph image path: {graph_image_path}')

        reply = graph_reply(self.label, start, end)
        try:
            await interaction.response.send_message(
                content=reply,
                file=discord.File(graph_image_path)
            )
        except Exception as e:
            logger.error(f'Failed to post message: {e}')
        finally:
            logger.info(f'Deleting {graph_image_path}')
            if graph_image_path.exists():
                graph_image_path.unlink()  # ファイルが存在する場合のみ削除
