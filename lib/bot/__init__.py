from asyncio import sleep
from datetime import datetime,timezone
from glob import glob
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Embed, File, DMChannel, Intents
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown)
from discord.ext.commands import when_mentioned_or, command, has_permissions
from ..db import db

OWNER_IDS = [843777158572671006]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

def get_prefix(bot, message):
	prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
	return when_mentioned_or(prefix)(bot, message)

class Ready(object):
	def __init__(self):
		for cog in COGS:
			setattr(self, cog, False)

	def ready_up(self, cog):
		setattr(self, cog, True)
		print(f" {cog} cog ready")

	def all_ready(self):
		return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
	def __init__(self):
		self.ready = False
		self.cogs_ready = Ready()
		self.guild = None
		self.scheduler = AsyncIOScheduler()

		try:
			with open("./data/banlist.txt", "r", encoding="utf-8") as f:
				self.banlist = [int(line.strip()) for line in f.readlines()]
		except FileNotFoundError:
			self.banlist = []

		db.autosave(self.scheduler)
		super().__init__(command_prefix=get_prefix, owner_ids=OWNER_IDS, intents=Intents.all())

	async def setup(self):
		for cog in COGS:
			await self.load_extension(f"lib.cogs.{cog}")
			print(f" {cog} cog loaded")
		print("setup complete")

	def update_db(self):
		db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
					 ((guild.id,) for guild in self.guilds))
		db.multiexec("INSERT OR IGNORE INTO exp (UserID) VALUES (?)",
					 ((member.id,) for member in self.guild.members if not member.bot))

		to_remove = []
		stored_members = db.column("SELECT UserID FROM exp")
		for id_ in stored_members:
			if not self.guild.get_member(id_):
				to_remove.append(id_)

		db.multiexec("DELETE FROM exp WHERE UserID = ?",
					 ((id_,) for id_ in to_remove))

		db.commit()

	def run(self, version):
		self.VERSION = version
		print("running setup...")

		with open("./lib/bot/token.0", "r", encoding="utf-8") as tf:
			self.TOKEN = tf.read().strip()  
		import asyncio

		try:
			asyncio.run(self.start_bot())  
		except KeyboardInterrupt:
			print("Bot shutting down...")

	async def start_bot(self):
		await self.setup() 
		async with self:
			await self.start(self.TOKEN)

		
	async def process_commands(self, message):
		ctx = await self.get_context(message, cls=Context)

		if ctx.command is not None and ctx.guild is not None:
			if message.author.id in self.banlist:
				await ctx.send("You are banned from using commands.")
			elif not self.ready:
				await ctx.send("I'm not ready to receive commands. Please wait a few seconds.")
			else:
				await self.invoke(ctx)

	async def rules_reminder(self):
		await self.stdout.send("Remember to adhere to the rules!")

	async def on_connect(self):
		print("bot connected")

	async def on_disconnect(self):
		print("bot disconnected")

	async def on_error(self, err, *args, **kwargs):
		if err == "on_command_error":
			await args[0].send("Something went wrong.")
		await self.stdout.send("An error occured.")
		raise

	async def on_command_error(self, ctx, exc):
		if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
			pass

		elif isinstance(exc, MissingRequiredArgument):
			await ctx.send("One or more required arguments are missing.")

		elif isinstance(exc, CommandOnCooldown):
			await ctx.send(f"That command is on {str(exc.cooldown.type).split('.')[-1]} cooldown. Try again in {exc.retry_after:,.2f} secs.")

		elif hasattr(exc, "original"):
			if isinstance(exc.original, Forbidden):
				await ctx.send("I do not have permission to do that.")
			else:
				raise exc
		else:
			raise exc

	async def on_ready(self):
		if not self.ready:
			self.guild = self.get_guild(1321019244867096657)#server id
			self.stdout = self.get_channel(1321019246435631208)#general channel id
			self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
			self.scheduler.start()
			self.update_db()
			
			while not self.cogs_ready.all_ready():
				await sleep(0.5)
			await self.stdout.send("Now online!")
			self.ready = True
			print("bot ready")

		else:
			print("bot reconnected")

	async def on_message(self, message):
		if not message.author.bot:
			if isinstance(message.channel, DMChannel):
				if len(message.content) < 50:
					await message.channel.send("Your message should be at least 50 characters in length.")

				else:
					member = self.guild.get_member(message.author.id)
					embed = Embed(title="Modmail",
								  colour=member.colour,
								  timestamp=datetime.now(timezone.utc))
					embed.set_thumbnail(url=member.avatar_url)

					fields = [("Member", member.display_name, False),
							  ("Message", message.content, False)]

					for name, value, inline in fields:
						embed.add_field(name=name, value=value, inline=inline)
					
					mod = self.get_cog("Mod")
					await mod.log_channel.send(embed=embed)
					await message.channel.send("Message relayed to moderators.")

			else:
				await self.process_commands(message)

bot = Bot()