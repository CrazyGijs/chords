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

with open('prefix.txt', 'r') as fp:
    prefix = fp.read()
bot = commands.Bot(command_prefix=prefix, help_command=None, self_bot=True, intents=intents)
slash = SlashCommand(bot, sync_commands=True)
bot.add_cog(Music(bot))
# bot.add_cog(Help(bot))


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    # print('------')

bot.run(os.getenv("TOKEN"))
