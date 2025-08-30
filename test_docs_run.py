import requests
import json

# Test script to trigger docs run

def test_docs_run():
    # Define test data
    base_url = "http://localhost:8000"

    # First, let's check if we can get a test user or create one
    # For now, let's assume there's a user with token 'test-token' from the test setup
    auth_token = "test-e2e-token"  # From test file

    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": auth_token
    }

    # Step 1: Try to connect a test repo
    repo_data = {
        "repo_url": "https://github.com/test/fixmydocs-test",
        "repo_name": "fixmydocs-test"
    }

    print("Step 1: Connecting test repository...")
    response = requests.post(f"{base_url}/api/repos/connect", json=repo_data, headers=headers)
    print(f"Connect response: {response.status_code}")
    if response.status_code == 200:
        repo_result = response.json()
        repo_id = repo_result.get("repo_id", 1)  # Fallback to 1 if not provided
        print(f"Repository connected with ID: {repo_id}")
    else:
        print(f"Failed to connect repo: {response.text}")
        # Try with existing repo ID 1
        repo_id = 1

    # Step 2: Trigger documentation run
    docs_data = {"repo_id": repo_id}
    print(f"Step 2: Triggering docs run for repo_id: {repo_id}")
    response = requests.post(f"{base_url}/api/docs/run", json=docs_data, headers=headers)
    print(f"Docs run response: {response.status_code}")
    if response.status_code == 200:
        docs_result = response.json()
        print(f"Docs run result: {docs_result}")
        job_id = docs_result.get("job_id")
        print(f"Job ID: {job_id}")

        # Step 3: Check job status
        print(f"Step 3: Checking status for job_id: {job_id}")
        status_response = requests.get(f"{base_url}/api/jobs/status/{job_id}", headers=headers)
        print(f"Status response: {status_response.json()}")
    else:
        print(f"Failed to trigger docs run: {response.text}")

if __name__ == "__main__":
    test_docs_run()