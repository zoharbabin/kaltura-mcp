# Local Monitoring System - QUICKWIN (1 hour)

**Complexity**: Low  
**Impact**: Medium - Enables monitoring without external dependencies  
**Priority**: MEDIUM (nice to have for production visibility)  
**Time Estimate**: 1 hour  
**Dependencies**: None

## Problem
The Kaltura MCP server lacks monitoring and observability capabilities for production deployments. While external services like Sentry provide comprehensive monitoring, there's a need for lightweight, local monitoring that doesn't require external dependencies or network connections.

## Solution
Implement a local monitoring system with:
- Performance metrics collection
- Error tracking and aggregation
- Health check endpoints
- Local log analysis
- Simple alerting via log warnings
- Minimal overhead and no external dependencies

## Implementation Steps

### 1. Create Monitoring Core Module (20 minutes)
**File: `src/kaltura_mcp/monitoring/core.py`**
```python
"""Core monitoring functionality for Kaltura MCP server."""

import time
import logging
import threading
from typing import Dict, Any, Optional, List
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Metric:
    """A single metric data point."""
    name: str
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    

@dataclass
class Alert:
    """An alert/notification."""
    level: AlertLevel
    message: str
    timestamp: float
    component: str
    details: Dict[str, Any] = field(default_factory=dict)


class MetricsCollector:
    """Thread-safe metrics collection."""
    
    def __init__(self, max_metrics: int = 10000):
        self.max_metrics = max_metrics
        self._metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics))
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._timers: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.RLock()
        
    def counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        with self._lock:
            key = self._build_key(name, tags)
            self._counters[key] += value
            self._add_metric(name, self._counters[key], tags)
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        with self._lock:
            key = self._build_key(name, tags)
            self._gauges[key] = value
            self._add_metric(name, value, tags)
    
    def timer(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Add a timing measurement."""
        with self._lock:
            key = self._build_key(name, tags)
            self._timers[key].append(value)
            # Keep only recent 1000 measurements
            if len(self._timers[key]) > 1000:
                self._timers[key] = self._timers[key][-1000:]
            self._add_metric(name, value, tags)
    
    def _add_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Add a metric to the time series."""
        metric = Metric(
            name=name,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        self._metrics[name].append(metric)
    
    def _build_key(self, name: str, tags: Optional[Dict[str, str]] = None) -> str:
        """Build a unique key for the metric."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}#{tag_str}"
    
    def get_metrics(self, name: str, since: Optional[float] = None) -> List[Metric]:
        """Get metrics for a given name."""
        with self._lock:
            metrics = list(self._metrics[name])
            if since:
                metrics = [m for m in metrics if m.timestamp >= since]
            return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all metrics."""
        with self._lock:
            now = time.time()
            hour_ago = now - 3600
            
            summary = {
                "timestamp": now,
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "timers_summary": {},
                "recent_metrics_count": {}
            }
            
            # Summarize timers
            for key, values in self._timers.items():
                if values:
                    recent_values = [v for v in values if time.time() - v < 3600]
                    if recent_values:
                        summary["timers_summary"][key] = {
                            "count": len(recent_values),
                            "avg": sum(recent_values) / len(recent_values),
                            "min": min(recent_values),
                            "max": max(recent_values)
                        }
            
            # Count recent metrics
            for name, metrics in self._metrics.items():
                recent_count = sum(1 for m in metrics if m.timestamp >= hour_ago)
                if recent_count > 0:
                    summary["recent_metrics_count"][name] = recent_count
            
            return summary


class PerformanceTimer:
    """Context manager for timing operations."""
    
    def __init__(self, collector: MetricsCollector, name: str, tags: Optional[Dict[str, str]] = None):
        self.collector = collector
        self.name = name
        self.tags = tags
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.collector.timer(self.name, duration, self.tags)


class Monitor:
    """Main monitoring system."""
    
    def __init__(self):
        self.metrics = MetricsCollector()
        self.alerts: deque = deque(maxlen=1000)
        self.start_time = time.time()
        self.health_checks: Dict[str, callable] = {}
        
        # Track system metrics
        self._setup_system_monitoring()
    
    def _setup_system_monitoring(self):
        """Set up automatic system monitoring."""
        # Start monitoring thread
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def _monitoring_loop(self):
        """Background monitoring loop."""
        while True:
            try:
                self._collect_system_metrics()
                self._check_alert_conditions()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _collect_system_metrics(self):
        """Collect basic system metrics."""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.gauge("system.memory.usage_percent", memory.percent)
            self.metrics.gauge("system.memory.available_mb", memory.available / 1024 / 1024)
            
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.metrics.gauge("system.cpu.usage_percent", cpu_percent)
            
            # Disk usage for current working directory
            disk = psutil.disk_usage('.')
            self.metrics.gauge("system.disk.usage_percent", (disk.used / disk.total) * 100)
            
        except ImportError:
            # psutil not available, collect basic metrics
            self.metrics.gauge("monitoring.psutil_available", 0)
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")
    
    def _check_alert_conditions(self):
        """Check for alert conditions."""
        try:
            # Check error rate
            hour_ago = time.time() - 3600
            error_metrics = self.metrics.get_metrics("errors.count", since=hour_ago)
            if len(error_metrics) > 10:  # More than 10 errors in last hour
                self.alert(AlertLevel.WARNING, "High error rate detected", "monitoring",
                          {"error_count": len(error_metrics), "timeframe": "1h"})
            
            # Check memory usage if available
            memory_metrics = self.metrics.get_metrics("system.memory.usage_percent")
            if memory_metrics:
                latest_memory = memory_metrics[-1].value
                if latest_memory > 90:
                    self.alert(AlertLevel.CRITICAL, f"High memory usage: {latest_memory:.1f}%", 
                              "system", {"memory_percent": latest_memory})
                elif latest_memory > 80:
                    self.alert(AlertLevel.WARNING, f"Elevated memory usage: {latest_memory:.1f}%",
                              "system", {"memory_percent": latest_memory})
        
        except Exception as e:
            logger.error(f"Error checking alert conditions: {e}")
    
    def timer(self, name: str, tags: Optional[Dict[str, str]] = None) -> PerformanceTimer:
        """Create a performance timer context manager."""
        return PerformanceTimer(self.metrics, name, tags)
    
    def count(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Increment a counter."""
        self.metrics.counter(name, value, tags)
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge value."""
        self.metrics.gauge(name, value, tags)
    
    def alert(self, level: AlertLevel, message: str, component: str, 
              details: Optional[Dict[str, Any]] = None):
        """Generate an alert."""
        alert = Alert(
            level=level,
            message=message,
            timestamp=time.time(),
            component=component,
            details=details or {}
        )
        
        self.alerts.append(alert)
        
        # Log the alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }[level]
        
        logger.log(log_level, f"[{component}] {message}", extra={"alert_details": details})
    
    def register_health_check(self, name: str, check_func: callable):
        """Register a health check function."""
        self.health_checks[name] = check_func
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        health = {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime_seconds": time.time() - self.start_time,
            "checks": {}
        }
        
        for name, check_func in self.health_checks.items():
            try:
                result = check_func()
                health["checks"][name] = {"status": "healthy", "result": result}
            except Exception as e:
                health["checks"][name] = {"status": "unhealthy", "error": str(e)}
                health["status"] = "degraded"
        
        return health
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        recent_alerts = [a for a in self.alerts if time.time() - a.timestamp < 3600]
        
        return {
            "uptime_seconds": time.time() - self.start_time,
            "metrics_summary": self.metrics.get_summary(),
            "recent_alerts": len(recent_alerts),
            "alerts_by_level": {
                level.value: len([a for a in recent_alerts if a.level == level])
                for level in AlertLevel
            },
            "health_checks": len(self.health_checks)
        }


# Global monitor instance
_monitor = None


def get_monitor() -> Monitor:
    """Get the global monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = Monitor()
    return _monitor
```

