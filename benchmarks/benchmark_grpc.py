import asyncio
import os
import statistics
import sys
import time

import grpc

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(current_dir, "..", "backend")
sys.path.append(backend_path)

from protos import (  # type: ignore  # noqa: E402
    auth_pb2,
    auth_pb2_grpc,
    members_pb2,
    members_pb2_grpc,
)

# --- CONFIGURATION ---
GRPC_ADDR = "localhost:50052"
TOTAL_USERS = 50
REQUESTS_PER_USER = 20


async def run_user_session(user_id):
    """
    Simulates a single user's lifecycle via gRPC
    """
    async with grpc.aio.insecure_channel(GRPC_ADDR) as channel:
        auth_stub = auth_pb2_grpc.AuthServiceStub(channel)
        member_stub = members_pb2_grpc.MemberServiceStub(channel)

        username = f"{user_id} {time.time()}"
        email = f"grpc_user_{user_id}_{time.time()}@example.com"
        password = "password123"
        latencies = []

        try:
            # 1. REGISTER
            start = time.perf_counter()
            await auth_stub.Register(
                auth_pb2.RegisterRequest(
                    username=username,
                    email=email,
                    password=password,
                    full_name=f"gRPC User {user_id}",
                )
            )
            latencies.append(time.perf_counter() - start)

            # 2. LOGIN
            start = time.perf_counter()
            login_resp = await auth_stub.Login(
                auth_pb2.LoginRequest(email=email, password=password)
            )
            token = login_resp.access_token
            metadata = (("authorization", f"Bearer {token}"),)
            latencies.append(time.perf_counter() - start)

            # 3. TYPICAL ACTIONS (READS)
            for _ in range(REQUESTS_PER_USER):
                # READ: List Members
                start = time.perf_counter()
                await member_stub.GetMembers(
                    members_pb2.GetMembersRequest(), metadata=metadata
                )
                latencies.append(time.perf_counter() - start)

            return latencies
        except Exception as e:
            print(f"User {user_id} failed: {e}")
            return []


async def main():
    print(
        f"Starting gRPC Benchmark: {TOTAL_USERS} users, {REQUESTS_PER_USER} requests/user"
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

        print("\n--- gRPC RESULTS ---")
        print(f"Total Requests: {len(all_latencies)}")
        print(f"Total Time:     {total_time:.2f}s")
        print(f"Throughput:     {throughput:.2f} req/s")
        print(f"Avg Latency:    {avg_latency:.2f}ms")
        print(f"P95 Latency:    {p95_latency:.2f}ms")
        print("--------------------\n")


if __name__ == "__main__":
    asyncio.run(main())
