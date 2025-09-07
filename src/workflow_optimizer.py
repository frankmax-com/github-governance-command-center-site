"""
GitHub Actions Workflow Optimization Engine
AI-powered workflow analysis and optimization recommendations
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import aiohttp
import asyncio

class OptimizationType(Enum):
    CACHING = "caching"
    PARALLELIZATION = "parallelization"
    RESOURCE_SIZING = "resource_sizing"
    DEPENDENCY_OPTIMIZATION = "dependency_optimization"
    WORKFLOW_STRUCTURE = "workflow_structure"

class OptimizationPriority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class OptimizationRecommendation:
    type: OptimizationType
    priority: OptimizationPriority
    title: str
    description: str
    estimated_savings_percent: float
    estimated_time_savings_minutes: float
    implementation_effort: str  # "low", "medium", "high"
    code_changes_required: bool
    yaml_snippet: Optional[str] = None

@dataclass
class WorkflowAnalysis:
    workflow_id: str
    workflow_name: str
    repository: str
    current_duration_minutes: float
    success_rate: float
    failure_patterns: List[str]
    bottlenecks: List[str]
    recommendations: List[OptimizationRecommendation]
    potential_total_savings: float

class WorkflowOptimizer:
    """AI-powered GitHub Actions workflow optimization engine"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.optimization_patterns = self._load_optimization_patterns()
    
    def _load_optimization_patterns(self) -> Dict[str, Any]:
        """Load optimization patterns and rules"""
        return {
            "caching_opportunities": {
                "node_modules": {
                    "pattern": r"npm install|yarn install",
                    "cache_key": "node-modules-${{ hashFiles('**/package-lock.json') }}",
                    "paths": ["node_modules"],
                    "savings_percent": 40
                },
                "pip_cache": {
                    "pattern": r"pip install",
                    "cache_key": "pip-${{ hashFiles('**/requirements*.txt') }}",
                    "paths": ["~/.cache/pip"],
                    "savings_percent": 30
                },
                "maven_cache": {
                    "pattern": r"mvn.*install|mvn.*compile",
                    "cache_key": "maven-${{ hashFiles('**/pom.xml') }}",
                    "paths": ["~/.m2/repository"],
                    "savings_percent": 35
                },
                "gradle_cache": {
                    "pattern": r"gradle.*build|./gradlew",
                    "cache_key": "gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}",
                    "paths": ["~/.gradle/caches", "~/.gradle/wrapper"],
                    "savings_percent": 35
                }
            },
            "parallelization_opportunities": {
                "test_splitting": {
                    "pattern": r"(test|spec)",
                    "suggested_strategy": "matrix",
                    "savings_percent": 50
                },
                "multi_environment": {
                    "pattern": r"(ubuntu|windows|macos)",
                    "suggested_strategy": "matrix",
                    "savings_percent": 30
                }
            },
            "common_bottlenecks": {
                "slow_dependency_install": {
                    "indicators": ["npm install", "pip install", "yarn install"],
                    "solutions": ["caching", "lock file optimization"]
                },
                "large_test_suites": {
                    "indicators": ["test", "pytest", "jest"],
                    "solutions": ["test parallelization", "test splitting"]
                },
                "docker_builds": {
                    "indicators": ["docker build", "docker push"],
                    "solutions": ["multi-stage builds", "layer caching"]
                }
            }
        }
    
    async def analyze_repository_workflows(self, owner: str, repo: str) -> List[WorkflowAnalysis]:
        """Analyze all workflows in a repository and provide optimization recommendations"""
        print(f"🔍 Analyzing workflows for {owner}/{repo}")
        
        analyses = []
        
        try:
            # Get workflow list
            async with aiohttp.ClientSession() as session:
                workflows = await self._get_workflows(session, owner, repo)
                analytics = await self._get_workflow_analytics(session, owner, repo)
                
                for workflow in workflows.get("workflows", []):
                    analysis = await self._analyze_single_workflow(session, owner, repo, workflow, analytics)
                    if analysis:
                        analyses.append(analysis)
                        
        except Exception as e:
            print(f"❌ Analysis failed for {owner}/{repo}: {e}")
        
        return analyses
    
    async def _get_workflows(self, session: aiohttp.ClientSession, owner: str, repo: str) -> Dict[str, Any]:
        """Get workflow list from API"""
        async with session.get(f"{self.base_url}/api/v1/actions/{owner}/{repo}/workflows") as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get workflows: {response.status}")
    
    async def _get_workflow_analytics(self, session: aiohttp.ClientSession, owner: str, repo: str) -> Dict[str, Any]:
        """Get workflow analytics from API"""
        async with session.get(f"{self.base_url}/api/v1/analytics/actions/{owner}/{repo}/workflow-metrics") as response:
            if response.status == 200:
                return await response.json()
            else:
                return {}  # Analytics might not be available
    
    async def _analyze_single_workflow(self, session: aiohttp.ClientSession, owner: str, repo: str, 
                                     workflow: Dict[str, Any], analytics: Dict[str, Any]) -> Optional[WorkflowAnalysis]:
        """Analyze a single workflow and generate recommendations"""
        workflow_id = str(workflow["id"])
        workflow_name = workflow["name"]
        
        print(f"   📋 Analyzing: {workflow_name}")
        
        # Get workflow analytics data
        workflow_analytics = self._find_workflow_analytics(workflow_id, analytics)
        
        # Get recent workflow runs for pattern analysis
        runs = await self._get_recent_runs(session, owner, repo, workflow_id)
        
        # Simulate workflow file analysis (in real implementation, would fetch actual .github/workflows/*.yml)
        workflow_content = self._simulate_workflow_content(workflow_name)
        
        # Analyze workflow for optimization opportunities
        recommendations = self._generate_recommendations(workflow_content, workflow_analytics, runs)
        
        # Identify bottlenecks and failure patterns
        bottlenecks = self._identify_bottlenecks(workflow_content, runs)
        failure_patterns = self._analyze_failure_patterns(runs)
        
        # Calculate potential savings
        total_savings = sum(rec.estimated_savings_percent for rec in recommendations)
        
        return WorkflowAnalysis(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            repository=f"{owner}/{repo}",
            current_duration_minutes=workflow_analytics.get("avg_duration_minutes", 10.0),
            success_rate=workflow_analytics.get("success_rate", 90.0),
            failure_patterns=failure_patterns,
            bottlenecks=bottlenecks,
            recommendations=recommendations,
            potential_total_savings=min(total_savings, 70)  # Cap at 70% max savings
        )
    
    def _find_workflow_analytics(self, workflow_id: str, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Find analytics data for specific workflow"""
        if "workflows" in analytics:
            for wf in analytics["workflows"]:
                if str(wf.get("workflow_id")) == workflow_id:
                    # Convert duration string to minutes
                    duration_str = wf.get("average_duration", "0m")
                    avg_minutes = self._parse_duration_to_minutes(duration_str)
                    wf["avg_duration_minutes"] = avg_minutes
                    return wf
        
        # Default values if not found
        return {
            "success_rate": 85.0,
            "avg_duration_minutes": 8.5,
            "runs": 20
        }
    
    def _parse_duration_to_minutes(self, duration_str: str) -> float:
        """Parse duration string like '12m 30s' to minutes"""
        if not duration_str:
            return 0.0
        
        minutes = 0.0
        # Extract minutes
        minute_match = re.search(r'(\d+)m', duration_str)
        if minute_match:
            minutes += float(minute_match.group(1))
        
        # Extract seconds and convert to minutes
        second_match = re.search(r'(\d+)s', duration_str)
        if second_match:
            minutes += float(second_match.group(1)) / 60
        
        return minutes
    
    async def _get_recent_runs(self, session: aiohttp.ClientSession, owner: str, repo: str, workflow_id: str) -> List[Dict[str, Any]]:
        """Get recent runs for specific workflow"""
        try:
            async with session.get(f"{self.base_url}/api/v1/actions/{owner}/{repo}/runs") as response:
                if response.status == 200:
                    data = await response.json()
                    # Filter runs for this specific workflow
                    return [run for run in data.get("workflow_runs", []) if str(run.get("workflow_id")) == workflow_id][:10]
        except:
            pass
        return []
    
    def _simulate_workflow_content(self, workflow_name: str) -> str:
        """Simulate workflow YAML content based on name (in real implementation, would fetch actual file)"""
        templates = {
            "CI/CD Pipeline": """
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test
      - name: Build
        run: npm run build
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: echo "Deploying..."
            """,
            "Security Scan": """
name: Security Scan
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install security tools
        run: pip install bandit safety
      - name: Run security scan
        run: bandit -r .
            """,
            "Deploy to Production": """
name: Deploy to Production
on:
  workflow_dispatch:
    inputs:
      environment:
        required: true
        default: 'production'
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy application
        run: echo "Deploying to ${{ github.event.inputs.environment }}"
            """
        }
        
        return templates.get(workflow_name, templates["CI/CD Pipeline"])
    
    def _generate_recommendations(self, workflow_content: str, analytics: Dict[str, Any], runs: List[Dict[str, Any]]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on workflow analysis"""
        recommendations = []
        
        # Check for caching opportunities
        for cache_type, config in self.optimization_patterns["caching_opportunities"].items():
            if re.search(config["pattern"], workflow_content, re.IGNORECASE):
                recommendations.append(OptimizationRecommendation(
                    type=OptimizationType.CACHING,
                    priority=OptimizationPriority.HIGH,
                    title=f"Implement {cache_type.replace('_', ' ').title()} Caching",
                    description=f"Add caching for {cache_type} to reduce installation time",
                    estimated_savings_percent=config["savings_percent"],
                    estimated_time_savings_minutes=analytics.get("avg_duration_minutes", 10) * (config["savings_percent"] / 100),
                    implementation_effort="low",
                    code_changes_required=True,
                    yaml_snippet=self._generate_cache_yaml(cache_type, config)
                ))
        
        # Check for parallelization opportunities
        if "test" in workflow_content.lower() and "matrix" not in workflow_content.lower():
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.PARALLELIZATION,
                priority=OptimizationPriority.MEDIUM,
                title="Parallelize Test Execution",
                description="Use matrix strategy to run tests in parallel across multiple environments",
                estimated_savings_percent=40,
                estimated_time_savings_minutes=analytics.get("avg_duration_minutes", 10) * 0.4,
                implementation_effort="medium",
                code_changes_required=True,
                yaml_snippet=self._generate_matrix_yaml()
            ))
        
        # Resource sizing recommendations
        avg_duration = analytics.get("avg_duration_minutes", 10)
        if avg_duration > 15:
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.RESOURCE_SIZING,
                priority=OptimizationPriority.MEDIUM,
                title="Use Larger GitHub Runners",
                description="Switch to 4-core runners for CPU-intensive workflows",
                estimated_savings_percent=25,
                estimated_time_savings_minutes=avg_duration * 0.25,
                implementation_effort="low",
                code_changes_required=True,
                yaml_snippet="runs-on: ubuntu-latest-4-cores"
            ))
        
        # Dependency optimization
        if "npm install" in workflow_content and "package-lock.json" not in workflow_content:
            recommendations.append(OptimizationRecommendation(
                type=OptimizationType.DEPENDENCY_OPTIMIZATION,
                priority=OptimizationPriority.HIGH,
                title="Optimize Dependency Installation",
                description="Use npm ci instead of npm install for faster, reliable builds",
                estimated_savings_percent=20,
                estimated_time_savings_minutes=2.0,
                implementation_effort="low",
                code_changes_required=True,
                yaml_snippet="run: npm ci"
            ))
        
        return recommendations
    
    def _generate_cache_yaml(self, cache_type: str, config: Dict[str, Any]) -> str:
        """Generate YAML snippet for caching implementation"""
        return f"""
- name: Cache {cache_type.replace('_', ' ').title()}
  uses: actions/cache@v3
  with:
    path: {' '.join(config['paths'])}
    key: {config['cache_key']}
    restore-keys: |
      {cache_type}-
        """.strip()
    
    def _generate_matrix_yaml(self) -> str:
        """Generate YAML snippet for matrix strategy"""
        return """
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    node-version: [16, 18, 20]
runs-on: ${{ matrix.os }}
        """.strip()
    
    def _identify_bottlenecks(self, workflow_content: str, runs: List[Dict[str, Any]]) -> List[str]:
        """Identify workflow bottlenecks"""
        bottlenecks = []
        
        for bottleneck_type, config in self.optimization_patterns["common_bottlenecks"].items():
            for indicator in config["indicators"]:
                if indicator.lower() in workflow_content.lower():
                    bottlenecks.append(f"{bottleneck_type.replace('_', ' ').title()}: {', '.join(config['solutions'])}")
        
        return bottlenecks
    
    def _analyze_failure_patterns(self, runs: List[Dict[str, Any]]) -> List[str]:
        """Analyze failure patterns from recent runs"""
        failure_patterns = []
        
        failed_runs = [run for run in runs if run.get("conclusion") == "failure"]
        if len(failed_runs) > len(runs) * 0.2:  # More than 20% failure rate
            failure_patterns.append("High failure rate detected - investigate flaky tests")
        
        # Look for patterns in failure timing
        failure_events = [run.get("event") for run in failed_runs]
        if failure_events.count("push") > failure_events.count("pull_request"):
            failure_patterns.append("More failures on push than PR - consider stricter PR checks")
        
        return failure_patterns
    
    def generate_optimization_report(self, analyses: List[WorkflowAnalysis]) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        total_workflows = len(analyses)
        total_potential_savings = sum(analysis.potential_total_savings for analysis in analyses)
        avg_potential_savings = total_potential_savings / total_workflows if total_workflows > 0 else 0
        
        # Group recommendations by type
        recommendation_summary = {}
        for analysis in analyses:
            for rec in analysis.recommendations:
                rec_type = rec.type.value
                if rec_type not in recommendation_summary:
                    recommendation_summary[rec_type] = {
                        "count": 0,
                        "total_savings": 0,
                        "high_priority_count": 0
                    }
                recommendation_summary[rec_type]["count"] += 1
                recommendation_summary[rec_type]["total_savings"] += rec.estimated_savings_percent
                if rec.priority == OptimizationPriority.HIGH:
                    recommendation_summary[rec_type]["high_priority_count"] += 1
        
        return {
            "summary": {
                "total_workflows_analyzed": total_workflows,
                "average_potential_savings_percent": round(avg_potential_savings, 1),
                "total_recommendations": sum(len(a.recommendations) for a in analyses),
                "high_priority_recommendations": sum(
                    len([r for r in a.recommendations if r.priority == OptimizationPriority.HIGH]) 
                    for a in analyses
                )
            },
            "recommendation_breakdown": recommendation_summary,
            "workflow_analyses": [
                {
                    "workflow_name": a.workflow_name,
                    "repository": a.repository,
                    "current_duration_minutes": a.current_duration_minutes,
                    "success_rate": a.success_rate,
                    "potential_savings_percent": a.potential_total_savings,
                    "recommendation_count": len(a.recommendations),
                    "bottlenecks": a.bottlenecks,
                    "failure_patterns": a.failure_patterns
                }
                for a in analyses
            ],
            "generated_at": datetime.now().isoformat()
        }

