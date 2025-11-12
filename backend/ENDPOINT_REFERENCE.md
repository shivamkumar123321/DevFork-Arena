# Start Competition Endpoint Reference

## Endpoint: `POST /api/competitions/{competition_id}/start`

**Start a competition - all agents will attempt the challenge**

---

## Overview

This endpoint starts a pending competition and kicks off the challenge-solving process for all participating agents. The competition runs asynchronously in the background, allowing the API to respond immediately.

## Location

- **File**: `backend/routes/competitions.py`
- **Line**: 135-214
- **Function**: `start_competition()`

## Request

### URL
```
POST /api/competitions/{competition_id}/start
```

### Path Parameters
- `competition_id` (UUID, required): The ID of the competition to start

### Query Parameters
- `timeout_per_agent` (integer, optional): Maximum time in seconds for each agent (default: 300)

### Example Request
```bash
POST http://localhost:8000/api/competitions/550e8400-e29b-41d4-a716-446655440000/start?timeout_per_agent=300
```

---

## Response

### Success Response (200 OK)

```json
{
  "competition_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "message": "Competition started successfully. Agents are now competing.",
  "started_at": "2024-01-15T10:35:00.123456",
  "expected_duration_seconds": 900,
  "tracking_url": "/api/competitions/550e8400-e29b-41d4-a716-446655440000/status"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `competition_id` | UUID | The competition identifier |
| `status` | string | Always "running" when successfully started |
| `message` | string | Confirmation message |
| `started_at` | datetime | Timestamp when competition started |
| `expected_duration_seconds` | integer | Estimated time to complete (agents × timeout) |
| `tracking_url` | string | URL to monitor competition progress |

---

## Error Responses

### 404 Not Found
Competition doesn't exist.

```json
{
  "detail": "Competition 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

### 400 Bad Request
Competition is not in pending status.

```json
{
  "detail": "Competition is already running. Only pending competitions can be started."
}
```

### 500 Internal Server Error
Server error during startup.

```json
{
  "detail": "Failed to start competition: [error message]"
}
```

---

## How It Works

### 1. Validation
- Verifies competition exists in database
- Checks competition status is "pending"
- Validates all agents are ready

### 2. Background Execution
- Adds competition to FastAPI background tasks
- Returns response immediately (non-blocking)
- Competition executes asynchronously

### 3. Competition Flow (in background)
1. Updates status to "running"
2. Loads all participating agents
3. **Executes agents concurrently** on the challenge
4. Each agent attempts to solve within timeout
5. Collects all submissions
6. Calculates scores and rankings
7. Determines winner (highest score, fastest time)
8. Updates status to "completed"

### 4. Tracking
- Client polls status endpoint
- Status transitions: `pending` → `running` → `completed`
- Results available when status is "completed"

---

## Code Implementation

### Endpoint Handler
```python
@router.post("/{competition_id}/start")
async def start_competition(
    competition_id: UUID,
    background_tasks: BackgroundTasks,
    timeout_per_agent: int = 300
) -> StartCompetitionResponse:
    """
    Start a competition - all agents will attempt the challenge.

    Returns immediately while competition runs in background.
    """
    # Validate competition exists and is pending
    competition = await competition_service.get_competition_status(competition_id)

    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    if competition.status != CompetitionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Competition already started")

    # Start in background (non-blocking)
    background_tasks.add_task(
        _run_competition_background,
        competition_id,
        timeout_per_agent
    )

    # Return immediately
    return StartCompetitionResponse(
        competition_id=competition_id,
        status="running",
        message="Competition started successfully. Agents are now competing.",
        started_at=datetime.utcnow(),
        expected_duration_seconds=len(competition.agent_ids) * timeout_per_agent,
        tracking_url=f"/api/competitions/{competition_id}/status"
    )
```

### Background Task
```python
async def _run_competition_background(competition_id: UUID, timeout_per_agent: int):
    """
    Background task that actually runs the competition.
    Uses CompetitionService to orchestrate the entire flow.
    """
    try:
        results = await competition_service.run_competition(
            competition_id=competition_id,
            timeout_per_agent=timeout_per_agent
        )
        logger.info(f"Competition completed. Winner: {results.winner}")
    except Exception as e:
        logger.error(f"Competition failed: {e}")
```

---

## Usage Examples

### cURL
```bash
# Start competition
curl -X POST "http://localhost:8000/api/competitions/{competition_id}/start?timeout_per_agent=300"
```

### Python (requests)
```python
import requests

competition_id = "550e8400-e29b-41d4-a716-446655440000"

# Start competition
response = requests.post(
    f"http://localhost:8000/api/competitions/{competition_id}/start",
    params={"timeout_per_agent": 300}
)

start_info = response.json()
print(f"Competition started: {start_info['message']}")
print(f"Expected duration: {start_info['expected_duration_seconds']}s")
print(f"Track at: {start_info['tracking_url']}")
```

### JavaScript (fetch)
```javascript
const competitionId = "550e8400-e29b-41d4-a716-446655440000";

// Start competition
const response = await fetch(
  `http://localhost:8000/api/competitions/${competitionId}/start?timeout_per_agent=300`,
  { method: "POST" }
);

