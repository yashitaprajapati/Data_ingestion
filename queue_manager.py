import time
import heapq
from threading import Lock

class BatchItem:
    def __init__(self, ingestion_id, batch_id, ids, priority, created_time):
        self.ingestion_id = ingestion_id
        self.batch_id = batch_id
        self.ids = ids
        self.priority = priority
        self.created_time = created_time

    def __lt__(self, other):
        # Priority order: HIGH < MEDIUM < LOW (for heapq min-heap)
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        if priority_order[self.priority] != priority_order[other.priority]:
            return priority_order[self.priority] < priority_order[other.priority]
        return self.created_time < other.created_time

class QueueManager:
    def __init__(self):
        self.lock = Lock()
        self.heap = []
        self.last_processed_time = 0

    def enqueue(self, batch_item: BatchItem):
        with self.lock:
            heapq.heappush(self.heap, batch_item)

    def dequeue(self):
        with self.lock:
            current_time = time.time()
            # Enforce rate limit: 1 batch per 5 seconds
            if self.heap and (current_time - self.last_processed_time) >= 5:
                batch_item = heapq.heappop(self.heap)
                self.last_processed_time = current_time
                return batch_item
            return None

    def is_empty(self):
        with self.lock:
            return len(self.heap) == 0
