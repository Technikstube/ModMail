import discord
from typing import Optional
from discord.ext import commands
from discord import app_commands

from utility import Ticket, Config
from view.yousure import YouSureView

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="close", description="Close a Ticket")
    @commands.guild_only()
    @app_commands.default_permissions(manage_nicknames=True)
    async def close_command(self, interaction: discord.Interaction, reason: Optional[str]):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                embed = discord.Embed(title="Ticket löschen?", description="Bist du dir sicher das du das Ticket löschen möchtest?", color=discord.Color.red())
                await interaction.response.send_message(content="", embed=embed, view=YouSureView(interaction.user.id, interaction, reason))
                return

        await interaction.response.send_message("Dieser Kanal ist kein Ticket.", ephemeral=True, delete_after=3)
    
    @app_commands.command(name="set_category", description="Set the Ticket-Category")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def set_command(self, interaction: discord.Interaction, category_id: int):
        conf = Config().get()
        
        if str(interaction.guild.id) not in conf:
            conf[str(interaction.guild.id)] = {}
        
        _chn = self.bot.get_channel(category_id)
        
        if not isinstance(_chn, discord.CategoryChannel):
            await interaction.response.send_message("Das ist keine Kategorie.", ephemeral=True)
        
        conf[str(interaction.guild.id)]["ticket_category"] = category_id
        Config().save(conf)
        
        await interaction.response.send_message(f"Ticket-Kategorie zu {_chn.name} gesetzt.", ephemeral=True)
    
async def setup(bot):
    await bot.add_cog(Commands(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Commands(bot))
    print(f"> {__name__} unloaded")