import json

config = "configuration/configuration.json"
tickets = "configuration/tickets.json"

class Config:
    def __init__(self):
        pass
    
    def get(self) -> dict:
        with open(config, "r") as cf:
            data = json.load(cf)
        return data

    def save(self, conf: dict) -> None:
        with open(config, "w") as cf:
            json.dump(conf, cf, indent=4)

class Ticket:
    def __init__(self):
        pass
    
    def get(self) -> dict:
        with open(tickets, "r") as tf:
            data = json.load(tf)
        return data
    
    def get_ticket(self, user_id: int) -> dict | None:
        with open(tickets, "r") as tf:
            data = json.load(tf)
        return data[str(user_id)] if str(user_id) in data else None

    def get_ticket_channel_id(self, user_id: int) -> int | None:
        with open(tickets, "r") as tf:
            data = json.load(tf)
        return data[str(user_id)]["channel"] if str(user_id) in data else None
    
    def add_message(self, ticket_user_id: int, original_id: int, copy_id: int) -> None:
        ticket = self.get()
        ticket[str(ticket_user_id)]["message_ids"][str(original_id)] = str(copy_id)
        self.save(ticket)
    
    def get_copy_message(self, ticket_user_id: int, original_id: int) -> None:
        ticket = self.get()
        if str(original_id) in ticket[str(ticket_user_id)]["message_ids"]:
            return ticket[str(ticket_user_id)]["message_ids"][str(original_id)]
        return None
        

    def save(self, ticket: dict) -> None:
        with open(tickets, "w") as tf:
            json.dump(ticket, tf, indent=4)