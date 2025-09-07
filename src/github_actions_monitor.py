"""
GitHub Actions Real-Time Monitoring Dashboard
Advanced workflow monitoring with live updates and alerts
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import dataclass
from enum import Enum

class WorkflowStatus(Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILURE = "failure"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class WorkflowAlert:
    level: AlertLevel
    workflow_id: str
    workflow_name: str
    message: str
    timestamp: datetime
    repository: str
    
@dataclass
class WorkflowMetrics:
    workflow_id: str
    workflow_name: str
    repository: str
    status: WorkflowStatus
    duration_seconds: Optional[int]
    success_rate: float
    avg_duration: float
    last_run: datetime
    failure_count: int

class GitHubActionsMonitor:
    """Real-time GitHub Actions workflow monitoring system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.active_workflows: Dict[str, WorkflowMetrics] = {}
        self.alerts: List[WorkflowAlert] = []
        self.alert_thresholds = {
            "max_duration_minutes": 30,
            "failure_rate_threshold": 0.2,  # 20%
            "queue_time_threshold": 300,     # 5 minutes
        }
    
    async def monitor_workflows(self, repositories: List[str], interval: int = 30):
        """
        Continuously monitor workflows across multiple repositories
        
        Args:
            repositories: List of "owner/repo" strings to monitor
            interval: Monitoring interval in seconds
        """
        print(f"🔍 Starting GitHub Actions monitoring for {len(repositories)} repositories")
        print(f"📊 Monitoring interval: {interval} seconds")
        
        while True:
            try:
                await self._monitor_cycle(repositories)
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _monitor_cycle(self, repositories: List[str]):
        """Single monitoring cycle across all repositories"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for repo in repositories:
                owner, repo_name = repo.split('/')
                tasks.append(self._monitor_repository(session, owner, repo_name))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and generate alerts
            for result in results:
                if isinstance(result, Exception):
                    print(f"⚠️ Repository monitoring failed: {result}")
                else:
                    await self._process_repository_data(result)
    
    async def _monitor_repository(self, session: aiohttp.ClientSession, owner: str, repo: str) -> Dict[str, Any]:
        """Monitor a single repository's workflows"""
        try:
            # Get workflow runs
            async with session.get(f"{self.base_url}/api/v1/actions/{owner}/{repo}/runs") as response:
                if response.status == 200:
                    runs_data = await response.json()
                    
                    # Get workflow analytics
                    async with session.get(f"{self.base_url}/api/v1/analytics/actions/{owner}/{repo}/workflow-metrics") as analytics_response:
                        analytics_data = await analytics_response.json() if analytics_response.status == 200 else {}
                    
                    return {
                        "repository": f"{owner}/{repo}",
                        "runs": runs_data,
                        "analytics": analytics_data,
                        "timestamp": datetime.now()
                    }
                else:
                    raise Exception(f"Failed to fetch runs for {owner}/{repo}: {response.status}")
        except Exception as e:
            raise Exception(f"Repository {owner}/{repo} monitoring failed: {e}")
    
    async def _process_repository_data(self, data: Dict[str, Any]):
        """Process repository data and generate metrics/alerts"""
        repository = data["repository"]
        runs = data["runs"].get("workflow_runs", [])
        analytics = data["analytics"]
        
        # Process recent workflow runs
        for run in runs[:10]:  # Monitor last 10 runs
            workflow_key = f"{repository}:{run['workflow_id']}"
            
            # Update metrics
            metrics = self._update_workflow_metrics(repository, run, analytics)
            self.active_workflows[workflow_key] = metrics
            
            # Check for alerts
            await self._check_workflow_alerts(metrics, run)
        
        # Print monitoring summary
        await self._print_monitoring_summary(repository, runs, analytics)
    
    def _update_workflow_metrics(self, repository: str, run: Dict[str, Any], analytics: Dict[str, Any]) -> WorkflowMetrics:
        """Update workflow metrics based on run data"""
        workflow_id = str(run["workflow_id"])
        workflow_name = run["name"]
        
        # Calculate duration if completed
        duration = None
        if run["status"] == "completed" and run.get("run_started_at") and run.get("updated_at"):
            start_time = datetime.fromisoformat(run["run_started_at"].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(run["updated_at"].replace('Z', '+00:00'))
            duration = int((end_time - start_time).total_seconds())
        
        # Get analytics data for this workflow
        workflow_analytics = {}
        if analytics and "workflows" in analytics:
            for wf in analytics["workflows"]:
                if str(wf["workflow_id"]) == workflow_id:
                    workflow_analytics = wf
                    break
        
        return WorkflowMetrics(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            repository=repository,
            status=WorkflowStatus(run["status"]),
            duration_seconds=duration,
            success_rate=workflow_analytics.get("success_rate", 0.0),
            avg_duration=self._parse_duration_string(workflow_analytics.get("average_duration", "0s")),
            last_run=datetime.fromisoformat(run["updated_at"].replace('Z', '+00:00')),
            failure_count=0  # Would be calculated from historical data
        )
    
    async def _check_workflow_alerts(self, metrics: WorkflowMetrics, run: Dict[str, Any]):
        """Check workflow metrics against alert thresholds"""
        alerts = []
        
        # Long-running workflow alert
        if metrics.duration_seconds and metrics.duration_seconds > self.alert_thresholds["max_duration_minutes"] * 60:
            alerts.append(WorkflowAlert(
                level=AlertLevel.WARNING,
                workflow_id=metrics.workflow_id,
                workflow_name=metrics.workflow_name,
                message=f"Workflow exceeded maximum duration: {metrics.duration_seconds//60}m (threshold: {self.alert_thresholds['max_duration_minutes']}m)",
                timestamp=datetime.now(),
                repository=metrics.repository
            ))
        
        # High failure rate alert
        if metrics.success_rate < (1 - self.alert_thresholds["failure_rate_threshold"]) and metrics.success_rate > 0:
            alerts.append(WorkflowAlert(
                level=AlertLevel.CRITICAL,
                workflow_id=metrics.workflow_id,
                workflow_name=metrics.workflow_name,
                message=f"High failure rate detected: {(1-metrics.success_rate)*100:.1f}% (threshold: {self.alert_thresholds['failure_rate_threshold']*100}%)",
                timestamp=datetime.now(),
                repository=metrics.repository
            ))
        
        # Workflow failure alert
        if run["conclusion"] == "failure":
            alerts.append(WorkflowAlert(
                level=AlertLevel.CRITICAL,
                workflow_id=metrics.workflow_id,
                workflow_name=metrics.workflow_name,
                message=f"Workflow failed: {run.get('display_title', 'No title')}",
                timestamp=datetime.now(),
                repository=metrics.repository
            ))
        
        # Add alerts to the queue
        for alert in alerts:
            self.alerts.append(alert)
            await self._send_alert(alert)
    
    async def _send_alert(self, alert: WorkflowAlert):
        """Send alert notification"""
        emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}[alert.level.value]
        print(f"{emoji} ALERT [{alert.level.value.upper()}] {alert.repository}")
        print(f"   Workflow: {alert.workflow_name} (ID: {alert.workflow_id})")
        print(f"   Message: {alert.message}")
        print(f"   Time: {alert.timestamp.strftime('%H:%M:%S')}")
        print()
    
    async def _print_monitoring_summary(self, repository: str, runs: List[Dict], analytics: Dict[str, Any]):
        """Print monitoring summary for repository"""
        print(f"📊 {repository} - {datetime.now().strftime('%H:%M:%S')}")
        
        if runs:
            # Status summary
            status_counts = {}
            for run in runs[:10]:
                status = run["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            status_summary = " | ".join([f"{status}: {count}" for status, count in status_counts.items()])
            print(f"   Status: {status_summary}")
            
            # Recent activity
            latest_run = runs[0]
            print(f"   Latest: {latest_run['name']} - {latest_run['status']} ({latest_run.get('conclusion', 'N/A')})")
        
        if analytics and "summary" in analytics:
            summary = analytics["summary"]
            print(f"   Success Rate: {summary.get('success_rate', 'N/A')}% | Avg Duration: {summary.get('average_duration_minutes', 'N/A')}m")
        
        print()
    
    def _parse_duration_string(self, duration_str: str) -> float:
        """Parse duration string like '12m 30s' to seconds"""
        if not duration_str or duration_str == "0s":
            return 0.0
        
        total_seconds = 0.0
        parts = duration_str.replace('m', ' m ').replace('s', ' s ').split()
        
        for i, part in enumerate(parts):
            if part == 'm' and i > 0:
                total_seconds += float(parts[i-1]) * 60
            elif part == 's' and i > 0:
                total_seconds += float(parts[i-1])
        
        return total_seconds
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data for UI display"""
        return {
            "active_workflows": len(self.active_workflows),
            "recent_alerts": self.alerts[-10:],  # Last 10 alerts
            "workflows": list(self.active_workflows.values()),
            "alert_summary": {
                "critical": len([a for a in self.alerts[-50:] if a.level == AlertLevel.CRITICAL]),
                "warning": len([a for a in self.alerts[-50:] if a.level == AlertLevel.WARNING]),
                "info": len([a for a in self.alerts[-50:] if a.level == AlertLevel.INFO])
            },
            "last_update": datetime.now().isoformat()
        }

# Example usage and demo
async def demo_monitoring():
    """Demonstrate the monitoring system"""
    monitor = GitHubActionsMonitor()
    
    # List of repositories to monitor
    repositories = [
        "microsoft/vscode",
        "facebook/react", 
        "kubernetes/kubernetes",
        "tensorflow/tensorflow"
    ]
    
    print("🚀 GitHub Actions Monitoring Dashboard Demo")
    print("=" * 50)
    
    # Run a few monitoring cycles
    for cycle in range(3):
        print(f"\n📡 Monitoring Cycle {cycle + 1}")
        print("-" * 30)
        
        try:
            await monitor._monitor_cycle(repositories)
        except Exception as e:
            print(f"❌ Monitoring cycle failed: {e}")
        
        # Print dashboard summary
        dashboard_data = monitor.get_dashboard_data()
        print(f"\n📈 Dashboard Summary:")
        print(f"   Active Workflows: {dashboard_data['active_workflows']}")
        print(f"   Recent Alerts: {len(dashboard_data['recent_alerts'])}")
        print(f"   Alert Summary: {dashboard_data['alert_summary']}")
        
        if cycle < 2:  # Don't sleep on last cycle
            print("\n⏳ Waiting 10 seconds before next cycle...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(demo_monitoring())
