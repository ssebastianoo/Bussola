import discord, aiosqlite, asyncio
from discord.ext import commands

class Servers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(aliases = ["invia"], usage = "<descrizione> | [invito]")
    @commands.has_permissions(administrator = True)
    async def submit(self, ctx, *, descrizione = None):
        "invia il tuo server nella lista, dovrà essere approvato da un moderatore."

        emb = discord.Embed()

        if not descrizione:
            emb.description = "Uso errato del comando, usare `//submit descrizione del server`"
            emb.colour = discord.Colour.red()
            return await ctx.send(embed = emb)

        if not ctx.guild.me.guild_permissions.create_instant_invite:
            emb = discord.Embed(description = f"{ctx.author.mention} devo avere il permesso per creare inviti nel server!", colour = discord.Colour.red())
            return await ctx.send(embed = emb)

        async with ctx.typing():

            converter = commands.TextChannelConverter()
            descrizione = descrizione.split(" | ")

            if len(descrizione) > 1:
                try:
                    channel_invite = await converter.convert(ctx, descrizione[1])

                except:
                    emb = discord.Embed(description = f"{ctx.author.mention} **{descrizione[1]}** non è un canale testuale valido!", colour = discord.Colour.red())
                    return await ctx.send(embed = emb)

            else:
                channel_invite = None

            descrizione = descrizione[0]

            if ctx.guild.member_count < 60:
                emb.title = "Il server deve avere minimo 60 membri!"
                emb.colour = discord.Colour.red()
                return await ctx.send(embed = emb)

            async with aiosqlite.connect("data/servers.db") as db:
                data = await db.execute("select id from servers")
                data = await data.fetchall()

                queue = await db.execute("select id from queue")
                queue = await queue.fetchall() 

            if ctx.guild.id in [int(server[0]) for server in data] or ctx.guild.id in [int(server[0]) for server in queue]:
                emb.title = f"Questo server è già stato inviato!"
                emb.colour = discord.Colour.red()
                return await ctx.send(embed = emb)

            emb.colour = 0xffe285
            emb.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
            emb.set_image(url = 'https://www.mappadiscordit.ga/Divisorio_Moduli.png')
            emb.set_thumbnail(url = str(ctx.guild.icon_url_as(static_format = "png")))

            emb.title = f'**{ctx.guild.name}**\n┏╋━━◥◣◆◢◤━━╋┓'
            emb.add_field(name = '__Proprietario__', value = str(ctx.guild.owner), inline = False)

            admins = [str(member) for member in ctx.guild.members if member.guild_permissions.administrator and not member.bot and member.id != ctx.guild.owner.id]
            
            if len(admins) > 0:
                emb.add_field(name = '__Amministratori__', value = "\n".join(admins), inline = False)
            emb.add_field(name = "__Data di Fondazione__", value = ctx.guild.created_at.strftime("%d %B %Y"), inline = False)
            emb.add_field(name = "__Descrizione del Server__", value = descrizione, inline = False)

            if channel_invite:
                invite = await channel_invite.create_invite()

            else:
                if ctx.guild.system_channel:
                    invite = await ctx.guild.system_channel.create_invite()

                else:
                    for channel in ctx.guild.text_channels:
                        try:
                            invite = await channel.create_invite()
                            break

                        except:
                            pass

            emb.add_field(name = '__Link Server__', value = f'*Per accedere al server clicca [qui]({invite})*', inline = False)

            async with aiosqlite.connect("data/servers.db") as db:
                await db.execute(f"INSERT into queue (id) VALUES ({ctx.guild.id})")
                await db.commit()

            channel = self.bot.get_channel(756634984818671747)
            msg = await channel.send(embed = emb, content = f"{ctx.guild.id} | {ctx.author.id} | <@&756635091928744087>")
            await msg.add_reaction("✅")
            await msg.add_reaction("❎")

            emb = discord.Embed(title = "Il tuo server è stato messo in queue, riceverai un messaggio per sapere se è stato approvato o meno.", colour = discord.Colour.green())
            await ctx.send(embed = emb)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        if payload.channel_id != 756634984818671747:
            return 

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        msg = message.content.split(" | ")
        guild = self.bot.get_guild(int(msg[0]))
        user = self.bot.get_user(int(msg[1]))
        ch = self.bot.get_channel(payload.channel_id)
        channel = self.bot.get_channel(756640447522275358)

        if payload.member.id == self.bot.user.id:
            return

        if payload.emoji.name == "✅":

            for letter in guild.name:
                if letter.lower() not in "abcdefghijklmnopqrstuvwxyz":
                    pass
                else:
                    channel_name = letter
                    break

            alfabetico = self.bot.get_channel(756799536286007327)
            alfabetico = discord.utils.get(alfabetico.channels, name = channel_name.lower())

            msg = await alfabetico.send(embed = message.embeds[0])
            # await numerico.send(embed = message.embeds[0])
            await message.clear_reactions()
            emb = discord.Embed(title = f"Il tuo server **{guild.name}** è stato approvato!", colour = discord.Colour.green())
            await user.send(embed = emb)

            async with aiosqlite.connect("data/servers.db") as db:
                await db.execute(f"INSERT into servers (id, channel, message) VALUES ({guild.id}, {msg.channel.id}, {msg.id})")
                await db.execute(f"UPDATE queue set id = 0 where id = {guild.id}")
                await db.commit()

            admins = [member for member in guild.members if member.guild_permissions.administrator and not member.bot]
            role = message.guild.get_role(758027050744545461)

            for admin in admins:
                m = message.guild.get_member(admin.id)
                if m:
                    await m.add_roles(role)
                else:
                    pass

        elif payload.emoji.name == "❎":
            await message.clear_reactions()

            ragione = await ch.send("Ragione?")
            
            def check(m):
                return m.channel.id == ch.id and m.author.id == payload.member.id

            try:
                msg = await self.bot.wait_for("message", check = check, timeout = 60)
            
            except asyncio.TimeoutError:
                await message.add_reaction("✅")
                await message.add_reaction("❎")

                return await ch.send("Tempo Scaduto!")

            async with aiosqlite.connect("data/servers.db") as db:
                await db.execute(f"UPDATE queue set id = 0 where id = {guild.id}")
                await db.commit()

            reason = msg.content

            emb = discord.Embed(title = f"• Il tuo server **{guild.name}** è stato declinato!\n• {reason}", colour = discord.Colour.red())
            await user.send(embed = emb)
            await ragione.edit("Server Declinato✅")

    @commands.command(aliases = ["pagina"])
    async def page(self, ctx):
        "ritorna un link per arrivare al messaggio del proprio server"

        async with aiosqlite.connect("data/servers.db") as db:
            data = await db.execute(f"select * from servers where id = {ctx.guild.id}")
            data = await data.fetchall()

        if len(data) == 0 or int(data[0][0]) == 0:
            emb = discord.Embed(title = "Il tuo server non è in lista!", colour = discord.Colour.red())
            return await ctx.send(embed = emb)

        channel = self.bot.get_channel(int(data[0][1]))
        message = await channel.fetch_message(int(data[0][2]))

        emb = discord.Embed(description = f"[{ctx.guild.name}]({message.jump_url})", colour = discord.Colour.green())
        await ctx.send(embed = emb)

    @commands.group(aliases = ["aggiorna"], invoke_without_command = True)
    @commands.has_permissions(administrator = True)
    async def update(self, ctx, *, descrizione = None):
        "aggiorna il server nella pagina"

        async with aiosqlite.connect("data/servers.db") as db:
            data = await db.execute(f"select * from servers where id = {ctx.guild.id}")
            data = await data.fetchall()

        if len(data) == 0 or int(data[0][0]) == 0:
            emb = discord.Embed(title = "Il tuo server non è in lista!", colour = discord.Colour.red())
            return await ctx.send(embed = emb)

        channel = self.bot.get_channel(int(data[0][1]))
        message = await channel.fetch_message(int(data[0][2]))

        if not descrizione:
            descrizione = message.embeds[0].fields[3].value

        emb = discord.Embed()

        emb.colour = 0xffe285
        emb.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
        emb.set_image(url = 'https://www.mappadiscordit.ga/Divisorio_Moduli.png')
        emb.set_thumbnail(url = str(ctx.guild.icon_url_as(static_format = "png")))

        emb.title = f'**{ctx.guild.name}**\n┏╋━━◥◣◆◢◤━━╋┓'
        emb.add_field(name = '__Proprietario__', value = str(ctx.guild.owner), inline = False)

        admins = [str(member) for member in ctx.guild.members if member.guild_permissions.administrator and not member.bot and member.id != ctx.guild.owner.id]
        
        if len(admins) > 0:
            emb.add_field(name = '__Amministratori__', value = "\n".join(admins), inline = False)
        emb.add_field(name = "__Data di Fondazione__", value = ctx.guild.created_at.strftime("%d %B %Y"), inline = False)
        emb.add_field(name = "__Descrizione del Server__", value = descrizione, inline = False)
        emb.add_field(name = '__Link Server__', value = message.embeds[0].fields[4].value, inline = False)

        await message.edit(embed = emb)
        emb = discord.Embed(title = "Server aggiornato con successo!", description = f"Puoi vedere il server [qui]({message.jump_url}).", colour = discord.Colour.green())
        await ctx.send(embed = emb)

    @update.command(aliases = ["invito"])
    @commands.has_permissions(administrator = True)
    async def invite(self, ctx, *, channel: discord.TextChannel = None):
        "aggiorna l'invito nel server"

        if not channel:
            if ctx.guild.system_channel:
                channel = ctx.guild.system_channel
                invite = await channel.create_invite()

            else:
                for textchannel in ctx.guild.text_channels:
                    try:
                        invite = await textchannel.create_invite()

                    except:
                        pass

        else:
            invite = await channel.create_invite()

        async with aiosqlite.connect("data/servers.db") as db:
            data = await db.execute(f"select * from servers where id = {ctx.guild.id}")
            data = await data.fetchall()

        if len(data) == 0 or int(data[0][0]) == 0:
            emb = discord.Embed(title = "Il tuo server non è in lista!", colour = discord.Colour.red())
            return await ctx.send(embed = emb)

        channel = self.bot.get_channel(int(data[0][1]))
        message = await channel.fetch_message(int(data[0][2]))

        emb = discord.Embed()

        emb.colour = 0xffe285
        emb.set_footer(text = ctx.guild.name, icon_url = ctx.guild.icon_url)
        emb.set_image(url = 'https://www.mappadiscordit.ga/Divisorio_Moduli.png')
        emb.set_thumbnail(url = str(ctx.guild.icon_url_as(static_format = "png")))

        emb.title = f'**{ctx.guild.name}**\n┏╋━━◥◣◆◢◤━━╋┓'
        emb.add_field(name = '__Proprietario__', value = str(ctx.guild.owner), inline = False)

        admins = [str(member) for member in ctx.guild.members if member.guild_permissions.administrator and not member.bot and member.id != ctx.guild.owner.id]
        
        if len(admins) > 0:
            emb.add_field(name = '__Amministratori__', value = "\n".join(admins), inline = False)
        emb.add_field(name = "__Data di Fondazione__", value = ctx.guild.created_at.strftime("%d %B %Y"), inline = False)
        emb.add_field(name = "__Descrizione del Server__", value = message.embeds[0].fields[3].value, inline = False)
        emb.add_field(name = '__Link Server__', value = f'*Per accedere al server clicca [qui]({invite})*', inline = False)

        await message.edit(embed = emb)
        emb = discord.Embed(title = "Server aggiornato con successo!", description = f"Puoi vedere il server [qui]({message.jump_url}).", colour = discord.Colour.green())
        await ctx.send(embed = emb)

    @commands.command(aliases = ["elimina"])
    @commands.has_permissions(administrator = True)
    async def delete(self, ctx):
        "elimina il server dalla lista"

        async with aiosqlite.connect("data/servers.db") as db:
            data = await db.execute(f"select channel, message from servers where id = {ctx.guild.id}")
            data = await data.fetchall()

            if len(data) == 0:
                emb = discord.Embed(title = "Il tuo server non è in lista!", colour = discord.Colour.red())
                return await ctx.send(embed = emb)

        emb = discord.Embed(title = f"Sei sicuro di voler eliminare il server **{ctx.guild.name}**?", colour = discord.Colour.green())
        msg = await ctx.send(embed = emb)
        await msg.add_reaction("✅")
        await msg.add_reaction("❎")

        def check(reaction, user):
            return reaction.message.id == msg.id and str(reaction.emoji) in ["✅", "❎"] and user.id == ctx.author.id

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check = check, timeout = 60)

        except asyncio.TimeoutError:
            emb = discord.Embed(title = "Tempo scaduto!", colour = discord.Colour.red())
            return await msg.edit(embed = emb)

        if str(reaction.emoji) == "✅":
            async with ctx.typing():
                async with aiosqlite.connect("data/servers.db") as db:
                    data = await db.execute(f"select channel, message from servers where id = {ctx.guild.id}")
                    data = await data.fetchall()

                    if len(data) == 0:
                        emb = discord.Embed(title = "Il tuo server non è in lista!", colour = discord.Colour.red())
                        return await msg.edit(embed = emb)

                    channel = self.bot.get_channel(int(data[0][0]))
                    message = await channel.fetch_message(int(data[0][1]))

                    await message.delete()

                    await db.execute(f"SELECT channel, message from servers")
                    await db.execute(f"UPDATE servers SET id = 0 where id = {ctx.guild.id}")

                    await db.commit()

            emb.title = "Il tuo server è stato eliminato con successo!"
            await msg.edit(embed = emb)

        elif str(reaction.emoji) == "❎":
            emb.title = "Ok, non eliminerò il server!"
            await msg.edit(embed = emb)
        
def setup(bot):
    bot.add_cog(Servers(bot))