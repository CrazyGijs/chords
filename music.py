import asyncio
import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext, cog_ext
from discord.ext.commands import Bot
from discord.ext.commands.core import command
from random import shuffle
from youtube_dl import YoutubeDL
from roles import voice_channel_moderator_roles

guild_id = [378542493547102209]


class Music(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

        self.is_playing = False
        self.current_song = None
        self.music_queue = []
        self.skip_votes = set()

        self.YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True", "cookiefile": "cookies.txt"}
        self.FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                               "options": "-vn"}
        self.vc = ""

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if not member.id == self.bot.user.id:
            return

        elif before.channel is None:
            voice = self.vc
            time = 0
            while True:
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing:
                    time = 0
                if time == 20:
                    await voice.disconnect()
                if not voice.is_connected():
                    break

    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)["entries"][0]
            except Exception:
                return False

        return {"source": info["formats"][0]["url"], "title": info["title"]}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]["source"]

            self.current_song = self.music_queue.pop(0)

            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(),
            )
        else:
            self.is_playing = False
            self.current_song = None

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]["source"]

            if self.vc == "" or not self.vc.is_connected() or self.vc is None:
                self.vc = await self.music_queue[0][1].connect()
            else:
                await self.vc.move_to(self.music_queue[0][1])

            play_embed = discord.Embed(title=f"Now playing",
                                       description=f":arrow_forward: Playing **{self.music_queue[0][0]['title']}** -- "
                                                   f"requested by {self.music_queue[0][2]}", color=discord.Color.blue())
            await ctx.send(embed=play_embed)

            self.vc.play(
                discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS),
                after=lambda e: self.play_next(),
            )
            self.current_song = self.music_queue.pop(0)

        else:
            self.is_playing = False
            self.current_song = None

    @cog_ext.cog_slash(name="play", description="Plays a selected song from youtube \U0001F3B5", guild_ids=guild_id)
    async def _play(self, ctx, input):  # ctx: SlashContext,
        query = "".join(input)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword.")
            else:
                queue_embed = discord.Embed(title=f"Queue",
                                            description=f':headphones: **{song["title"]}** has been added to the queue '
                                                        f'by {ctx.author.mention}', color=discord.Color.blue())
                self.music_queue.append([song, voice_channel, ctx.author.mention])
                # if len(self.music_queue) > 1:
                await ctx.send(embed=queue_embed)
                if self.is_playing is False:
                    await self.play_music(ctx)

    # @commands.command(
    #     name="cp",
    #     help="Shows the currently playing song \U0001F440",
    #     aliases=["playing"],
    # )
    @cog_ext.cog_slash(name="cp", description="Shows the currently playing song \U0001F440", guild_ids=guild_id)
    async def _cp(self, ctx):
        msg = "No music playing" if self.current_song is None else f"""Currently Playing: 
        **{self.current_song[0]['title']}** -- added by {self.current_song[2]}\n"""
        await ctx.send(msg)

    # @commands.command(
    #     name="q",
    #     help="Shows the music added in list/queue \U0001F440",
    #     aliases=["queue"],
    # )
    @cog_ext.cog_slash(name="q", description="Shows the music added in list/queue \U0001F440", guild_ids=guild_id)
    async def _q(self, ctx):
        retval = ""
        for (i, m) in enumerate(self.music_queue):
            retval += f"""{i + 1}. **{m[0]['title']}** -- added by {m[2]}\n"""

        if retval != "":
            embed_return = discord.Embed(title="Queue", description=retval)
            await ctx.send(embed=embed_return)
        else:
            q_ret = discord.Embed(title=f"Queue",
                                  description="No music in queue", color=discord.Color.blue())
            await ctx.send(embed=q_ret)

    @cog_ext.cog_slash(name="cq", description="Clears the queue", guild_ids=guild_id)
    # @commands.command(name="cq", help="Clears the queue", aliases=["clear"])
    async def _cq(self, ctx):
        self.music_queue = []
        await ctx.send("""***Queue cleared !***""")

    # @commands.command(name="shuffle", help="Shuffles the queue")
    @cog_ext.cog_slash(name="shuffle", description="Shuffles the queue", guild_ids=guild_id)
    async def _shuffle(self, ctx):
        shuffle(self.music_queue)
        await ctx.send("""***Queue shuffled !***""")

    # @commands.command(
    #     name="s", help="Skips the current song being played", aliases=["skip"]
    # )
    @cog_ext.cog_slash(name="skip", description="Skips the current song being played", guild_ids=guild_id)
    async def _skip(self, ctx):
        if self.vc != "" and self.vc:
            await ctx.send("""***Skipped current song !***""")
            self.skip_votes = set()
            self.vc.stop()
            await self.play_music(ctx)

    # @commands.command(
    #     name="voteskip",
    #     help="Vote to skip the current song being played",
    #     aliases=["vs"],
    # )
    @cog_ext.cog_slash(name="voteskip", description="Vote to skip the current song being played", guild_ids=guild_id)
    async def _voteskip(self, ctx):
        if ctx.voice_client is None:
            return
        num_members = len(ctx.voice_client.channel.members) - 1
        self.skip_votes.add(ctx.author.id)
        votes = len(self.skip_votes)
        if votes >= num_members / 2:
            await ctx.send(f"Vote passed by majority ({votes}/{num_members}).")
            await self.skip(ctx)

    # @commands.command(
    #     name="l",
    #     help="Commands the bot to leave the voice channel \U0001F634",
    #     aliases=["leave"],
    # )

    # @cog_ext.has_any_role(*voice_channel_moderator_roles)
    @cog_ext.cog_slash(name="leave", description="Commands the bot to leave the voice channel \U0001F634",
                       guild_ids=guild_id)
    async def _leave(self, ctx):
        if self.vc.is_connected():
            await ctx.send("""**Tschüss**""")
            await self.vc.disconnect(force=True)

    # @commands.command(
    #     name="pn", help="Moves the song to the top of the queue \U0001F4A5"
    # )
    # @commands.has_any_role(*voice_channel_moderator_roles)
    @cog_ext.cog_slash(name="playnext", description="Moves the song to the top of the queue \U0001F4A5",
                       guild_ids=guild_id)
    async def _playnext(self, ctx, args):
        query = "".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword."
                )
            else:
                vote_message = await ctx.send(
                    f":headphones: **{song['title']}** will be added to the top of the queue by {ctx.author.mention}\n"
                    "You have 30 seconds to vote by reacting :+1: on this message.\n"
                    "If more than 50% of the people in your channel agree, the request will be up next!"
                )
                await vote_message.add_reaction("\U0001F44D")
                await asyncio.sleep(30)
                voters = len(voice_channel.members)
                voters = voters - 1 if self.vc else voters
                result_vote_msg = await ctx.fetch_message(vote_message.id)
                votes = next(react for react in result_vote_msg.reactions if str(react.emoji) == "\U0001F44D").count - 1
                if votes >= voters / 2:
                    self.music_queue.insert(
                        0,
                        [song, voice_channel, ctx.author.mention]
                    )
                    await ctx.send(
                        f":headphones: **{song['title']}** will be added played next!"
                    )
                else:
                    self.music_queue.append(
                        [song, voice_channel, ctx.author.mention]
                    )
                    await ctx.send(
                        f":headphones: **{song['title']}** will be played add the end of the queue!"
                    )

                if self.is_playing is False or (
                        self.vc == "" or not self.vc.is_connected() or self.vc == None
                ):
                    await self.play_music(ctx)

    """Pause the currently playing song."""

    # @commands.command(name="pause", help="Pause the currently playing song")
    # @commands.has_any_role(*voice_channel_moderator_roles)
    @cog_ext.cog_slash(name="pause", description="Pause the currently playing song",
                       guild_ids=guild_id)
    async def _pause(self, ctx):
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send("I am currently playing nothing!", delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f":pause_button:  {ctx.author.mention} Paused the song!")

    """Resume the currently playing song."""

    # @commands.command(name="resume", help="Resume the currently playing song")
    # @commands.has_any_role(*voice_channel_moderator_roles)
    @cog_ext.cog_slash(name="resume", description="Resume the currently playing song",
                       guild_ids=guild_id)
    async def _resume(self, ctx):
        vc = ctx.voice_client

        if not vc or vc.is_playing():
            return await ctx.send("I am already playing a song!", delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f":play_pause:  {ctx.author.mention} Resumed the song!")

    # @commands.command(
    #     name="r",
    #     help="removes song from queue at index given. \U0001F4A9",
    #     aliases=["remove"],
    # )
    # @commands.has_any_role(*voice_channel_moderator_roles)
    @cog_ext.cog_slash(name="remove", description="Removes song from queue at index given. \U0001F4A9",
                       guild_ids=guild_id)
    async def _remove(self, ctx, args):
        query = "".join(args)
        index = 0
        negative = True if (query[0] == "-") else False
        if not negative:
            for i in range(len(query)):
                convert = (int)(query[i])
                index = index * 10 + convert
        index -= 1

        if negative:
            await ctx.send("Index cannot be less than one")
        elif index >= len(self.music_queue):
            await ctx.send("Wrong index. Indexed music not present in the queue")
        else:
            await ctx.send(
                f""":x: Music at index {query} removed by {ctx.author.mention}"""
            )
            self.music_queue.pop(index)

    # @commands.command(
    #     name="rep",
    #     help="Restarts the current song. \U000027F2",
    #     aliases=["restart"],
    # )
    # @commands.has_any_role(*voice_channel_moderator_roles)
    @cog_ext.cog_slash(name="restart", description="Restarts the current song. \U000027F2", guild_ids=guild_id)
    async def _restart(self, ctx):
        song = []
        if self.current_song is not None:
            song = self.current_song[0]
            voice_channel = ctx.author.voice.channel
            self.music_queue.insert(0, [song, voice_channel, ctx.author.mention])
            self.vc.stop()
            if len(self.music_queue) > 0:
                self.is_playing = True

                m_url = self.music_queue[0][0]["source"]

                if self.vc == "" or not self.vc.is_connected() or self.vc == None:
                    self.vc = await self.music_queue[0][1].connect()
                    await ctx.send("No music added")
                else:
                    await self.vc.move_to(self.music_queue[0][1])

                    await ctx.send(f""":repeat: Replaying **{self.music_queue[0][0]['title']}**
                         -- requested by {self.music_queue[0][2]}""")

                    self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
                    self.current_song = self.music_queue.pop(0)

        else:
            self.is_playing = False
            self.current_song = None
            await ctx.send(f""":x: No music playing""")
