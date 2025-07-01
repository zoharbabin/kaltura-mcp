#!/usr/bin/env python3
"""
Video Timeline Retention Visualization Example

This example demonstrates how to use get_video_timeline_analytics
to create retention curves and identify viewer behavior patterns.
"""

import json
import asyncio
from datetime import datetime, timedelta

# Example of creating retention visualizations from timeline data


async def analyze_video_retention(manager, entry_id):
    """Get and analyze retention data for a video."""
    
    print(f"Analyzing retention for video: {entry_id}")
    
    # Get retention data
    result = await get_video_timeline_analytics(
        manager,
        entry_id=entry_id
    )
    
    data = json.loads(result)
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return None
    
    return data


def create_retention_chart_config(retention_data):
    """Create Chart.js configuration for retention curve."""
    
    retention_curve = retention_data["retention_curve"]
    insights = retention_data["insights"]
    
    # Main retention line
    retention_dataset = {
        "label": "Viewer Retention",
        "data": [{"x": p["percentile"], "y": p["retention_rate"]} for p in retention_curve],
        "borderColor": "rgb(75, 192, 192)",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "tension": 0.4,
        "fill": True
    }
    
    # Drop-off indicators
    dropoff_points = []
    for drop in insights.get("major_drop_offs", []):
        dropoff_points.append({
            "x": drop["percentile"],
            "y": next(p["retention_rate"] for p in retention_curve if p["percentile"] == drop["percentile"])
        })
    
    dropoff_dataset = {
        "label": "Major Drop-offs",
        "data": dropoff_points,
        "borderColor": "rgb(255, 99, 132)",
        "backgroundColor": "rgb(255, 99, 132)",
        "pointRadius": 8,
        "pointHoverRadius": 10,
        "showLine": False
    }
    
    # Replay hotspots
    replay_points = []
    for replay in insights.get("replay_hotspots", []):
        replay_points.append({
            "x": replay["percentile"],
            "y": next(p["retention_rate"] for p in retention_curve if p["percentile"] == replay["percentile"])
        })
    
    replay_dataset = {
        "label": "Replay Hotspots",
        "data": replay_points,
        "borderColor": "rgb(255, 205, 86)",
        "backgroundColor": "rgb(255, 205, 86)",
        "pointRadius": 8,
        "pointStyle": "star",
        "showLine": False
    }
    
    return {
        "type": "line",
        "data": {
            "datasets": [retention_dataset, dropoff_dataset, replay_dataset]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": f"Video Retention Analysis - {retention_data['video_id']}"
                },
                "annotation": {
                    "annotations": {
                        "fifty_percent": {
                            "type": "line",
                            "xMin": insights["fifty_percent_point"],
                            "xMax": insights["fifty_percent_point"],
                            "borderColor": "rgb(255, 99, 132)",
                            "borderWidth": 2,
                            "borderDash": [5, 5],
                            "label": {
                                "content": "50% Retention",
                                "enabled": True
                            }
                        }
                    }
                }
            },
            "scales": {
                "x": {
                    "type": "linear",
                    "display": True,
                    "title": {
                        "display": True,
                        "text": "Video Progress (%)"
                    },
                    "min": 0,
                    "max": 100
                },
                "y": {
                    "display": True,
                    "title": {
                        "display": True,
                        "text": "Retention Rate (%)"
                    },
                    "min": 0,
                    "max": 100
                }
            }
        }
    }


def create_heatmap_data(retention_curve):
    """Create heatmap data showing engagement intensity."""
    
    heatmap_data = []
    
    for i, point in enumerate(retention_curve):
        # Calculate engagement score based on retention and replays
        engagement = point["retention_rate"]
        if point["replays"] > 0 and point["unique_users"] > 0:
            replay_boost = (point["replays"] / point["unique_users"]) * 20
            engagement = min(100, engagement + replay_boost)
        
        heatmap_data.append({
            "percentile": point["percentile"],
            "engagement": engagement,
            "viewers": point["viewers"],
            "replays": point["replays"]
        })
    
    return heatmap_data


async def compare_cohorts(manager, entry_id):
    """Compare retention between different viewer cohorts."""
    
    print(f"\nComparing cohorts for video: {entry_id}")
    
    # Get data with cohort comparison
    result = await get_video_timeline_analytics(
        manager,
        entry_id=entry_id,
        user_ids="Unknown",  # Anonymous viewers
        compare_cohorts=True
    )
    
    data = json.loads(result)
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return None
    
    if "cohort_comparison" in data:
        all_viewers = data["cohort_comparison"]["all_viewers"]
        anonymous = data["cohort_comparison"]["filtered_cohort"]
        
        print("\nCohort Comparison Insights:")
        print(f"All Viewers - Avg Retention: {all_viewers['insights']['avg_retention']}%")
        print(f"Anonymous - Avg Retention: {anonymous['insights']['avg_retention']}%")
        print(f"All Viewers - Completion: {all_viewers['insights']['completion_rate']}%")
        print(f"Anonymous - Completion: {anonymous['insights']['completion_rate']}%")
    
    return data


