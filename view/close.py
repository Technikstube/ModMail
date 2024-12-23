import discord
from typing import Optional
from discord import ui

from view.yousure import YouSureView
from utility import Ticket

class CloseView(ui.View):
    def __init__(self, bot, message: Optional[discord.Message]=None):
        super().__init__(
            timeout=None
        )
        self.bot = bot
        self.closebutton = ui.Button(
            style=discord.ButtonStyle.gray,
            custom_id="close_ticket",
            row=1,
            label="Ticket schließen",
        )
        self.inactivitytogglebutton = ui.Button(
            style=discord.ButtonStyle.success,
            custom_id="archive_ticket",
            row=1,
            label="Inaktivitätslöschung umschalten",
        )
        
        self.original_message = None
        if message is not None:
            self.original_message = message
        
        self.add_item(self.closebutton)
        self.add_item(self.inactivitytogglebutton)
        
        self.closebutton.callback = self.close_callback
        self.inactivitytogglebutton.callback = self.inactivitytoggle_callback
        
    async def close_callback(self, interaction: discord.Interaction):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                embed = discord.Embed(title="Ticket unwiderruflich schließen?", description="", color=discord.Color.red())
                await interaction.response.send_message(content="", embed=embed, view=YouSureView(self.bot, interaction.user.id, interaction, None))
                self.stop()
                return
        await interaction.response.send_message(content="Dieses Ticket wurde nicht gefunden. Bitte einen Administrator darum, es zu löschen.", ephemeral=True, delete_after=3)
        
    async def inactivitytoggle_callback(self, interaction: discord.Interaction):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                tickets = Ticket().get()
                if tickets[str(ticket)]["delete_if_stale"]:
                    self.inactivitytogglebutton.style = discord.ButtonStyle.danger
                    tickets[str(ticket)]["delete_if_stale"] = False
                else:
                    self.inactivitytogglebutton.style = discord.ButtonStyle.success
                    tickets[str(ticket)]["delete_if_stale"] = True
                Ticket().save(tickets)
                
                if self.original_message is not None:
                    await self.original_message.edit(view=self)
                
                embed = discord.Embed(title="hat die Inaktivitätslöschung " + ("aktiviert" if tickets[str(ticket)]["delete_if_stale"] else "deaktiviert"), description="", color=discord.Color.green() if tickets[str(ticket)]["delete_if_stale"] else discord.Color.red())
                embed.set_author(name=f"{interaction.user.global_name} ({interaction.user.name})", icon_url=interaction.user.avatar.url if interaction.user.avatar is not None else interaction.user.default_avatar.url)
                embed.set_footer(text=f"Technikstube ModMail — {interaction.user.name} ({interaction.user.id})")
            
                await interaction.response.send_message(embed=embed)
                break