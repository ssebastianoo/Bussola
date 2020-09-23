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

        else:
            print(error)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = self.bot.get_channel(758303451699740695)
        text = f"**{str(self.bot.user)}** è entrato in **{guild.name}**"
        text = discord.utils.escape_mentions(text)
        await channel.send(text)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = self.bot.get_channel(758303451699740695)
        text = f"**{str(self.bot.user)}** è uscito da **{guild.name}**"
        text = discord.utils.escape_mentions(text)
        await channel.send(text)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(758303451699740695)
        text = f"**{str(member)}** è entrato"
        text = discord.utils.escape_mentions(text)
        await channel.send(text)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(758303451699740695)
        text = f"**{str(member)}** è uscito"
        text = discord.utils.escape_mentions(text)
        await channel.send(text)

def setup(bot):
    bot.add_cog(Events(bot))