def generate_retention_report(retention_data):
    """Generate a text report from retention data."""
    
    insights = retention_data["insights"]
    
    report = f"""
Video Retention Report
=====================
Video ID: {retention_data['video_id']}
Date Range: {retention_data['date_range']['from']} to {retention_data['date_range']['to']}

Key Metrics:
- Average Retention: {insights['avg_retention']}%
- 50% Retention Point: {insights['fifty_percent_point']}% of video
- Completion Rate: {insights['completion_rate']}%
- Engagement Score: {insights['engagement_score']}

Major Drop-off Points:
"""
    
    for drop in insights.get("major_drop_offs", []):
        report += f"- {drop['percentile']}% mark: {drop['drop_percentage']}% viewer loss\n"
    
    report += "\nReplay Hotspots:\n"
    for replay in insights.get("replay_hotspots", []):
        report += f"- {replay['percentile']}% mark: {replay['replay_ratio']*100:.1f}% replay rate\n"
    
    report += f"""
Recommendations:
1. Review content at {insights['fifty_percent_point']}% - this is where you lose half your audience
2. Investigate drop-offs to identify problematic content
3. Extract and promote high-replay segments
4. Consider trimming content after {insights.get('major_drop_offs', [{'percentile': 100}])[0]['percentile']}% if completion is low
"""
    
    return report


def create_engagement_timeline(retention_curve):
    """Create a timeline showing engagement throughout the video."""
    
    timeline = []
    
    for i in range(0, 101, 10):  # Every 10%
        point = next((p for p in retention_curve if p["percentile"] == i), None)
        if point:
            status = "🟢 High" if point["retention_rate"] > 70 else "🟡 Medium" if point["retention_rate"] > 40 else "🔴 Low"
            replay_indicator = "🔄" if point["replays"] > point["unique_users"] * 0.2 else ""
            
            timeline.append({
                "position": f"{i}%",
                "retention": f"{point['retention_rate']:.1f}%",
                "status": status,
                "replay": replay_indicator
            })
    
    return timeline


async def main():
    """Example usage of video timeline analytics."""
    
    print("Video Timeline Analytics Example")
    print("================================\n")
    
    # Example retention data structure
    example_data = {
        "video_id": "1_abc123",
        "date_range": {"from": "2024-01-01", "to": "2024-01-31"},
        "retention_curve": [
            {"percentile": 0, "retention_rate": 100.0, "viewers": 1000, "unique_users": 850, "replays": 150},
            {"percentile": 10, "retention_rate": 85.0, "viewers": 850, "unique_users": 750, "replays": 100},
            {"percentile": 25, "retention_rate": 70.0, "viewers": 700, "unique_users": 650, "replays": 50},
            {"percentile": 50, "retention_rate": 55.0, "viewers": 550, "unique_users": 500, "replays": 50},
            {"percentile": 75, "retention_rate": 45.0, "viewers": 450, "unique_users": 400, "replays": 50},
            {"percentile": 90, "retention_rate": 40.0, "viewers": 400, "unique_users": 350, "replays": 50},
            {"percentile": 100, "retention_rate": 38.0, "viewers": 380, "unique_users": 330, "replays": 50}
        ],
        "insights": {
            "avg_retention": 65.5,
            "fifty_percent_point": 35,
            "completion_rate": 38.0,
            "major_drop_offs": [
                {"percentile": 10, "drop_percentage": 15.0},
                {"percentile": 25, "drop_percentage": 15.0}
            ],
            "replay_hotspots": [
                {"percentile": 45, "replay_ratio": 0.35},
                {"percentile": 78, "replay_ratio": 0.28}
            ],
            "engagement_score": 51.75
        }
    }
    
    # Generate visualizations
    print("1. Chart.js Configuration:")
    chart_config = create_retention_chart_config(example_data)
    print(json.dumps(chart_config, indent=2))
    
    print("\n2. Engagement Timeline:")
    timeline = create_engagement_timeline(example_data["retention_curve"])
    for point in timeline:
        print(f"{point['position']}: {point['retention']} {point['status']} {point['replay']}")
    
    print("\n3. Retention Report:")
    report = generate_retention_report(example_data)
    print(report)
    
    print("\n4. Heatmap Data (first 5 points):")
    heatmap = create_heatmap_data(example_data["retention_curve"])
    for point in heatmap[:5]:
        print(f"Position {point['percentile']}%: Engagement {point['engagement']:.1f}")
    
    # HTML Dashboard Example
    html_dashboard = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Video Retention Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .metric-value {{
                font-size: 36px;
                font-weight: bold;
                color: #333;
            }}
            .metric-label {{
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }}
            .chart-container {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Video Retention Analysis</h1>
            
            <div class="metrics">
                <div class="metric-card">
                    <div class="metric-value">{example_data['insights']['avg_retention']:.1f}%</div>
                    <div class="metric-label">Average Retention</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{example_data['insights']['completion_rate']:.1f}%</div>
                    <div class="metric-label">Completion Rate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{example_data['insights']['fifty_percent_point']}%</div>
                    <div class="metric-label">50% Drop-off Point</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{example_data['insights']['engagement_score']:.1f}</div>
                    <div class="metric-label">Engagement Score</div>
                </div>
            </div>
            
            <div class="chart-container">
                <canvas id="retentionChart"></canvas>
            </div>
            
            <div class="insights">
                <h2>Key Insights</h2>
                <ul>
                    <li>Major viewer drop-off at {example_data['insights']['major_drop_offs'][0]['percentile']}% mark</li>
                    <li>High replay activity at {example_data['insights']['replay_hotspots'][0]['percentile']}% mark</li>
                    <li>Video retains {example_data['insights']['completion_rate']:.1f}% of initial viewers</li>
                </ul>
            </div>
        </div>
        
        <script>
            const ctx = document.getElementById('retentionChart');
            const config = {json.dumps(chart_config)};
            new Chart(ctx, config);
        </script>
    </body>
    </html>
    """
    
    # Save dashboard
    with open("retention_dashboard.html", "w") as f:
        f.write(html_dashboard)
    
    print("\nGenerated retention_dashboard.html - open in browser to view interactive chart")


if __name__ == "__main__":
    asyncio.run(main())