"""Debug tool for retention calculation issues."""

import json


def debug_retention_data(kaltura_data_string):
    """
    Debug retention calculation for given Kaltura data.
    
    Args:
        kaltura_data_string: The raw data string from Kaltura API
                           e.g., "0,100,100;10,85,80;50,45,40"
    """
    print("=== DEBUGGING RETENTION CALCULATION ===")
    print(f"Input data: {kaltura_data_string[:100]}...")
    
    # Parse the data
    if ";" in kaltura_data_string and "\n" not in kaltura_data_string:
        rows = kaltura_data_string.strip().split(";")
        print(f"Split by semicolon: {len(rows)} rows")
    else:
        rows = kaltura_data_string.strip().split("\n")
        print(f"Split by newline: {len(rows)} rows")
    
    # First pass - collect data
    raw_data_points = []
    print("\nParsing rows:")
    for i, row in enumerate(rows[:5]):  # Show first 5
        if row.strip():
            if "|" in row:
                values = row.split("|")
            else:
                values = row.split(",")
            
            print(f"  Row {i}: {row} → {values}")
            
            if len(values) >= 3:
                try:
                    point = {
                        "percentile": int(values[0]),
                        "viewers": int(values[1]),
                        "unique_users": int(values[2])
                    }
                    raw_data_points.append(point)
                except (ValueError, TypeError) as e:
                    print(f"    ERROR parsing: {e}")
    
    if len(rows) > 5:
        print(f"  ... and {len(rows) - 5} more rows")
    
    # Find max viewers
    max_viewers = max((p["viewers"] for p in raw_data_points), default=0)
    print(f"\nMax viewers found: {max_viewers}")
    
    # Find initial viewers
    initial_viewers = 0
    for point in raw_data_points:
        if point["percentile"] == 0 and point["viewers"] > 0:
            initial_viewers = point["viewers"]
            print(f"Initial viewers from percentile 0: {initial_viewers}")
            break
    
    if initial_viewers == 0:
        initial_viewers = max_viewers
        print(f"No viewers at start, using max as initial: {initial_viewers}")
    
    # Show retention calculation
    print("\nRetention calculation:")
    print("Percentile | Viewers | Retention % | Calculation")
    print("-" * 60)
    
    for point in raw_data_points[:10]:  # Show first 10
        if initial_viewers > 0:
            retention_pct = (point["viewers"] / initial_viewers * 100)
        else:
            retention_pct = 0 if point["viewers"] == 0 else 100
        
        calc = f"{point['viewers']}/{initial_viewers}*100" if initial_viewers > 0 else "special case"
        print(f"{point['percentile']:10d} | {point['viewers']:7d} | {retention_pct:10.2f}% | {calc}")
    
    # Check for issues
    print("\n=== ANALYSIS ===")
    
    # Check if all viewers are the same
    unique_viewer_counts = set(p["viewers"] for p in raw_data_points)
    if len(unique_viewer_counts) == 1:
        print("⚠️  All viewer counts are the same:", list(unique_viewer_counts)[0])
        print("   This will result in 100% retention throughout (which is correct)")
    
    # Check if data is monotonically decreasing
    is_decreasing = all(
        raw_data_points[i]["viewers"] >= raw_data_points[i+1]["viewers"] 
        for i in range(len(raw_data_points)-1)
    )
    if not is_decreasing:
        print("⚠️  Viewer counts are not monotonically decreasing")
        print("   This suggests viewers joining mid-video or data anomalies")
    
    # Show viewer count distribution
    print(f"\nViewer count range: {min(unique_viewer_counts)} to {max(unique_viewer_counts)}")
    print(f"Unique viewer counts: {sorted(unique_viewer_counts)[:10]}")
    if len(unique_viewer_counts) > 10:
        print(f"  ... and {len(unique_viewer_counts) - 10} more")


# Example usage
if __name__ == "__main__":
    # Test with normal drop-off data
    print("Example 1: Normal video with drop-off")
    debug_retention_data("0,100,100;10,85,80;25,65,60;50,45,40;75,30,25;100,20,15")
    
    print("\n" + "="*70 + "\n")
    
    # Test with all same values (will show 100% throughout)
    print("Example 2: Video where everyone watches to the end")
    debug_retention_data("0,50,50;10,50,50;25,50,50;50,50,50;75,50,50;100,50,50")
    
    print("\n" + "="*70 + "\n")
    
    # Test with zero start
    print("Example 3: Video with zero viewers at start")
    debug_retention_data("0,0,0;1,21,2;2,19,2;3,22,2;10,17,1;50,6,1;100,1,1")