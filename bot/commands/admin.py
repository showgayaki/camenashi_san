from discord.ext import commands


class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def reload(self, ctx):
        """
        すべての拡張機能をホットリロードするコマンド
        """
        try:
            for extension in self.bot.extensions:
                await self.bot.reload_extension(extension)

            await ctx.send(f'Reloaded extensions: {self.bot.extensions.keys()}')
        except Exception as e:
            await ctx.send(f'Failed to reload extension: {extension}\nError: {e}')


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
