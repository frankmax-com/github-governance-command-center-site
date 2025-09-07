"""
GitHub Actions Enterprise Integration Hub
Advanced integration platform for enterprise DevOps automation
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegrationType(Enum):
    SLACK = "slack"
    JIRA = "jira"
    PROMETHEUS = "prometheus"
    GRAFANA = "grafana"
    PAGERDUTY = "pagerduty"
    DATADOG = "datadog"
    GITHUB_ISSUES = "github_issues"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure_devops"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class IntegrationConfig:
    type: IntegrationType
    enabled: bool
    endpoint: str
    credentials: Dict[str, str]
    settings: Dict[str, Any]

@dataclass
class WorkflowEvent:
    repository: str
    workflow_id: str
    workflow_name: str
    event_type: str  # started, completed, failed, cancelled
    status: str
    conclusion: Optional[str]
    duration_seconds: Optional[int]
    run_id: str
    run_number: int
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class Alert:
    id: str
    severity: AlertSeverity
    title: str
    description: str
    repository: str
    workflow_name: str
    timestamp: datetime
    resolved: bool = False
    integration_responses: Dict[str, bool] = None

    def __post_init__(self):
        if self.integration_responses is None:
            self.integration_responses = {}

class EnterpriseIntegrationHub:
    """Enterprise-grade integration platform for GitHub Actions"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.base_url = "http://localhost:8000"
        self.integrations: Dict[IntegrationType, IntegrationConfig] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.event_history: List[WorkflowEvent] = []
        self.metrics_buffer: List[Dict[str, Any]] = []
        
        if config_file:
            self.load_config(config_file)
        else:
            self._setup_default_integrations()
    
    def _setup_default_integrations(self):
        """Setup default integration configurations"""
        self.integrations = {
            IntegrationType.SLACK: IntegrationConfig(
                type=IntegrationType.SLACK,
                enabled=True,
                endpoint="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
                credentials={"token": "xoxb-your-slack-bot-token"},
                settings={
                    "channel": "#devops-alerts",
                    "mention_on_critical": True,
                    "thread_failures": True
                }
            ),
            IntegrationType.JIRA: IntegrationConfig(
                type=IntegrationType.JIRA,
                enabled=True,
                endpoint="https://your-domain.atlassian.net",
                credentials={"email": "your-email@company.com", "api_token": "your-api-token"},
                settings={
                    "project_key": "DEVOPS",
                    "issue_type": "Bug",
                    "auto_create_issues": True,
                    "assign_to": "devops-team"
                }
            ),
            IntegrationType.PROMETHEUS: IntegrationConfig(
                type=IntegrationType.PROMETHEUS,
                enabled=True,
                endpoint="http://prometheus:9090",
                credentials={},
                settings={
                    "metrics_prefix": "github_actions_",
                    "push_interval": 30,
                    "job_name": "github-actions-metrics"
                }
            ),
            IntegrationType.PAGERDUTY: IntegrationConfig(
                type=IntegrationType.PAGERDUTY,
                enabled=True,
                endpoint="https://events.pagerduty.com/v2/enqueue",
                credentials={"integration_key": "your-pagerduty-integration-key"},
                settings={
                    "service_id": "github-actions-service",
                    "escalation_policy": "devops-escalation",
                    "auto_resolve": True
                }
            )
        }
    
    def load_config(self, config_file: str):
        """Load integration configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
                
            for integration_data in config_data.get("integrations", []):
                int_type = IntegrationType(integration_data["type"])
                self.integrations[int_type] = IntegrationConfig(**integration_data)
                
            logger.info(f"Loaded configuration for {len(self.integrations)} integrations")
        except Exception as e:
            logger.error(f"Failed to load config from {config_file}: {e}")
            self._setup_default_integrations()
    
    async def start_monitoring(self, repositories: List[str]):
        """Start comprehensive monitoring with all integrations"""
        logger.info(f"🚀 Starting Enterprise Integration Hub for {len(repositories)} repositories")
        
        # Start concurrent monitoring tasks
        tasks = [
            self._workflow_event_monitor(repositories),
            self._metrics_collector(repositories),
            self._alert_processor(),
            self._integration_health_checker()
        ]
        
        await asyncio.gather(*tasks)
    
    async def _workflow_event_monitor(self, repositories: List[str]):
        """Monitor workflow events and trigger integrations"""
        logger.info("📡 Starting workflow event monitoring")
        
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    for repo in repositories:
                        owner, repo_name = repo.split('/')
                        events = await self._fetch_workflow_events(session, owner, repo_name)
                        
                        for event in events:
                            await self._process_workflow_event(event)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                logger.error(f"Workflow monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _fetch_workflow_events(self, session: aiohttp.ClientSession, owner: str, repo: str) -> List[WorkflowEvent]:
        """Fetch recent workflow events from API"""
        try:
            async with session.get(f"{self.base_url}/api/v1/actions/{owner}/{repo}/runs") as response:
                if response.status == 200:
                    data = await response.json()
                    events = []
                    
                    for run in data.get("workflow_runs", [])[:5]:  # Process last 5 runs
                        event = WorkflowEvent(
                            repository=f"{owner}/{repo}",
                            workflow_id=str(run["workflow_id"]),
                            workflow_name=run["name"],
                            event_type=self._determine_event_type(run),
                            status=run["status"],
                            conclusion=run.get("conclusion"),
                            duration_seconds=self._calculate_duration(run),
                            run_id=str(run["id"]),
                            run_number=run["run_number"],
                            timestamp=datetime.fromisoformat(run["updated_at"].replace('Z', '+00:00')),
                            metadata={
                                "head_branch": run["head_branch"],
                                "head_sha": run["head_sha"][:8],
                                "event": run["event"],
                                "actor": run.get("triggering_actor", {}).get("login", "unknown")
                            }
                        )
                        events.append(event)
                    
                    return events
        except Exception as e:
            logger.error(f"Failed to fetch events for {owner}/{repo}: {e}")
        
        return []
    
    def _determine_event_type(self, run: Dict[str, Any]) -> str:
        """Determine event type from run data"""
        if run["status"] == "completed":
            return "failed" if run.get("conclusion") == "failure" else "completed"
        elif run["status"] == "in_progress":
            return "started"
        elif run["status"] == "cancelled":
            return "cancelled"
        else:
            return "queued"
    
    def _calculate_duration(self, run: Dict[str, Any]) -> Optional[int]:
        """Calculate workflow duration in seconds"""
        if run.get("run_started_at") and run.get("updated_at"):
            try:
                start = datetime.fromisoformat(run["run_started_at"].replace('Z', '+00:00'))
                end = datetime.fromisoformat(run["updated_at"].replace('Z', '+00:00'))
                return int((end - start).total_seconds())
            except:
                pass
        return None
    
    async def _process_workflow_event(self, event: WorkflowEvent):
        """Process workflow event and trigger appropriate integrations"""
        # Skip if we've already processed this event
        event_key = f"{event.repository}:{event.run_id}:{event.event_type}"
        if any(e.run_id == event.run_id and e.event_type == event.event_type for e in self.event_history[-100:]):
            return
        
        self.event_history.append(event)
        logger.info(f"📝 Processing event: {event.repository} - {event.workflow_name} - {event.event_type}")
        
        # Generate alerts if needed
        alert = self._generate_alert_from_event(event)
        if alert:
            await self._process_alert(alert)
        
        # Send to integrations
        await self._send_to_integrations(event)
        
        # Update metrics
        self._update_metrics(event)
    
    def _generate_alert_from_event(self, event: WorkflowEvent) -> Optional[Alert]:
        """Generate alert from workflow event if conditions are met"""
        if event.event_type == "failed":
            severity = AlertSeverity.HIGH
            if "production" in event.workflow_name.lower() or "deploy" in event.workflow_name.lower():
                severity = AlertSeverity.CRITICAL
            
            return Alert(
                id=f"alert-{event.run_id}-{datetime.now().timestamp()}",
                severity=severity,
                title=f"Workflow Failed: {event.workflow_name}",
                description=f"Workflow '{event.workflow_name}' failed in {event.repository} (Run #{event.run_number})",
                repository=event.repository,
                workflow_name=event.workflow_name,
                timestamp=event.timestamp
            )
        
        elif event.duration_seconds and event.duration_seconds > 1800:  # 30+ minutes
            return Alert(
                id=f"alert-{event.run_id}-duration-{datetime.now().timestamp()}",
                severity=AlertSeverity.MEDIUM,
                title=f"Long Running Workflow: {event.workflow_name}",
                description=f"Workflow '{event.workflow_name}' has been running for {event.duration_seconds//60} minutes",
                repository=event.repository,
                workflow_name=event.workflow_name,
                timestamp=event.timestamp
            )
        
        return None
    
    async def _process_alert(self, alert: Alert):
        """Process and distribute alert to integrations"""
        self.active_alerts[alert.id] = alert
        logger.warning(f"🚨 ALERT [{alert.severity.value.upper()}]: {alert.title}")
        
        # Send to enabled integrations
        tasks = []
        if self.integrations.get(IntegrationType.SLACK, {}).enabled:
            tasks.append(self._send_slack_alert(alert))
        if self.integrations.get(IntegrationType.PAGERDUTY, {}).enabled and alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
            tasks.append(self._send_pagerduty_alert(alert))
        if self.integrations.get(IntegrationType.JIRA, {}).enabled and alert.severity == AlertSeverity.CRITICAL:
            tasks.append(self._create_jira_issue(alert))
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Integration failed: {result}")
                else:
                    logger.info(f"Alert sent to integration {i+1}")
    
    async def _send_to_integrations(self, event: WorkflowEvent):
        """Send event data to all enabled integrations"""
        tasks = []
        
        # Prometheus metrics
        if self.integrations.get(IntegrationType.PROMETHEUS, {}).enabled:
            tasks.append(self._send_prometheus_metrics(event))
        
        # Slack notifications for important events
        if (self.integrations.get(IntegrationType.SLACK, {}).enabled and 
            event.event_type in ["completed", "failed"]):
            tasks.append(self._send_slack_notification(event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_slack_alert(self, alert: Alert) -> bool:
        """Send alert to Slack"""
        try:
            config = self.integrations[IntegrationType.SLACK]
            
            emoji = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "🚨"}[alert.severity.value]
            color = {"low": "warning", "medium": "warning", "high": "danger", "critical": "danger"}[alert.severity.value]
            
            message = {
                "channel": config.settings["channel"],
                "attachments": [{
                    "color": color,
                    "title": f"{emoji} {alert.title}",
                    "text": alert.description,
                    "fields": [
                        {"title": "Repository", "value": alert.repository, "short": True},
                        {"title": "Workflow", "value": alert.workflow_name, "short": True},
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                    ],
                    "footer": "GitHub Actions Integration Hub",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            # Simulate sending (in real implementation, would use Slack API)
            logger.info(f"📤 Slack alert sent: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
            return False
    
    async def _send_pagerduty_alert(self, alert: Alert) -> bool:
        """Send alert to PagerDuty"""
        try:
            config = self.integrations[IntegrationType.PAGERDUTY]
            
            event_data = {
                "routing_key": config.credentials["integration_key"],
                "event_action": "trigger",
                "payload": {
                    "summary": alert.title,
                    "source": alert.repository,
                    "severity": alert.severity.value,
                    "component": "github-actions",
                    "group": "workflow-failures",
                    "class": "workflow",
                    "custom_details": {
                        "workflow_name": alert.workflow_name,
                        "repository": alert.repository,
                        "description": alert.description
                    }
                }
            }
            
            # Simulate sending (in real implementation, would use PagerDuty API)
            logger.info(f"📟 PagerDuty alert sent: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send PagerDuty alert: {e}")
            return False
    
    async def _create_jira_issue(self, alert: Alert) -> bool:
        """Create JIRA issue for critical alerts"""
        try:
            config = self.integrations[IntegrationType.JIRA]
            
            issue_data = {
                "fields": {
                    "project": {"key": config.settings["project_key"]},
                    "summary": alert.title,
                    "description": f"{alert.description}\n\nRepository: {alert.repository}\nWorkflow: {alert.workflow_name}\nTimestamp: {alert.timestamp}",
                    "issuetype": {"name": config.settings["issue_type"]},
                    "priority": {"name": "High" if alert.severity == AlertSeverity.CRITICAL else "Medium"},
                    "labels": ["github-actions", "automated", "workflow-failure"]
                }
            }
            
            # Simulate creating (in real implementation, would use JIRA API)
            logger.info(f"🎫 JIRA issue created: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create JIRA issue: {e}")
            return False
    
    async def _send_slack_notification(self, event: WorkflowEvent):
        """Send workflow completion notification to Slack"""
        try:
            if event.event_type == "completed":
                emoji = "✅" if event.conclusion == "success" else "❌"
                color = "good" if event.conclusion == "success" else "danger"
            else:
                return  # Only send for completed workflows
            
            duration_text = f" ({event.duration_seconds//60}m {event.duration_seconds%60}s)" if event.duration_seconds else ""
            
            logger.info(f"📤 Slack notification: {event.repository} - {event.workflow_name} - {event.conclusion}{duration_text}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    async def _send_prometheus_metrics(self, event: WorkflowEvent):
        """Send metrics to Prometheus"""
        try:
            metric = {
                "workflow_run_duration_seconds": event.duration_seconds or 0,
                "workflow_run_count": 1,
                "workflow_success": 1 if event.conclusion == "success" else 0,
                "workflow_failure": 1 if event.conclusion == "failure" else 0,
                "labels": {
                    "repository": event.repository,
                    "workflow": event.workflow_name,
                    "branch": event.metadata.get("head_branch", "unknown"),
                    "status": event.status,
                    "conclusion": event.conclusion or "unknown"
                },
                "timestamp": event.timestamp.timestamp()
            }
            
            self.metrics_buffer.append(metric)
            logger.debug(f"📊 Metrics buffered for {event.repository} - {event.workflow_name}")
            
        except Exception as e:
            logger.error(f"Failed to buffer Prometheus metrics: {e}")
    
    def _update_metrics(self, event: WorkflowEvent):
        """Update internal metrics tracking"""
        # This would update internal counters, rates, etc.
        pass
    
    async def _metrics_collector(self, repositories: List[str]):
        """Collect and export metrics periodically"""
        logger.info("📊 Starting metrics collection")
        
        while True:
            try:
                if self.metrics_buffer:
                    # Export buffered metrics to Prometheus/Grafana
                    metrics_count = len(self.metrics_buffer)
                    logger.info(f"📤 Exporting {metrics_count} metrics to Prometheus")
                    
                    # Simulate export (in real implementation, would push to Prometheus)
                    self.metrics_buffer.clear()
                
                await asyncio.sleep(60)  # Export every minute
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _alert_processor(self):
        """Process and manage alerts lifecycle"""
        logger.info("🚨 Starting alert processing")
        
        while True:
            try:
                # Auto-resolve old alerts
                current_time = datetime.now()
                for alert_id, alert in list(self.active_alerts.items()):
                    if not alert.resolved and (current_time - alert.timestamp).hours > 24:
                        alert.resolved = True
                        logger.info(f"✅ Auto-resolved alert: {alert.title}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Alert processing error: {e}")
                await asyncio.sleep(300)
    
    async def _integration_health_checker(self):
        """Monitor integration health and connectivity"""
        logger.info("🏥 Starting integration health monitoring")
        
        while True:
            try:
                for int_type, config in self.integrations.items():
                    if config.enabled:
                        # Simulate health check (in real implementation, would ping endpoints)
                        logger.debug(f"✅ {int_type.value} integration healthy")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Integration health check error: {e}")
                await asyncio.sleep(300)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        active_alerts = [alert for alert in self.active_alerts.values() if not alert.resolved]
        
        return {
            "integrations": {
                int_type.value: {
                    "enabled": config.enabled,
                    "endpoint": config.endpoint,
                    "healthy": True  # Would be actual health status
                }
                for int_type, config in self.integrations.items()
            },
            "alerts": {
                "active": len(active_alerts),
                "critical": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                "high": len([a for a in active_alerts if a.severity == AlertSeverity.HIGH]),
                "medium": len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]),
                "recent": [asdict(alert) for alert in active_alerts[-5:]]
            },
            "events": {
                "total_processed": len(self.event_history),
                "recent": [asdict(event) for event in self.event_history[-10:]],
                "metrics_buffered": len(self.metrics_buffer)
            },
            "status": {
                "uptime": "operational",
                "last_update": datetime.now().isoformat(),
                "repositories_monitored": len(set(event.repository for event in self.event_history[-100:]))
            }
        }

# Demo function
async def demo_enterprise_integration():
    """Demonstrate the enterprise integration hub"""
    hub = EnterpriseIntegrationHub()
    
    print("🏢 GitHub Actions Enterprise Integration Hub Demo")
    print("=" * 55)
    
    # Show integration status
    dashboard = hub.get_dashboard_data()
    print(f"\n🔌 Active Integrations:")
    for name, info in dashboard["integrations"].items():
        status = "🟢 Enabled" if info["enabled"] else "🔴 Disabled"
        print(f"   {name.upper()}: {status}")
    
    # Simulate monitoring for a short period
    repositories = ["microsoft/vscode", "kubernetes/kubernetes"]
    
    print(f"\n📡 Starting monitoring for {len(repositories)} repositories...")
    print("   (Running for 30 seconds to demonstrate integration flows)")
    
    try:
        # Run monitoring for 30 seconds
        await asyncio.wait_for(hub.start_monitoring(repositories), timeout=30.0)
    except asyncio.TimeoutError:
        print("\n⏰ Demo timeout reached")
    
    # Show final dashboard
    dashboard = hub.get_dashboard_data()
    print(f"\n📊 Final Dashboard Status:")
    print(f"   Events Processed: {dashboard['events']['total_processed']}")
    print(f"   Active Alerts: {dashboard['alerts']['active']}")
    print(f"   Metrics Buffered: {dashboard['events']['metrics_buffered']}")
    print(f"   Repositories Monitored: {dashboard['status']['repositories_monitored']}")

if __name__ == "__main__":
    asyncio.run(demo_enterprise_integration())
