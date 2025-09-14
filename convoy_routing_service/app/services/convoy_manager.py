import uuid
from datetime import datetime
from ..api import schemas

# In-memory store for active convoys.
# Production-ready version would use Redis.
ACTIVE_CONVOY_STORE: dict[uuid.UUID, schemas.ActiveConvoy] = {}

class ConvoyManager:
    def start_new_convoy(self, call_sign: str, initial_path: list, start_loc, dest_loc) -> schemas.ActiveConvoy:
        convoy = schemas.ActiveConvoy(
            call_sign=call_sign,
            current_path=initial_path,
            current_location=start_loc,
            destination=dest_loc
        )
        ACTIVE_CONVOY_STORE[convoy.id] = convoy
        return convoy

    def get_convoy(self, convoy_id: uuid.UUID) -> schemas.ActiveConvoy | None:
        return ACTIVE_CONVOY_STORE.get(convoy_id)
        
    def get_all_active_convoys(self) -> list[schemas.ActiveConvoy]:
        return list(ACTIVE_CONVOY_STORE.values())

    def update_convoy(self, convoy_id: uuid.UUID, updates: dict):
        if convoy := self.get_convoy(convoy_id):
            convoy_data = convoy.model_dump()
            convoy_data.update(updates)
            convoy_data["last_update_time"] = datetime.utcnow()
            new_convoy_state = schemas.ActiveConvoy(**convoy_data)
            ACTIVE_CONVOY_STORE[convoy_id] = new_convoy_state
            return new_convoy_state
        return None
        
    def clear_all_convoys(self):
        ACTIVE_CONVOY_STORE.clear()

convoy_manager = ConvoyManager()