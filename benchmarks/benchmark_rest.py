import asyncio
import statistics
import time

import httpx

BASE_URL = "http://localhost:8000/api"
TOTAL_USERS = 50
REQUESTS_PER_USER = 20


async def run_user_session(user_id):
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        email = f"user_{user_id}_{time.time()}@example.com"
        password = "password123"
        latencies = []

        try:
            start = time.perf_counter()
            resp = await client.post(
                "/auth/register",
                json={
                    "email": email,
                    "password": password,
                    "full_name": f"Benchmark User {user_id}",
                },
            )
            latencies.append(time.perf_counter() - start)

            # LOGIN
            start = time.perf_counter()
            resp = await client.post(
                "/auth/login",
                data={
                    "username": email,
                    "password": password,
                },
            )
            token = resp.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            latencies.append(time.perf_counter() - start)

            # READS
            for _ in range(REQUESTS_PER_USER):
                start = time.perf_counter()
                await client.get("/members", headers=headers)
                latencies.append(time.perf_counter() - start)

            return latencies
        except Exception as e:
            print(f"User {user_id} failed: {e}")
            return []


async def main():
    print(
        f"Starting REST Benchmark: {TOTAL_USERS} users, {REQUESTS_PER_USER} requests/user"
    )
    start_time = time.perf_counter()

    tasks = [run_user_session(i) for i in range(TOTAL_USERS)]
    results = await asyncio.gather(*tasks)

    total_time = time.perf_counter() - start_time

    all_latencies = [result for user_result in results for result in user_result]

    if all_latencies:
        avg_latency = statistics.mean(all_latencies) * 1000
        p95_latency = statistics.quantiles(all_latencies, n=20)[18] * 1000
        throughput = len(all_latencies) / total_time

        print("\n--- REST RESULTS ---")
        print(f"Total Requests: {len(all_latencies)}")
        print(f"Total Time:     {total_time:.2f}s")
        print(f"Throughput:     {throughput:.2f} req/s")
        print(f"Avg Latency:    {avg_latency:.2f}ms")
        print(f"P95 Latency:    {p95_latency:.2f}ms")
        print("--------------------\n")


if __name__ == "__main__":
    asyncio.run(main())
