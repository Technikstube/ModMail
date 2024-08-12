import discord
from discord.ext import commands
from discord import ui

from utility import Ticket, Config
from view.close import CloseView

class StartTicketModal(ui.Modal):
    def __init__(self, message: discord.Message, bot: commands.Bot):
        super().__init__(
            title="Ticket öffnen",
            timeout=300,
            custom_id="open_dm_ticket"
        )
        
        self.msg: discord.Message = message
        self.bot: commands.Bot = bot
        self.reason = ui.TextInput(
            label="Begründung",
            style=discord.TextStyle.short,
            min_length=4,
            max_length=64,
            placeholder="Deine Begründung...",
            required=True,
            row=0
        )
        
        self.add_item(self.reason)
        
    async def on_submit(self, interaction: discord.Interaction):        
        conf = Config().get()
        
        if "ticket_category" not in conf:
            await interaction.response.send_message("Die Ticket-Kategorie ist nicht eingerichtet. Bitte melde dich bei der Administration.")
            return
        
        category = self.bot.get_channel(int(conf["ticket_category"]))
        channel = await category.create_text_channel(f"ticket-{interaction.user.name}")
        
        tickets = Ticket().get()
        tickets[str(interaction.user.id)] = {}
        tickets[str(interaction.user.id)]["channel"] = channel.id
        tickets[str(interaction.user.id)]["message_ids"] = {}
        Ticket().save(tickets)
        
        embed = discord.Embed(
            title=f"Neues Ticket von {interaction.user.name}", 
            description=f"**Begründung:** {self.reason.value}",
            colour=discord.Color.lighter_gray())
        
        embed_user = discord.Embed(title="", description=self.msg.content, color=discord.Color.brand_green())
        embed_user.set_author(name=self.msg.author.name, icon_url=self.msg.author.avatar.url if self.msg.author.avatar.url is not None else self.msg.author.default_avatar.url)
        
        await interaction.response.send_message(interaction.user.mention, embed=embed)
        embed.add_field(name="", value="Nutze `+` am am Anfang deiner Nachricht um sie nicht zum Nutzer zu senden.\n"\
            "Nutze `/close` um das Ticket zu schließen.")
        msg = await channel.send(interaction.user.mention, embed=embed, view=CloseView())
        await msg.pin()
        await channel.purge(limit=1)
        await channel.send(embed=embed_user)
        
    
    def on_timeout(self):
        self.stop()
    
    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message("Etwas ist schiefgelaufen! Versuche es später erneut...")
        self.stop()