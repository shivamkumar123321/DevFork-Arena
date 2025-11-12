"""
API Test Script

Simple script to test the competition API endpoints.
Demonstrates the complete flow: create → start → monitor → results
"""
import requests
import time
import json
from uuid import uuid4

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(title)
    print("="*60 + "\n")


def test_health_check():
    """Test the health check endpoints."""
    print_section("1. Health Check")

    # API health
    response = requests.get(f"{BASE_URL}/health")
    print(f"API Health: {response.json()}")

    # Competition service health
    response = requests.get(f"{BASE_URL}/api/competitions/health")
    print(f"Competition Service Health: {response.json()}")


def test_create_competition():
    """Test creating a competition."""
    print_section("2. Create Competition")

    # Generate sample agent IDs
    agent_ids = [uuid4() for _ in range(3)]
    print(f"Creating competition with {len(agent_ids)} agents:")
    for i, agent_id in enumerate(agent_ids, 1):
        print(f"  Agent {i}: {agent_id}")

    response = requests.post(
        f"{BASE_URL}/api/competitions/",
        json={
            "challenge_id": "challenge-test-001",
            "agent_ids": [str(aid) for aid in agent_ids],
            "name": "Test Competition",
            "description": "API test competition",
            "timeout_per_agent": 180
        }
    )

    if response.status_code == 201:
        competition = response.json()
        print(f"\n✓ Competition created successfully!")
        print(f"  ID: {competition['id']}")
        print(f"  Status: {competition['status']}")
        print(f"  Challenge: {competition['challenge_id']}")
        return competition['id']
    else:
        print(f"\n✗ Failed to create competition: {response.status_code}")
        print(f"  Error: {response.json()}")
        return None


def test_start_competition(competition_id):
    """Test starting a competition."""
    print_section("3. Start Competition")

    print(f"Starting competition: {competition_id}")

    response = requests.post(
        f"{BASE_URL}/api/competitions/{competition_id}/start",
        params={"timeout_per_agent": 180}
    )

    if response.status_code == 200:
        start_info = response.json()
        print(f"\n✓ Competition started successfully!")
        print(f"  Status: {start_info['status']}")
        print(f"  Message: {start_info['message']}")
        print(f"  Started at: {start_info['started_at']}")
        print(f"  Expected duration: {start_info['expected_duration_seconds']}s")
        print(f"  Tracking URL: {start_info['tracking_url']}")
        return True
    else:
        print(f"\n✗ Failed to start competition: {response.status_code}")
        print(f"  Error: {response.json()}")
        return False


def test_monitor_competition(competition_id, max_wait=300):
    """Test monitoring a competition until completion."""
    print_section("4. Monitor Competition")

    print(f"Monitoring competition: {competition_id}")
    print(f"Will check status every 5 seconds (max wait: {max_wait}s)\n")

    start_time = time.time()
    check_count = 0

    while True:
        check_count += 1
        elapsed = time.time() - start_time

        if elapsed > max_wait:
            print(f"\n⏰ Timeout reached ({max_wait}s). Stopping monitoring.")
            return None

        # Get status
        response = requests.get(
            f"{BASE_URL}/api/competitions/{competition_id}/status"
        )

        if response.status_code == 200:
            status_info = response.json()
            status = status_info['status']

            print(f"[Check {check_count}] Status: {status} (elapsed: {elapsed:.1f}s)")

            if status == "completed":
                print(f"\n✓ Competition completed!")
                print(f"  Winner: {status_info.get('winner', 'N/A')}")
                print(f"  Total time: {elapsed:.2f}s")
                return status_info

            elif status == "failed":
                print(f"\n✗ Competition failed!")
                print(f"  Error: {status_info.get('error_message', 'Unknown')}")
                return status_info

            elif status == "cancelled":
                print(f"\n⚠ Competition cancelled!")
                return status_info

        else:
            print(f"\n✗ Failed to get status: {response.status_code}")
            return None

        time.sleep(5)  # Wait 5 seconds before next check


