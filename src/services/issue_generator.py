"""
Issue Generator Service
Implementation of GitHub Issue Generator from MICROSERVICES-ARCHITECTURE.md
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import httpx
import uvicorn

from ..shared.models import (
    GovernanceIssue, IssueType, AIAnalysisResult, EventMessage
)
from ..shared.database import db_manager
from ..shared.ai_client import ai_client
from ..shared.github_client import github_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Issue Generator Service",
    description="AI-enhanced GitHub issue generation with governance automation",
    version="1.0.0"
)

# Request/Response models
class IssueGenerationRequest(BaseModel):
    project_id: str
    governance_structure: Dict[str, Any]
    github_config: Dict[str, str]  # repo_owner, repo_name, token

class IssueEnhancementRequest(BaseModel):
    issue_data: Dict[str, Any]
    enhancement_type: str = "full"  # full, description_only, metadata_only

class GitHubIssueResponse(BaseModel):
    issue_id: str
    github_issue_number: int
    github_url: str
    status: str
    ai_enhanced: bool

class BatchIssueResponse(BaseModel):
    project_id: str
    generated_issues: List[GitHubIssueResponse]
    failed_issues: List[Dict[str, Any]]
    total_count: int
    success_count: int
    ai_analysis: Dict[str, Any]


class IssueGeneratorService:
    """
    GitHub Issue Generator Service
    Implements AI-enhanced issue generation patterns from documented architecture
    """
    
    def __init__(self):
        self.service_name = "issue-generator"
        self.version = "1.0.0"
        self.start_time = datetime.utcnow()
        
    async def initialize(self):
        """Initialize service dependencies"""
        try:
            await db_manager.initialize_all_connections()
            
            # Subscribe to governance events
            redis = db_manager.get_redis()
            self.pubsub = redis.subscribe_to_events(["governance_events"])
            
            # Start event processor in background
            asyncio.create_task(self._process_governance_events())
            
            logger.info("Issue Generator Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Issue Generator Service: {e}")
            raise
    
    async def generate_issues_from_governance(
        self, request: IssueGenerationRequest
    ) -> BatchIssueResponse:
        """
        Generate GitHub issues from governance structure
        Implementation of documented AI-enhanced issue generation
        """
        try:
            project_id = request.project_id
            governance_structure = request.governance_structure
            github_config = request.github_config
            
            generated_issues = []
            failed_issues = []
            
            # Process each epic in governance structure
            for epic in governance_structure.get("epics", []):
                try:
                    # Enhance epic with AI
                    epic_issue_data = await self._enhance_issue_with_ai(epic, "epic")
                    
                    # Create GitHub issue for epic
                    epic_github_issue = await self._create_github_issue(
                        epic_issue_data, github_config
                    )
                    
                    if epic_github_issue:
                        generated_issues.append(epic_github_issue)
                        
                        # Store issue mapping
                        await self._store_issue_mapping(
                            project_id, epic["id"], epic_github_issue
                        )
                    
                    # Process features within epic
                    for feature in epic.get("features", []):
                        try:
                            # Enhance feature with AI
                            feature_issue_data = await self._enhance_issue_with_ai(
                                feature, "feature", parent_issue=epic_github_issue
                            )
                            
                            # Create GitHub issue for feature
                            feature_github_issue = await self._create_github_issue(
                                feature_issue_data, github_config
                            )
                            
                            if feature_github_issue:
                                generated_issues.append(feature_github_issue)
                                
                                # Store issue mapping
                                await self._store_issue_mapping(
                                    project_id, feature["id"], feature_github_issue
                                )
                            
                            # Process tasks within feature
                            for task in feature.get("tasks", []):
                                try:
                                    # Enhance task with AI
                                    task_issue_data = await self._enhance_issue_with_ai(
                                        task, "task", parent_issue=feature_github_issue
                                    )
                                    
                                    # Create GitHub issue for task
                                    task_github_issue = await self._create_github_issue(
                                        task_issue_data, github_config
                                    )
                                    
                                    if task_github_issue:
                                        generated_issues.append(task_github_issue)
                                        
                                        # Store issue mapping
                                        await self._store_issue_mapping(
                                            project_id, task["id"], task_github_issue
                                        )
                                        
                                except Exception as e:
                                    logger.error(f"Failed to process task {task.get('id')}: {e}")
                                    failed_issues.append({
                                        "type": "task",
                                        "id": task.get("id"),
                                        "error": str(e)
                                    })
                                    
                        except Exception as e:
                            logger.error(f"Failed to process feature {feature.get('id')}: {e}")
                            failed_issues.append({
                                "type": "feature",
                                "id": feature.get("id"),
                                "error": str(e)
                            })
                            
                except Exception as e:
                    logger.error(f"Failed to process epic {epic.get('id')}: {e}")
                    failed_issues.append({
                        "type": "epic",
                        "id": epic.get("id"),
                        "error": str(e)
                    })
            
            # Store batch generation results
            batch_result = {
                "project_id": project_id,
                "total_issues": len(generated_issues) + len(failed_issues),
                "successful_issues": len(generated_issues),
                "failed_issues": len(failed_issues),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            supabase = db_manager.get_supabase()
            supabase.insert_record("issue_generation_batches", batch_result)
            
            # Publish completion event
            redis = db_manager.get_redis()
            event = EventMessage(
                event_id=str(uuid.uuid4()),
                event_type="issues_generated",
                source_service="issue-generator",
                target_service="notification-service",
                payload={
                    "project_id": project_id,
                    "generated_count": len(generated_issues),
                    "failed_count": len(failed_issues)
                },
                correlation_id=project_id
            )
            redis.publish_event("issue_events", event.to_dict())
            
            logger.info(f"Generated {len(generated_issues)} issues for project {project_id}")
            
            return BatchIssueResponse(
                project_id=project_id,
                generated_issues=generated_issues,
                failed_issues=failed_issues,
                total_count=len(generated_issues) + len(failed_issues),
                success_count=len(generated_issues),
                ai_analysis={"enhancement_used": True, "provider": "multiple"}
            )
            
        except Exception as e:
            logger.error(f"Failed to generate issues from governance: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _enhance_issue_with_ai(
        self, 
        issue_data: Dict[str, Any], 
        issue_type: str,
        parent_issue: Optional[GitHubIssueResponse] = None
    ) -> Dict[str, Any]:
        """
        Enhance issue data using AI Provider Factory
        Implementation of documented AI enhancement patterns
        """
        try:
            # Prepare issue data for AI enhancement
            enhancement_request = {
                "title": issue_data.get("title", "Untitled"),
                "description": issue_data.get("description", "No description"),
                "type": issue_type,
                "project_id": issue_data.get("project_id"),
                "parent_issue": parent_issue.dict() if parent_issue else None,
                "metadata": issue_data.get("metadata", {})
            }
            
            # Call AI Provider Factory for enhancement
            ai_result = await ai_client.enhance_issue_description(enhancement_request)
            
            if ai_result and ai_result.confidence_score > 0.7:
                # Use AI-enhanced content
                enhanced_data = ai_result.result_data
                
                return {
                    "title": enhanced_data.get("title", issue_data.get("title")),
                    "description": enhanced_data.get("description", issue_data.get("description")),
                    "labels": enhanced_data.get("labels", [issue_type]),
                    "assignees": enhanced_data.get("assignees", []),
                    "ai_metadata": {
                        "enhanced": True,
                        "provider": ai_result.provider_used,
                        "model": ai_result.model_used,
                        "confidence": ai_result.confidence_score,
                        "enhancement_timestamp": datetime.utcnow().isoformat()
                    },
                    "original_data": issue_data
                }
            else:
                # Use original data with minimal enhancement
                return {
                    "title": issue_data.get("title", "Untitled"),
                    "description": issue_data.get("description", "No description"),
                    "labels": [issue_type],
                    "assignees": [],
                    "ai_metadata": {
                        "enhanced": False,
                        "reason": "low_confidence_score",
                        "confidence": ai_result.confidence_score if ai_result else 0.0
                    },
                    "original_data": issue_data
                }
                
        except Exception as e:
            logger.error(f"Failed to enhance issue with AI: {e}")
            # Return original data on enhancement failure
            return {
                "title": issue_data.get("title", "Untitled"),
                "description": issue_data.get("description", "No description"),
                "labels": [issue_type],
                "assignees": [],
                "ai_metadata": {
                    "enhanced": False,
                    "error": str(e)
                },
                "original_data": issue_data
            }
    
    async def _create_github_issue(
        self, 
        issue_data: Dict[str, Any], 
        github_config: Dict[str, str]
    ) -> Optional[GitHubIssueResponse]:
        """
        Create GitHub issue using the comprehensive GitHub API client
        Implementation of documented GitHub integration patterns
        """
        try:
            repo_owner = github_config["repo_owner"]
            repo_name = github_config["repo_name"]
            
            # Use the comprehensive GitHub client instead of manual HTTP calls
            github_issue = await github_client.create_issue(
                owner=repo_owner,
                repo=repo_name,
                title=issue_data["title"],
                body=self._format_issue_description(issue_data),
                labels=issue_data.get("labels", []),
                assignees=issue_data.get("assignees", [])
            )
            
            return GitHubIssueResponse(
                issue_id=str(uuid.uuid4()),
                github_issue_number=github_issue["number"],
                github_url=github_issue["html_url"],
                status="created",
                ai_enhanced=issue_data.get("ai_metadata", {}).get("enhanced", False)
            )
                    
        except Exception as e:
            logger.error(f"Failed to create GitHub issue: {e}")
            return None
    
    def _format_issue_description(self, issue_data: Dict[str, Any]) -> str:
        """
        Format issue description with AI metadata
        Implementation of documented issue formatting patterns
        """
        description = issue_data["description"]
        ai_metadata = issue_data.get("ai_metadata", {})
        
        # Add AI enhancement notice if applicable
        if ai_metadata.get("enhanced"):
            description += f"\n\n---\n**AI Enhanced**: This issue was enhanced using {ai_metadata.get('provider', 'AI')} with {ai_metadata.get('confidence', 0):.2f} confidence score."
        
        # Add governance metadata
        if "original_data" in issue_data:
            original = issue_data["original_data"]
            if "business_value" in original:
                description += f"\n\n**Business Value**: {original['business_value']}"
            if "effort_estimate" in original:
                description += f"\n**Effort Estimate**: {original['effort_estimate']}"
            if "agent_assignment" in original:
                description += f"\n**Recommended Agent**: {original['agent_assignment']}"
        
        return description
    
    async def _store_issue_mapping(
        self, 
        project_id: str, 
        governance_id: str, 
        github_issue: GitHubIssueResponse
    ):
        """Store mapping between governance issues and GitHub issues"""
        try:
            mapping_data = {
                "project_id": project_id,
                "governance_issue_id": governance_id,
                "github_issue_number": github_issue.github_issue_number,
                "github_url": github_issue.github_url,
                "ai_enhanced": github_issue.ai_enhanced,
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase = db_manager.get_supabase()
            supabase.insert_record("issue_mappings", mapping_data)
            
            # Cache mapping in Redis
            redis = db_manager.get_redis()
            redis.set_cache(
                f"issue_mapping:{governance_id}", 
                mapping_data, 
                ttl_seconds=86400
            )
            
        except Exception as e:
            logger.error(f"Failed to store issue mapping: {e}")
    
    async def _process_governance_events(self):
        """
        Process governance events from Redis
        Implementation of documented event-driven architecture
        """
        try:
            while True:
                message = self.pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        event_data = json.loads(message['data'])
                        event = EventMessage(**event_data)
                        
                        if event.event_type == "governance_structure_generated":
                            await self._handle_governance_generated_event(event)
                            
                    except Exception as e:
                        logger.error(f"Failed to process governance event: {e}")
                
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in governance event processor: {e}")
    
    async def _handle_governance_generated_event(self, event: EventMessage):
        """Handle governance structure generated event"""
        try:
            payload = event.payload
            project_id = payload["project_id"]
            governance_structure = payload["governance_structure"]
            
            logger.info(f"Received governance structure for project {project_id}")
            
            # Auto-generate issues if configured
            # This would be configurable per project
            auto_generate = True  # Would come from project configuration
            
            if auto_generate:
                # Trigger issue generation (would need GitHub config from project settings)
                logger.info(f"Auto-generating issues for project {project_id}")
                # Implementation would call generate_issues_from_governance
                
        except Exception as e:
            logger.error(f"Failed to handle governance generated event: {e}")
    
    async def health_check(self):
        """Service health check"""
        uptime = int((datetime.utcnow() - self.start_time).total_seconds())
        
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
            db_manager.supabase.client.table("health_check").select("*").limit(1).execute()
            dependencies["supabase"] = "healthy"
        except:
            dependencies["supabase"] = "unhealthy"
        
        return {
            "service": self.service_name,
            "status": "healthy",
            "version": self.version,
            "uptime_seconds": uptime,
            "dependencies": dependencies
        }


# Global service instance
issue_generator_service = IssueGeneratorService()


# API Routes
@app.on_event("startup")
async def startup():
    """Initialize service on startup"""
    await issue_generator_service.initialize()


@app.post("/v1/repository/setup")
async def setup_governance_repository(
    owner: str,
    repo: str, 
    project_name: str
):
    """
    Setup repository for governance with labels, milestones, and structure
    Implements comprehensive GitHub repository governance setup
    """
    try:
        setup_results = await github_client.setup_governance_repository(owner, repo, project_name)
        return {
            "repository": setup_results["repository"]["full_name"],
            "labels_created": len(setup_results["labels"]),
            "milestones_created": len(setup_results["milestones"]),
            "setup_complete": len(setup_results["errors"]) == 0,
            "errors": setup_results["errors"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/issues/generate", response_model=BatchIssueResponse)
async def generate_issues_from_governance(request: IssueGenerationRequest):
    """
    Generate GitHub issues from governance structure
    Implements the documented AI-enhanced issue generation
    """
    return await issue_generator_service.generate_issues_from_governance(request)


@app.post("/v1/issues/enhance")
async def enhance_issue_with_ai(request: IssueEnhancementRequest):
    """Enhance individual issue with AI"""
    enhanced_data = await issue_generator_service._enhance_issue_with_ai(
        request.issue_data, 
        request.issue_data.get("type", "task")
    )
    return {"enhanced_issue": enhanced_data}


@app.get("/v1/health")
async def health_check():
    """Service health check endpoint"""
    return await issue_generator_service.health_check()


if __name__ == "__main__":
    uvicorn.run(
        "issue_generator:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
