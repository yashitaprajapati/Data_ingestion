import React, { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [idsInput, setIdsInput] = useState('');
  const [priority, setPriority] = useState('HIGH');
  const [ingestionId, setIngestionId] = useState('');
  const [statusResult, setStatusResult] = useState(null);
  const [statusInput, setStatusInput] = useState('');
  const [error, setError] = useState('');

  const handleIngestSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIngestionId('');
    setStatusResult(null);

    // Parse ids input
    const ids = idsInput.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
    if (ids.length === 0) {
      setError('Please enter valid IDs separated by commas.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids, priority }),
      });
      if (!response.ok) {
        throw new Error('Failed to submit ingestion request');
      }
      const data = await response.json();
      setIngestionId(data.ingestion_id);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStatusCheck = async (e) => {
    e.preventDefault();
    setError('');
    setStatusResult(null);

    if (!statusInput) {
      setError('Please enter an ingestion ID to check status.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/status/${statusInput}`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Ingestion ID not found');
        } else {
          throw new Error('Failed to fetch status');
        }
      }
      const data = await response.json();
      setStatusResult(data);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: 'auto', padding: 20, fontFamily: 'Arial, sans-serif' }}>
      <h1>Data Ingestion System</h1>

      <section style={{ marginBottom: 40 }}>
        <h2>Submit Ingestion Request</h2>
        <form onSubmit={handleIngestSubmit}>
          <div style={{ marginBottom: 10 }}>
            <label>
              IDs (comma separated):<br />
              <input
                type="text"
                value={idsInput}
                onChange={(e) => setIdsInput(e.target.value)}
                style={{ width: '100%', padding: 8 }}
                placeholder="e.g. 1, 2, 3, 4"
              />
            </label>
          </div>
          <div style={{ marginBottom: 10 }}>
            <label>
              Priority:<br />
              <select value={priority} onChange={(e) => setPriority(e.target.value)} style={{ width: '100%', padding: 8 }}>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
              </select>
            </label>
          </div>
          <button type="submit" style={{ padding: '10px 20px' }}>Submit</button>
        </form>
        {ingestionId && (
          <p style={{ marginTop: 10, color: 'green' }}>
            Ingestion submitted successfully. Ingestion ID: <strong>{ingestionId}</strong>
          </p>
        )}
      </section>

      <section>
        <h2>Check Ingestion Status</h2>
        <form onSubmit={handleStatusCheck}>
          <div style={{ marginBottom: 10 }}>
            <label>
              Ingestion ID:<br />
              <input
                type="text"
                value={statusInput}
                onChange={(e) => setStatusInput(e.target.value)}
                style={{ width: '100%', padding: 8 }}
                placeholder="Enter ingestion ID"
              />
            </label>
          </div>
          <button type="submit" style={{ padding: '10px 20px' }}>Check Status</button>
        </form>
        {statusResult && (
          <div style={{ marginTop: 20 }}>
            <h3>Status: {statusResult.status}</h3>
            <h4>Batches:</h4>
            <ul>
              {statusResult.batches.map(batch => (
                <li key={batch.batch_id}>
                  Batch ID: {batch.batch_id} | IDs: [{batch.ids.join(', ')}] | Status: {batch.status}
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      {error && (
        <p style={{ color: 'red', marginTop: 20 }}>
          Error: {error}
        </p>
      )}
    </div>
  );
}

export default App;
