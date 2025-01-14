from help import Help
from music import Music
import os
import discord
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.members = True


with open('prefix.txt', 'r') as fp:
    prefix = fp.read()

bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command('help')
bot.add_cog(Music(bot))
bot.add_cog(Help(bot))


@bot.event
async def on_ready():
    a = f'Logged in as {bot.user} (ID: {bot.user.id})'
    print(a)
    print('-' * len(a))
    # await bot.change_presence(activity=discord.Game('Tijd voor matige muziek.'))
    await bot.change_presence(activity=discord.Activity(name='Matige muziek', type=discord.ActivityType.listening))

bot.run(os.getenv("TOKEN"))