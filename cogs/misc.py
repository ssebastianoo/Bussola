import discord, psutil
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

        emb = discord.Embed(title = "Help", description = f"{self.bot.description}\n", colour = discord.Colour.green(), timestamp = ctx.message.created_at)
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

    @commands.command(aliases = ["informazioni"])
    async def info(self, ctx):
        "informazioni riguardanti il server e bussola"

        content = f"""**Mappa Discord Italia** è un server con l'obbiettivo di listare vari server italiani con lo scopo di aiutare gli utenti di discord italia ad orientarsi ed ha trovare il server adatto a loro. 

**È possibile pubblicare il proprio il server** invitando {self.bot.user.mention} nel vostro server tramite il link 

• <https://bit.ly/bussolabot>

• Usando il comando `//submit descrizione del server` in automatico il bot creerà un invito per il canale di sistema del server. 

• È possibile specificare un canale per l'invito con `//submit descrizione | menzione canale`

• Il server verrà approvato o declinato dai moderatori, riceverete un messaggio da Bussola per sapere l'esito.
"""
        embed = discord.Embed(colour = 0x2f3136, description = content) 
        await ctx.send(embed = embed)

    @commands.command()
    async def stats(self, ctx):
        "statistiche del bot"

        space = "       "
        emb = discord.Embed(description = f"**Server:** `{len(self.bot.guilds)}`\n**Utenti:** `{len(self.bot.users)}`\n**CPU:** `{psutil.cpu_percent()}%`\n**Memoria:** `{psutil.virtual_memory()[2]}%`", colour = 0xffe285)
        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(Misc(bot))
