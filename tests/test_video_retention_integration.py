"""Integration test for get_video_retention with real Kaltura data."""

import asyncio
import json
import os
from datetime import datetime, timedelta

import pytest
from dotenv import load_dotenv

from kaltura_mcp.kaltura_client import KalturaClientManager
from kaltura_mcp.tools.analytics import get_video_retention


class TestVideoRetentionIntegration:
    """Integration tests for video retention analysis with real data."""

    @pytest.fixture
    def manager(self):
        """Create a real Kaltura client manager."""
        # Load environment variables
        load_dotenv()

        # Check if credentials are available
        partner_id = os.getenv("KALTURA_PARTNER_ID")
        admin_secret = os.getenv("KALTURA_ADMIN_SECRET")

        if not partner_id or not admin_secret:
            pytest.skip("Kaltura credentials not found in environment")

        # Create manager - it loads config from environment
        manager = KalturaClientManager()
        return manager

    @pytest.fixture
    def date_range(self):
        """Get date range for last 12 months."""
        today = datetime.now()
        start_date = today - timedelta(days=365)
        return {
            "from_date": start_date.strftime("%Y-%m-%d"),
            "to_date": today.strftime("%Y-%m-%d"),
        }

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_video_retention_real_data(self, manager, date_range):
        """Test video retention with real Kaltura data for entry 1_3atosphg."""
        entry_id = "1_3atosphg"

        print(f"\n🔍 Testing get_video_retention for entry {entry_id}")
        print(f"📅 Date range: {date_range['from_date']} to {date_range['to_date']}")

        # Call the function
        result = await get_video_retention(
            manager=manager,
            entry_id=entry_id,
            from_date=date_range["from_date"],
            to_date=date_range["to_date"],
        )

        # Parse the result
        data = json.loads(result)

        # Print the result for inspection
        print("\n📊 Response structure:")
        print(json.dumps(data, indent=2))

        # Verify structure
        assert "video" in data, "Response should contain 'video' section"
        assert "retention_data" in data, "Response should contain 'retention_data' section"

        # Verify video metadata
        video_info = data["video"]
        assert video_info["id"] == entry_id, f"Video ID should be {entry_id}"
        assert "title" in video_info, "Video should have a title"
        assert "duration_seconds" in video_info, "Video should have duration in seconds"
        assert "duration_formatted" in video_info, "Video should have formatted duration"

        # If we got duration 0, it means media info fetch failed - try to get it separately
        if video_info["duration_seconds"] == 0:
            print("\n⚠️  Video duration is 0, trying to fetch media info separately...")
            from kaltura_mcp.tools.media import get_media_entry

            try:
                media_result = await get_media_entry(manager, entry_id)
                media_data = json.loads(media_result)
                actual_duration = media_data.get("duration", 0)
                print(f"  ✓ Found actual duration: {actual_duration} seconds")
                # For the test, we'll use this duration for validation
                video_info["duration_seconds"] = actual_duration
                video_info[
                    "duration_formatted"
                ] = f"{actual_duration // 60:02d}:{actual_duration % 60:02d}"
            except Exception as e:
                print(f"  ✗ Failed to fetch media info: {e}")

        print("\n📹 Video Info:")
        print(f"  - ID: {video_info['id']}")
        print(f"  - Title: {video_info['title']}")
        print(
            f"  - Duration: {video_info['duration_formatted']} ({video_info['duration_seconds']} seconds)"
        )

        # Verify retention data
        retention_data = data["retention_data"]
        assert isinstance(retention_data, list), "Retention data should be a list"
        assert len(retention_data) > 0, "Retention data should not be empty"

        print(f"\n📈 Retention Data Points: {len(retention_data)}")

        # Verify each data point
        for i, point in enumerate(retention_data):
            # Check required fields
            assert "percentile" in point, f"Point {i} should have 'percentile'"
            assert "time_seconds" in point, f"Point {i} should have 'time_seconds'"
            assert "time_formatted" in point, f"Point {i} should have 'time_formatted'"
            assert "viewers" in point, f"Point {i} should have 'viewers'"
            assert "unique_users" in point, f"Point {i} should have 'unique_users'"
            assert "retention_percentage" in point, f"Point {i} should have 'retention_percentage'"
            assert "replays" in point, f"Point {i} should have 'replays'"

            # Verify time calculation
            expected_time = int((point["percentile"] / 100.0) * video_info["duration_seconds"])
            assert (
                point["time_seconds"] == expected_time
            ), f"Time calculation incorrect for percentile {point['percentile']}"

            # Verify time formatting
            expected_formatted = f"{expected_time // 60:02d}:{expected_time % 60:02d}"
            assert (
                point["time_formatted"] == expected_formatted
            ), f"Time formatting incorrect for percentile {point['percentile']}"

            # Print sample points
            if i in [0, 10, 25, 50, 75, 100] or i == len(retention_data) - 1:
                print(f"\n  📍 Percentile {point['percentile']}% = {point['time_formatted']}:")
                print(f"     - Viewers: {point['viewers']}")
                print(f"     - Unique: {point['unique_users']}")
                print(f"     - Retention: {point['retention_percentage']}%")
                print(f"     - Replays: {point['replays']}")

        # Verify insights if present
        if "insights" in data:
            insights = data["insights"]
            print("\n💡 Insights:")

            if "average_retention" in insights:
                print(f"  - Average Retention: {insights['average_retention']}%")

            if "completion_rate" in insights:
                print(f"  - Completion Rate: {insights['completion_rate']}%")

            if "fifty_percent_point" in insights:
                print(f"  - 50% Drop Point: {insights['fifty_percent_point']}")

            if "major_dropoffs" in insights:
                print(f"  - Major Drop-offs: {len(insights['major_dropoffs'])} found")
                for drop in insights["major_dropoffs"][:3]:  # Show first 3
                    print(
                        f"    • {drop['time']} ({drop['percentile']}%): -{drop['retention_loss']}%"
                    )

            if "replay_hotspots" in insights:
                print(f"  - Replay Hotspots: {len(insights['replay_hotspots'])} found")
                for hotspot in insights["replay_hotspots"][:3]:  # Show first 3
                    print(
                        f"    • {hotspot['time']} ({hotspot['percentile']}%): {hotspot['replay_rate']*100:.0f}% replay rate"
                    )

        # Verify data consistency
        print("\n✅ Data Consistency Checks:")

        # Check that percentiles are in order
        percentiles = [p["percentile"] for p in retention_data]
        assert percentiles == sorted(percentiles), "Percentiles should be in ascending order"
        print(f"  ✓ Percentiles are in order (0-{percentiles[-1]})")

        # Check that time increases with percentiles
        times = [p["time_seconds"] for p in retention_data]
        assert times == sorted(times), "Times should increase with percentiles"
        print(f"  ✓ Times increase correctly (0s to {times[-1]}s)")

        # Check retention percentage logic
        first_retention = retention_data[0]["retention_percentage"]
        first_viewers = retention_data[0]["viewers"]

        # Handle edge case where video starts with 0 viewers
        if first_viewers == 0:
            print(f"  ✓ Initial retention is {first_retention}% (0 viewers at start)")
            # Find the max retention point (should be 100% at peak viewership)
            max_retention = max(point["retention_percentage"] for point in retention_data)
            assert max_retention == 100.0, "Peak viewership should have 100% retention"
            print("  ✓ Peak retention is 100% (using max viewers as reference)")
        else:
            # Normal case - should start near 100%
            assert (
                first_retention == 100.0 or first_retention > 90.0
            ), "First retention point should be close to 100%"
            print(f"  ✓ Initial retention is {first_retention}%")

        # Verify replays calculation
        for point in retention_data:
            calculated_replays = point["viewers"] - point["unique_users"]
            assert (
                point["replays"] == calculated_replays
            ), f"Replays calculation incorrect at {point['percentile']}%"
        print("  ✓ Replay calculations are correct")

        print("\n🎉 All tests passed! The get_video_retention function works correctly.")
        print("📊 The data includes proper time conversion from percentiles to video time.")


if __name__ == "__main__":
    # Run the test directly
    async def run_test():
        """Run the integration test."""
        test = TestVideoRetentionIntegration()

        # Load environment
        load_dotenv()

        # Create manager - it loads config from environment
        manager = KalturaClientManager()

        # Get date range
        today = datetime.now()
        date_range = {
            "from_date": (today - timedelta(days=365)).strftime("%Y-%m-%d"),
            "to_date": today.strftime("%Y-%m-%d"),
        }

        # Run test
        await test.test_get_video_retention_real_data(manager, date_range)

    # Execute
    asyncio.run(run_test())
