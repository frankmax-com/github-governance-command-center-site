"""
Shared Data Models for GitHub Governance Factory Microservices
Implementation of models documented in MICROSERVICES-ARCHITECTURE.md
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import json


class TaskType(Enum):
    """AI task types for provider routing"""
    PLANNING = "planning"
    ANALYSIS = "analysis"
    WRITING = "writing"
    THINKING = "thinking"
    RESEARCH = "research"
    REVIEW = "review"


class IssueType(Enum):
    """GitHub issue types"""
    EPIC = "epic"
    FEATURE = "feature"
    TASK = "task"
    BUG = "bug"
    STORY = "story"


class ServiceStatus(Enum):
    """Microservice health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class AIProviderConfig:
    """AI Provider configuration"""
    provider_name: str
    model_name: str
    task_types: List[TaskType]
    confidence_threshold: float = 0.8
    max_retries: int = 3
    timeout_seconds: int = 30
    api_endpoint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "model_name": self.model_name,
            "task_types": [t.value for t in self.task_types],
            "confidence_threshold": self.confidence_threshold,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "api_endpoint": self.api_endpoint
        }


@dataclass
class ProjectSpecification:
    """Project specification for governance processing"""
    id: str
    name: str
    description: str
    requirements: List[str]
    constraints: List[str]
    stakeholders: List[str]
    deadline: Optional[datetime] = None
    priority: str = "medium"
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "requirements": self.requirements,
            "constraints": self.constraints,
            "stakeholders": self.stakeholders,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "priority": self.priority,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class GovernanceIssue:
    """GitHub issue with governance metadata"""
    id: str
    title: str
    description: str
    issue_type: IssueType
    labels: List[str]
    assignees: List[str]
    epic_id: Optional[str] = None
    feature_id: Optional[str] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    ai_metadata: Dict[str, Any] = field(default_factory=dict)
    github_issue_number: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "issue_type": self.issue_type.value,
            "labels": self.labels,
            "assignees": self.assignees,
            "epic_id": self.epic_id,
            "feature_id": self.feature_id,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "ai_metadata": self.ai_metadata,
            "github_issue_number": self.github_issue_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class AIAnalysisResult:
    """Result from AI Provider Factory analysis"""
    task_id: str
    provider_used: str
    model_used: str
    task_type: TaskType
    confidence_score: float
    result_data: Dict[str, Any]
    processing_time_ms: int
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "provider_used": self.provider_used,
            "model_used": self.model_used,
            "task_type": self.task_type.value,
            "confidence_score": self.confidence_score,
            "result_data": self.result_data,
            "processing_time_ms": self.processing_time_ms,
            "tokens_used": self.tokens_used,
            "cost_estimate": self.cost_estimate,
            "created_at": self.created_at.isoformat()
        }


@dataclass
class ServiceHealth:
    """Microservice health status"""
    service_name: str
    status: ServiceStatus
    version: str
    uptime_seconds: int
    last_check: datetime = field(default_factory=datetime.utcnow)
    dependencies: Dict[str, ServiceStatus] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "status": self.status.value,
            "version": self.version,
            "uptime_seconds": self.uptime_seconds,
            "last_check": self.last_check.isoformat(),
            "dependencies": {k: v.value for k, v in self.dependencies.items()},
            "metrics": self.metrics
        }


@dataclass
class EventMessage:
    """Event-driven messaging between services"""
    event_id: str
    event_type: str
    source_service: str
    target_service: str
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source_service": self.source_service,
            "target_service": self.target_service,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "retry_count": self.retry_count
        }


@dataclass
class AgentServiceMetadata:
    """Agent service assignment metadata"""
    agent_type: str
    agent_id: str
    capabilities: List[str]
    workload_score: float
    performance_metrics: Dict[str, float]
    availability_status: str
    last_assignment: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_type": self.agent_type,
            "agent_id": self.agent_id,
            "capabilities": self.capabilities,
            "workload_score": self.workload_score,
            "performance_metrics": self.performance_metrics,
            "availability_status": self.availability_status,
            "last_assignment": self.last_assignment.isoformat() if self.last_assignment else None
        }
