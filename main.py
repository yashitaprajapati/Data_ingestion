from fastapi import FastAPI, BackgroundTasks, HTTPException
from data_ingestion.models import IngestRequest, StatusResponse
from data_ingestion.ingestion_worker import submit_ingestion_request, get_status
import uuid
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/ingest")
async def ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    # Generate unique ingestion_id
    ingestion_id = str(uuid.uuid4())
    # Submit ingestion request to background processing
    background_tasks.add_task(submit_ingestion_request, ingestion_id, request)
    # Return ingestion_id immediately
    return JSONResponse(content={"ingestion_id": ingestion_id})

@app.get("/status/{ingestion_id}", response_model=StatusResponse)
async def status(ingestion_id: str):
    status_response = get_status(ingestion_id)
    if not status_response:
        raise HTTPException(status_code=404, detail="Ingestion ID not found")
    return status_response
