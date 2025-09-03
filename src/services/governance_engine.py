"""
Governance Engine Service
Implementation of Core Governance Engine from MICROSERVICES-ARCHITECTURE.md
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

from ..shared.models import (
    ProjectSpecification, GovernanceIssue, IssueType, 
    AIAnalysisResult, EventMessage
)
from ..shared.database import db_manager
from ..shared.ai_client import ai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Governance Engine Service",
    description="Core governance automation with AI-powered Epic → Feature → Task generation",
    version="1.0.0"
)

# Request/Response models
class ProjectSpecRequest(BaseModel):
    name: str
    description: str
    requirements: List[str]
    constraints: List[str]
    stakeholders: List[str]
    priority: str = "medium"

class GovernanceResponse(BaseModel):
    project_id: str
    governance_structure: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    status: str
    created_at: str

class HealthResponse(BaseModel):
    service: str
    status: str
    version: str
    uptime_seconds: int
    dependencies: Dict[str, str]


class GovernanceEngineService:
    """
    Core Governance Engine Service
    Implements AI-powered governance automation patterns from documented architecture
    """
    
    def __init__(self):
        self.service_name = "governance-engine"
        self.version = "1.0.0"
        self.start_time = datetime.utcnow()
        
    async def initialize(self):
        """Initialize service dependencies"""
        try:
            await db_manager.initialize_all_connections()
            logger.info("Governance Engine Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Governance Engine Service: {e}")
            raise
    
    async def process_project_specification(self, spec_request: ProjectSpecRequest) -> GovernanceResponse:
        """
        Process project specification and generate governance structure
        Implementation of documented AI-powered governance generation logic
        """
        try:
            # Create project specification
            project_id = str(uuid.uuid4())
            project_spec = ProjectSpecification(
                id=project_id,
                name=spec_request.name,
                description=spec_request.description,
                requirements=spec_request.requirements,
                constraints=spec_request.constraints,
                stakeholders=spec_request.stakeholders,
                priority=spec_request.priority
            )
            
            # Store project specification in MongoDB
            mongodb = db_manager.get_mongodb()
            await mongodb.insert_document("project_specifications", project_spec.to_dict())
            
            # Call AI Provider Factory for Epic → Feature → Task breakdown
            logger.info(f"Calling AI Provider Factory for project {project_id}")
            ai_result = await ai_client.generate_epic_breakdown(project_spec.to_dict())
            
            # Parse AI-generated governance structure
            governance_structure = self._parse_ai_governance_structure(ai_result)
            
            # Create governance issues
            governance_issues = await self._create_governance_issues(
                project_id, governance_structure, ai_result
            )
            
            # Store governance structure in MongoDB
            governance_doc = {
                "project_id": project_id,
                "structure": governance_structure,
                "ai_metadata": ai_result.to_dict(),
                "issues": [issue.to_dict() for issue in governance_issues],
                "status": "generated",
                "created_at": datetime.utcnow()
            }
            await mongodb.insert_document("governance_structures", governance_doc)
            
            # Store analytics data in Supabase
            supabase = db_manager.get_supabase()
            analytics_data = {
                "project_id": project_id,
                "project_name": spec_request.name,
                "epic_count": len(governance_structure.get("epics", [])),
                "feature_count": sum(len(epic.get("features", [])) for epic in governance_structure.get("epics", [])),
                "task_count": sum(
                    len(feature.get("tasks", [])) 
                    for epic in governance_structure.get("epics", [])
                    for feature in epic.get("features", [])
                ),
                "ai_provider_used": ai_result.provider_used,
                "ai_confidence_score": ai_result.confidence_score,
                "processing_time_ms": ai_result.processing_time_ms,
                "created_at": datetime.utcnow().isoformat()
            }
            supabase.insert_record("project_analytics", analytics_data)
            
            # Cache project data in Redis
            redis = db_manager.get_redis()
            redis.set_cache(f"project:{project_id}", governance_doc, ttl_seconds=3600)
            
            # Publish event for other services
            event = EventMessage(
                event_id=str(uuid.uuid4()),
                event_type="governance_structure_generated",
                source_service="governance-engine",
                target_service="issue-generator",
                payload={
                    "project_id": project_id,
                    "governance_structure": governance_structure,
                    "ai_analysis": ai_result.to_dict()
                },
                correlation_id=project_id
            )
            redis.publish_event("governance_events", event.to_dict())
            
            logger.info(f"Generated governance structure for project {project_id}")
            
            return GovernanceResponse(
                project_id=project_id,
                governance_structure=governance_structure,
                ai_analysis=ai_result.to_dict(),
                status="completed",
                created_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Failed to process project specification: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    def _parse_ai_governance_structure(self, ai_result: AIAnalysisResult) -> Dict[str, Any]:
        """
        Parse AI-generated governance structure
        Implements the documented governance structure format
        """
        try:
            # Extract governance structure from AI result
            result_data = ai_result.result_data
            
            if "governance_structure" in result_data:
                return result_data["governance_structure"]
            
            # Fallback parsing for different AI response formats
            epics = []
            
            if "epics" in result_data:
                epics = result_data["epics"]
            elif isinstance(result_data, list):
                epics = result_data
            else:
                # Create fallback structure
                epics = [{
                    "id": str(uuid.uuid4()),
                    "title": "AI-Generated Epic",
                    "description": "Epic generated from project specification",
                    "business_value": "High",
                    "features": [{
                        "id": str(uuid.uuid4()),
                        "title": "Core Feature",
                        "description": "Feature implementation",
                        "tasks": [{
                            "id": str(uuid.uuid4()),
                            "title": "Implementation Task",
                            "description": "Task implementation",
                            "effort_estimate": "medium",
                            "agent_assignment": "dev-agent"
                        }]
                    }]
                }]
            
            return {
                "epics": epics,
                "metadata": {
                    "ai_provider": ai_result.provider_used,
                    "ai_model": ai_result.model_used,
                    "confidence_score": ai_result.confidence_score,
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to parse AI governance structure: {e}")
            # Return minimal fallback structure
            return {
                "epics": [{
                    "id": str(uuid.uuid4()),
                    "title": "Fallback Epic",
                    "description": "Generated due to parsing error",
                    "features": []
                }],
                "metadata": {
                    "fallback": True,
                    "error": str(e)
                }
            }
    
    async def _create_governance_issues(
        self, project_id: str, governance_structure: Dict[str, Any], ai_result: AIAnalysisResult
    ) -> List[GovernanceIssue]:
        """
        Create GovernanceIssue objects from structure
        Implements the documented issue hierarchy creation
        """
        issues = []
        
        try:
            for epic in governance_structure.get("epics", []):
                # Create Epic issue
                epic_issue = GovernanceIssue(
                    id=epic.get("id", str(uuid.uuid4())),
                    title=epic.get("title", "Untitled Epic"),
                    description=epic.get("description", "No description"),
                    issue_type=IssueType.EPIC,
                    labels=["epic", f"project:{project_id}"],
                    assignees=epic.get("assignees", []),
                    ai_metadata={
                        "ai_generated": True,
                        "ai_provider": ai_result.provider_used,
                        "ai_confidence": ai_result.confidence_score,
                        "business_value": epic.get("business_value", "medium")
                    }
                )
                issues.append(epic_issue)
                
                # Create Feature issues
                for feature in epic.get("features", []):
                    feature_issue = GovernanceIssue(
                        id=feature.get("id", str(uuid.uuid4())),
                        title=feature.get("title", "Untitled Feature"),
                        description=feature.get("description", "No description"),
                        issue_type=IssueType.FEATURE,
                        labels=["feature", f"project:{project_id}", f"epic:{epic_issue.id}"],
                        assignees=feature.get("assignees", []),
                        epic_id=epic_issue.id,
                        parent_id=epic_issue.id,
                        ai_metadata={
                            "ai_generated": True,
                            "ai_provider": ai_result.provider_used,
                            "priority": feature.get("priority", "medium")
                        }
                    )
                    issues.append(feature_issue)
                    epic_issue.children_ids.append(feature_issue.id)
                    
                    # Create Task issues
                    for task in feature.get("tasks", []):
                        task_issue = GovernanceIssue(
                            id=task.get("id", str(uuid.uuid4())),
                            title=task.get("title", "Untitled Task"),
                            description=task.get("description", "No description"),
                            issue_type=IssueType.TASK,
                            labels=["task", f"project:{project_id}", f"feature:{feature_issue.id}"],
                            assignees=task.get("assignees", []),
                            epic_id=epic_issue.id,
                            feature_id=feature_issue.id,
                            parent_id=feature_issue.id,
                            ai_metadata={
                                "ai_generated": True,
                                "ai_provider": ai_result.provider_used,
                                "effort_estimate": task.get("effort_estimate", "medium"),
                                "agent_assignment": task.get("agent_assignment", "unassigned")
                            }
                        )
                        issues.append(task_issue)
                        feature_issue.children_ids.append(task_issue.id)
            
            return issues
            
        except Exception as e:
            logger.error(f"Failed to create governance issues: {e}")
            return []
    
    async def get_project_governance(self, project_id: str) -> Dict[str, Any]:
        """Get governance structure for project"""
        try:
            # Try Redis cache first
            redis = db_manager.get_redis()
            cached_data = redis.get_cache(f"project:{project_id}")
            if cached_data:
                return cached_data
            
            # Fallback to MongoDB
            mongodb = db_manager.get_mongodb()
            documents = await mongodb.find_documents(
                "governance_structures", 
                {"project_id": project_id}
            )
            
            if documents:
                governance_data = documents[0]
                # Update cache
                redis.set_cache(f"project:{project_id}", governance_data, ttl_seconds=3600)
                return governance_data
            else:
                raise HTTPException(status_code=404, detail="Project not found")
                
        except Exception as e:
            logger.error(f"Failed to get project governance: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def health_check(self) -> HealthResponse:
        """Service health check"""
        uptime = int((datetime.utcnow() - self.start_time).total_seconds())
        
        # Check dependencies
        dependencies = {}
        try:
            await db_manager.mongodb.client.admin.command('ping')
            dependencies["mongodb"] = "healthy"
        except:
            dependencies["mongodb"] = "unhealthy"
        
        try:
            db_manager.redis.client.ping()
            dependencies["redis"] = "healthy"
        except:
            dependencies["redis"] = "unhealthy"
        
        try:
            # Simple Supabase check
            db_manager.supabase.client.table("health_check").select("*").limit(1).execute()
            dependencies["supabase"] = "healthy"
        except:
            dependencies["supabase"] = "unhealthy"
        
        return HealthResponse(
            service=self.service_name,
            status="healthy",
            version=self.version,
            uptime_seconds=uptime,
            dependencies=dependencies
        )


# Global service instance
governance_service = GovernanceEngineService()


# API Routes
@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await governance_service.initialize()


@app.post("/v1/governance/generate", response_model=GovernanceResponse)
async def generate_governance_structure(
    spec_request: ProjectSpecRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate governance structure from project specification
    Implements the documented AI-powered governance generation
    """
    return await governance_service.process_project_specification(spec_request)


@app.get("/v1/governance/project/{project_id}")
async def get_project_governance(project_id: str):
    """Get governance structure for specific project"""
    return await governance_service.get_project_governance(project_id)


@app.get("/v1/health", response_model=HealthResponse)
async def health_check():
    """Service health check endpoint"""
    return await governance_service.health_check()


if __name__ == "__main__":
    uvicorn.run(
        "governance_engine:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