# Demo function
async def demo_workflow_optimization():
    """Demonstrate the workflow optimization engine"""
    optimizer = WorkflowOptimizer()
    
    print("🤖 GitHub Actions Workflow Optimization Engine Demo")
    print("=" * 55)
    
    # Analyze repositories
    repositories = [
        ("microsoft", "vscode"),
        ("facebook", "react"),
        ("kubernetes", "kubernetes")
    ]
    
    all_analyses = []
    
    for owner, repo in repositories:
        print(f"\n🔍 Analyzing {owner}/{repo}")
        print("-" * 40)
        
        try:
            analyses = await optimizer.analyze_repository_workflows(owner, repo)
            all_analyses.extend(analyses)
            
            for analysis in analyses:
                print(f"\n📋 Workflow: {analysis.workflow_name}")
                print(f"   Current Duration: {analysis.current_duration_minutes:.1f} minutes")
                print(f"   Success Rate: {analysis.success_rate:.1f}%")
                print(f"   Potential Savings: {analysis.potential_total_savings:.1f}%")
                print(f"   Recommendations: {len(analysis.recommendations)}")
                
                for rec in analysis.recommendations[:2]:  # Show top 2 recommendations
                    print(f"   🔧 {rec.title}")
                    print(f"      Priority: {rec.priority.value} | Savings: {rec.estimated_savings_percent}%")
                    print(f"      Effort: {rec.implementation_effort} | Time Saved: {rec.estimated_time_savings_minutes:.1f}m")
                
                if analysis.bottlenecks:
                    print(f"   🚫 Bottlenecks: {', '.join(analysis.bottlenecks[:2])}")
                
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
    
    # Generate overall report
    if all_analyses:
        print(f"\n📊 OPTIMIZATION REPORT")
        print("=" * 30)
        
        report = optimizer.generate_optimization_report(all_analyses)
        summary = report["summary"]
        
        print(f"Workflows Analyzed: {summary['total_workflows_analyzed']}")
        print(f"Average Potential Savings: {summary['average_potential_savings_percent']}%")
        print(f"Total Recommendations: {summary['total_recommendations']}")
        print(f"High Priority Items: {summary['high_priority_recommendations']}")
        
        print(f"\n📈 Top Optimization Types:")
        for opt_type, data in report["recommendation_breakdown"].items():
            print(f"  {opt_type.replace('_', ' ').title()}: {data['count']} opportunities, {data['total_savings']:.0f}% total savings")

if __name__ == "__main__":
    asyncio.run(demo_workflow_optimization())
