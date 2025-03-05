from datetime import datetime,timezone
from discord import Intents,Embed,File
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument,CommandOnCooldown)
from discord.errors import HTTPException, Forbidden
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

PREFIX="+"
OWNER_IDS=[843777158572671006]#server owner id

class Bot(BotBase):
    def __init__(self):
        self.PREFIX=PREFIX
        self.ready=False
        self.guild=None
        self.scheduler=AsyncIOScheduler()
                
        super().__init__(
            command_prefix=PREFIX, 
            owner_ids=OWNER_IDS,
            intents=Intents.all())
    
    def run(self,version):
        self.VERSION=version

        with open("./lib/bot/token.0","r", encoding="utf-8") as tf:
            self.TOKEN=tf.read()
        
        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

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
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.ready=True
            self.guild=self.get_guild(1321019244867096657)#server id
            print("bot ready")        
            channel=self.get_channel(1321019246435631208)#general channel   

            # embed=Embed(title="Now online!", description="Festus is now online.", 
            #             colour=0xFF0000, timestamp=datetime.now(timezone.utc))
            # fields = [("Name", "Value", True),
            #           ("Another field", "This field is next to the other one.", True),
            #           ("A non-inline field", "This field will appear on it's own row.", False)]
            # for name, value, inline in fields:
            #     embed.add_field(name=name, value=value, inline=inline)
            
            # #server name, icon
            # embed.set_author (name="NetherVibes", icon_url=self.guild.icon) 
            # embed.set_footer (text="This is a footer!")
            # await channel.send(embed=embed)

        else:
            print("bot reconnected")

    async def on_message(self,message):
        pass

bot=Bot()