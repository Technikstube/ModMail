import discord
from discord import ui

from modal.start_ticket import StartTicketModal

class StartTicketView(ui.View):
    def __init__(self, user_msg: discord.Message, bot_msg: discord.Message, bot):
        super().__init__(
            timeout=180
        )
        self.bot = bot
        self.startbutton = ui.Button(
            style=discord.ButtonStyle.green,
            custom_id="open_dm_ticket_button",
            emoji="<:helioscheckcircle:1267515445582237797>",
            row=1,
            label="Ticket starten",
        )
        self.cancelbutton = ui.Button(
            style=discord.ButtonStyle.danger,
            custom_id="cancel_dm_ticket_button",
            # emoji="",
            row=1,
            label="Abbrechen",
        )
        self.faq = ui.Button(
            style=discord.ButtonStyle.gray,
            url="https://discord.com/channels/1030608164367913031/1139689635702915072",
            row=0,
            label="FAQ",
        )
        
        self.add_item(self.startbutton)
        self.add_item(self.cancelbutton)
        self.add_item(self.faq)
        
        self.orig = bot_msg
        self.user_msg = user_msg
        
        self.startbutton.callback = self.start_callback
        self.cancelbutton.callback = self.cancel_callback
        
    async def start_callback(self, interaction: discord.Interaction):
        self.startbutton.disabled = True
        self.cancelbutton.disabled = True
        
        await interaction.response.send_modal(StartTicketModal(self.user_msg, self.bot))
        await self.orig.edit(content="", view=self)
        
        self.stop()

    async def cancel_callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Vorgang abgebrochen...",
            description="Du hast das Ticket abgebrochen... Schreibe mich einfach wieder an, wenn du ein Anliegen hast!",
            color=discord.Colour.red()
        )
        
        await interaction.response.send_message(embed=embed)
        
        self.startbutton.disabled = True
        self.cancelbutton.disabled = True
        
        await self.orig.edit(content="", view=self)
        self.stop()
        
    async def on_timeout(self):
        embed = discord.Embed(
            title="Vorgang abgebrochen...",
            description="Der Vorgang wurde automatisch abgebrochen... Schreibe mich einfach wieder an, wenn du ein Anliegen hast!",
            color=discord.Colour.red()
        )

        await self.orig.channel.send(embed=embed)
        
        self.startbutton.disabled = True
        self.cancelbutton.disabled = True
        
        await self.orig.edit(content="", view=self)
        self.stop()