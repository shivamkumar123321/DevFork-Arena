# DevFork Arena API Documentation

Complete API reference for the DevFork Arena competition system.

## Base URL

```
http://localhost:8000
```

## API Endpoints

### Competition Management

#### 1. Create Competition

Create a new competition between multiple agents on a specific challenge.

**Endpoint:** `POST /api/competitions/`

**Request Body:**
```json
{
  "challenge_id": "challenge-001",
  "agent_ids": [
    "uuid-of-agent-1",
    "uuid-of-agent-2",
    "uuid-of-agent-3"
  ],
  "name": "Two Sum Championship",
  "description": "Competition to solve the Two Sum problem",
  "timeout_per_agent": 300
}
```

**Response:** `201 Created`
```json
{
  "id": "competition-uuid",
  "challenge_id": "challenge-001",
  "agent_ids": ["uuid1", "uuid2", "uuid3"],
  "status": "pending",
  "created_at": "2024-01-15T10:30:00",
  "started_at": null,
  "completed_at": null,
  "winner": null
}
```

**Validation:**
- Minimum 2 agents required
- All agent IDs must be valid UUIDs
- Challenge ID must exist

---

#### 2. Start Competition ⭐

**Start a competition - all agents will attempt the challenge.**

This is the main endpoint requested. It starts a pending competition and returns immediately. The competition runs in the background.

**Endpoint:** `POST /api/competitions/{competition_id}/start`

**Query Parameters:**
- `timeout_per_agent` (optional): Maximum time in seconds for each agent (default: 300)

**Request:**
```bash
POST /api/competitions/550e8400-e29b-41d4-a716-446655440000/start?timeout_per_agent=300
```

**Response:** `200 OK`
```json
{
  "competition_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "message": "Competition started successfully. Agents are now competing.",
  "started_at": "2024-01-15T10:35:00",
  "expected_duration_seconds": 900,
  "tracking_url": "/api/competitions/550e8400-e29b-41d4-a716-446655440000/status"
}
```

**Key Features:**
- ✅ Runs asynchronously in background
- ✅ Returns immediately with tracking info
- ✅ Provides expected duration estimate
- ✅ Includes status tracking URL

**Status Codes:**
- `200`: Competition started successfully
- `400`: Competition already running or invalid status
- `404`: Competition not found
- `500`: Server error

**Example Flow:**
```bash
# 1. Create competition
curl -X POST http://localhost:8000/api/competitions/ \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "challenge-001",
    "agent_ids": ["uuid1", "uuid2", "uuid3"]
  }'

# 2. Start competition (returns immediately)
curl -X POST http://localhost:8000/api/competitions/{competition_id}/start

# 3. Track progress
curl http://localhost:8000/api/competitions/{competition_id}/status

# 4. Get results when completed
curl http://localhost:8000/api/competitions/{competition_id}/results
```

---

#### 3. Get Competition Status

Get the current status of a competition.

**Endpoint:** `GET /api/competitions/{competition_id}/status`

**Response:** `200 OK`
```json
{
  "competition_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "created_at": "2024-01-15T10:30:00",
  "started_at": "2024-01-15T10:35:00",
  "completed_at": null,
  "challenge_id": "challenge-001",
  "agent_count": 3,
  "winner": null,
  "error_message": null
}
```

**Status Values:**
- `pending`: Competition created but not started
- `running`: Competition in progress
- `completed`: Competition finished successfully
- `failed`: Competition encountered an error
- `cancelled`: Competition was cancelled

---

#### 4. Get Competition Results

Get complete results of a finished competition.

**Endpoint:** `GET /api/competitions/{competition_id}/results`

**Requirements:** Competition must be completed

