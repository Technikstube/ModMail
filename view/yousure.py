import discord
from discord import ui

from utility import Ticket

class YouSureView(ui.View):
    def __init__(self, executor_id: int, msg: discord.Interaction, reason: str | None=None):
        super().__init__(
            timeout=60
        )
        self.deletebutton = ui.Button(
            style=discord.ButtonStyle.danger,
            custom_id="sure",
            row=1,
            label="Löschen",
        )
        self.cancelbutton = ui.Button(
            style=discord.ButtonStyle.gray,
            custom_id="notsure",
            row=1,
            label="Behalten",
        )
        
        self.add_item(self.deletebutton)
        self.add_item(self.cancelbutton)
        
        self.orig = msg
        self.reason = reason
        self.executor = executor_id
        
        self.deletebutton.callback = self.delete_callback
        self.cancelbutton.callback = self.cancel_callback
        
    async def interaction_check(self, interaction: discord.Interaction):
        if self.executor != interaction.user.id:
            await interaction.response.send_message("Das darfst du nicht...", ephemeral=True, delete_after=3)
            return False
        return True
        
    async def delete_callback(self, interaction: discord.Interaction):
        self.deletebutton.disabled = True
        self.cancelbutton.disabled = True
        await self.orig.edit_original_response(content="", view=self)
        
        tickets = Ticket().get()
        member = None
        for ticket in tickets:
            if Ticket().get_ticket_channel_id(ticket) == interaction.channel.id:
                member = interaction.guild.get_member(int(ticket))
                tickets.pop(ticket)
                break
        if member is not None:
            embed = discord.Embed(title="Dein Ticket wurde geschlossen...", description=f"**Begründung:** {self.reason}" if self.reason is not None else "", color=discord.Color.red())
            await member.send(embed=embed)
        Ticket().save(tickets)
        await interaction.channel.delete()
        
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        await self.orig.delete_original_response()
        await interaction.response.send_message("Vorgang abgebrochen...", ephemeral=True, delete_after=5)
        self.stop()
        
    async def on_timeout(self):
        await self.orig.delete_original_response()
        self.stop()
        