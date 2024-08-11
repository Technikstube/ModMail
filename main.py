import discord
import os
from dotenv import get_key
from discord.ext import commands

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

    async def setup_hook(self):
        self.add_view(CloseView())
    
    async def on_ready(self):
        
        for path in paths:
            for file in os.listdir(path):
                if file.startswith("-"):
                    continue
                if file.endswith(".py"):
                    await self.load_extension(f"{path.replace("/", ".")}{file[:-3]}")
    
        sync = await self.tree.sync()
        print(f"> Synced {len(sync)} Commands")
    
        print(
            "------------------------------" \
            f"< {self.user.name} Ready >" \
            "------------------------------")

bot = Modmail()

bot.run(get_key(".env", "TOKEN"))
