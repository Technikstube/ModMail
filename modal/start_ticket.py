import discord
from datetime import datetime
from discord.ext import commands
from discord import ui

from utility import Ticket, Config
from view.close import CloseView

class StartTicketModal(ui.Modal):
    def __init__(self, message: discord.Message, bot: commands.Bot):
        super().__init__(
            title="Ticket öffnen",
            timeout=180,
            custom_id="open_dm_ticket"
        )
        
        self.start = round(datetime.now().timestamp())
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
        tickets = Ticket().get()
        
        if "ticket_category" not in conf:
            await interaction.response.send_message("Die Ticket-Kategorie ist nicht eingerichtet. Bitte melde dich bei der Administration.")
            return
        
        if str(interaction.user.id) in tickets:
            await interaction.response.send_message("Du hast bereits ein Ticket.", ephemeral=True, delete_after=3)
            return
        
        category = self.bot.get_channel(int(conf["ticket_category"]))
        channel = await category.create_text_channel(f"ticket-{interaction.user.name}")
        await channel.move(beginning=True)
        
        tickets[str(interaction.user.id)] = {
            "channel": channel.id,
            "message_ids": {},
            "last_activity": datetime.now().timestamp(),
            "stale": False,
            "transcript": f"ticket-{interaction.user.name}-{interaction.user.id}.txt"
        }
        Ticket().save(tickets)
        
        embed = discord.Embed(
            title="", 
            description=f"## :ticket: Ticket von {interaction.user.name} \n**Begründung:** {self.reason.value}\n\n",
            colour=discord.Color.lighter_gray())
        
        with open(f"configuration/ticket-{interaction.user.name}-{interaction.user.id}.txt", "w", encoding="utf-8") as f:
            date = datetime.now()
            f.write(
                f"# Ticket erstellt am: {date.day}.{date.month}.{date.year}, {date.hour}:{date.minute}:{date.second}\n" \
                f"# Grund: {self.reason.value}\n" \
                f"# von: {interaction.user.name} ({interaction.user.id})\n\n" \
                f"{date.day}.{date.month}.{str(date.year)[2:]}, {date.hour}:{date.minute}:{date.second} | {interaction.user.name}: {self.msg.content}\n"
            )
        
        embed_user = discord.Embed(title="", description=self.msg.content, color=discord.Color.brand_green())
        embed_user.set_author(name=self.msg.author.name, icon_url=self.msg.author.avatar.url if self.msg.author.avatar.url is not None else self.msg.author.default_avatar.url)
        embed_user.add_field(name="", value=f"**Gesendet:** <t:{self.start}:R>")
        
        await interaction.response.send_message(interaction.user.mention, embed=embed)
        embed.add_field(name="", value="Nutze `+` am am Anfang deiner Nachricht um sie nicht zum Nutzer zu senden.\n"\
            "Nutze `/close` um das Ticket zu schließen")
        msg = await channel.send(f"<a:loading:1272649967936471202> | {interaction.user.mention} <@&1139638391684726884>")
        await msg.edit(content=f"{interaction.user.mention} <@&1139638391684726884>", embed=embed, view=CloseView(self.bot, msg))
        await msg.pin()
        await self.msg.add_reaction("📨")
        await channel.purge(limit=1)
        ticket_msg = await channel.send(embed=embed_user)
        Ticket().add_message(self.msg.author.id, self.msg.id, ticket_msg.id)
        
    
    def on_timeout(self):
        self.stop()
    
    async def on_error(self, interaction: discord.Interaction):
        await interaction.response.send_message("Etwas ist schiefgelaufen! Versuche es später erneut...")
        self.stop()