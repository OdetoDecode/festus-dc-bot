from datetime import datetime, timedelta, timezone
from discord import Embed
from discord.ext import commands, tasks

numbers = ("1️⃣", "2⃣", "3⃣", "4⃣", "5⃣", 
           "6⃣", "7⃣", "8⃣", "9⃣", "🔟")


class Polls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polls = []
        self.check_polls.start()
    
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("poll")

    @commands.command(name="createpoll", aliases=["mkpoll"])
    @commands.has_permissions(manage_guild=True)
    async def create_poll(self, ctx, minutes: int, question: str, *options):
        if len(options) > 10:
            await ctx.send("You can only supply a maximum of 10 options.")
            return
        
        embed = Embed(
            title="Poll",
            description=question,
            colour=ctx.author.colour,
            timestamp=datetime.now(timezone.utc)
        )

        fields = [
            ("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
            ("Instructions", "React to cast a vote!", False)
        ]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        message = await ctx.send(embed=embed)

        for emoji in numbers[:len(options)]:
            await message.add_reaction(emoji)

        self.polls.append((message.channel.id, message.id, datetime.now(timezone.utc) + timedelta(minutes=minutes)))

    @tasks.loop(minutes=1)
    async def check_polls(self):
        now = datetime.now(timezone.utc)
        for poll in self.polls[:]:
            channel_id, message_id, end_time = poll
            if now >= end_time:
                await self.complete_poll(channel_id, message_id)
                self.polls.remove(poll)

    async def complete_poll(self, channel_id, message_id):
        channel = self.bot.get_channel(channel_id)
        if channel:
            message = await channel.fetch_message(message_id)
            most_voted = max(message.reactions, key=lambda r: r.count, default=None)

            if most_voted:
                await channel.send(f"The results are in! The most popular option was **{most_voted.emoji}** with **{most_voted.count - 1} votes!**")
            else:
                await channel.send("Poll ended, but no votes were cast.")

    @check_polls.before_loop
    async def before_check_polls(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Polls(bot))

