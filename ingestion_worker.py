import time
import threading
import uuid
from typing import Dict, List
from .models import IngestRequest, StatusResponse, Batch
from .queue_manager import QueueManager, BatchItem

# In-memory storage for ingestion requests and batch statuses
ingestion_store: Dict[str, Dict] = {}
queue_manager = QueueManager()

def simulate_external_api_call(id: int) -> dict:
    # Simulate delay
    time.sleep(1)
    # Return static response
    return {"id": id, "data": "processed"}

def process_batch(batch_item: BatchItem):
    ingestion_id = batch_item.ingestion_id
    batch_id = batch_item.batch_id
    ids = batch_item.ids

    # Update batch status to triggered
    ingestion_store[ingestion_id]["batches"][batch_id]["status"] = "triggered"

    # Process each id in the batch
    for id in ids:
        simulate_external_api_call(id)

    # Update batch status to completed
    ingestion_store[ingestion_id]["batches"][batch_id]["status"] = "completed"

def batch_processor():
    while True:
        batch_item = queue_manager.dequeue()
        if batch_item:
            process_batch(batch_item)
        else:
            # Sleep briefly to avoid busy waiting
            time.sleep(0.5)

# Start batch processor thread
processor_thread = threading.Thread(target=batch_processor, daemon=True)
processor_thread.start()

def submit_ingestion_request(ingestion_id: str, request: IngestRequest):
    # Split ids into batches of max 3
    ids = request.ids
    priority = request.priority.value
    batches = []
    created_time = time.time()

    # Initialize ingestion_store entry
    ingestion_store[ingestion_id] = {
        "priority": priority,
        "created_time": created_time,
        "batches": {}
    }

    # Create batches and enqueue
    for i in range(0, len(ids), 3):
        batch_ids = ids[i:i+3]
        batch_id = str(uuid.uuid4())
        batch = Batch(batch_id=batch_id, ids=batch_ids, status="yet_to_start")
        ingestion_store[ingestion_id]["batches"][batch_id] = batch.dict()
        batch_item = BatchItem(ingestion_id, batch_id, batch_ids, priority, created_time)
        queue_manager.enqueue(batch_item)

def get_status(ingestion_id: str) -> StatusResponse:
    if ingestion_id not in ingestion_store:
        return None
    batches_data = ingestion_store[ingestion_id]["batches"]
    batches = []
    statuses = set()
    for batch_id, batch_info in batches_data.items():
        batches.append(Batch(**batch_info))
        statuses.add(batch_info["status"])

    # Determine overall status
    if statuses == {"yet_to_start"}:
        overall_status = "yet_to_start"
    elif "triggered" in statuses:
        overall_status = "triggered"
    elif statuses == {"completed"}:
        overall_status = "completed"
    else:
        # Mixed statuses, consider triggered as priority
        overall_status = "triggered"

    return StatusResponse(
        ingestion_id=ingestion_id,
        status=overall_status,
        batches=batches
    )
