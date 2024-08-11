import discord
from discord import ui

from view.yousure import YouSureView
from utility import Ticket

class CloseView(ui.View):
    def __init__(self):
        super().__init__(
            timeout=None
        )
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
        
        self.add_item(self.closebutton)
        self.add_item(self.archivebutton)
        
        self.closebutton.callback = self.close_callback
        self.archivebutton.callback = self.archive_callback
        
    async def close_callback(self, interaction: discord.Interaction):
        for ticket in Ticket().get():
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                embed = discord.Embed(title="Ticket löschen", description="Bist du dir sicher das du das Ticket löschen möchtest?", color=discord.Color.red())
                await interaction.response.send_message(content="", embed=embed, view=YouSureView(interaction.user.id, interaction, None))
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
                await interaction.channel.edit(name=name.replace("ticket", "archived"))
                await interaction.response.send_message(content="Dieses Ticket wurde archiviert.", ephemeral=True)
                return
        await interaction.response.send_message(content="Dieses Ticket wurde schon archiviert.", ephemeral=True, delete_after=3)
        
        