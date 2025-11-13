"""
Quick Demo: Start Competition Endpoint

Demonstrates the POST /{competition_id}/start endpoint functionality.
This shows the complete flow of creating and starting a competition.
"""
import asyncio
import sys
from uuid import uuid4

sys.path.append('backend')

from models import (
    ChallengeResponse,
    TestCase,
    DifficultyLevel,
    AgentRecord,
    CompetitionResponse,
    CompetitionStatus
)
from services import create_competition_service


async def demo_start_competition_endpoint():
    """
    Simulate what the API endpoint does when you call:
    POST /api/competitions/{competition_id}/start
    """
    print("\n" + "="*70)
    print("DEMO: POST /api/competitions/{competition_id}/start")
    print("="*70 + "\n")

    # Create service
    service = create_competition_service(database=None)

    # Step 1: Create sample challenge
    challenge = ChallengeResponse(
        id="challenge-demo",
        title="Two Sum Problem",
        description="Find two numbers that add up to target",
        difficulty=DifficultyLevel.EASY,
        test_cases=[
            TestCase(input="[2,7,11,15], 9", expected_output="[0,1]"),
            TestCase(input="[3,2,4], 6", expected_output="[1,2]"),
            TestCase(input="[3,3], 6", expected_output="[0,1]"),
        ],
        tags=["array", "hash-table"]
    )

    # Step 2: Create sample agents
    agent_ids = [uuid4() for _ in range(3)]
    print(f"📋 Created challenge: {challenge.title}")
    print(f"🤖 Created {len(agent_ids)} agents")

    # Step 3: Create competition (simulating POST /api/competitions/)
    print("\n1️⃣  Creating competition...")
    competition = await service.create_competition(
        challenge_id=challenge.id,
        agent_ids=agent_ids,
        name="Demo Competition"
    )
    print(f"   ✓ Competition created: {competition.id}")
    print(f"   ✓ Status: {competition.status.value}")

    # Step 4: Start competition (simulating POST /{competition_id}/start)
    print("\n2️⃣  Starting competition (this is the endpoint you requested)...")
    print(f"   📡 POST /api/competitions/{competition.id}/start")

    # This is what happens in the background_tasks.add_task() call
    print("\n   ⚙️  Competition running in background...")
    print(f"   ⚙️  All {len(agent_ids)} agents attempting challenge...")
    print("   ⚙️  This runs asynchronously (doesn't block the API)")

    # Actually run it (in real API, this runs in background)
    results = await service.run_competition(
        competition_id=competition.id,
        timeout_per_agent=180
    )

    # Step 5: Show results
    print(f"\n3️⃣  Competition completed!")
    print(f"   🏆 Winner: {results.winner}")
    print(f"   ⏱️  Duration: {results.total_duration:.2f}s")
    print(f"   📊 Leaderboard:")

    for entry in results.leaderboard:
        print(f"      #{entry['rank']}: Score {entry['score']} "
              f"({entry['status']}, {entry['execution_time']:.2f}s)")

    print("\n" + "="*70)
    print("ENDPOINT SUMMARY")
    print("="*70)
    print(f"""
The endpoint POST /api/competitions/{{competition_id}}/start does:

✅ Validates competition exists and is in 'pending' status
✅ Starts competition in background using FastAPI BackgroundTasks
✅ Returns immediately with:
   - competition_id: {competition.id}
   - status: "running"
   - message: "Competition started successfully. Agents are now competing."
   - expected_duration_seconds: {len(agent_ids) * 180}
   - tracking_url: "/api/competitions/{competition.id}/status"

🔄 While running in background:
   - All agents attempt the challenge concurrently
   - Submissions are collected and scored
   - Winner is determined
   - Status is updated to 'completed'

📍 You can track progress with:
   GET /api/competitions/{competition.id}/status

📊 Get final results with:
   GET /api/competitions/{competition.id}/results
""")


async def show_api_usage():
    """Show how to use the endpoint with HTTP requests."""
    print("\n" + "="*70)
    print("HTTP API USAGE EXAMPLES")
    print("="*70 + "\n")

    competition_id = "550e8400-e29b-41d4-a716-446655440000"

    print("1️⃣  Create a competition:")
    print(f"""
    POST http://localhost:8000/api/competitions/
    Content-Type: application/json

    {{
      "challenge_id": "challenge-001",
      "agent_ids": ["uuid1", "uuid2", "uuid3"],
      "name": "My Competition",
      "timeout_per_agent": 300
    }}

    Response: {{ "id": "{competition_id}", "status": "pending", ... }}
    """)

    print("\n2️⃣  Start the competition (THE ENDPOINT YOU REQUESTED):")
    print(f"""
    POST http://localhost:8000/api/competitions/{competition_id}/start

    Response (immediate):
    {{
      "competition_id": "{competition_id}",
      "status": "running",
      "message": "Competition started successfully. Agents are now competing.",
      "started_at": "2024-01-15T10:35:00Z",
      "expected_duration_seconds": 900,
      "tracking_url": "/api/competitions/{competition_id}/status"
    }}
    """)

    print("\n3️⃣  Monitor progress:")
    print(f"""
    GET http://localhost:8000/api/competitions/{competition_id}/status

    Response:
    {{
      "competition_id": "{competition_id}",
      "status": "running",  // or "completed", "failed"
      "agent_count": 3,
      "winner": null,  // filled when completed
      ...
    }}
    """)

    print("\n4️⃣  Get results (when completed):")
    print(f"""
    GET http://localhost:8000/api/competitions/{competition_id}/results

    Response:
    {{
      "winner": "winning-agent-uuid",
      "leaderboard": [...],
      "submissions": [...],
      "total_duration": 245.67
    }}
    """)

    print("\n" + "="*70)
    print("PYTHON CLIENT EXAMPLE")
    print("="*70 + "\n")

    print("""
import requests
import time

# 1. Create competition
response = requests.post(
    "http://localhost:8000/api/competitions/",
    json={{
        "challenge_id": "challenge-001",
        "agent_ids": ["uuid1", "uuid2", "uuid3"]
    }}
)
competition_id = response.json()["id"]

# 2. Start competition (returns immediately!)
response = requests.post(
    f"http://localhost:8000/api/competitions/{{competition_id}}/start"
)
start_info = response.json()
print(f"Started! Expected duration: {{start_info['expected_duration_seconds']}}s")

# 3. Poll for completion
while True:
    status = requests.get(
        f"http://localhost:8000/api/competitions/{{competition_id}}/status"
    ).json()

    if status["status"] == "completed":
        break

    print(f"Status: {{status['status']}}")
    time.sleep(5)

# 4. Get results
results = requests.get(
    f"http://localhost:8000/api/competitions/{{competition_id}}/results"
).json()
print(f"Winner: {{results['winner']}}")
    """)


async def main():
    print("\n" + "="*70)
    print("START COMPETITION ENDPOINT DEMONSTRATION")
    print("="*70)
    print("\nThis demonstrates the POST /{competition_id}/start endpoint")
    print("that starts a competition with all agents competing.\n")

    choice = input("Choose demo:\n1. Run actual competition\n2. Show API usage examples\n3. Both\n\nChoice (1-3): ").strip()

    if choice == "1":
        await demo_start_competition_endpoint()
    elif choice == "2":
        await show_api_usage()
    elif choice == "3":
        await demo_start_competition_endpoint()
        await show_api_usage()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted.")
