from pydantic import BaseModel


class ReleaseLockPayload(BaseModel):
    lock_name: str
    owner_id: str


class RenewLockPayload(BaseModel):
    lock_name: str
    owner_id: str
    lease_seconds: int = 120
