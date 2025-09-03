"""
AI Provider Factory Client for GitHub Governance Factory
Implementation of AI integration patterns documented in MICROSERVICES-ARCHITECTURE.md
"""

import os
import aiohttp
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from .models import TaskType, AIAnalysisResult, AIProviderConfig

logger = logging.getLogger(__name__)


class AIProviderFactoryClient:
    """Client for AI Provider Factory with 17+ providers and 100+ models"""
    
    def __init__(self):
        self.base_url = os.getenv('AI_PROVIDER_FACTORY_URL', 'http://localhost:8001')
        self.api_key = os.getenv('AI_PROVIDER_FACTORY_API_KEY')
        self.timeout = aiohttp.ClientTimeout(total=120)  # 2 minutes for complex AI tasks
        
        # AI Provider configurations based on documented architecture
        self.provider_configs = {
            TaskType.PLANNING: [
                AIProviderConfig("vscode_lm", "gpt-4o", [TaskType.PLANNING], 0.9),
                AIProviderConfig("claude", "sonnet-3.5", [TaskType.PLANNING], 0.85),
                AIProviderConfig("openai", "gpt-4", [TaskType.PLANNING], 0.8)
            ],
            TaskType.ANALYSIS: [
                AIProviderConfig("openai", "gpt-4", [TaskType.ANALYSIS], 0.9),
                AIProviderConfig("claude", "sonnet-3.5", [TaskType.ANALYSIS], 0.85),
                AIProviderConfig("google", "gemini-pro", [TaskType.ANALYSIS], 0.8)
            ],
            TaskType.WRITING: [
                AIProviderConfig("claude", "sonnet-3.5", [TaskType.WRITING], 0.9),
                AIProviderConfig("openai", "gpt-4", [TaskType.WRITING], 0.85),
                AIProviderConfig("anthropic", "claude-3", [TaskType.WRITING], 0.8)
            ],
            TaskType.THINKING: [
                AIProviderConfig("openai", "gpt-4", [TaskType.THINKING], 0.9),
                AIProviderConfig("claude", "sonnet-3.5", [TaskType.THINKING], 0.85),
                AIProviderConfig("vscode_lm", "gpt-4o", [TaskType.THINKING], 0.8)
            ],
            TaskType.RESEARCH: [
                AIProviderConfig("perplexity", "pro", [TaskType.RESEARCH], 0.9),
                AIProviderConfig("openai", "gpt-4", [TaskType.RESEARCH], 0.85),
                AIProviderConfig("google", "gemini-pro", [TaskType.RESEARCH], 0.8)
            ],
            TaskType.REVIEW: [
                AIProviderConfig("github_copilot", "chat", [TaskType.REVIEW], 0.9),
                AIProviderConfig("openai", "gpt-4", [TaskType.REVIEW], 0.85),
                AIProviderConfig("claude", "sonnet-3.5", [TaskType.REVIEW], 0.8)
            ]
        }
    
    async def generate_epic_breakdown(self, project_spec: Dict[str, Any]) -> AIAnalysisResult:
        """
        Generate Epic → Feature → Task breakdown using AI Provider Factory
        Implementation of pseudocode from MICROSERVICES-ARCHITECTURE.md
        """
        task_data = {
            "task_type": TaskType.PLANNING.value,
            "context": {
                "project_specification": project_spec,
                "requested_format": "epic_feature_task_hierarchy",
                "governance_rules": await self._get_governance_rules(),
                "enterprise_constraints": await self._get_enterprise_constraints()
            },
            "prompt": self._build_epic_breakdown_prompt(project_spec),
            "provider_preferences": [config.to_dict() for config in self.provider_configs[TaskType.PLANNING]]
        }
        
        return await self._call_ai_provider(task_data)
    
    async def enhance_issue_description(self, issue_data: Dict[str, Any]) -> AIAnalysisResult:
        """
        Enhance issue descriptions using AI Provider Factory
        Implementation of WRITING task type routing
        """
        task_data = {
            "task_type": TaskType.WRITING.value,
            "context": {
                "basic_issue": issue_data,
                "enhancement_requirements": [
                    "detailed_technical_requirements",
                    "clear_acceptance_criteria",
                    "effort_estimation",
                    "agent_service_assignment_reasoning"
                ],
                "project_context": await self._get_project_context(issue_data.get('project_id')),
                "agent_capabilities": await self._get_agent_capabilities()
            },
            "prompt": self._build_issue_enhancement_prompt(issue_data),
            "provider_preferences": [config.to_dict() for config in self.provider_configs[TaskType.WRITING]]
        }
        
        return await self._call_ai_provider(task_data)
    
    async def analyze_compliance_requirements(self, governance_data: Dict[str, Any]) -> AIAnalysisResult:
        """
        Analyze governance compliance using AI Provider Factory
        Implementation of ANALYSIS task type routing
        """
        task_data = {
            "task_type": TaskType.ANALYSIS.value,
            "context": {
                "governance_data": governance_data,
                "compliance_frameworks": await self._get_compliance_frameworks(),
                "enterprise_policies": await self._get_enterprise_policies(),
                "audit_requirements": await self._get_audit_requirements()
            },
            "prompt": self._build_compliance_analysis_prompt(governance_data),
            "provider_preferences": [config.to_dict() for config in self.provider_configs[TaskType.ANALYSIS]]
        }
        
        return await self._call_ai_provider(task_data)
    
    async def research_best_practices(self, domain: str, specific_requirements: List[str]) -> AIAnalysisResult:
        """
        Research best practices using AI Provider Factory
        Implementation of RESEARCH task type routing
        """
        task_data = {
            "task_type": TaskType.RESEARCH.value,
            "context": {
                "domain": domain,
                "specific_requirements": specific_requirements,
                "current_practices": await self._get_current_practices(domain),
                "industry_standards": await self._get_industry_standards(domain)
            },
            "prompt": self._build_research_prompt(domain, specific_requirements),
            "provider_preferences": [config.to_dict() for config in self.provider_configs[TaskType.RESEARCH]]
        }
        
        return await self._call_ai_provider(task_data)
    
    async def review_governance_implementation(self, implementation_data: Dict[str, Any]) -> AIAnalysisResult:
        """
        Review governance implementation using AI Provider Factory
        Implementation of REVIEW task type routing
        """
        task_data = {
            "task_type": TaskType.REVIEW.value,
            "context": {
                "implementation": implementation_data,
                "governance_standards": await self._get_governance_standards(),
                "quality_metrics": await self._get_quality_metrics(),
                "compliance_checklist": await self._get_compliance_checklist()
            },
            "prompt": self._build_review_prompt(implementation_data),
            "provider_preferences": [config.to_dict() for config in self.provider_configs[TaskType.REVIEW]]
        }
        
        return await self._call_ai_provider(task_data)
    
    async def _call_ai_provider(self, task_data: Dict[str, Any]) -> AIAnalysisResult:
        """
        Call AI Provider Factory with intelligent provider selection
        Implements the documented failover and retry logic
        """
        start_time = datetime.utcnow()
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}' if self.api_key else None
        }
        headers = {k: v for k, v in headers.items() if v is not None}
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                url = f"{self.base_url}/v1/ai/analyze"
                
                async with session.post(url, json=task_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                        
                        return AIAnalysisResult(
                            task_id=result.get('task_id', 'unknown'),
                            provider_used=result.get('provider_used', 'unknown'),
                            model_used=result.get('model_used', 'unknown'),
                            task_type=TaskType(task_data['task_type']),
                            confidence_score=result.get('confidence_score', 0.0),
                            result_data=result.get('result_data', {}),
                            processing_time_ms=processing_time,
                            tokens_used=result.get('tokens_used'),
                            cost_estimate=result.get('cost_estimate')
                        )
                    else:
                        error_msg = f"AI Provider Factory error: {response.status}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                        
            except Exception as e:
                logger.error(f"Failed to call AI Provider Factory: {e}")
                
                # Return fallback result for graceful degradation
                processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                return AIAnalysisResult(
                    task_id="fallback",
                    provider_used="fallback",
                    model_used="fallback",
                    task_type=TaskType(task_data['task_type']),
                    confidence_score=0.0,
                    result_data={"error": str(e), "fallback_mode": True},
                    processing_time_ms=processing_time
                )
    
    def _build_epic_breakdown_prompt(self, project_spec: Dict[str, Any]) -> str:
        """Build prompt for epic breakdown generation"""
        return f"""
        Analyze the following project specification and generate a comprehensive Epic → Feature → Task breakdown:
        
        PROJECT SPECIFICATION:
        Name: {project_spec.get('name', 'Unknown')}
        Description: {project_spec.get('description', 'No description')}
        Requirements: {project_spec.get('requirements', [])}
        Constraints: {project_spec.get('constraints', [])}
        
        GENERATE:
        1. Strategic Epics with business value mapping
        2. Detailed Features with dependency analysis
        3. Granular Tasks with effort estimation
        4. Agent service assignment recommendations
        5. Risk assessment and mitigation strategies
        6. Compliance validation points
        
        FORMAT: JSON structure with epic → feature → task hierarchy including metadata for governance automation.
        """
    
    def _build_issue_enhancement_prompt(self, issue_data: Dict[str, Any]) -> str:
        """Build prompt for issue description enhancement"""
        return f"""
        Enhance the following GitHub issue with comprehensive details:
        
        BASIC ISSUE:
        Title: {issue_data.get('title', 'No title')}
        Description: {issue_data.get('description', 'No description')}
        Type: {issue_data.get('type', 'task')}
        
        ENHANCE WITH:
        1. Detailed technical requirements
        2. Clear acceptance criteria
        3. Effort estimation with confidence levels
        4. Agent service assignment reasoning
        5. Related issue linkage suggestions
        6. Risk factors and mitigation approaches
        
        FORMAT: Enhanced issue description ready for GitHub with governance metadata.
        """
    
    def _build_compliance_analysis_prompt(self, governance_data: Dict[str, Any]) -> str:
        """Build prompt for compliance analysis"""
        return f"""
        Analyze governance compliance for the following data:
        
        GOVERNANCE DATA:
        {json.dumps(governance_data, indent=2)}
        
        ANALYZE FOR:
        1. Regulatory compliance gaps
        2. Enterprise policy adherence
        3. Audit trail completeness
        4. Risk assessment findings
        5. Remediation recommendations
        6. Continuous monitoring setup
        
        FORMAT: Comprehensive compliance report with actionable insights.
        """
    
    def _build_research_prompt(self, domain: str, requirements: List[str]) -> str:
        """Build prompt for best practices research"""
        return f"""
        Research best practices for domain: {domain}
        
        SPECIFIC REQUIREMENTS:
        {chr(10).join(f"- {req}" for req in requirements)}
        
        RESEARCH FOCUS:
        1. Industry standards and frameworks
        2. Leading practices from top organizations
        3. Emerging trends and innovations
        4. Implementation strategies
        5. Success metrics and KPIs
        6. Common pitfalls and how to avoid them
        
        FORMAT: Comprehensive research report with actionable recommendations.
        """
    
    def _build_review_prompt(self, implementation_data: Dict[str, Any]) -> str:
        """Build prompt for governance review"""
        return f"""
        Review the following governance implementation:
        
        IMPLEMENTATION DATA:
        {json.dumps(implementation_data, indent=2)}
        
        REVIEW FOR:
        1. Governance standard compliance
        2. Quality metrics assessment
        3. Security and compliance gaps
        4. Performance optimization opportunities
        5. Scalability considerations
        6. Maintenance and monitoring setup
        
        FORMAT: Detailed review report with improvement recommendations.
        """
    
    async def _get_governance_rules(self) -> Dict[str, Any]:
        """Get current governance rules from MongoDB"""
        # Placeholder - would integrate with database
        return {"rules": "enterprise_governance_standards"}
    
    async def _get_enterprise_constraints(self) -> Dict[str, Any]:
        """Get enterprise constraints"""
        # Placeholder - would integrate with configuration
        return {"constraints": "enterprise_policy_constraints"}
    
    async def _get_project_context(self, project_id: str) -> Dict[str, Any]:
        """Get project context from databases"""
        # Placeholder - would integrate with project data
        return {"context": f"project_{project_id}_context"}
    
    async def _get_agent_capabilities(self) -> Dict[str, Any]:
        """Get agent service capabilities"""
        # Placeholder - would integrate with agent service registry
        return {"capabilities": "agent_service_capabilities"}
    
    async def _get_compliance_frameworks(self) -> List[str]:
        """Get applicable compliance frameworks"""
        return ["SOC2", "ISO27001", "GDPR", "SOX"]
    
    async def _get_enterprise_policies(self) -> Dict[str, Any]:
        """Get enterprise policies"""
        return {"policies": "enterprise_security_policies"}
    
    async def _get_audit_requirements(self) -> Dict[str, Any]:
        """Get audit requirements"""
        return {"requirements": "enterprise_audit_requirements"}
    
    async def _get_current_practices(self, domain: str) -> Dict[str, Any]:
        """Get current practices for domain"""
        return {"practices": f"current_{domain}_practices"}
    
    async def _get_industry_standards(self, domain: str) -> List[str]:
        """Get industry standards for domain"""
        return [f"{domain}_standard_1", f"{domain}_standard_2"]
    
    async def _get_governance_standards(self) -> Dict[str, Any]:
        """Get governance standards"""
        return {"standards": "governance_quality_standards"}
    
    async def _get_quality_metrics(self) -> Dict[str, Any]:
        """Get quality metrics"""
        return {"metrics": "code_quality_metrics"}
    
    async def _get_compliance_checklist(self) -> List[str]:
        """Get compliance checklist"""
        return ["security_check", "policy_check", "audit_check"]


# Global AI Provider Factory client instance
ai_client = AIProviderFactoryClient()
