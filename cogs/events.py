import discord
from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            emb = discord.Embed(description = f"{ctx.author.mention} devi essere un Amministratore per usare questo comando!", colour = discord.Colour.red())
            return await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Events(bot))