"""
Multi-Cloud Deployment Orchestrator for GitHub Actions
Advanced deployment automation across AWS, Azure, GCP, and on-premises
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import logging

logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISES = "on_premises"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"

class DeploymentStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    DEPLOYING = "deploying"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

class DeploymentStrategy(Enum):
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    RECREATE = "recreate"
    A_B_TEST = "a_b_test"

@dataclass
class CloudTarget:
    provider: CloudProvider
    region: str
    environment: str  # dev, staging, prod
    cluster_name: Optional[str] = None
    namespace: Optional[str] = None
    resource_group: Optional[str] = None
    project_id: Optional[str] = None
    credentials_secret: str = ""
    capacity_limits: Dict[str, Any] = None

@dataclass
class DeploymentConfig:
    application_name: str
    version: str
    image_tag: str
    strategy: DeploymentStrategy
    targets: List[CloudTarget]
    rollback_enabled: bool = True
    health_checks: List[str] = None
    traffic_split: Dict[str, float] = None  # For canary/A-B testing
    timeout_minutes: int = 30
    auto_promote: bool = False
    notifications: List[str] = None

@dataclass
class DeploymentResult:
    deployment_id: str
    target: CloudTarget
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    health_score: float = 0.0
    error_message: Optional[str] = None
    rollback_available: bool = False
    metrics: Dict[str, Any] = None
    logs_url: Optional[str] = None

@dataclass
class TrafficSplit:
    version_a: str
    version_b: str
    traffic_a_percent: float
    traffic_b_percent: float
    success_metrics: Dict[str, float]
    decision_criteria: Dict[str, Any]

class MultiCloudOrchestrator:
    """Advanced multi-cloud deployment orchestrator"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.active_deployments: Dict[str, DeploymentResult] = {}
        self.deployment_history: List[DeploymentResult] = []
        self.cloud_adapters = self._initialize_cloud_adapters()
        self.monitoring_config = self._setup_monitoring()
    
    def _initialize_cloud_adapters(self) -> Dict[CloudProvider, Dict[str, Any]]:
        """Initialize cloud provider adapters"""
        return {
            CloudProvider.AWS: {
                "services": ["ECS", "EKS", "Lambda", "EC2", "Fargate"],
                "regions": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                "deployment_tools": ["CodeDeploy", "CloudFormation", "CDK"],
                "monitoring": ["CloudWatch", "X-Ray"]
            },
            CloudProvider.AZURE: {
                "services": ["AKS", "Container Instances", "App Service", "Functions"],
                "regions": ["East US", "West Europe", "Southeast Asia"],
                "deployment_tools": ["ARM Templates", "Bicep", "DevOps"],
                "monitoring": ["Application Insights", "Monitor"]
            },
            CloudProvider.GCP: {
                "services": ["GKE", "Cloud Run", "App Engine", "Compute Engine"],
                "regions": ["us-central1", "europe-west1", "asia-east1"],
                "deployment_tools": ["Cloud Deploy", "Deployment Manager"],
                "monitoring": ["Cloud Monitoring", "Cloud Trace"]
            },
            CloudProvider.KUBERNETES: {
                "services": ["Deployment", "StatefulSet", "DaemonSet", "Job"],
                "strategies": ["kubectl", "Helm", "Kustomize", "ArgoCD"],
                "monitoring": ["Prometheus", "Grafana", "Jaeger"]
            },
            CloudProvider.ON_PREMISES: {
                "services": ["Docker", "Podman", "systemd", "PM2"],
                "deployment_tools": ["Ansible", "Chef", "Puppet"],
                "monitoring": ["Nagios", "Zabbix", "PRTG"]
            }
        }
    
    def _setup_monitoring(self) -> Dict[str, Any]:
        """Setup deployment monitoring configuration"""
        return {
            "health_checks": {
                "http_endpoint": {
                    "path": "/health",
                    "expected_status": 200,
                    "timeout_seconds": 10,
                    "interval_seconds": 30
                },
                "tcp_port": {
                    "port": 8080,
                    "timeout_seconds": 5
                },
                "custom_script": {
                    "command": "curl -f http://localhost:8080/ready",
                    "expected_exit_code": 0
                }
            },
            "metrics": {
                "cpu_threshold": 80.0,
                "memory_threshold": 85.0,
                "error_rate_threshold": 5.0,
                "response_time_threshold": 2000.0
            },
            "alerting": {
                "channels": ["slack", "email", "pagerduty"],
                "escalation_time_minutes": 15
            }
        }
    
    async def create_deployment(self, config: DeploymentConfig) -> str:
        """Create a new multi-cloud deployment"""
        deployment_id = f"deploy-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{config.application_name}"
        
        logger.info(f"🚀 Creating deployment: {deployment_id}")
        logger.info(f"   Application: {config.application_name} v{config.version}")
        logger.info(f"   Strategy: {config.strategy.value}")
        logger.info(f"   Targets: {len(config.targets)} cloud targets")
        
        # Validate deployment configuration
        validation_result = await self._validate_deployment_config(config)
        if not validation_result["valid"]:
            logger.error(f"❌ Deployment validation failed: {validation_result['errors']}")
            return deployment_id
        
        # Create deployment plan
        deployment_plan = await self._create_deployment_plan(config)
        logger.info(f"   📋 Plan: {len(deployment_plan['phases'])} deployment phases")
        
        # Execute deployment across all targets
        results = []
        for target in config.targets:
            result = await self._deploy_to_target(deployment_id, config, target)
            results.append(result)
            self.active_deployments[f"{deployment_id}-{target.provider.value}"] = result
        
        # Monitor overall deployment progress
        await self._monitor_deployment_progress(deployment_id, results)
        
        return deployment_id
    
    async def _validate_deployment_config(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Validate deployment configuration"""
        errors = []
        warnings = []
        
        # Validate targets
        if not config.targets:
            errors.append("No deployment targets specified")
        
        # Validate traffic split for canary deployments
        if config.strategy == DeploymentStrategy.CANARY:
            if not config.traffic_split:
                warnings.append("No traffic split configured for canary deployment")
            elif sum(config.traffic_split.values()) != 100:
                errors.append("Traffic split percentages must sum to 100")
        
        # Validate cloud provider configurations
        for target in config.targets:
            provider_config = self.cloud_adapters.get(target.provider)
            if not provider_config:
                errors.append(f"Unsupported cloud provider: {target.provider.value}")
            
            # Check region availability
            if "regions" in provider_config and target.region not in provider_config["regions"]:
                warnings.append(f"Region {target.region} not in supported list for {target.provider.value}")
        
        # Validate image and version
        if not config.image_tag:
            errors.append("Container image tag is required")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def _create_deployment_plan(self, config: DeploymentConfig) -> Dict[str, Any]:
        """Create detailed deployment execution plan"""
        plan = {
            "deployment_id": f"deploy-{config.application_name}-{config.version}",
            "strategy": config.strategy.value,
            "phases": []
        }
        
        if config.strategy == DeploymentStrategy.BLUE_GREEN:
            plan["phases"] = [
                {"name": "Deploy Green", "targets": config.targets, "parallel": True},
                {"name": "Health Check", "wait_time": 120},
                {"name": "Switch Traffic", "traffic_split": {"green": 100, "blue": 0}},
                {"name": "Cleanup Blue", "delay_minutes": 30}
            ]
        
        elif config.strategy == DeploymentStrategy.CANARY:
            plan["phases"] = [
                {"name": "Deploy Canary", "targets": config.targets[:1], "traffic": 10},
                {"name": "Monitor Canary", "duration_minutes": 15},
                {"name": "Scale Canary", "traffic": 50},
                {"name": "Full Deployment", "targets": config.targets, "traffic": 100}
            ]
        
        elif config.strategy == DeploymentStrategy.ROLLING:
            # Group targets into batches
            batch_size = max(1, len(config.targets) // 3)
            batches = [config.targets[i:i + batch_size] for i in range(0, len(config.targets), batch_size)]
            
            for i, batch in enumerate(batches):
                plan["phases"].append({
                    "name": f"Rolling Batch {i+1}",
                    "targets": batch,
                    "wait_for_health": True
                })
        
        else:  # RECREATE
            plan["phases"] = [
                {"name": "Stop Old Version", "targets": config.targets},
                {"name": "Deploy New Version", "targets": config.targets, "parallel": True}
            ]
        
        return plan
    
    async def _deploy_to_target(self, deployment_id: str, config: DeploymentConfig, 
                              target: CloudTarget) -> DeploymentResult:
        """Deploy application to a specific cloud target"""
        start_time = datetime.now()
        
        result = DeploymentResult(
            deployment_id=f"{deployment_id}-{target.provider.value}",
            target=target,
            status=DeploymentStatus.DEPLOYING,
            start_time=start_time
        )
        
        try:
            logger.info(f"   🎯 Deploying to {target.provider.value} ({target.region})")
            
            # Simulate cloud-specific deployment
            deployment_commands = await self._generate_deployment_commands(config, target)
            
            # Execute deployment
            await self._execute_deployment_commands(deployment_commands, target)
            
            # Wait for deployment to stabilize
            await asyncio.sleep(2)  # Simulate deployment time
            
            # Perform health checks
            health_result = await self._perform_health_checks(config, target)
            
            result.status = DeploymentStatus.COMPLETED if health_result["healthy"] else DeploymentStatus.FAILED
            result.health_score = health_result["score"]
            result.end_time = datetime.now()
            result.duration_seconds = int((result.end_time - start_time).total_seconds())
            result.rollback_available = True
            result.logs_url = f"https://{target.provider.value}.console.com/logs/{deployment_id}"
            
            # Generate deployment metrics
            result.metrics = {
                "pods_ready": 3,
                "pods_total": 3,
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "response_time_ms": 120,
                "error_rate": 0.1
            }
            
            logger.info(f"   ✅ {target.provider.value} deployment completed (health: {health_result['score']:.1%})")
            
        except Exception as e:
            result.status = DeploymentStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
            result.duration_seconds = int((result.end_time - start_time).total_seconds())
            
            logger.error(f"   ❌ {target.provider.value} deployment failed: {e}")
        
        return result
    
    async def _generate_deployment_commands(self, config: DeploymentConfig, 
                                          target: CloudTarget) -> List[str]:
        """Generate cloud-specific deployment commands"""
        commands = []
        
        if target.provider == CloudProvider.AWS:
            if "EKS" in self.cloud_adapters[CloudProvider.AWS]["services"]:
                commands = [
                    f"aws eks update-kubeconfig --region {target.region} --name {target.cluster_name}",
                    f"kubectl set image deployment/{config.application_name} {config.application_name}={config.image_tag}",
                    f"kubectl rollout status deployment/{config.application_name} --timeout=300s"
                ]
        
        elif target.provider == CloudProvider.AZURE:
            commands = [
                f"az aks get-credentials --resource-group {target.resource_group} --name {target.cluster_name}",
                f"kubectl set image deployment/{config.application_name} {config.application_name}={config.image_tag}",
                f"kubectl rollout status deployment/{config.application_name}"
            ]
        
        elif target.provider == CloudProvider.GCP:
            commands = [
                f"gcloud container clusters get-credentials {target.cluster_name} --region {target.region}",
                f"kubectl set image deployment/{config.application_name} {config.application_name}={config.image_tag}",
                f"kubectl rollout status deployment/{config.application_name}"
            ]
        
        elif target.provider == CloudProvider.KUBERNETES:
            commands = [
                f"kubectl config use-context {target.cluster_name}",
                f"kubectl set image deployment/{config.application_name} {config.application_name}={config.image_tag} -n {target.namespace}",
                f"kubectl rollout status deployment/{config.application_name} -n {target.namespace}"
            ]
        
        return commands
    
    async def _execute_deployment_commands(self, commands: List[str], target: CloudTarget):
        """Execute deployment commands (simulated)"""
        for command in commands:
            logger.debug(f"      🔧 Executing: {command}")
            await asyncio.sleep(0.5)  # Simulate command execution time
    
    async def _perform_health_checks(self, config: DeploymentConfig, 
                                   target: CloudTarget) -> Dict[str, Any]:
        """Perform comprehensive health checks"""
        health_checks = config.health_checks or ["http_endpoint"]
        
        results = []
        for check_type in health_checks:
            if check_type == "http_endpoint":
                # Simulate HTTP health check
                results.append({"type": "http", "passed": True, "response_time": 150})
            elif check_type == "tcp_port":
                # Simulate TCP port check
                results.append({"type": "tcp", "passed": True, "response_time": 5})
            elif check_type == "custom_script":
                # Simulate custom health check
                results.append({"type": "custom", "passed": True, "output": "Service healthy"})
        
        passed_checks = len([r for r in results if r["passed"]])
        health_score = passed_checks / len(results) if results else 0.0
        
        return {
            "healthy": health_score >= 0.8,
            "score": health_score,
            "checks": results
        }
    
    async def _monitor_deployment_progress(self, deployment_id: str, results: List[DeploymentResult]):
        """Monitor overall deployment progress"""
        logger.info(f"   📊 Monitoring deployment progress...")
        
        # Check results periodically
        for _ in range(3):  # Simulate monitoring cycles
            await asyncio.sleep(1)
            
            completed = len([r for r in results if r.status in [DeploymentStatus.COMPLETED, DeploymentStatus.FAILED]])
            progress = completed / len(results) * 100 if results else 0
            
            logger.info(f"      Progress: {progress:.0f}% ({completed}/{len(results)} targets)")
        
        # Final status summary
        successful = len([r for r in results if r.status == DeploymentStatus.COMPLETED])
        failed = len([r for r in results if r.status == DeploymentStatus.FAILED])
        
        if failed == 0:
            logger.info(f"   🎉 Deployment {deployment_id} completed successfully!")
        elif successful > 0:
            logger.warning(f"   ⚠️ Deployment {deployment_id} partially successful ({successful}/{len(results)})")
        else:
            logger.error(f"   💥 Deployment {deployment_id} failed on all targets")
    
    async def rollback_deployment(self, deployment_id: str, target_provider: Optional[CloudProvider] = None) -> Dict[str, Any]:
        """Rollback deployment to previous version"""
        logger.info(f"🔄 Initiating rollback for deployment: {deployment_id}")
        
        # Find deployments to rollback
        deployments_to_rollback = []
        for key, deployment in self.active_deployments.items():
            if deployment_id in key:
                if target_provider is None or deployment.target.provider == target_provider:
                    deployments_to_rollback.append(deployment)
        
        if not deployments_to_rollback:
            return {"success": False, "message": "No active deployments found to rollback"}
        
        rollback_results = []
        for deployment in deployments_to_rollback:
            logger.info(f"   🔙 Rolling back {deployment.target.provider.value}")
            
            # Simulate rollback process
            rollback_start = datetime.now()
            await asyncio.sleep(1)  # Simulate rollback time
            
            # Update deployment status
            deployment.status = DeploymentStatus.ROLLED_BACK
            
            rollback_results.append({
                "target": deployment.target.provider.value,
                "success": True,
                "duration": int((datetime.now() - rollback_start).total_seconds())
            })
            
            logger.info(f"   ✅ {deployment.target.provider.value} rollback completed")
        
        return {
            "success": True,
            "rollback_count": len(rollback_results),
            "results": rollback_results
        }
    
    async def manage_traffic_split(self, deployment_id: str, traffic_config: TrafficSplit) -> Dict[str, Any]:
        """Manage traffic splitting for A/B testing and canary deployments"""
        logger.info(f"🚦 Managing traffic split for deployment: {deployment_id}")
        logger.info(f"   Version A ({traffic_config.version_a}): {traffic_config.traffic_a_percent}%")
        logger.info(f"   Version B ({traffic_config.version_b}): {traffic_config.traffic_b_percent}%")
        
        # Simulate traffic management
        await asyncio.sleep(1)
        
        # Collect metrics for both versions
        metrics_a = {
            "response_time": 145,
            "error_rate": 0.1,
            "cpu_usage": 42.3,
            "user_satisfaction": 0.92
        }
        
        metrics_b = {
            "response_time": 132,
            "error_rate": 0.05,
            "cpu_usage": 38.7,
            "user_satisfaction": 0.95
        }
        
        # Analyze performance
        version_b_better = (
            metrics_b["response_time"] < metrics_a["response_time"] and
            metrics_b["error_rate"] < metrics_a["error_rate"] and
            metrics_b["user_satisfaction"] > metrics_a["user_satisfaction"]
        )
        
        recommendation = "promote_b" if version_b_better else "keep_a"
        
        logger.info(f"   📊 Performance Analysis:")
        logger.info(f"      Version A: {metrics_a['response_time']}ms, {metrics_a['error_rate']}% errors")
        logger.info(f"      Version B: {metrics_b['response_time']}ms, {metrics_b['error_rate']}% errors")
        logger.info(f"   🎯 Recommendation: {recommendation}")
        
        return {
            "traffic_updated": True,
            "metrics": {
                "version_a": metrics_a,
                "version_b": metrics_b
            },
            "recommendation": recommendation,
            "confidence_score": 0.85
        }
    
    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get comprehensive deployment status"""
        active_deployments = {k: v for k, v in self.active_deployments.items() if deployment_id in k}
        
        if not active_deployments:
            return {"status": "not_found", "message": "Deployment not found"}
        
        total_targets = len(active_deployments)
        completed = len([d for d in active_deployments.values() if d.status == DeploymentStatus.COMPLETED])
        failed = len([d for d in active_deployments.values() if d.status == DeploymentStatus.FAILED])
        
        overall_status = "completed" if completed == total_targets else "failed" if failed > 0 else "in_progress"
        
        return {
            "deployment_id": deployment_id,
            "overall_status": overall_status,
            "progress": {
                "total_targets": total_targets,
                "completed": completed,
                "failed": failed,
                "progress_percent": completed / total_targets * 100 if total_targets > 0 else 0
            },
            "targets": [
                {
                    "provider": d.target.provider.value,
                    "region": d.target.region,
                    "status": d.status.value,
                    "health_score": d.health_score,
                    "duration": d.duration_seconds
                }
                for d in active_deployments.values()
            ]
        }
    
    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate comprehensive deployment analytics report"""
        all_deployments = list(self.active_deployments.values()) + self.deployment_history
        
        if not all_deployments:
            return {"message": "No deployments found"}
        
        # Calculate metrics
        total_deployments = len(all_deployments)
        successful_deployments = len([d for d in all_deployments if d.status == DeploymentStatus.COMPLETED])
        success_rate = successful_deployments / total_deployments * 100 if total_deployments > 0 else 0
        
        # Average deployment time by provider
        provider_stats = {}
        for deployment in all_deployments:
            provider = deployment.target.provider.value
            if provider not in provider_stats:
                provider_stats[provider] = {"deployments": 0, "total_duration": 0, "success_count": 0}
            
            provider_stats[provider]["deployments"] += 1
            if deployment.duration_seconds:
                provider_stats[provider]["total_duration"] += deployment.duration_seconds
            if deployment.status == DeploymentStatus.COMPLETED:
                provider_stats[provider]["success_count"] += 1
        
        # Calculate averages
        for provider, stats in provider_stats.items():
            stats["avg_duration"] = stats["total_duration"] / stats["deployments"] if stats["deployments"] > 0 else 0
            stats["success_rate"] = stats["success_count"] / stats["deployments"] * 100 if stats["deployments"] > 0 else 0
        
        return {
            "summary": {
                "total_deployments": total_deployments,
                "successful_deployments": successful_deployments,
                "success_rate_percent": success_rate,
                "active_deployments": len(self.active_deployments)
            },
            "provider_statistics": provider_stats,
            "recent_deployments": [
                {
                    "id": d.deployment_id,
                    "provider": d.target.provider.value,
                    "status": d.status.value,
                    "duration": d.duration_seconds,
                    "health_score": d.health_score
                }
                for d in sorted(all_deployments, key=lambda x: x.start_time, reverse=True)[:10]
            ]
        }

# Demo function
async def demo_multi_cloud_orchestrator():
    """Demonstrate the multi-cloud deployment orchestrator"""
    orchestrator = MultiCloudOrchestrator()
    
    print("🌐 Multi-Cloud Deployment Orchestrator Demo")
    print("=" * 50)
    
    # Create deployment configuration
    config = DeploymentConfig(
        application_name="web-service",
        version="2.1.0",
        image_tag="myapp:v2.1.0",
        strategy=DeploymentStrategy.CANARY,
        targets=[
            CloudTarget(
                provider=CloudProvider.AWS,
                region="us-west-2",
                environment="production",
                cluster_name="prod-cluster",
                credentials_secret="aws-prod-creds"
            ),
            CloudTarget(
                provider=CloudProvider.AZURE,
                region="West Europe",
                environment="production",
                cluster_name="aks-prod",
                resource_group="prod-rg",
                credentials_secret="azure-prod-creds"
            ),
            CloudTarget(
                provider=CloudProvider.GCP,
                region="europe-west1",
                environment="production",
                cluster_name="gke-prod",
                project_id="my-project-prod",
                credentials_secret="gcp-prod-creds"
            )
        ],
        traffic_split={"v2.0.0": 90, "v2.1.0": 10},
        health_checks=["http_endpoint", "tcp_port"],
        timeout_minutes=30,
        notifications=["slack://ops-channel", "email://ops@company.com"]
    )
    
    print(f"\n🚀 Starting Canary Deployment")
    print(f"   Application: {config.application_name} v{config.version}")
    print(f"   Strategy: {config.strategy.value}")
    print(f"   Targets: {len(config.targets)} cloud providers")
    
    # Execute deployment
    deployment_id = await orchestrator.create_deployment(config)
    
    # Check deployment status
    print(f"\n📊 Deployment Status:")
    status = orchestrator.get_deployment_status(deployment_id)
    print(f"   Overall Status: {status['overall_status']}")
    print(f"   Progress: {status['progress']['progress_percent']:.0f}%")
    
    for target in status['targets']:
        print(f"   {target['provider'].upper()}: {target['status']} (health: {target['health_score']:.1%})")
    
    # Demonstrate traffic management
    print(f"\n🚦 Managing Traffic Split...")
    traffic_config = TrafficSplit(
        version_a="v2.0.0",
        version_b="v2.1.0",
        traffic_a_percent=90,
        traffic_b_percent=10,
        success_metrics={"response_time": 150, "error_rate": 0.1},
        decision_criteria={"auto_promote_threshold": 0.95}
    )
    
    traffic_result = await orchestrator.manage_traffic_split(deployment_id, traffic_config)
    print(f"   Traffic Management: {'✅ Success' if traffic_result['traffic_updated'] else '❌ Failed'}")
    print(f"   Recommendation: {traffic_result['recommendation']}")
    
    # Demonstrate rollback capability
    print(f"\n🔄 Testing Rollback Capability...")
    rollback_result = await orchestrator.rollback_deployment(deployment_id, CloudProvider.AWS)
    print(f"   Rollback Result: {'✅ Success' if rollback_result['success'] else '❌ Failed'}")
    if rollback_result['success']:
        print(f"   Rollbacks Completed: {rollback_result['rollback_count']}")
    
    # Generate comprehensive report
    print(f"\n📈 Deployment Analytics Report:")
    report = orchestrator.generate_deployment_report()
    summary = report["summary"]
    
    print(f"   Total Deployments: {summary['total_deployments']}")
    print(f"   Success Rate: {summary['success_rate_percent']:.1f}%")
    print(f"   Active Deployments: {summary['active_deployments']}")
    
    print(f"\n🏆 Provider Performance:")
    for provider, stats in report["provider_statistics"].items():
        print(f"   {provider.upper()}: {stats['success_rate']:.1f}% success, avg {stats['avg_duration']:.0f}s")

if __name__ == "__main__":
    asyncio.run(demo_multi_cloud_orchestrator())
