import discord
from discord.ext import commands

class DMS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_messages = True)
    @commands.command(hidden = True)
    async def close(self, ctx, *, channel: discord.TextChannel = None):
        "chiudi un ticket"
        
        channel = channel or ctx.channel

        if channel.category.id == 756944434322735174:
            user = self.bot.get_user(int(channel.topic))
            emb = discord.Embed(description = f"Il ticket è stato chiuso da **{str(ctx.author)}**", colour = discord.Colour.red())
            await user.send(embed = emb)
            await ctx.send(f"Ticket **{channel.name}** chiuso:thumbup:")
            await channel.delete()
        
        else:
            await channel.send("mhh... quel canale non è un ticket!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return 

        guild = self.bot.get_guild(606861507237773322)
        category = self.bot.get_channel(756944434322735174)

        if not message.guild:

            if str(message.author.id) in [g.topic for g in category.channels]:
                channel = discord.utils.get(category.channels, topic = str(message.author.id))

            else:
                channel = await guild.create_text_channel(name = str(message.author), category = category, topic = message.author.id, sync_permissions = True)
                await message.channel.send("Il tuo messaggio è stato inoltrato allo staff, attendi una risposta.")
            
            emb = discord.Embed(description = f"**{message.author}**: {message.content}", colour = 0x2F3136)
            if message.attachments:
                if message.attachments[0].filename.endswith(("png", "jpg", "jpeg", "webp", "gif")):
                    emb.set_image(url = message.attachments[0].url)

                else:
                    emb.description += f"\n\n[{message.attachments[0].filename}]({message.attachments[0].url})"
            await channel.send(embed = emb)

        elif message.guild == guild:
            if message.channel.category == category:
                user = self.bot.get_user(int(message.channel.topic))
                if not user:
                    return

                else:
                    emb = discord.Embed(description = f"**{message.author}**: {message.content}", colour = 0x2F3136)
                    if message.attachments:
                        if message.attachments[0].filename.endswith(("png", "jpg", "jpeg", "webp", "gif")):
                            emb.set_image(url = message.attachments[0].url)

                        else:
                            emb.description += f"\n\n[{message.attachments[0].filename}]({message.attachments[0].url})"
                    await user.send(embed = emb)

def setup(bot):
    bot.add_cog(DMS(bot))
