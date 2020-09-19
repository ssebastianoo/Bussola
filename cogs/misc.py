import discord
from discord.ext import commands

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.help_command = None

    @commands.command(aliases = ["invita"])
    async def invite(self, ctx):
        "invita il bot nel tuo server"

        perms = discord.Permissions(permissions = 18497)
        invite = discord.utils.oauth_url(self.bot.user.id, permissions = perms)

        emb = discord.Embed(title = "Invitami", url = invite, colour = discord.Colour.green())
        await ctx.send(embed = emb)

    @commands.command(aliases = ["aiuto"], hidden = True)
    async def help(self, ctx, *, command = None):
        "lista di comandi"

        emb = discord.Embed(title = "Help", description = "", colour = discord.Colour.green(), timestamp = ctx.message.created_at)
        emb.set_author(name = ctx.author, icon_url = str(ctx.author.avatar_url_as(static_format = "png")))

        for cog in self.bot.cogs:
            cog = self.bot.get_cog(cog)
            ac_cm = [command for command in cog.get_commands() if not command.hidden]

            if len(ac_cm) >= 1:
                emb.description += f"\n**__{cog.qualified_name}__**\n"
                for command in ac_cm:
                    sign = f"{command.name} {command.signature}" if command.signature else command.name
                    emb.description += f"• `{sign}` {command.help}\n"

        await ctx.send(embed = emb)
        
def setup(bot):
    bot.add_cog(Misc(bot))