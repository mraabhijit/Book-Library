import time
import requests

# Configuration
BASE_URL = "http://localhost:8000/api"
EMAIL = "user@example.com"
PASSWORD = "password123"  # Assuming standard password for testing


def measure_request(method, url, headers=None, data=None):
    start_time = time.perf_counter()
    if method == "GET":
        response = requests.get(url, headers=headers)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        response = requests.put(url, headers=headers, json=data)
    elif method == "DELETE":
        response = requests.delete(url, headers=headers)

    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000

    return response, latency_ms


def run_benchmark():
    print("--- Starting Performance Benchmark ---")

    # 1. Login
    print(f"Logging in as {EMAIL}...")
    login_data = {"username": EMAIL, "password": PASSWORD}
    # OAuth2 specifies form data for the login endpoint
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Login successful.\n")

    results = []

    # 2. GET Books (Cold Start - No Cache)
    print("Test 1: GET /books (Cold Start)")
    _, time1 = measure_request("GET", f"{BASE_URL}/books", headers=headers)
    results.append(("GET /books (Cold)", f"{time1:.2f} ms"))
    print(f"Latency: {time1:.2f} ms\n")

    # 3. GET Books (Warm Start - From Cache)
    print("Test 2: GET /books (Warm Start - Cached)")
    _, time2 = measure_request("GET", f"{BASE_URL}/books", headers=headers)
    results.append(("GET /books (Warm)", f"{time2:.2f} ms"))
    print(f"Latency: {time2:.2f} ms\n")

    # 4. GET Single Book (Cold)
    # We need an ID from the first request
    books_response = requests.get(f"{BASE_URL}/books", headers=headers).json()
    if not books_response:
        print("No books found to test single GET.")
        return
    book_id = books_response[0]["id"]

    print(f"Test 3: GET /books/{book_id} (Cold Start)")
    _, time3 = measure_request("GET", f"{BASE_URL}/books/{book_id}", headers=headers)
    results.append((f"GET /books/{book_id} (Cold)", f"{time3:.2f} ms"))
    print(f"Latency: {time3:.2f} ms\n")

    # 5. GET Single Book (Warm)
    print(f"Test 4: GET /books/{book_id} (Warm Start - Cached)")
    _, time4 = measure_request("GET", f"{BASE_URL}/books/{book_id}", headers=headers)
    results.append((f"GET /books/{book_id} (Warm)", f"{time4:.2f} ms"))
    print(f"Latency: {time4:.2f} ms\n")

    # 6. POST Book (Invalidates List Cache)
    print("Test 5: POST /books (Creates new data & Invalidate list cache)")
    new_book = {
        "title": f"Benchmarked Book {int(time.time())}",
        "author": "Latency Tester",
        "isbn": f"TEST-{int(time.time())}",
        "description": "Benchmark test book",
    }
    post_response, time5 = measure_request(
        "POST", f"{BASE_URL}/books", headers=headers, data=new_book
    )
    results.append(("POST /books (Mutation)", f"{time5:.2f} ms"))
    print(f"Latency: {time5:.2f} ms\n")

    created_book_id = post_response.json()["id"]

    # 7. GET Books (Recold - Should be slower as cache was invalidated)
    print("Test 6: GET /books (Recold - post-invalidation)")
    _, time6 = measure_request("GET", f"{BASE_URL}/books", headers=headers)
    results.append(("GET /books (Post-Invalidation)", f"{time6:.2f} ms"))
    print(f"Latency: {time6:.2f} ms\n")

    # 8. DELETE Book (Cleanup)
    print(f"Test 7: DELETE /books/{created_book_id}")
    _, time7 = measure_request(
        "DELETE", f"{BASE_URL}/books/{created_book_id}", headers=headers
    )
    results.append(("DELETE /books", f"{time7:.2f} ms"))
    print(f"Latency: {time7:.2f} ms\n")

    # Final Summary
    print("\n" + "=" * 40)
    print(f"{'Operation':<30} | {'Latency':<10}")
    print("-" * 40)
    for op, latency in results:
        print(f"{op:<30} | {latency:<10}")
    print("=" * 40)


if __name__ == "__main__":
    run_benchmark()
