import discord
import os
import random
from dotenv import get_key
from discord.ext import commands, tasks

from view.close import CloseView

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

paths = [
    "ext/"
]

class Modmail(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=">>",
            help_command=None,
            intents=intents
        )

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
        self.add_view(CloseView())
    
    async def on_connect(self):
        choices: discord.Activity or discord.CustomActivity = [
            discord.CustomActivity(name="¯\_(ツ)_/¯")
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
        
        await self.presence_tick.start()

bot = Modmail()

bot.run(os.environ.get("TOKEN", get_key("./.env", "TOKEN")))
