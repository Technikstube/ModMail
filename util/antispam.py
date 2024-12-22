import discord

from datetime import datetime

TIME_WINDOW_SECS = 5
MAX_MESSAGES = 5
DELETE_MESSAGES = MAX_MESSAGES

cache = {}

class Antispam:
    def __init__(self):
        self.antispam_users = None
        
        if not cache.get("users"):
            cache["users"] = {}
            
        self.antispam_users = cache["users"]
    
    def _check(self, member_id):
        if not self.antispam_users.get(member_id):
            self.antispam_users[member_id] = {
                "last_message": datetime.now(),
                "count": 0,
                "notified": False
            }
    
    def _add_point(self, member_id, points: int=1):
        self._check(member_id)
        
        antispam_user = self.antispam_users[member_id]
        last_message = antispam_user["last_message"]
        
        if (datetime.now() - last_message).seconds >= TIME_WINDOW_SECS:
            del cache["users"][member_id]
        
        antispam_user["count"] += 1
        
    async def spamming(self, message: discord.Message) -> bool:
        self._add_point(message.author.id)                
        self._check(message.author.id)
        if self.antispam_users[message.author.id]["notified"] is True:
            return True
        if self.antispam_users[message.author.id]["count"] == MAX_MESSAGES:
            if not self.antispam_users[message.author.id]["notified"]:
                await message.author.send("> :warning: Spam ist nicht erwünscht!", delete_after=5)
                self.antispam_users[message.author.id]["notified"] = True
            return True
        return False