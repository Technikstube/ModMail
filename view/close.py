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
        self.archivebutton = ui.Button(
            style=discord.ButtonStyle.gray,
            custom_id="archive_ticket",
            row=1,
            label="Ticket archivieren",
        )
        self.inactivitytogglebutton = ui.Button(
            style=discord.ButtonStyle.gray,
            custom_id="archive_ticket",
            row=1,
            label="Inaktivitätslöschung umschalten",
        )
        
        if message is not None:
            self.original_message = message
        
        self.add_item(self.closebutton)
        # self.add_item(self.archivebutton)
        self.add_item(self.inactivitytogglebutton)
        
        self.closebutton.callback = self.close_callback
        self.archivebutton.callback = self.archive_callback
        self.inactivitytogglebutton.callback = self.inactivitytoggle_callback
        
    async def close_callback(self, interaction: discord.Interaction):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                embed = discord.Embed(title="Ticket löschen", description="Bist du dir sicher das du das Ticket löschen möchtest?", color=discord.Color.red())
                await interaction.response.send_message(content="", embed=embed, view=YouSureView(self.bot, interaction.user.id, interaction, None))
                self.stop()
                return
        await interaction.response.send_message(content="Dieses Ticket wurde archiviert. Bitte einen Administrator darum, es zu löschen.", ephemeral=True, delete_after=3)
        
    async def archive_callback(self, interaction: discord.Interaction):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                tickets = Ticket().get()
                member = None
                for ticket in tickets:
                    if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                        member = interaction.guild.get_member(int(ticket))
                        tickets.pop(ticket)
                        break
                if member is not None:
                    embed = discord.Embed(title="Dein Ticket wurde geschlossen...", description="", color=discord.Color.red())
                    await member.send(embed=embed)
                Ticket().save(tickets)
                name = interaction.channel.name
                self.closebutton.disabled = True
                self.archivebutton.disabled = True
                await self.original_message.edit(view=self)
                await interaction.channel.edit(name=name.replace("ticket", "archived"))
                await interaction.response.send_message(content="Dieses Ticket wurde archiviert.", ephemeral=True)
                return
        await interaction.response.send_message(content="Dieses Ticket wurde schon archiviert.", ephemeral=True, delete_after=3)
        
    async def inactivitytoggle_callback(self, interaction: discord.Interaction):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                tickets = Ticket().get()
                if tickets[str(interaction.user.id)]["delete_if_stale"]:
                    tickets[str(interaction.user.id)]["delete_if_stale"] = False
                else:
                    tickets[str(interaction.user.id)]["delete_if_stale"] = True
                Ticket().save(tickets)
                
                embed = discord.Embed(title="Inaktivitätslöschung " + ("aktiviert" if tickets[str(interaction.user.id)]["delete_if_stale"] else "deaktiviert"), description="", color=discord.Color.orange())
                embed.set_footer(text=interaction.user.name)
                
                await interaction.response.send_message(content="Inaktivitätslöschung " + ("aktiviert" if tickets[str(interaction.user.id)]["delete_if_stale"] else "deaktiviert"), ephemeral=True)
                await interaction.channel.send(embed=embed)