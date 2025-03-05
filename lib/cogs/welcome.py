from discord import Forbidden
from discord.ext.commands import Cog
from discord.ext.commands import command
from ..db import db

class Welcome(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("welcome")

	@Cog.listener()
	async def on_member_join(self, member):
		db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)
		await self.bot.get_channel(1346949926093062297).send(f"Welcome to **{member.guild.name}** {member.mention}! Head over to <#1321019246435631208> to say hi!")

		try:
			await member.send(f"Welcome to **{member.guild.name}**! Enjoy your stay!")
		except Forbidden:
			pass

	@Cog.listener()
	async def on_member_remove(self, member):
		db.execute("DELETE FROM exp WHERE UserID = ?", member.id)
		await self.bot.get_channel(1346949926093062297).send(f"{member.display_name} has left {member.guild.name}.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))