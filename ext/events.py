import discord
import os
from datetime import datetime
from discord.ext import commands

from util.antispam import Antispam
from utility import Ticket, Config
from view.start_ticket import StartTicketView

def get_message_embed(message: discord.Message, deleted: bool=False, edited: bool=False):
    
    color = discord.Color.brand_green()
    field_text = "Gesendet: "
    delete = ""
    edit = ""
    
    if deleted:
        color = discord.Color.brand_red()
        delete = "(gelöscht)"
        field_text = "Gelöscht: "
        
    if edited:
        edit = "(editiert)"
        field_text = "Editiert: "
    
    message_embed = discord.Embed(title="", description=message.content if message.content is not None else "", color=color)
    message_embed.set_author(name=f"{message.author.global_name} ({message.author.name}) {delete}{edit}", icon_url=message.author.avatar.url if message.author.avatar is not None else message.author.default_avatar.url)
    message_embed.add_field(name="", value=f"**{field_text}**" + f"<t:{round(datetime.now().timestamp())}:R>")
    message_embed.set_footer(text=f"Technikstube ModMail — {message.author.name} ({message.author.id})")
    return message_embed

async def start_ticket_creation(bot, message: discord.Message):
    bot_msg = await message.reply("<a:loading:1272649967936471202> Einen Moment, ich bereite alles vor...")
    user_msg = message
    
    create_embed = discord.Embed(
        title="",
        description="## :ticket: Ticket eröffnen \nWillkommen im Technikstube Support, wenn du bereit bist dein Ticket zu öffnen, klicke einfach auf **`Ticket eröffnen`**.\n" \
            "Deine Nachricht die du mir geschrieben hast, wird als erste Nachricht im Ticket verwendet, du musst sie also nicht nochmal schreiben.\n\n" \
            "> Inaktive Tickets werden nach einer Zeit automatisiert geschlossen.\n\n" \
            "-# <:helioschevronright:1267515447406887014> Du wirst darüber benachrichtigt wenn unser Team dir geantwortet hat.",
        color=discord.Color.green()
    )
    await bot_msg.edit(content="", embed=create_embed, view=StartTicketView(user_msg, bot_msg, bot))

def add_to_transcript(transcript, message: discord.Message):
    with open(f"configuration/{transcript}", "a", encoding="utf-8") as f:
        date = datetime.now()
        f.write(
            f"{date.day}.{date.month}.{str(date.year)[2:]}, {date.hour}:{date.minute}:{date.second} | {message.author.name}: {message.content}\n"
        )

