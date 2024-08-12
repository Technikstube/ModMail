import discord
from datetime import datetime
from discord.ext import commands

from utility import Ticket
from view.start_ticket import StartTicketView

# Anti-Spam
TIME_WINDOW_SECS = 5
MAX_MESSAGES = 5
DELETE_MESSAGES = MAX_MESSAGES

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.cache = {}
    
    @commands.Cog.listener(name="on_message")
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        member_id = message.author.id
        
        if not self.cache.get("users"):
            self.cache["users"] = {}
            
        antispam_users = self.cache["users"]
        
        if not antispam_users.get(member_id):
            antispam_users[member_id] = {
                "last_message": datetime.now(),
                "count": 0,
                "notified": False
            }
            
        antispam_user = antispam_users[member_id]
        last_message = antispam_user["last_message"]
        
        if (datetime.now() - last_message).seconds >= TIME_WINDOW_SECS:
            del self.cache["users"][member_id]
        
        antispam_user["count"] += 1
        
        embed = discord.Embed(title="", description=message.content if message.content is not None else "", color=discord.Color.brand_green())
        embed.set_author(name=message.author.name, icon_url=message.author.avatar.url if message.author.avatar.url is not None else message.author.default_avatar.url)
        embed.add_field(name="", value=f"**Gesendet:** <t:{round(datetime.now().timestamp())}:R>")

        if isinstance(message.channel, discord.DMChannel):
            if antispam_user["notified"] is True:
                return
            if antispam_user["count"] == MAX_MESSAGES:
                if not antispam_user["notified"]:
                    await message.author.send("> :warning: Spam ist nicht erwünscht!", delete_after=5)
                    antispam_user["notified"] = True
                return
            if not Ticket().get_ticket(message.author.id):
                bot_msg = await message.reply("<a:loading:1272207705913819176>")
                user_msg = message
                
                embed = discord.Embed(
                    title="Neues Ticket eröffnen",
                    description="Willkommen im Technikstube Support, wenn du Bereit bist dein Ticket zu öffnen, klicke einfach auf **Ticket starten**.\n" \
                        "Deine Nachricht die du mir geschrieben hast, wird als erste Nachricht im Ticket verwendet, du musst sie also nicht nochmal schreiben.\n\n" \
                        "Du wirst darüber benachrichtigt wenn unser Team dir geantwortet hast.",
                    color=discord.Color.blurple()
                )
                await bot_msg.edit(content="", embed=embed, view=StartTicketView(user_msg, bot_msg, self.bot))
                return
            
            channel = self.bot.get_channel(Ticket().get_ticket(message.author.id)["channel"])
            files = []
            for attachment in message.attachments:
                files.append(await attachment.to_file())
            
            msg = await channel.send(embed=embed)
            if files:
                await channel.send(files=files)
            Ticket().add_message(message.author.id, message.id, msg.id)
            await message.add_reaction("📨")
            
        if isinstance(message.channel, discord.TextChannel):
            if not message.channel.name.startswith("ticket-"):
                return
            if antispam_user["notified"] is True:
                return
            if antispam_user["count"] == MAX_MESSAGES:
                if not antispam_user["notified"]:
                    await message.channel.send("> :warning: Spam ist nicht erwünscht!", delete_after=5)
                    antispam_user["notified"] = True                
                return
            
            member = None
            tickets = Ticket().get()
            
            for ticket in tickets:
                if Ticket().get_ticket_channel_id(ticket) == message.channel.id:
                    member = message.guild.get_member(int(ticket))
                    break
            if message.content.startswith("+"):
                return
            files = []
            for attachment in message.attachments:
                files.append(await attachment.to_file())
            msg = await member.send(embed=embed)
            if files:
                await member.send(files=files)
            Ticket().add_message(member.id, message.id, msg.id)
            await message.add_reaction("📨")
    
    @commands.Cog.listener(name="on_message_delete")
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        
        embed = discord.Embed(title="", description=message.content, color=discord.Color.brand_red())
        embed.set_author(name=message.author.name + " (gelöscht)", icon_url=message.author.avatar.url if message.author.avatar.url is not None else message.author.default_avatar.url)
        embed.add_field(name="", value=f"**Gelöscht:** <t:{round(datetime.now().timestamp())}:R>")    	

        if isinstance(message.channel, discord.DMChannel):
            ticket = Ticket().get_ticket(message.author.id)
            msg_id = Ticket().get_copy_message(message.author.id, message.id)
            channel = self.bot.get_channel(Ticket().get_ticket(message.author.id)["channel"])
            msg = await channel.fetch_message(int(msg_id))
            
            await msg.edit(embed=embed, attachments=message.attachments)
        
        if isinstance(message.channel, discord.TextChannel):
            if not message.channel.name.startswith("ticket-"):
                return
            
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
        
        embed = discord.Embed(title="", description=after.content, color=discord.Color.brand_green())
        embed.set_author(name=before.author.name + " (editiert)", icon_url=before.author.avatar.url if before.author.avatar.url is not None else before.author.default_avatar.url)
        embed.add_field(name="", value=f"**Editiert:** <t:{round(datetime.now().timestamp())}:R>")
        
        if isinstance(before.channel, discord.DMChannel):
            ticket = Ticket().get_ticket(before.author.id)
            msg_id = Ticket().get_copy_message(before.author.id, before.id)
            channel = self.bot.get_channel(ticket["channel"])
            msg = await channel.fetch_message(int(msg_id))
            await msg.edit(embed=embed, attachments=after.attachments)
        
        if isinstance(before.channel, discord.TextChannel):
            if not before.channel.name.startswith("ticket-"):
                return
            
            tickets = Ticket().get()
            for ticket in tickets:
                if Ticket().get_ticket_channel_id(ticket) == before.channel.id:
                    msg_id = Ticket().get_copy_message(int(ticket), before.id)
                    member = before.guild.get_member(int(ticket))
                    channel = member.dm_channel
                    try:
                        msg = await channel.fetch_message(int(msg_id))
                        await msg.edit(embed=embed, attachments=after.attachments)
                    except Exception:
                        pass
        
async def setup(bot):
    await bot.add_cog(Events(bot))
    print(f"> {__name__} loaded")
    
async def teardown(bot):
    await bot.remove_cog(Events(bot))
    print(f"> {__name__} unloaded")