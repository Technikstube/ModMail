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
                await interaction.response.send_message(content="", embed=embed, view=YouSureView(self.bot, interaction.user.id, interaction, reason))
                return

        await interaction.response.send_message("Dieser Kanal ist kein Ticket.", ephemeral=True, delete_after=3)
    
    @app_commands.command(name="set_category", description="Set the Ticket-Category")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def category_command(self, interaction: discord.Interaction, category_id: str):
        conf = Config().get()
        
        _chn = self.bot.get_channel(int(category_id))
        
        if not isinstance(_chn, discord.CategoryChannel):
            await interaction.response.send_message("Das ist keine Kategorie.", ephemeral=True)
        
        conf["ticket_category"] = category_id
        Config().save(conf)
        
        await interaction.response.send_message(f"Ticket-Kategorie zu `{_chn.name}` gesetzt.", ephemeral=True)

    @app_commands.command(name="set_transcripts", description="Set the transcripts-channel")
    @commands.guild_only()
    @app_commands.default_permissions(manage_guild=True)
    async def transcript_command(self, interaction: discord.Interaction, transcript_channel: discord.TextChannel):
        conf = Config().get()
        
        if not isinstance(transcript_channel, discord.TextChannel):
            await interaction.response.send_message("Das ist kein Textkanal.", ephemeral=True)
        
        conf["transcript_channel"] = transcript_channel.id
        Config().save(conf)
        
        await interaction.response.send_message(f"Transkript-Kanal zu {transcript_channel.mention} gesetzt.", ephemeral=True)
    
async def setup(bot):
    await bot.add_cog(Commands(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Commands(bot))
    print(f"> {__name__} unloaded")