#!/usr/bin/env python3
"""
Performance testing script for the Kaltura-MCP Server.

This script tests the performance of the Kaltura-MCP Server with large datasets
to validate context management strategies.
"""
import argparse
import asyncio
import json
import statistics
import time
from typing import Any, Dict, List, Tuple

from mcp.client.session import ClientSession as Client
from mcp.client.stdio import stdio_client

# Default test parameters
DEFAULT_PAGE_SIZE = 50
DEFAULT_NUM_REQUESTS = 10
DEFAULT_STRATEGIES = ["pagination", "selective", "summarization"]
DEFAULT_OPERATIONS = [
    "list_media",
    "get_media",
    "list_categories",
    "get_category",
    "list_users",
    "get_user",
]


class PerformanceTester:
    """Performance tester for the Kaltura-MCP Server."""

    def __init__(self, client: Client):
        """Initialize the performance tester."""
        self.client = client
        self.results = {}

    async def test_list_media(self, page_size: int, strategy: str = None) -> Tuple[float, int]:
        """Test the performance of listing media entries."""
        start_time = time.time()

        # Build the URI with strategy parameter if provided
        uri = f"kaltura://media/list?page_size={page_size}"
        if strategy:
            uri += f"&strategy={strategy}"

        # Read the resource
        result = await self.client.read_resource(uri)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Parse the result to get the total count
        result_json = json.loads(result)
        total_count = result_json.get("totalCount", 0)

        return elapsed_time, total_count

    async def test_get_media(self, entry_id: str, strategy: str = None) -> Tuple[float, Dict[str, Any]]:
        """Test the performance of getting a media entry."""
        start_time = time.time()

        # Build the URI with strategy parameter if provided
        uri = f"kaltura://media/{entry_id}"
        if strategy:
            uri += f"?strategy={strategy}"

        # Read the resource
        result = await self.client.read_resource(uri)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Parse the result
        result_json = json.loads(result)

        return elapsed_time, result_json

    async def test_list_categories(self, page_size: int, strategy: str = None) -> Tuple[float, int]:
        """Test the performance of listing categories."""
        start_time = time.time()

        # Build the URI with strategy parameter if provided
        uri = f"kaltura://categories/list?page_size={page_size}"
        if strategy:
            uri += f"&strategy={strategy}"

        # Read the resource
        result = await self.client.read_resource(uri)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Parse the result to get the total count
        result_json = json.loads(result)
        total_count = result_json.get("totalCount", 0)

        return elapsed_time, total_count

    async def test_get_category(self, category_id: int, strategy: str = None) -> Tuple[float, Dict[str, Any]]:
        """Test the performance of getting a category."""
        start_time = time.time()

        # Build the URI with strategy parameter if provided
        uri = f"kaltura://categories/{category_id}"
        if strategy:
            uri += f"?strategy={strategy}"

        # Read the resource
        result = await self.client.read_resource(uri)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Parse the result
        result_json = json.loads(result)

        return elapsed_time, result_json

    async def test_list_users(self, page_size: int, strategy: str = None) -> Tuple[float, int]:
        """Test the performance of listing users."""
        start_time = time.time()

        # Build the URI with strategy parameter if provided
        uri = f"kaltura://users/list?page_size={page_size}"
        if strategy:
            uri += f"&strategy={strategy}"

        # Read the resource
        result = await self.client.read_resource(uri)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Parse the result to get the total count
        result_json = json.loads(result)
        total_count = result_json.get("totalCount", 0)

        return elapsed_time, total_count

    async def test_get_user(self, user_id: str, strategy: str = None) -> Tuple[float, Dict[str, Any]]:
        """Test the performance of getting a user."""
        start_time = time.time()

        # Build the URI with strategy parameter if provided
        uri = f"kaltura://users/{user_id}"
        if strategy:
            uri += f"?strategy={strategy}"

        # Read the resource
        result = await self.client.read_resource(uri)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Parse the result
        result_json = json.loads(result)

        return elapsed_time, result_json

    async def run_tests(self, operations: List[str], strategies: List[str], num_requests: int, page_size: int) -> Dict[str, Any]:
        """Run performance tests."""
        results = {}

        # Get a media entry ID for testing
        media_id = await self._get_media_id()

        # Get a category ID for testing
        category_id = await self._get_category_id()

        # Get a user ID for testing
        user_id = await self._get_user_id()

        # Run tests for each operation and strategy
        for operation in operations:
            results[operation] = {}

            for strategy in strategies:
                print(f"Testing {operation} with {strategy} strategy...")
                times = []

                for i in range(num_requests):
                    if operation == "list_media":
                        elapsed_time, total_count = await self.test_list_media(page_size, strategy)
                        print(f"  Request {i+1}/{num_requests}: {elapsed_time:.4f}s, {total_count} entries")
                    elif operation == "get_media":
                        elapsed_time, _ = await self.test_get_media(media_id, strategy)
                        print(f"  Request {i+1}/{num_requests}: {elapsed_time:.4f}s")
                    elif operation == "list_categories":
                        elapsed_time, total_count = await self.test_list_categories(page_size, strategy)
                        print(f"  Request {i+1}/{num_requests}: {elapsed_time:.4f}s, {total_count} categories")
                    elif operation == "get_category":
                        elapsed_time, _ = await self.test_get_category(category_id, strategy)
                        print(f"  Request {i+1}/{num_requests}: {elapsed_time:.4f}s")
                    elif operation == "list_users":
                        elapsed_time, total_count = await self.test_list_users(page_size, strategy)
                        print(f"  Request {i+1}/{num_requests}: {elapsed_time:.4f}s, {total_count} users")
                    elif operation == "get_user":
                        elapsed_time, _ = await self.test_get_user(user_id, strategy)
                        print(f"  Request {i+1}/{num_requests}: {elapsed_time:.4f}s")

                    times.append(elapsed_time)

                # Calculate statistics
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                median_time = statistics.median(times)
                stdev_time = statistics.stdev(times) if len(times) > 1 else 0

                results[operation][strategy] = {
                    "avg_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "median_time": median_time,
                    "stdev_time": stdev_time,
                    "times": times,
                }

                print(
                    f"  Average: {avg_time:.4f}s, Min: {min_time:.4f}s, Max: {max_time:.4f}s, Median: {median_time:.4f}s, StdDev: {stdev_time:.4f}s"
                )

        return results

    async def _get_media_id(self) -> str:
        """Get a media entry ID for testing."""
        result = await self.client.read_resource("kaltura://media/list?page_size=1")
        result_json = json.loads(result)

        if result_json.get("objects") and len(result_json["objects"]) > 0:
            return result_json["objects"][0]["id"]

        raise ValueError("No media entries found")

    async def _get_category_id(self) -> int:
        """Get a category ID for testing."""
        result = await self.client.read_resource("kaltura://categories/list?page_size=1")
        result_json = json.loads(result)

        if result_json.get("objects") and len(result_json["objects"]) > 0:
            return result_json["objects"][0]["id"]

        raise ValueError("No categories found")

    async def _get_user_id(self) -> str:
        """Get a user ID for testing."""
        result = await self.client.read_resource("kaltura://users/list?page_size=1")
        result_json = json.loads(result)

        if result_json.get("objects") and len(result_json["objects"]) > 0:
            return result_json["objects"][0]["id"]

        raise ValueError("No users found")


