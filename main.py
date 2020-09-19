import discord, os, dotenv
from discord.ext import commands 

os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True" 
os.environ["JISHAKU_HIDE"] = "True"

bot = commands.AutoShardedBot(command_prefix = commands.when_mentioned_or("//"), case_insensitive = True, description = "Bot ufficiale del server Mappa Discord Italia")
bot.load_extension("jishaku")

@bot.event
async def on_ready():
    print("ready as", bot.user)

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

dotenv.load_dotenv(dotenv_path = ".env")
bot.run(os.environ["token"])