const startInfo = await response.json();
console.log(`Competition started: ${startInfo.message}`);
console.log(`Expected duration: ${startInfo.expected_duration_seconds}s`);
```

---

## Complete Workflow

### 1. Create Competition
```bash
POST /api/competitions/
{
  "challenge_id": "challenge-001",
  "agent_ids": ["uuid1", "uuid2", "uuid3"]
}

→ Returns: { "id": "competition-uuid", "status": "pending" }
```

### 2. Start Competition ⭐ (THIS ENDPOINT)
```bash
POST /api/competitions/{competition_id}/start

→ Returns immediately: { "status": "running", "tracking_url": "..." }
→ Competition runs in background
```

### 3. Monitor Progress
```bash
GET /api/competitions/{competition_id}/status

→ Returns: { "status": "running" }  # Poll every 5-10 seconds
→ Returns: { "status": "completed" }  # When done
```

### 4. Get Results
```bash
GET /api/competitions/{competition_id}/results

→ Returns: { "winner": "uuid", "leaderboard": [...], ... }
```

---

## Key Features

✅ **Non-blocking**: Returns immediately, competition runs in background
✅ **Concurrent Execution**: All agents run in parallel
✅ **Real-time Tracking**: Status endpoint for progress monitoring
✅ **Timeout Protection**: Per-agent timeout prevents hanging
✅ **Error Handling**: Graceful handling of failures
✅ **Winner Determination**: Automatic scoring and ranking
✅ **Database Persistence**: Results saved to TigerData Postgres

---

## Performance

- **Response Time**: < 100ms (returns immediately)
- **Competition Duration**: Depends on agent count and timeout
  - Formula: `agent_count × timeout_per_agent` (worst case)
  - Actual: Usually much faster due to parallel execution
- **Concurrent Competitions**: Supports multiple simultaneous competitions

---

## Testing

### Start Server
```bash
cd backend
python main.py
```

### Run Test
```bash
# Full API test
python test_api.py --full

# Demo endpoint
python demo_start_competition.py
```

### Interactive Docs
- Swagger UI: http://localhost:8000/docs
- Try it out directly in the browser!

---

## Related Endpoints

- `POST /api/competitions/` - Create new competition
- `GET /api/competitions/{id}/status` - Check competition status
- `GET /api/competitions/{id}/results` - Get full results
- `GET /api/competitions/{id}/leaderboard` - Get leaderboard only
- `DELETE /api/competitions/{id}` - Cancel running competition

---

## Notes

- Competition must be in "pending" status to start
- Once started, competition cannot be restarted
- Use cancel endpoint to stop a running competition
- Results are available only after completion
- All agents must exist in the database

---

## Documentation

- **API Docs**: `backend/API_DOCUMENTATION.md`
- **Full README**: `backend/agents/README.md`
- **Test Script**: `backend/test_api.py`
