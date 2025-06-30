#!/usr/bin/env python3
"""
Analytics Graph Visualization Example

This example demonstrates how to use the get_analytics_graph function
to retrieve time-series data suitable for creating charts and visualizations.
"""

import json
import asyncio
from datetime import datetime, timedelta

# Example of using graph data with popular visualization libraries

async def get_content_performance_graph(manager, entry_id=None):
    """Get content performance metrics as time-series data."""
    
    # Calculate date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Get graph data
    result = await get_analytics_graph(
        manager,
        from_date=start_date.strftime("%Y-%m-%d"),
        to_date=end_date.strftime("%Y-%m-%d"),
        report_type="content",
        entry_id=entry_id,
        interval="days"
    )
    
    data = json.loads(result)
    
    if "error" in data:
        print(f"Error: {data['error']}")
        return None
    
    return data


def format_for_chartjs(graph_data):
    """Format graph data for Chart.js visualization library."""
    
    datasets = []
    
    # Define colors for different metrics
    metric_colors = {
        "count_plays": "rgb(255, 99, 132)",
        "sum_time_viewed": "rgb(54, 162, 235)",
        "avg_time_viewed": "rgb(255, 205, 86)",
        "unique_viewers": "rgb(75, 192, 192)",
        "avg_completion_rate": "rgb(153, 102, 255)",
    }
    
    for graph in graph_data["graphs"]:
        metric = graph["metric"]
        
        # Extract dates and values
        dates = [point["date"] for point in graph["data"]]
        values = [point["value"] for point in graph["data"]]
        
        # Create dataset for Chart.js
        dataset = {
            "label": metric.replace("_", " ").title(),
            "data": values,
            "borderColor": metric_colors.get(metric, "rgb(201, 203, 207)"),
            "backgroundColor": metric_colors.get(metric, "rgba(201, 203, 207, 0.5)"),
            "tension": 0.1
        }
        
        datasets.append(dataset)
    
    # Get unique dates for labels
    all_dates = set()
    for graph in graph_data["graphs"]:
        all_dates.update(point["date"] for point in graph["data"])
    
    labels = sorted(list(all_dates))
    
    return {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": datasets
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": f"{graph_data['reportType']} - {graph_data['dateRange']['from']} to {graph_data['dateRange']['to']}"
                }
            },
            "scales": {
                "y": {
                    "beginAtZero": True
                }
            }
        }
    }


def format_for_plotly(graph_data):
    """Format graph data for Plotly visualization library."""
    
    traces = []
    
    for graph in graph_data["graphs"]:
        metric = graph["metric"]
        
        # Extract dates and values
        dates = [point["date"] for point in graph["data"]]
        values = [point["value"] for point in graph["data"]]
        
        # Create trace for Plotly
        trace = {
            "x": dates,
            "y": values,
            "mode": "lines+markers",
            "name": metric.replace("_", " ").title(),
            "type": "scatter"
        }
        
        traces.append(trace)
    
    layout = {
        "title": f"{graph_data['reportType']} Analytics",
        "xaxis": {"title": "Date"},
        "yaxis": {"title": "Value"},
        "hovermode": "x unified"
    }
    
    return {"data": traces, "layout": layout}


def generate_html_dashboard(graph_data):
    """Generate a simple HTML dashboard with the graph data."""
    
    chartjs_config = format_for_chartjs(graph_data)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kaltura Analytics Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .summary {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                border-left: 4px solid #007bff;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }}
            .metric-label {{
                font-size: 14px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Kaltura Analytics Dashboard</h1>
            
            <div class="summary">
    """
    
    # Add summary metrics
    if "summary" in graph_data:
        for key, value in graph_data["summary"].items():
            if isinstance(value, (int, float)):
                formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                html += f"""
                <div class="metric-card">
                    <div class="metric-label">{key.replace('_', ' ').title()}</div>
                    <div class="metric-value">{formatted_value}</div>
                </div>
                """
    
    html += """
            </div>
            
            <div style="position: relative; height:400px;">
                <canvas id="myChart"></canvas>
            </div>
        </div>
        
        <script>
            const ctx = document.getElementById('myChart');
            const config = """ + json.dumps(chartjs_config) + """;
            new Chart(ctx, config);
        </script>
    </body>
    </html>
    """
    
    return html


async def main():
    """Example usage of graph analytics."""
    
    # Note: In real usage, you would initialize your Kaltura manager here
    # manager = KalturaClientManager(partner_id, admin_secret, service_url)
    
    print("Kaltura Analytics Graph Example")
    print("================================")
    print()
    print("This example shows how to:")
    print("1. Retrieve time-series analytics data using get_analytics_graph")
    print("2. Format the data for popular visualization libraries")
    print("3. Generate HTML dashboards with the data")
    print()
    print("Key features of get_analytics_graph:")
    print("- Returns multiple metrics as separate time series")
    print("- Each metric includes date/value pairs")
    print("- Includes summary totals for the period")
    print("- Supports all standard report types")
    print("- Allows interval selection (days, weeks, months)")
    print()
    
    # Example response structure
    example_response = {
        "reportType": "Top Content",
        "reportTypeCode": "content",
        "reportTypeId": 1,
        "dateRange": {
            "from": "2024-01-01",
            "to": "2024-01-31",
            "interval": "days"
        },
        "graphs": [
            {
                "metric": "count_plays",
                "data": [
                    {"date": "2024-01-01", "value": 150},
                    {"date": "2024-01-02", "value": 200},
                    {"date": "2024-01-03", "value": 180},
                    # ... more data points
                ]
            },
            {
                "metric": "avg_time_viewed",
                "data": [
                    {"date": "2024-01-01", "value": 45.5},
                    {"date": "2024-01-02", "value": 52.3},
                    {"date": "2024-01-03", "value": 48.7},
                    # ... more data points
                ]
            }
        ],
        "summary": {
            "total_plays": 5430,
            "total_time_viewed": 248750,
            "unique_viewers": 1832,
            "avg_completion_rate": 0.72
        }
    }
    
    print("Example Chart.js configuration:")
    print(json.dumps(format_for_chartjs(example_response), indent=2))
    print()
    
    print("Example Plotly configuration:")
    print(json.dumps(format_for_plotly(example_response), indent=2))
    print()
    
    # Generate HTML dashboard
    html_content = generate_html_dashboard(example_response)
    
    # Save to file
    with open("analytics_dashboard.html", "w") as f:
        f.write(html_content)
    
    print("Generated analytics_dashboard.html - open in browser to view")


if __name__ == "__main__":
    asyncio.run(main())