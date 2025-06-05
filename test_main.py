import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
import pytest
from fastapi.testclient import TestClient
from data_ingestion.main import app

client = TestClient(app)

def test_ingest_and_status():
    # Submit ingestion request
    response = client.post("/ingest", json={"ids": [1, 2, 3, 4, 5], "priority": "MEDIUM"})
    assert response.status_code == 200
    data = response.json()
    assert "ingestion_id" in data
    ingestion_id = data["ingestion_id"]

    # Immediately check status - should be yet_to_start or triggered
    response = client.get(f"/status/{ingestion_id}")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["ingestion_id"] == ingestion_id
    assert status_data["status"] in ["yet_to_start", "triggered", "completed"]
    assert len(status_data["batches"]) > 0

    # Wait for some time to allow processing
    time.sleep(7)

    # Check status again - should be triggered or completed
    response = client.get(f"/status/{ingestion_id}")
    assert response.status_code == 200
    status_data = response.json()
    assert status_data["status"] in ["triggered", "completed"]

def test_status_not_found():
    response = client.get("/status/nonexistent_id")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Ingestion ID not found"