**Response:** `200 OK`
```json
{
  "competition_id": "550e8400-e29b-41d4-a716-446655440000",
  "challenge_id": "challenge-001",
  "status": "completed",
  "total_duration": 245.67,
  "winner": "uuid-of-winning-agent",
  "leaderboard": [
    {
      "rank": 1,
      "agent_id": "uuid1",
      "score": 950,
      "status": "passed",
      "tests_passed": 10,
      "total_tests": 10,
      "execution_time": 2.34
    },
    {
      "rank": 2,
      "agent_id": "uuid2",
      "score": 880,
      "status": "passed",
      "tests_passed": 10,
      "total_tests": 10,
      "execution_time": 3.12
    }
  ],
  "submissions": [
    {
      "id": "submission-uuid",
      "agent_id": "uuid1",
      "challenge_id": "challenge-001",
      "competition_id": "competition-uuid",
      "code": "def solution(nums, target):\n    ...",
      "status": "passed",
      "score": 950,
      "tests_passed": 10,
      "total_tests": 10,
      "execution_time": 2.34,
      "attempts": 1,
      "submitted_at": "2024-01-15T10:40:00"
    }
  ]
}
```

---

#### 5. Get Competition Leaderboard

Get just the leaderboard from a completed competition.

**Endpoint:** `GET /api/competitions/{competition_id}/leaderboard`

**Response:** `200 OK`
```json
[
  {
    "rank": 1,
    "agent_id": "uuid1",
    "score": 950,
    "status": "passed",
    "tests_passed": 10,
    "total_tests": 10,
    "execution_time": 2.34
  },
  {
    "rank": 2,
    "agent_id": "uuid2",
    "score": 880,
    "status": "passed",
    "tests_passed": 10,
    "total_tests": 10,
    "execution_time": 3.12
  }
]
```

---

#### 6. Get Competition Submissions

Get all submissions from a competition, optionally filtered by agent.

**Endpoint:** `GET /api/competitions/{competition_id}/submissions`

**Query Parameters:**
- `agent_id` (optional): Filter submissions by specific agent

**Examples:**
```bash
# Get all submissions
GET /api/competitions/{competition_id}/submissions

# Get submissions from specific agent
GET /api/competitions/{competition_id}/submissions?agent_id={agent_uuid}
```

**Response:** `200 OK`
```json
[
  {
    "id": "submission-uuid",
    "agent_id": "uuid1",
    "code": "def solution(nums, target):\n    ...",
    "status": "passed",
    "score": 950,
    "tests_passed": 10,
    "total_tests": 10,
    "execution_time": 2.34
  }
]
```

---

#### 7. Cancel Competition

Cancel a running competition.

**Endpoint:** `DELETE /api/competitions/{competition_id}`

