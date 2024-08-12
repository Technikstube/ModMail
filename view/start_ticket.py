import discord
from discord import ui

from modal.start_ticket import StartTicketModal

class StartTicketView(ui.View):
    def __init__(self, user_message: discord.Message, bot_message: discord.Message, bot):
        super().__init__(
            timeout=180
        )
        self.bot = bot
        self.startbutton = ui.Button(
            style=discord.ButtonStyle.green,
            emoji="<:helioscheckcircle:1267515445582237797>",
            row=0,
            label="Ticket starten",
        )
        self.cancelbutton = ui.Button(
            style=discord.ButtonStyle.danger,
            row=0,
            label="Abbrechen",
        )
        self.faq = ui.Button(
            style=discord.ButtonStyle.gray,
            url="https://discord.com/channels/1030608164367913031/1139689635702915072",
            row=1,
            label="FAQ",
        )
        self.rules = ui.Button(
            style=discord.ButtonStyle.gray,
            url="https://discord.com/channels/1030608164367913031/1134285504343453788",
            row=1,
            label="Regelwerk",
        )
        
        self.add_item(self.startbutton)
        self.add_item(self.cancelbutton)
        self.add_item(self.rules)
        self.add_item(self.faq)
        
        
        self.original_message = bot_message
        self.user_message = user_message
        
        self.startbutton.callback = self.start_callback
        self.cancelbutton.callback = self.cancel_callback
        
    async def start_callback(self, interaction: discord.Interaction):
        self.startbutton.disabled = True
        self.cancelbutton.disabled = True
        
        await interaction.response.send_modal(StartTicketModal(self.user_message, self.bot))
        await self.original_message.edit(content="", view=self)
        
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Vorgang abgebrochen...",
            description="Das Ticket wurde verworfen. Vielen Dank für dein Interesse an Technikstube.",
            color=discord.Colour.red()
        )
        
        await interaction.response.send_message(embed=embed)
        
        self.startbutton.disabled = True
        self.cancelbutton.disabled = True
        
        await self.original_message.edit(content="", view=self)
        self.stop()
        
    async def on_timeout(self):
        embed = discord.Embed(
            title="Vorgang abgebrochen...",
            description="Das Ticket wurde verworfen.",
            color=discord.Colour.red()
        )

        await self.original_message.channel.send(embed=embed)
        
        self.startbutton.disabled = True
        self.cancelbutton.disabled = True
        
        await self.original_message.edit(content="", view=self)
        self.stop()