### 2. Create Tool Monitoring Decorators (15 minutes)
**File: `src/kaltura_mcp/monitoring/decorators.py`**
```python
"""Monitoring decorators for tool execution."""

import functools
import logging
from typing import Any, Dict, Optional
from .core import get_monitor, AlertLevel

logger = logging.getLogger(__name__)


def monitor_tool_execution(tool_name: Optional[str] = None):
    """
    Decorator to monitor tool execution performance and errors.
    
    Args:
        tool_name: Optional tool name override
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            monitor = get_monitor()
            actual_tool_name = tool_name or getattr(func, '__name__', 'unknown_tool')
            
            # Start timing
            with monitor.timer(f"tool.execution_time", {"tool": actual_tool_name}):
                try:
                    # Count execution
                    monitor.count("tool.executions", tags={"tool": actual_tool_name})
                    
                    # Execute the tool
                    result = await func(*args, **kwargs)
                    
                    # Count success
                    monitor.count("tool.successes", tags={"tool": actual_tool_name})
                    
                    return result
                    
                except Exception as e:
                    # Count error
                    monitor.count("tool.errors", tags={
                        "tool": actual_tool_name,
                        "error_type": type(e).__name__
                    })
                    monitor.count("errors.count")
                    
                    # Generate alert for critical errors
                    if "authentication" in str(e).lower() or "connection" in str(e).lower():
                        monitor.alert(
                            AlertLevel.ERROR,
                            f"Tool {actual_tool_name} failed: {str(e)}",
                            "tool_execution",
                            {"tool": actual_tool_name, "error": str(e)}
                        )
                    
                    raise
        
        return wrapper
    return decorator


def monitor_api_call(api_name: Optional[str] = None):
    """
    Decorator to monitor Kaltura API calls.
    
    Args:
        api_name: Optional API name override
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_monitor()
            actual_api_name = api_name or getattr(func, '__name__', 'unknown_api')
            
            with monitor.timer(f"api.call_time", {"api": actual_api_name}):
                try:
                    monitor.count("api.calls", tags={"api": actual_api_name})
                    
                    result = func(*args, **kwargs)
                    
                    monitor.count("api.successes", tags={"api": actual_api_name})
                    return result
                    
                except Exception as e:
                    monitor.count("api.errors", tags={
                        "api": actual_api_name,
                        "error_type": type(e).__name__
                    })
                    
                    # Alert on repeated API failures
                    error_count = len(monitor.metrics.get_metrics("api.errors"))
                    if error_count > 5:
                        monitor.alert(
                            AlertLevel.WARNING,
                            f"Multiple API failures for {actual_api_name}",
                            "api",
                            {"api": actual_api_name, "error_count": error_count}
                        )
                    
                    raise
        
        return wrapper
    return decorator


def monitor_performance(operation_name: str, alert_threshold_seconds: float = 30.0):
    """
    Decorator to monitor operation performance and alert on slow operations.
    
    Args:
        operation_name: Name of the operation
        alert_threshold_seconds: Threshold for slow operation alerts
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = get_monitor()
            
            with monitor.timer(f"performance.{operation_name}") as timer:
                result = await func(*args, **kwargs)
                
                # Check if operation was slow
                duration = timer.start_time and (time.time() - timer.start_time)
                if duration and duration > alert_threshold_seconds:
                    monitor.alert(
                        AlertLevel.WARNING,
                        f"Slow operation detected: {operation_name} took {duration:.2f}s",
                        "performance",
                        {"operation": operation_name, "duration": duration}
                    )
                
                return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = get_monitor()
            
            with monitor.timer(f"performance.{operation_name}") as timer:
                result = func(*args, **kwargs)
                
                # Check if operation was slow
                duration = timer.start_time and (time.time() - timer.start_time)
                if duration and duration > alert_threshold_seconds:
                    monitor.alert(
                        AlertLevel.WARNING,
                        f"Slow operation detected: {operation_name} took {duration:.2f}s",
                        "performance",
                        {"operation": operation_name, "duration": duration}
                    )
                
                return result
        
        # Return appropriate wrapper based on whether function is async
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
```

