from datetime import datetime, timezone, timedelta
import asyncio
from discord.ext import commands, tasks
from ..db import db
IST = timezone(timedelta(hours=5, minutes=30))

class Reminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = []
        self.check_reminders.start()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("reminder")

    @commands.command(name="remindme")
    async def set_reminder(self, ctx, date: str, time: str, *, message: str):
        #format: !remindme DD-MM-YYYY HH:MM message
        try:
            reminder_time = datetime.strptime(f"{date} {time}", "%d-%m-%Y %H:%M").replace(tzinfo=IST)
            
            reminder_time_utc = reminder_time.astimezone(timezone.utc)

            if reminder_time_utc < datetime.now(timezone.utc):
                await ctx.send("❌ You cannot set a reminder for the past!")
                return

            db.execute("INSERT INTO reminders (UserID, Time, Message) VALUES (?, ?, ?)", 
                       ctx.author.id, reminder_time_utc.timestamp(), message)
            db.commit()
            
            await ctx.send(f"✅ Reminder set for **{date} at {time} IST!**")
        except ValueError:
            await ctx.send("❌ Invalid format! Use `!remindme DD-MM-YYYY HH:MM Your message`")

    @tasks.loop(minutes=1)
    async def check_reminders(self):
        now_utc = datetime.now(timezone.utc).timestamp()

        reminders = db.records("SELECT ID, UserID, Time, Message FROM reminders WHERE Time <= ?", now_utc)
        for reminder_id, user_id, reminder_time, message in reminders:
            user = self.bot.get_user(user_id)
            
            # Convert UTC timestamp back to IST
            local_time = datetime.fromtimestamp(reminder_time, timezone.utc).astimezone(IST)

            if user:
                try:
                    await user.send(f"⏰ **Reminder:** {message} (Scheduled for {local_time.strftime('%d-%m-%Y %I:%M %p IST')})")
                except:
                    pass  # Handle cases where the user has DMs disabled

            db.execute("DELETE FROM reminders WHERE ID = ?", reminder_id)
        db.commit()

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Reminder(bot))