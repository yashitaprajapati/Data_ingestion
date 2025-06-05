from pydantic import BaseModel
from typing import List, Literal
from enum import Enum

class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class IngestRequest(BaseModel):
    ids: List[int]
    priority: Priority

class Batch(BaseModel):
    batch_id: str
    ids: List[int]
    status: Literal["yet_to_start", "triggered", "completed"]

class StatusResponse(BaseModel):
    ingestion_id: str
    status: Literal["yet_to_start", "triggered", "completed"]
    batches: List[Batch]