### 3. Add Health Check Endpoints (15 minutes)
**File: `src/kaltura_mcp/monitoring/health.py`**
```python
"""Health check functionality."""

import time
import logging
from typing import Dict, Any, Optional
from .core import get_monitor

logger = logging.getLogger(__name__)


def register_default_health_checks():
    """Register default health checks."""
    monitor = get_monitor()
    
    monitor.register_health_check("uptime", check_uptime)
    monitor.register_health_check("memory", check_memory_usage)
    monitor.register_health_check("recent_errors", check_recent_errors)


def check_uptime() -> Dict[str, Any]:
    """Check system uptime."""
    monitor = get_monitor()
    uptime = time.time() - monitor.start_time
    
    return {
        "uptime_seconds": uptime,
        "uptime_human": format_uptime(uptime),
        "status": "ok"
    }


def check_memory_usage() -> Dict[str, Any]:
    """Check memory usage if available."""
    try:
        import psutil
        memory = psutil.virtual_memory()
        
        status = "ok"
        if memory.percent > 90:
            status = "critical" 
        elif memory.percent > 80:
            status = "warning"
        
        return {
            "usage_percent": memory.percent,
            "available_mb": memory.available / 1024 / 1024,
            "status": status
        }
    except ImportError:
        return {"status": "unavailable", "reason": "psutil not installed"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_recent_errors() -> Dict[str, Any]:
    """Check for recent errors."""
    monitor = get_monitor()
    hour_ago = time.time() - 3600
    
    recent_alerts = [a for a in monitor.alerts if a.timestamp >= hour_ago]
    error_alerts = [a for a in recent_alerts if a.level.value in ['error', 'critical']]
    
    status = "ok"
    if len(error_alerts) > 5:
        status = "critical"
    elif len(error_alerts) > 0:
        status = "warning"
    
    return {
        "recent_alerts": len(recent_alerts),
        "error_alerts": len(error_alerts),
        "status": status
    }


def check_kaltura_connectivity(manager) -> Dict[str, Any]:
    """Check Kaltura API connectivity."""
    try:
        # Try to get session info (doesn't require API call if session exists)
        session_info = manager.get_session_info()
        
        if session_info["status"] == "active":
            return {"status": "ok", "session_status": "active"}
        elif session_info["status"] == "expired":
            return {"status": "warning", "session_status": "expired"}
        else:
            return {"status": "warning", "session_status": "no_session"}
            
    except Exception as e:
        return {"status": "error", "error": str(e)}


def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def get_monitoring_status() -> Dict[str, Any]:
    """Get comprehensive monitoring status."""
    monitor = get_monitor()
    
    return {
        "monitoring": monitor.get_summary(),
        "health": monitor.get_health_status(),
        "alerts": {
            "total": len(monitor.alerts),
            "recent": len([a for a in monitor.alerts if time.time() - a.timestamp < 3600])
        }
    }
```

