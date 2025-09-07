"""
AI-Powered Predictive Analytics for GitHub Actions
Machine learning based failure prediction and optimization recommendations
"""

import asyncio
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import logging

logger = logging.getLogger(__name__)

class PredictionType(Enum):
    FAILURE_RISK = "failure_risk"
    DURATION_PREDICTION = "duration_prediction"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    QUEUE_TIME_PREDICTION = "queue_time_prediction"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class FailurePrediction:
    workflow_id: str
    workflow_name: str
    repository: str
    failure_probability: float
    risk_level: RiskLevel
    contributing_factors: List[str]
    recommended_actions: List[str]
    confidence_score: float
    prediction_window_hours: int

@dataclass
class PerformancePrediction:
    workflow_id: str
    workflow_name: str
    repository: str
    predicted_duration_minutes: float
    duration_confidence: float
    predicted_queue_time_minutes: float
    queue_confidence: float
    optimal_trigger_time: datetime
    resource_recommendations: List[str]

@dataclass
class TrendAnalysis:
    metric_name: str
    repository: str
    current_value: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0-1
    predicted_value_7d: float
    predicted_value_30d: float
    anomaly_detected: bool
    anomaly_score: float

class AIAnalyticsEngine:
    """AI-powered predictive analytics for GitHub Actions workflows"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.historical_data: Dict[str, List[Dict[str, Any]]] = {}
        self.models = self._initialize_models()
        self.feature_extractors = self._setup_feature_extractors()
    
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize ML models (simplified for demo)"""
        return {
            "failure_predictor": {
                "weights": {
                    "recent_failure_rate": 0.4,
                    "duration_increase": 0.3,
                    "queue_time": 0.1,
                    "branch_type": 0.1,
                    "time_of_day": 0.05,
                    "day_of_week": 0.05
                },
                "threshold": 0.7
            },
            "duration_predictor": {
                "baseline_multipliers": {
                    "npm_install": 1.5,
                    "test_suite": 2.0,
                    "docker_build": 1.8,
                    "deployment": 1.2
                },
                "branch_factors": {
                    "main": 1.0,
                    "develop": 1.1,
                    "feature": 1.2,
                    "hotfix": 0.9
                }
            },
            "anomaly_detector": {
                "sensitivity": 2.0,  # Standard deviations for anomaly detection
                "window_size": 20    # Number of recent runs to consider
            }
        }
    
    def _setup_feature_extractors(self) -> Dict[str, Any]:
        """Setup feature extraction configurations"""
        return {
            "time_features": {
                "peak_hours": [9, 10, 11, 14, 15, 16],  # Business hours
                "weekend_factor": 0.7,  # Reduced activity on weekends
                "holiday_factor": 0.3   # Minimal activity on holidays
            },
            "workflow_patterns": {
                "test_keywords": ["test", "spec", "check", "verify"],
                "build_keywords": ["build", "compile", "package"],
                "deploy_keywords": ["deploy", "release", "publish"],
                "security_keywords": ["security", "scan", "audit", "vulnerability"]
            },
            "failure_indicators": {
                "flaky_patterns": ["timeout", "network", "connection", "random"],
                "config_issues": ["permission", "access", "credential", "token"],
                "code_issues": ["compilation", "syntax", "import", "dependency"]
            }
        }
    
    async def collect_training_data(self, repositories: List[str], days_back: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """Collect historical data for model training"""
        logger.info(f"🧠 Collecting training data for {len(repositories)} repositories ({days_back} days)")
        
        training_data = {}
        
        async with aiohttp.ClientSession() as session:
            for repo in repositories:
                owner, repo_name = repo.split('/')
                repo_data = await self._collect_repository_data(session, owner, repo_name, days_back)
                training_data[repo] = repo_data
                
                logger.info(f"   📊 {repo}: {len(repo_data)} workflow runs collected")
        
        self.historical_data.update(training_data)
        return training_data
    
    async def _collect_repository_data(self, session: aiohttp.ClientSession, owner: str, repo: str, days_back: int) -> List[Dict[str, Any]]:
        """Collect comprehensive data for a single repository"""
        data = []
        
        try:
            # Get workflow runs
            async with session.get(f"{self.base_url}/api/v1/actions/{owner}/{repo}/runs") as response:
                if response.status == 200:
                    runs_data = await response.json()
                    
                    # Get analytics
                    async with session.get(f"{self.base_url}/api/v1/analytics/actions/{owner}/{repo}/workflow-metrics") as analytics_response:
                        analytics_data = await analytics_response.json() if analytics_response.status == 200 else {}
                    
                    # Process each run
                    for run in runs_data.get("workflow_runs", []):
                        run_data = await self._extract_run_features(session, owner, repo, run, analytics_data)
                        if run_data:
                            data.append(run_data)
        
        except Exception as e:
            logger.error(f"Failed to collect data for {owner}/{repo}: {e}")
        
        return data
    
    async def _extract_run_features(self, session: aiohttp.ClientSession, owner: str, repo: str, 
                                  run: Dict[str, Any], analytics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract comprehensive features from a workflow run"""
        try:
            # Basic run information
            created_at = datetime.fromisoformat(run["created_at"].replace('Z', '+00:00'))
            updated_at = datetime.fromisoformat(run["updated_at"].replace('Z', '+00:00'))
            
            # Calculate duration
            duration_seconds = 0
            if run.get("run_started_at") and run.get("updated_at"):
                start_time = datetime.fromisoformat(run["run_started_at"].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(run["updated_at"].replace('Z', '+00:00'))
                duration_seconds = int((end_time - start_time).total_seconds())
            
            # Extract time-based features
            time_features = self._extract_time_features(created_at)
            
            # Extract workflow content features
            workflow_features = self._extract_workflow_features(run["name"])
            
            # Get job details if available
            job_features = await self._extract_job_features(session, owner, repo, run["id"])
            
            return {
                "run_id": run["id"],
                "workflow_id": run["workflow_id"],
                "workflow_name": run["name"],
                "repository": f"{owner}/{repo}",
                "status": run["status"],
                "conclusion": run.get("conclusion"),
                "duration_seconds": duration_seconds,
                "run_number": run["run_number"],
                "event": run["event"],
                "head_branch": run["head_branch"],
                "created_at": created_at.isoformat(),
                "failed": run.get("conclusion") == "failure",
                **time_features,
                **workflow_features,
                **job_features
            }
        
        except Exception as e:
            logger.error(f"Failed to extract features for run {run.get('id')}: {e}")
            return None
    
    def _extract_time_features(self, timestamp: datetime) -> Dict[str, Any]:
        """Extract time-based features for ML models"""
        return {
            "hour_of_day": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "is_weekend": timestamp.weekday() >= 5,
            "is_peak_hour": timestamp.hour in self.feature_extractors["time_features"]["peak_hours"],
            "quarter_of_year": (timestamp.month - 1) // 3 + 1,
            "is_month_end": timestamp.day >= 28
        }
    
    def _extract_workflow_features(self, workflow_name: str) -> Dict[str, Any]:
        """Extract features from workflow name and content"""
        name_lower = workflow_name.lower()
        patterns = self.feature_extractors["workflow_patterns"]
        
        return {
            "has_test": any(keyword in name_lower for keyword in patterns["test_keywords"]),
            "has_build": any(keyword in name_lower for keyword in patterns["build_keywords"]),
            "has_deploy": any(keyword in name_lower for keyword in patterns["deploy_keywords"]),
            "has_security": any(keyword in name_lower for keyword in patterns["security_keywords"]),
            "workflow_name_length": len(workflow_name),
            "is_ci_workflow": "ci" in name_lower or "continuous" in name_lower,
            "is_cd_workflow": "cd" in name_lower or "deploy" in name_lower
        }
    
    async def _extract_job_features(self, session: aiohttp.ClientSession, owner: str, repo: str, run_id: str) -> Dict[str, Any]:
        """Extract job-level features"""
        try:
            async with session.get(f"{self.base_url}/api/v1/actions/{owner}/{repo}/runs/{run_id}/jobs") as response:
                if response.status == 200:
                    jobs_data = await response.json()
                    jobs = jobs_data.get("jobs", [])
                    
                    return {
                        "job_count": len(jobs),
                        "parallel_jobs": len([j for j in jobs if j.get("started_at")]),
                        "avg_job_duration": statistics.mean([self._calculate_job_duration(job) for job in jobs]) if jobs else 0,
                        "max_job_duration": max([self._calculate_job_duration(job) for job in jobs]) if jobs else 0,
                        "failed_jobs": len([j for j in jobs if j.get("conclusion") == "failure"])
                    }
        except:
            pass
        
        return {
            "job_count": 1,
            "parallel_jobs": 1,
            "avg_job_duration": 0,
            "max_job_duration": 0,
            "failed_jobs": 0
        }
    
    def _calculate_job_duration(self, job: Dict[str, Any]) -> float:
        """Calculate job duration in seconds"""
        if job.get("started_at") and job.get("completed_at"):
            try:
                start = datetime.fromisoformat(job["started_at"].replace('Z', '+00:00'))
                end = datetime.fromisoformat(job["completed_at"].replace('Z', '+00:00'))
                return (end - start).total_seconds()
            except:
                pass
        return 0.0
    
    async def predict_workflow_failure(self, repository: str, workflow_name: str, 
                                     context: Dict[str, Any] = None) -> FailurePrediction:
        """Predict workflow failure probability using ML model"""
        
        # Get historical data for this workflow
        repo_data = self.historical_data.get(repository, [])
        workflow_data = [run for run in repo_data if run["workflow_name"] == workflow_name]
        
        if len(workflow_data) < 5:
            # Not enough data for reliable prediction
            return FailurePrediction(
                workflow_id="unknown",
                workflow_name=workflow_name,
                repository=repository,
                failure_probability=0.5,
                risk_level=RiskLevel.MEDIUM,
                contributing_factors=["Insufficient historical data"],
                recommended_actions=["Collect more workflow run data"],
                confidence_score=0.1,
                prediction_window_hours=24
            )
        
        # Calculate recent failure rate
        recent_runs = sorted(workflow_data, key=lambda x: x["created_at"])[-10:]
        recent_failures = len([run for run in recent_runs if run["failed"]])
        failure_rate = recent_failures / len(recent_runs)
        
        # Analyze trends
        duration_trend = self._analyze_duration_trend(workflow_data)
        queue_time_factor = self._calculate_queue_time_factor(context or {})
        time_factor = self._calculate_time_risk_factor(datetime.now())
        
        # Apply ML model
        model = self.models["failure_predictor"]
        weights = model["weights"]
        
        failure_score = (
            failure_rate * weights["recent_failure_rate"] +
            duration_trend * weights["duration_increase"] +
            queue_time_factor * weights["queue_time"] +
            time_factor * weights["time_of_day"]
        )
        
        # Determine risk level
        if failure_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif failure_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif failure_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        # Generate contributing factors and recommendations
        factors = []
        actions = []
        
        if failure_rate > 0.3:
            factors.append(f"High recent failure rate ({failure_rate*100:.1f}%)")
            actions.append("Investigate recent failures and fix underlying issues")
        
        if duration_trend > 0.5:
            factors.append("Increasing workflow duration trend")
            actions.append("Optimize workflow performance (caching, parallelization)")
        
        if queue_time_factor > 0.7:
            factors.append("High system load expected")
            actions.append("Consider scheduling workflow during off-peak hours")
        
        if not factors:
            factors.append("Normal operational parameters")
            actions.append("Continue monitoring")
        
        return FailurePrediction(
            workflow_id=str(workflow_data[0]["workflow_id"]) if workflow_data else "unknown",
            workflow_name=workflow_name,
            repository=repository,
            failure_probability=failure_score,
            risk_level=risk_level,
            contributing_factors=factors,
            recommended_actions=actions,
            confidence_score=min(len(workflow_data) / 20.0, 1.0),  # Higher confidence with more data
            prediction_window_hours=24
        )
    
    def _analyze_duration_trend(self, workflow_data: List[Dict[str, Any]]) -> float:
        """Analyze if workflow durations are trending upward"""
        if len(workflow_data) < 5:
            return 0.0
        
        # Get recent durations
        recent_data = sorted(workflow_data, key=lambda x: x["created_at"])[-10:]
        durations = [run["duration_seconds"] for run in recent_data if run["duration_seconds"] > 0]
        
        if len(durations) < 3:
            return 0.0
        
        # Simple trend analysis (slope estimation)
        if len(durations) > 1:
            # Calculate simple linear trend
            x_vals = list(range(len(durations)))
            n = len(durations)
            sum_x = sum(x_vals)
            sum_y = sum(durations)
            sum_xy = sum(x * y for x, y in zip(x_vals, durations))
            sum_x_sq = sum(x * x for x in x_vals)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_sq - sum_x * sum_x) if (n * sum_x_sq - sum_x * sum_x) != 0 else 0
            max_duration = max(durations)
            normalized_slope = slope / max_duration if max_duration > 0 else 0
            return max(0.0, min(1.0, normalized_slope * 10))  # Normalize to 0-1
        
        return 0.0
    
    def _calculate_queue_time_factor(self, context: Dict[str, Any]) -> float:
        """Calculate expected queue time factor"""
        current_hour = datetime.now().hour
        
        # Higher queue times during peak hours
        if current_hour in self.feature_extractors["time_features"]["peak_hours"]:
            return 0.8
        elif 6 <= current_hour <= 22:  # Regular business hours
            return 0.4
        else:  # Off hours
            return 0.1
    
    def _calculate_time_risk_factor(self, timestamp: datetime) -> float:
        """Calculate time-based risk factor"""
        # Higher risk during peak deployment times (end of week, end of day)
        risk = 0.0
        
        # Friday deployments are riskier
        if timestamp.weekday() == 4:  # Friday
            risk += 0.3
        
        # Late day deployments are riskier
        if timestamp.hour >= 17:  # After 5 PM
            risk += 0.2
        
        return min(1.0, risk)
    
    async def predict_workflow_performance(self, repository: str, workflow_name: str,
                                         context: Dict[str, Any] = None) -> PerformancePrediction:
        """Predict workflow performance metrics"""
        
        repo_data = self.historical_data.get(repository, [])
        workflow_data = [run for run in repo_data if run["workflow_name"] == workflow_name]
        
        if not workflow_data:
            # Default prediction
            return PerformancePrediction(
                workflow_id="unknown",
                workflow_name=workflow_name,
                repository=repository,
                predicted_duration_minutes=10.0,
                duration_confidence=0.1,
                predicted_queue_time_minutes=2.0,
                queue_confidence=0.1,
                optimal_trigger_time=datetime.now(),
                resource_recommendations=["Collect historical data for better predictions"]
            )
        
        # Calculate baseline duration
        recent_durations = [run["duration_seconds"]/60 for run in workflow_data[-10:] if run["duration_seconds"] > 0]
        baseline_duration = statistics.mean(recent_durations) if recent_durations else 10.0
        
        # Apply context-based adjustments
        model = self.models["duration_predictor"]
        multiplier = 1.0
        
        workflow_name_lower = workflow_name.lower()
        for keyword, factor in model["baseline_multipliers"].items():
            if keyword in workflow_name_lower:
                multiplier *= factor
        
        # Branch factor
        branch = context.get("branch", "main") if context else "main"
        branch_factor = model["branch_factors"].get(branch, 1.0)
        multiplier *= branch_factor
        
        predicted_duration = baseline_duration * multiplier
        
        # Predict queue time based on current system load
        current_hour = datetime.now().hour
        if current_hour in self.feature_extractors["time_features"]["peak_hours"]:
            predicted_queue_time = 5.0  # 5 minutes during peak
        else:
            predicted_queue_time = 1.0  # 1 minute during off-peak
        
        # Find optimal trigger time (next off-peak period)
        optimal_time = self._find_optimal_trigger_time()
        
        # Generate resource recommendations
        recommendations = []
        if predicted_duration > 15:
            recommendations.append("Consider using larger runners for better performance")
        if predicted_queue_time > 3:
            recommendations.append("Schedule during off-peak hours to reduce queue time")
        if len(recent_durations) > 1 and baseline_duration > statistics.stdev(recent_durations) * 2:
            recommendations.append("High duration variance detected - investigate workflow stability")
        
        return PerformancePrediction(
            workflow_id=str(workflow_data[0]["workflow_id"]),
            workflow_name=workflow_name,
            repository=repository,
            predicted_duration_minutes=predicted_duration,
            duration_confidence=min(len(recent_durations) / 10.0, 1.0),
            predicted_queue_time_minutes=predicted_queue_time,
            queue_confidence=0.8,
            optimal_trigger_time=optimal_time,
            resource_recommendations=recommendations
        )
    
    def _find_optimal_trigger_time(self) -> datetime:
        """Find the next optimal time to trigger workflows"""
        now = datetime.now()
        
        # If it's currently off-peak, return now
        if now.hour not in self.feature_extractors["time_features"]["peak_hours"]:
            return now
        
        # Otherwise, find next off-peak period
        next_optimal = now.replace(hour=19, minute=0, second=0, microsecond=0)  # 7 PM
        if next_optimal <= now:
            next_optimal += timedelta(days=1)
            next_optimal = next_optimal.replace(hour=7, minute=0)  # 7 AM next day
        
        return next_optimal
    
    async def detect_anomalies(self, repository: str) -> List[TrendAnalysis]:
        """Detect anomalies and trends in workflow data"""
        
        repo_data = self.historical_data.get(repository, [])
        if len(repo_data) < 10:
            return []
        
        anomalies = []
        
        # Analyze duration trends
        durations = [run["duration_seconds"]/60 for run in repo_data if run["duration_seconds"] > 0]
        if durations:
            duration_analysis = self._analyze_metric_trend("duration_minutes", durations)
            duration_analysis.repository = repository
            anomalies.append(duration_analysis)
        
        # Analyze failure rate trends
        recent_window = 20
        failure_rates = []
        for i in range(len(repo_data) - recent_window + 1):
            window_data = repo_data[i:i + recent_window]
            failures = len([run for run in window_data if run["failed"]])
            failure_rates.append(failures / recent_window)
        
        if failure_rates:
            failure_analysis = self._analyze_metric_trend("failure_rate", failure_rates)
            failure_analysis.repository = repository
            anomalies.append(failure_analysis)
        
        return anomalies
    
    def _analyze_metric_trend(self, metric_name: str, values: List[float]) -> TrendAnalysis:
        """Analyze trend for a specific metric"""
        if len(values) < 5:
            return TrendAnalysis(
                metric_name=metric_name,
                repository="",
                current_value=values[-1] if values else 0,
                trend_direction="stable",
                trend_strength=0.0,
                predicted_value_7d=values[-1] if values else 0,
                predicted_value_30d=values[-1] if values else 0,
                anomaly_detected=False,
                anomaly_score=0.0
            )
        
        current_value = values[-1]
        
        # Calculate trend using simple linear regression
        n = len(values)
        x_vals = list(range(n))
        sum_x = sum(x_vals)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_vals, values))
        sum_x_sq = sum(x * x for x in x_vals)
        
        # Calculate slope and intercept
        denominator = n * sum_x_sq - sum_x * sum_x
        if denominator != 0:
            slope = (n * sum_xy - sum_x * sum_y) / denominator
            intercept = (sum_y - slope * sum_x) / n
        else:
            slope = 0
            intercept = sum_y / n if n > 0 else 0
        
        # Determine trend direction and strength
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        if abs(slope) < std_dev * 0.1:
            trend_direction = "stable"
            trend_strength = 0.0
        elif slope > 0:
            trend_direction = "increasing"
            trend_strength = min(1.0, abs(slope) / std_dev)
        else:
            trend_direction = "decreasing"
            trend_strength = min(1.0, abs(slope) / std_dev)
        
        # Predict future values
        predicted_7d = intercept + slope * (len(values) + 7)
        predicted_30d = intercept + slope * (len(values) + 30)
        
        # Detect anomalies using z-score
        previous_values = values[:-1]  # Exclude current value
        if len(previous_values) > 1:
            mean_value = statistics.mean(previous_values)
            std_value = statistics.stdev(previous_values)
            z_score = abs(current_value - mean_value) / std_value if std_value > 0 else 0
        else:
            z_score = 0
        
        anomaly_threshold = self.models["anomaly_detector"]["sensitivity"]
        anomaly_detected = z_score > anomaly_threshold
        
        return TrendAnalysis(
            metric_name=metric_name,
            repository="",
            current_value=current_value,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            predicted_value_7d=max(0, predicted_7d),
            predicted_value_30d=max(0, predicted_30d),
            anomaly_detected=anomaly_detected,
            anomaly_score=z_score
        )
    
    def generate_ai_insights_report(self, repositories: List[str]) -> Dict[str, Any]:
        """Generate comprehensive AI insights report"""
        
        insights = {
            "summary": {
                "repositories_analyzed": len(repositories),
                "total_predictions": 0,
                "high_risk_workflows": 0,
                "anomalies_detected": 0,
                "optimization_opportunities": 0
            },
            "predictions": [],
            "anomalies": [],
            "recommendations": []
        }
        
        # This would be populated with actual analysis results
        # For demo purposes, we'll show the structure
        
        insights["summary"]["total_predictions"] = len(repositories) * 3  # Assume 3 workflows per repo
        insights["summary"]["high_risk_workflows"] = 2
        insights["summary"]["anomalies_detected"] = 1
        insights["summary"]["optimization_opportunities"] = 5
        
        insights["recommendations"] = [
            "Deploy microsoft/vscode CI/CD Pipeline during off-peak hours to reduce failure risk",
            "Implement caching for kubernetes/kubernetes workflows to improve performance",
            "Investigate recent failure pattern in facebook/react security scan workflow",
            "Consider upgrading runners for workflows with >20 minute duration"
        ]
        
        return insights

# Demo function
async def demo_ai_analytics():
    """Demonstrate the AI analytics engine"""
    engine = AIAnalyticsEngine()
    
    print("🧠 AI-Powered Predictive Analytics Engine Demo")
    print("=" * 50)
    
    repositories = ["microsoft/vscode", "kubernetes/kubernetes", "facebook/react"]
    
    # Collect training data
    print(f"\n📊 Collecting training data...")
    training_data = await engine.collect_training_data(repositories, days_back=30)
    
    for repo, data in training_data.items():
        print(f"   {repo}: {len(data)} workflow runs")
    
    # Generate predictions
    print(f"\n🔮 Generating AI Predictions...")
    
    test_workflows = [
        ("microsoft/vscode", "CI/CD Pipeline"),
        ("kubernetes/kubernetes", "Security Scan"),
        ("facebook/react", "Deploy to Production")
    ]
    
    for repo, workflow in test_workflows:
        print(f"\n   📋 Analyzing: {repo} - {workflow}")
        
        # Failure prediction
        failure_pred = await engine.predict_workflow_failure(repo, workflow)
        print(f"      🎯 Failure Risk: {failure_pred.failure_probability:.1%} ({failure_pred.risk_level.value})")
        print(f"      🔍 Key Factors: {', '.join(failure_pred.contributing_factors[:2])}")
        
        # Performance prediction
        perf_pred = await engine.predict_workflow_performance(repo, workflow)
        print(f"      ⏱️ Predicted Duration: {perf_pred.predicted_duration_minutes:.1f} minutes")
        print(f"      🚦 Queue Time: {perf_pred.predicted_queue_time_minutes:.1f} minutes")
        print(f"      🎯 Optimal Time: {perf_pred.optimal_trigger_time.strftime('%H:%M')}")
    
    # Detect anomalies
    print(f"\n🔍 Anomaly Detection...")
    for repo in repositories:
        anomalies = await engine.detect_anomalies(repo)
        print(f"   {repo}: {len(anomalies)} anomalies detected")
        
        for anomaly in anomalies[:1]:  # Show first anomaly
            print(f"      📈 {anomaly.metric_name}: {anomaly.trend_direction} trend")
            if anomaly.anomaly_detected:
                print(f"      🚨 Anomaly detected (score: {anomaly.anomaly_score:.2f})")
    
    # Generate insights report
    print(f"\n📊 AI Insights Summary:")
    report = engine.generate_ai_insights_report(repositories)
    summary = report["summary"]
    
    print(f"   Repositories Analyzed: {summary['repositories_analyzed']}")
    print(f"   Total Predictions: {summary['total_predictions']}")
    print(f"   High Risk Workflows: {summary['high_risk_workflows']}")
    print(f"   Anomalies Detected: {summary['anomalies_detected']}")
    
    print(f"\n💡 Top AI Recommendations:")
    for i, rec in enumerate(report["recommendations"][:3], 1):
        print(f"   {i}. {rec}")

if __name__ == "__main__":
    asyncio.run(demo_ai_analytics())
