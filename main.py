import discord
import os
import sys
import asyncio
import signal
import random
from dotenv import get_key
from datetime import datetime
from discord.ext import commands, tasks

from utility import Ticket, Config
from view.close import CloseView

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

paths = [
    "ext/"
]

MAXIMUM_INACTIVE_SECONDS = 86400 # 24 hours in seconds

class Modmail(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=">>",
            help_command=None,
            intents=intents
        )
        
    @tasks.loop(hours=1)
    async def inactivity_checker(self):
        TICKETS = Ticket().get() # One List that doesnt change, so that the for loop doesnt break lol.
        tickets = Ticket().get()
        conf = Config().get()
        
        stale_embed = discord.Embed(title="Dieses Ticket wurde als Inaktiv markiert.",
                                    description="Dieses Ticket wird bei anhaltender Inaktivität automatisch gelöscht.",
                                    color=discord.Color.orange()
                                    )
        
        for ticket in TICKETS:
            member = None
            channel = None
            channel = self.get_channel(Ticket().get_ticket_channel_id(int(ticket)))
            member = channel.guild.get_member(int(ticket))
            dist = round(datetime.now().timestamp()) - round(tickets[str(ticket)]["last_activity"])
            if tickets[str(ticket)]["stale"]:
                if dist <= MAXIMUM_INACTIVE_SECONDS:
                    tickets[str(ticket)]["stale"] = False
                    Ticket().save(tickets)
                    continue
                channel = self.get_channel(Ticket().get_ticket_channel_id(int(ticket)))
                tickets.pop(str(ticket))
                if member is not None:
                    embed = discord.Embed(title="Dein Ticket wurde geschlossen...", description="**Begründung:** Inaktivität", color=discord.Color.red())
                    await member.send(embed=embed)
                Ticket().save(tickets)
                await channel.delete()
                if "transcript_channel" in conf:
                    tc = self.get_channel(int(conf["transcript_channel"]))
                    with open(f"ticket-{member.name}-{member.id}.txt", "rb") as f:
                        embed = discord.Embed(title="", description=f"{channel.name} wurde von {self.user.mention} geschlossen.", color=discord.Color.blue())
                        await tc.send(embed=embed, file=discord.File(f))
                    os.remove(f"./ticket-{member.name}-{member.id}.txt")
                continue
            if dist >= MAXIMUM_INACTIVE_SECONDS:
                tickets[str(ticket)]["stale"] = True
                Ticket().save(tickets)
                await channel.send(embed=stale_embed)
                if member is not None:
                    await member.send(embed=stale_embed)
                continue

    @tasks.loop(minutes=60)
    async def presence_tick(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.Activity(
                type=discord.ActivityType.watching, name="Tickets"
            ),
            discord.CustomActivity(name="Technikstube Support"),
            discord.CustomActivity(name="ModMail"),
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.online
        )

    async def setup_hook(self):
        self.add_view(CloseView(self))
    
    async def on_connect(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="¯\\_(ツ)_/¯")
        ]

        await self.change_presence(
            activity=random.choice(choices), status=discord.Status.dnd
        )
    
    async def on_ready(self):
        
        for path in paths:
            for file in os.listdir(path):
                if file.startswith("-"):
                    continue
                if file.endswith(".py"):
                    await self.load_extension(f"{path.replace("/", ".")}{file[:-3]}")
    
        sync = await self.tree.sync()
        print(f"> Synced {len(sync)} commands")
    
        print(
            f">> {self.user.name} Ready"
            )
        
        self.presence_tick.start()
        self.inactivity_checker.start()

# Shutdown Handler
def shutdown_handler(signum, frame):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Modmail().logout())
    # Cancel all tasks lingering
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    [task.cancel() for task in tasks]

    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
    loop.close()

    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)

bot = Modmail()

bot.run(os.environ.get("TOKEN", get_key("./.env", "TOKEN")))
