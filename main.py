import discord, os, dotenv
from discord.ext import commands 

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"

intents = discord.Intents.default()
intents.members = True

bot = commands.AutoShardedBot(intents = intents, command_prefix = commands.when_mentioned_or("//"), case_insensitive = True, description = "Bot ufficiale del server Mappa Discord Italia")
bot.load_extension("jishaku")

@bot.event
async def on_ready():
    print("ready as", bot.user)

@bot.check
def dm_check(ctx):
    if not ctx.guild:
        return False

    else:
        return True

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

dotenv.load_dotenv(dotenv_path = ".env")
bot.run(os.environ["token"])