def test_get_results(competition_id):
    """Test getting competition results."""
    print_section("5. Get Results")

    print(f"Fetching results for competition: {competition_id}")

    response = requests.get(
        f"{BASE_URL}/api/competitions/{competition_id}/results"
    )

    if response.status_code == 200:
        results = response.json()
        print(f"\n✓ Results retrieved successfully!")
        print(f"\n🏆 Winner: {results.get('winner', 'N/A')}")
        print(f"Duration: {results.get('total_duration', 0):.2f}s")

        print(f"\nLeaderboard:")
        for entry in results.get('leaderboard', []):
            print(f"  #{entry['rank']}: Agent {entry['agent_id']}")
            print(f"    Score: {entry['score']}")
            print(f"    Status: {entry['status']}")
            print(f"    Tests: {entry['tests_passed']}/{entry['total_tests']}")
            print(f"    Time: {entry['execution_time']:.2f}s")

        print(f"\nSubmissions: {len(results.get('submissions', []))}")
        return results
    elif response.status_code == 400:
        print(f"\n⚠ Competition not completed yet")
        print(f"  Message: {response.json()['detail']}")
        return None
    else:
        print(f"\n✗ Failed to get results: {response.status_code}")
        print(f"  Error: {response.json()}")
        return None


def test_get_leaderboard(competition_id):
    """Test getting just the leaderboard."""
    print_section("6. Get Leaderboard")

    response = requests.get(
        f"{BASE_URL}/api/competitions/{competition_id}/leaderboard"
    )

    if response.status_code == 200:
        leaderboard = response.json()
        print(f"✓ Leaderboard retrieved ({len(leaderboard)} entries)")
        for entry in leaderboard:
            print(f"  #{entry['rank']}: Score {entry['score']}")
        return leaderboard
    else:
        print(f"✗ Failed to get leaderboard: {response.status_code}")
        return None


def test_full_flow():
    """Test the complete competition flow."""
    print("\n" + "="*60)
    print("COMPLETE COMPETITION FLOW TEST")
    print("="*60)

    try:
        # 1. Health check
        test_health_check()

        # 2. Create competition
        competition_id = test_create_competition()
        if not competition_id:
            print("\n⚠ Cannot continue - failed to create competition")
            return

        # 3. Start competition
        started = test_start_competition(competition_id)
        if not started:
            print("\n⚠ Cannot continue - failed to start competition")
            return

        # 4. Monitor until completion
        status = test_monitor_competition(competition_id, max_wait=300)
        if not status:
            print("\n⚠ Monitoring stopped")
            return

        # 5. Get results (if completed)
        if status.get('status') == 'completed':
            results = test_get_results(competition_id)
            if results:
                test_get_leaderboard(competition_id)

        print("\n" + "="*60)
        print("TEST COMPLETED!")
        print("="*60 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to API server")
        print("  Make sure the server is running: python backend/main.py")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


def test_individual_endpoint():
    """Test individual endpoints interactively."""
    print("\n" + "="*60)
    print("INDIVIDUAL ENDPOINT TESTS")
    print("="*60 + "\n")

    print("Choose a test:")
    print("1. Health Check")
    print("2. Create Competition")
    print("3. Start Competition (need ID)")
    print("4. Get Status (need ID)")
    print("5. Get Results (need ID)")
    print("6. Full Flow Test")
    print("0. Exit\n")

    choice = input("Enter choice (0-6): ").strip()

    if choice == "1":
        test_health_check()
    elif choice == "2":
        test_create_competition()
    elif choice == "3":
        comp_id = input("Enter competition ID: ").strip()
        test_start_competition(comp_id)
    elif choice == "4":
        comp_id = input("Enter competition ID: ").strip()
        response = requests.get(f"{BASE_URL}/api/competitions/{comp_id}/status")
        print(json.dumps(response.json(), indent=2))
    elif choice == "5":
        comp_id = input("Enter competition ID: ").strip()
        test_get_results(comp_id)
    elif choice == "6":
        test_full_flow()
    elif choice == "0":
        print("Exiting...")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        # Run full flow test
        test_full_flow()
    else:
        # Interactive mode
        test_individual_endpoint()
