from help import Help
from music import Music
import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.members = True

# bot = commands.Bot(command_prefix="-", intents=intents)
# bot.remove_command("help")
with open('prefix.txt', 'r') as fp:
    prefix = fp.read()
bot = commands.Bot(command_prefix=prefix, self_bot=True, help_command=False, intents=intents)
slash = SlashCommand(bot, sync_commands=True)
# bot.remove_command('help')
bot.add_cog(Music(bot))
bot.add_cog(Help(bot))

bot.run(os.getenv("TOKEN"))