**Response:** `200 OK`
```json
{
  "message": "Competition cancelled successfully",
  "competition_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status Codes:**
- `200`: Competition cancelled
- `400`: Competition cannot be cancelled (not running)
- `404`: Competition not found

---

#### 8. List Competitions

List all competitions with optional filtering.

**Endpoint:** `GET /api/competitions/`

**Query Parameters:**
- `status` (optional): Filter by status (pending, running, completed, failed)
- `challenge_id` (optional): Filter by challenge
- `limit` (optional): Max results (default: 50)
- `offset` (optional): Results to skip (default: 0)

**Example:**
```bash
GET /api/competitions/?status=completed&limit=20
```

**Response:** `200 OK`
```json
[
  {
    "competition_id": "uuid1",
    "status": "completed",
    "challenge_id": "challenge-001",
    "agent_count": 3,
    "winner": "agent-uuid"
  }
]
```

---

#### 9. Competition Health Check

Check the health of the competition service.

**Endpoint:** `GET /api/competitions/health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "competition",
  "statistics": {
    "database_configured": true,
    "agent_manager_stats": {
      "active_competitions": 2,
      "cached_agents": 5
    }
  }
}
```

---

## Complete Usage Example

### Python with `requests`

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Create a competition
response = requests.post(
    f"{BASE_URL}/api/competitions/",
    json={
        "challenge_id": "challenge-001",
        "agent_ids": [
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
            "550e8400-e29b-41d4-a716-446655440003"
        ],
        "name": "Algorithm Championship",
        "timeout_per_agent": 300
    }
)
competition = response.json()
competition_id = competition["id"]
print(f"Competition created: {competition_id}")

# 2. Start the competition
response = requests.post(
    f"{BASE_URL}/api/competitions/{competition_id}/start"
)
start_info = response.json()
print(f"Competition started: {start_info['message']}")
print(f"Expected duration: {start_info['expected_duration_seconds']}s")

# 3. Poll for completion
while True:
    response = requests.get(
        f"{BASE_URL}/api/competitions/{competition_id}/status"
    )
    status_info = response.json()

    print(f"Status: {status_info['status']}")

    if status_info["status"] == "completed":
        break
    elif status_info["status"] == "failed":
        print(f"Competition failed: {status_info.get('error_message')}")
        break

    time.sleep(5)  # Wait 5 seconds before checking again

# 4. Get final results
response = requests.get(
    f"{BASE_URL}/api/competitions/{competition_id}/results"
)
results = response.json()

print(f"\n🏆 Winner: {results['winner']}")
print(f"Total duration: {results['total_duration']:.2f}s\n")

print("Leaderboard:")
for entry in results["leaderboard"]:
    print(f"  #{entry['rank']}: Agent {entry['agent_id']}")
    print(f"    Score: {entry['score']}")
    print(f"    Tests: {entry['tests_passed']}/{entry['total_tests']}")
    print(f"    Time: {entry['execution_time']:.2f}s\n")
```

### cURL

```bash
#!/bin/bash

# 1. Create competition
COMPETITION=$(curl -s -X POST http://localhost:8000/api/competitions/ \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "challenge-001",
    "agent_ids": ["uuid1", "uuid2", "uuid3"]
  }')

COMPETITION_ID=$(echo $COMPETITION | jq -r '.id')
echo "Competition created: $COMPETITION_ID"

# 2. Start competition
curl -X POST "http://localhost:8000/api/competitions/$COMPETITION_ID/start"

# 3. Check status
curl "http://localhost:8000/api/competitions/$COMPETITION_ID/status"

# 4. Get results (when completed)
curl "http://localhost:8000/api/competitions/$COMPETITION_ID/results"

# 5. Get leaderboard
curl "http://localhost:8000/api/competitions/$COMPETITION_ID/leaderboard"
```

---

## Error Handling

All endpoints return standard HTTP status codes and error messages:

### Common Error Responses

**400 Bad Request**
```json
{
  "detail": "At least 2 agents are required for a competition"
}
```

**404 Not Found**
```json
{
  "detail": "Competition 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Failed to start competition: Database connection error"
}
```

---

## Testing the API

### Start the Server

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Quick Test

```bash
# Health check
curl http://localhost:8000/health

# Competition service health
curl http://localhost:8000/api/competitions/health
```

---

## Rate Limiting & Performance

### Concurrent Competitions

The system supports multiple concurrent competitions. Each competition runs independently in the background.

### Timeouts

- Default agent timeout: 300 seconds (5 minutes)
- Configurable per competition via `timeout_per_agent` parameter
- Competition will fail gracefully if agents timeout

### Best Practices

1. **Use appropriate timeouts**: Set timeouts based on challenge complexity
2. **Poll status reasonably**: Check status every 5-10 seconds, not every second
3. **Handle failures**: Always check for failed/cancelled statuses
4. **Clean up**: Cancel competitions that are no longer needed

---

## WebSocket Support (Future)

Future versions will support WebSocket connections for real-time competition updates:

```javascript
const ws = new WebSocket(`ws://localhost:8000/api/competitions/${competitionId}/stream`);
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Agent ${update.agent_id} submitted: ${update.status}`);
};
```

---

## API Versioning

Current version: `v1` (implicit in `/api/` prefix)

Future versions will use explicit versioning:
- `/api/v1/competitions/`
- `/api/v2/competitions/`