async def renew_ticket(ticket_owner_id: int, channel: discord.TextChannel, message: discord.Message):
    ticket = Ticket().get()
    ticket[str(ticket_owner_id)]["last_activity"] = datetime.now().timestamp()
    if ticket[str(ticket_owner_id)]["stale"] is True:
        ticket[str(ticket_owner_id)]["stale"] = False
        await channel.edit(name=channel.name.replace("inactive", "ticket"))
        await channel.move(beginning=True)
    Ticket().save(ticket)

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.cache = {}
    
    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return       
    
        if isinstance(message.channel, discord.DMChannel):
            if await Antispam().spamming(message):
                return
            
            conf = Config().get()
            message_embed = get_message_embed(message)
            files = []
            
            # Check for ticket-category, if not set, notify user
            if "ticket_category" not in conf:
                await message.channel.send("Die Ticket-Kategorie ist nicht eingerichtet. Melde dich bitte bei der Administration.")
                return

            # Check for existing ticket, if no ticket exists, start creation of ticket
            if not Ticket().get_ticket(message.author.id):
                return await start_ticket_creation(self.bot, message)

            # Get Ticket Channel in Guild
            channel = self.bot.get_channel(Ticket().get_ticket(message.author.id)["channel"])

            # Add Attachments to files list
            for attachment in message.attachments:
                files.append(await attachment.to_file())

            # Send message embed and files if any
            msg = await channel.send(embed=message_embed)
            if files:
                await channel.send(files=files)

            # Add message to the transcript
            add_to_transcript(Ticket().get_ticket(message.author.id).get("transcript"), message)
            Ticket().add_message(message.author.id, message.id, msg.id)
            
            # Renew ticket (new last_activity timestamp, remove stale status if set)
            await renew_ticket(message.author.id, channel, message)

        if isinstance(message.channel, discord.TextChannel):
            if not message.channel.name.startswith(("inactive-", "ticket-")):
                return
            
            if await Antispam().spamming(message):
                return
            
            conf = Config().get()
            message_embed = get_message_embed(message)
            files = []

            tickets = Ticket().get()
            member = None
            transcript = None
            ticket_owner_id = None

            # Get Ticket Owner ID
            for _ticket in tickets:
                if Ticket().get_ticket_channel_id(_ticket) == message.channel.id:
                    ticket_owner_id = _ticket
                    break
            
            # Set Variables
            member = message.guild.get_member(int(ticket_owner_id))
            transcript = tickets[str(ticket_owner_id)].get("transcript")
            
            # Add Attachments if any to files
            for attachment in message.attachments:
                files.append(await attachment.to_file())
            
            # Send message to ticket owner
            msg = await member.send(embed=message_embed)
            
            # Add message to transcript
            add_to_transcript(transcript, message)
            Ticket().add_message(member.id, message.id, msg.id)
            
            # Renew ticket
            await renew_ticket(int(ticket_owner_id), message.channel, message)
            
    @commands.Cog.listener(name="on_message_delete")
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        
        embed = get_message_embed(message, True)

        if isinstance(message.channel, discord.DMChannel):
            ticket = Ticket().get_ticket(message.author.id)
            msg_id = Ticket().get_copy_message(message.author.id, message.id)
            channel = self.bot.get_channel(Ticket().get_ticket(message.author.id)["channel"])
            msg = await channel.fetch_message(int(msg_id))
            
            await msg.edit(embed=embed, attachments=message.attachments)
        
        if isinstance(message.channel, discord.TextChannel):           
            tickets = Ticket().get()
            for ticket in tickets:
                if Ticket().get_ticket_channel_id(ticket) == message.channel.id:
                    msg_id = Ticket().get_copy_message(ticket, message.id)
                    member = message.guild.get_member(int(ticket))
                    channel = member.dm_channel
                    try:
                        msg = await channel.fetch_message(int(msg_id))
                        await msg.delete()
                    except Exception:
                        pass
        
    @commands.Cog.listener(name="on_message_edit")
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot:
            return
        
        embed = get_message_embed(after, edited=True)
        
        if isinstance(before.channel, discord.DMChannel):
            ticket = Ticket().get_ticket(before.author.id)
            transcript = ticket.get("transcript")
            msg_id = Ticket().get_copy_message(before.author.id, before.id)
            channel = self.bot.get_channel(ticket["channel"])
            msg = await channel.fetch_message(int(msg_id))
            
            await msg.edit(embed=embed, attachments=after.attachments)
            
            with open(f"configuration/{transcript}", "a") as f:
                date = datetime.now()
                f.write(
                    f"{date.day}.{date.month}.{str(date.year)[2:]}, {date.hour}:{date.minute}:{date.second} | [Editiert] {before.author.name}: {after.content}\n > vorher: {before.content}\n" \
                )
        
        if isinstance(before.channel, discord.TextChannel):            
            tickets = Ticket().get()
            transcript = ""
            for ticket in tickets:
                if Ticket().get_ticket_channel_id(ticket) == before.channel.id:
                    msg_id = Ticket().get_copy_message(int(ticket), before.id)
                    member = before.guild.get_member(int(ticket))
                    transcript = tickets[str(ticket)].get("transcript")
                    with open(f"configuration/{transcript}", "a") as f:
                        date = datetime.now()
                        f.write(
                            f"{date.day}.{date.month}.{str(date.year)[2:]}, {date.hour}:{date.minute}:{date.second} | [Editiert] {before.author.name}: {after.content}\n > vorher: {before.content}\n" \
                        )
                    channel = member.dm_channel
                    try:
                        msg = await channel.fetch_message(int(msg_id))
                        await msg.edit(embed=embed, attachments=after.attachments)
                    except Exception:
                        pass
                    
    @commands.Cog.listener(name="on_member_remove")
    async def on_member_remove(self, member: discord.Member):
        conf = Config().get()
        tickets = Ticket().get()
        transcript = ""
        
        for ticket in tickets:
            if ticket == str(member.id):
                channel = self.bot.get_channel(Ticket().get_ticket_channel_id(int(ticket)))
                transcript = tickets[str(ticket)]["transcript"]
                tickets.pop(str(ticket))
                Ticket().save(tickets)
                await channel.delete()
                if "transcript_channel" in conf:
                    tc = self.bot.get_channel(int(conf["transcript_channel"]))
                    with open(f"configuration/{transcript}", "rb") as f:
                        embed = discord.Embed(title="", description=f"{channel.name} wurde von {self.bot.user.mention} geschlossen. (Nutzer hat den Server verlassen)", color=discord.Color.blue())
                        await tc.send(embed=embed, file=discord.File(f))
                    os.remove(f"./configuration/{transcript}")
                break
        
async def setup(bot):
    await bot.add_cog(Events(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Events(bot))
    print(f"> {__name__} unloaded")