### 4. Integrate with Existing Servers (10 minutes)
**Update `src/kaltura_mcp/server.py`:**
```python
# Add to imports
from .monitoring.core import get_monitor
from .monitoring.decorators import monitor_tool_execution
from .monitoring.health import register_default_health_checks

# Add to initialize_server()
def initialize_server():
    # ... existing code ...
    
    # Initialize monitoring
    monitor = get_monitor()
    register_default_health_checks()
    logger.info("Monitoring system initialized")

# Update call_tool with monitoring
@server.call_tool()
@monitor_tool_execution()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    # ... existing implementation ...
```

**Update `src/kaltura_mcp/remote_server.py`:**
```python
# Add monitoring endpoints
from .monitoring.health import get_monitoring_status

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    monitor = get_monitor()
    return monitor.get_health_status()

@app.get("/metrics")
async def get_metrics():
    """Get monitoring metrics."""
    return get_monitoring_status()
```

## Benefits
- ✅ **Zero external dependencies** - Pure Python implementation
- ✅ **Lightweight overhead** - Minimal performance impact
- ✅ **Production ready** - Thread-safe metrics collection
- ✅ **Automatic alerting** - Log-based alerts for critical issues
- ✅ **Health checks** - Built-in system and application health monitoring
- ✅ **Performance tracking** - Automatic timing of tool executions and API calls
- ✅ **Error tracking** - Comprehensive error counting and categorization
- ✅ **Resource monitoring** - Memory, CPU, and disk usage tracking (when psutil available)
- ✅ **Easy integration** - Decorator-based monitoring for existing code

## Files Created
- `src/kaltura_mcp/monitoring/__init__.py`
- `src/kaltura_mcp/monitoring/core.py`
- `src/kaltura_mcp/monitoring/decorators.py`
- `src/kaltura_mcp/monitoring/health.py`

## Files Modified
- `src/kaltura_mcp/server.py` (add monitoring integration)
- `src/kaltura_mcp/remote_server.py` (add health/metrics endpoints)

## Usage Examples

### Basic Monitoring
```python
from kaltura_mcp.monitoring import get_monitor

monitor = get_monitor()

# Count events
monitor.count("user_login")

# Track values
monitor.gauge("active_sessions", 42)

# Time operations
with monitor.timer("database_query"):
    # ... long operation ...
    pass

# Generate alerts
monitor.alert(AlertLevel.WARNING, "High memory usage", "system")
```

### Decorator Usage
```python
@monitor_tool_execution("my_tool")
async def my_tool_function():
    # Automatically monitored
    pass

@monitor_performance("slow_operation", alert_threshold_seconds=10.0)
async def potentially_slow_operation():
    # Alerts if takes > 10 seconds
    pass
```

### Health Checks
```bash
# Check health via remote server
curl http://localhost:8000/health

# Get metrics
curl http://localhost:8000/metrics
```

This local monitoring solution provides production-grade observability without requiring external services or network dependencies.