async def main():
    """Run the performance tests."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Performance testing for Kaltura-MCP Server")
    parser.add_argument(
        "--page-size",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"Page size for list operations (default: {DEFAULT_PAGE_SIZE})",
    )
    parser.add_argument(
        "--num-requests",
        type=int,
        default=DEFAULT_NUM_REQUESTS,
        help=f"Number of requests per test (default: {DEFAULT_NUM_REQUESTS})",
    )
    parser.add_argument(
        "--strategies",
        type=str,
        default=",".join(DEFAULT_STRATEGIES),
        help=f"Comma-separated list of strategies to test (default: {','.join(DEFAULT_STRATEGIES)})",
    )
    parser.add_argument(
        "--operations",
        type=str,
        default=",".join(DEFAULT_OPERATIONS),
        help=f"Comma-separated list of operations to test (default: {','.join(DEFAULT_OPERATIONS)})",
    )
    parser.add_argument("--output", type=str, help="Output file for results (JSON format)")

    args = parser.parse_args()

    # Parse strategies and operations
    strategies = args.strategies.split(",")
    operations = args.operations.split(",")

    print("Connecting to Kaltura-MCP Server...")

    async with stdio_client() as streams:
        client = Client()
        await client.connect(streams[0], streams[1])

        print("Connected to Kaltura-MCP Server")

        # Create performance tester
        tester = PerformanceTester(client)

        # Run tests
        print(f"\nRunning performance tests with {args.num_requests} requests per test and page size {args.page_size}...")
        results = await tester.run_tests(operations, strategies, args.num_requests, args.page_size)

        # Print summary
        print("\nPerformance Test Summary:")
        print("========================")

        for operation in results:
            print(f"\n{operation}:")

            for strategy in results[operation]:
                stats = results[operation][strategy]
                print(f"  {strategy}:")
                print(f"    Average: {stats['avg_time']:.4f}s")
                print(f"    Min: {stats['min_time']:.4f}s")
                print(f"    Max: {stats['max_time']:.4f}s")
                print(f"    Median: {stats['median_time']:.4f}s")
                print(f"    StdDev: {stats['stdev_time']:.4f}s")

        # Save results to file if specified
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    asyncio.run(main())
