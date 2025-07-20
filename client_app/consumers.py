import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Lead  # Import your Lead model

class KanbanConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("kanban_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("kanban_updates", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        lead_id = data["lead_id"]
        new_status = data["status"]

        # Update the database
        await self.update_lead_status(lead_id, new_status)

        # Broadcast the update
        await self.channel_layer.group_send(
            "kanban_updates",
            {
                "type": "lead_update",
                "lead_id": lead_id,
                "status": new_status,
            }
        )

    async def lead_update(self, event):
        await self.send(text_data=json.dumps({
            "lead_id": event["lead_id"],
            "status": event["status"],
        }))

    @sync_to_async
    def update_lead_status(self, lead_id, new_status):
        lead = Lead.objects.get(id=lead_id)
        lead.status = new_status
        lead.save()
