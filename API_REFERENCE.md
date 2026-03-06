# 📡 API Reference - Federated Learning Server

Base URL: `http://localhost:5000/api`

## Table of Contents
- [Health Check](#health-check)
- [Client Management](#client-management)
- [Federated Training](#federated-training)
- [Centralized Training](#centralized-training)
- [Metrics & Status](#metrics--status)

---

## Health Check

### GET /health

Check if server is running and healthy.

**Request:**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "server": "federated-learning"
}
```

**Status Codes:**
- `200 OK` - Server is healthy

---

## Client Management

### POST /register-client

Register a new client with the server.

**Request:**
```http
POST /api/register-client
Content-Type: application/json

{
  "client_id": 1
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "client_id": 1,
  "total_clients": 3
}
```

**Status Codes:**
- `200 OK` - Registration successful
- `400 Bad Request` - Missing client_id
- `500 Internal Server Error` - Server error

---

### GET /clients

Get list of all registered clients.

**Request:**
```http
GET /api/clients
```

**Response:**
```json
{
  "clients": [1, 2, 3],
  "count": 3
}
```

**Status Codes:**
- `200 OK` - Success

---

## Federated Training

### POST /federated/start

Start a new federated training session.

**Request:**
```http
POST /api/federated/start
Content-Type: application/json

{
  "use_case": "attendance",
  "num_rounds": 10,
  "num_clients": 3
}
```

**Parameters:**
- `use_case` (required): "attendance" or "learning"
- `num_rounds` (optional): Number of training rounds (default: 10)
- `num_clients` (optional): Expected number of clients

**Response:**
```json
{
  "message": "Training started",
  "use_case": "attendance",
  "num_rounds": 10,
  "registered_clients": 3
}
```

**Status Codes:**
- `200 OK` - Training started
- `400 Bad Request` - Invalid parameters
- `500 Internal Server Error` - Server error

---

### POST /federated/upload-weights

Upload model weights from client after local training.

**Request:**
```http
POST /api/federated/upload-weights
Content-Type: application/json

{
  "client_id": 1,
  "weights": [[0.1, 0.2], [0.3, 0.4]],
  "num_samples": 100,
  "round": 1,
  "weight_size": 1024
}
```

**Parameters:**
- `client_id` (required): Client identifier
- `weights` (required): Serialized model weights
- `num_samples` (required): Number of training samples
- `round` (required): Current round number
- `weight_size` (optional): Size in bytes

**Response:**
```json
{
  "message": "Weights received",
  "round": 1,
  "clients_submitted": 2
}
```

**Status Codes:**
- `200 OK` - Weights received
- `400 Bad Request` - Missing required fields
- `500 Internal Server Error` - Server error

---

### GET /federated/global-model

Download current global model weights.

**Request:**
```http
GET /api/federated/global-model
```

**Response:**
```json
{
  "weights": [[0.15, 0.25], [0.35, 0.45]],
  "round": 5
}
```

**Status Codes:**
- `200 OK` - Model available
- `404 Not Found` - No global model available yet

---

### GET /federated/status

Get current training status.

**Request:**
```http
GET /api/federated/status
```

**Response:**
```json
{
  "active": true,
  "current_round": 5,
  "total_rounds": 10,
  "use_case": "attendance",
  "registered_clients": 3,
  "latest_metrics": {
    "round": 5,
    "accuracy": 0.8542,
    "loss": 0.3421,
    "privacy_budget": 2.236,
    "communication_cost": 5242880,
    "num_clients": 3
  }
}
```

**Status Codes:**
- `200 OK` - Success

---

## Centralized Training

### POST /centralized/train

Train a centralized model for comparison.

**Request:**
```http
POST /api/centralized/train
Content-Type: application/json

{
  "use_case": "attendance",
  "num_clients": 5
}
```

**Parameters:**
- `use_case` (required): "attendance" or "learning"
- `num_clients` (optional): Number of clients to collect data from (default: 5)

**Response:**
```json
{
  "message": "Centralized training completed",
  "metrics": {
    "accuracy": 0.8723,
    "loss": 0.3156,
    "training_time": 28.45,
    "total_samples": 500
  }
}
```

**Status Codes:**
- `200 OK` - Training completed
- `400 Bad Request` - Invalid parameters
- `500 Internal Server Error` - Training error

---

## Metrics & Status

### GET /metrics

Get all training metrics across rounds.

**Request:**
```http
GET /api/metrics
```

**Response:**
```json
{
  "rounds": [1, 2, 3, 4, 5],
  "accuracy": [0.65, 0.72, 0.78, 0.82, 0.85],
  "loss": [0.68, 0.55, 0.45, 0.38, 0.34],
  "privacy_budget": [1.0, 1.41, 1.73, 2.0, 2.24],
  "communication_cost": [1048576, 1048576, 1048576, 1048576, 1048576],
  "num_clients": [3, 3, 3, 3, 3]
}
```

**Status Codes:**
- `200 OK` - Success

---

### GET /comparison

Get comparison between centralized and federated approaches.

**Request:**
```http
GET /api/comparison
```

**Response:**
```json
{
  "centralized": {
    "accuracy": 0.8723,
    "training_time": 28.45,
    "communication_cost": 0,
    "privacy_score": 0,
    "total_samples": 500
  },
  "federated": {
    "accuracy": 0.8542,
    "training_time": 0,
    "communication_cost": 5242880,
    "privacy_score": 100,
    "num_rounds": 10
  },
  "differences": {
    "accuracy_diff": -0.0181,
    "privacy_gain": 100,
    "communication_overhead": 5242880
  },
  "winner": {
    "accuracy": "centralized",
    "privacy": "federated",
    "overall": "federated"
  }
}
```

**Status Codes:**
- `200 OK` - Comparison available
- `404 Not Found` - No centralized or federated metrics available

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message description"
}
```

**Common Status Codes:**
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

---

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider implementing rate limiting.

---

## Authentication

Currently no authentication is required for API endpoints. This is a demonstration system. For production use, implement proper authentication (JWT, OAuth, etc.).

---

## CORS

The server is configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:5173`
- `http://localhost:5174`

Modify `config.py` to add additional origins.

---

## Example Usage

### Python

```python
import requests

# Start training
response = requests.post('http://localhost:5000/api/federated/start', json={
    'use_case': 'attendance',
    'num_rounds': 10
})
print(response.json())

# Get status
response = requests.get('http://localhost:5000/api/federated/status')
print(response.json())

# Get metrics
response = requests.get('http://localhost:5000/api/metrics')
metrics = response.json()
print(f"Accuracy: {metrics['accuracy']}")
```

### JavaScript (Axios)

```javascript
import axios from 'axios';

// Start training
const startTraining = async () => {
  const response = await axios.post('http://localhost:5000/api/federated/start', {
    use_case: 'attendance',
    num_rounds: 10
  });
  console.log(response.data);
};

// Get status
const getStatus = async () => {
  const response = await axios.get('http://localhost:5000/api/federated/status');
  console.log(response.data);
};

// Get metrics
const getMetrics = async () => {
  const response = await axios.get('http://localhost:5000/api/metrics');
  console.log(response.data.accuracy);
};
```

### cURL

```bash
# Start training
curl -X POST http://localhost:5000/api/federated/start \
  -H "Content-Type: application/json" \
  -d '{"use_case": "attendance", "num_rounds": 10}'

# Get status
curl http://localhost:5000/api/federated/status

# Get metrics
curl http://localhost:5000/api/metrics

# Train centralized
curl -X POST http://localhost:5000/api/centralized/train \
  -H "Content-Type: application/json" \
  -d '{"use_case": "attendance", "num_clients": 5}'
```

---

## WebSocket Support

Currently not implemented. All updates are via polling. For real-time updates, consider implementing WebSocket support in future versions.

---

## Versioning

Current API Version: `v1`

No version prefix is currently used in URLs. For production, consider versioning: `/api/v1/...`

---

## Data Formats

### Weights Format

Model weights are serialized as nested lists:

```json
{
  "weights": [
    [[0.1, 0.2], [0.3, 0.4]],  // Layer 1 weights
    [0.5, 0.6],                 // Layer 1 biases
    [[0.7, 0.8]],               // Layer 2 weights
    [0.9]                       // Layer 2 biases
  ]
}
```

### Metrics Format

Training metrics are arrays indexed by round:

```json
{
  "rounds": [1, 2, 3],
  "accuracy": [0.65, 0.72, 0.78],
  "loss": [0.68, 0.55, 0.45]
}
```

---

## Best Practices

1. **Check server health** before starting training
2. **Register clients** before they participate
3. **Poll status** every 3-5 seconds during training
4. **Handle errors** gracefully with try-catch
5. **Validate responses** before using data
6. **Use timeouts** for long-running requests
7. **Implement retries** for failed requests

---

## Troubleshooting

### Connection Refused
- Ensure server is running: `python server.py`
- Check port 5000 is not blocked
- Verify firewall settings

### 404 Not Found
- Check endpoint URL is correct
- Ensure API prefix `/api` is included
- Verify server is running latest version

### 500 Internal Server Error
- Check server logs for details
- Verify request payload is valid JSON
- Ensure all required fields are present

### CORS Errors
- Add your origin to `config.CORS_ORIGINS`
- Restart server after config changes
- Check browser console for details

---

**For more information, see the main README.md and QUICKSTART.md files.**
