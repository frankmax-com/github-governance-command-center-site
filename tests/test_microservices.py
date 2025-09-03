"""
Test Suite for GitHub Governance Factory Microservices
Implementation validation for documented architecture patterns
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
import json

# Import the modules to test
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.shared.models import (
    ProjectSpecification, GovernanceIssue, IssueType, 
    AIAnalysisResult, TaskType, EventMessage
)
from src.shared.ai_client import AIProviderFactoryClient
from src.services.governance_engine import GovernanceEngineService, ProjectSpecRequest
from src.services.issue_generator import IssueGeneratorService, IssueGenerationRequest


class TestSharedModels:
    """Test shared data models"""
    
    def test_project_specification_creation(self):
        """Test ProjectSpecification model creation and serialization"""
        spec = ProjectSpecification(
            id="test-123",
            name="Test Project",
            description="Test Description",
            requirements=["req1", "req2"],
            constraints=["constraint1"],
            stakeholders=["user1", "user2"]
        )
        
        assert spec.id == "test-123"
        assert spec.name == "Test Project"
        assert len(spec.requirements) == 2
        
        # Test serialization
        spec_dict = spec.to_dict()
        assert spec_dict["id"] == "test-123"
        assert "created_at" in spec_dict
    
    def test_governance_issue_creation(self):
        """Test GovernanceIssue model creation"""
        issue = GovernanceIssue(
            id="issue-123",
            title="Test Issue",
            description="Test Description",
            issue_type=IssueType.EPIC,
            labels=["epic", "test"],
            assignees=["user1"]
        )
        
        assert issue.id == "issue-123"
        assert issue.issue_type == IssueType.EPIC
        assert "epic" in issue.labels
        
        # Test serialization
        issue_dict = issue.to_dict()
        assert issue_dict["issue_type"] == "epic"
    
    def test_ai_analysis_result_creation(self):
        """Test AIAnalysisResult model creation"""
        result = AIAnalysisResult(
            task_id="task-123",
            provider_used="openai",
            model_used="gpt-4",
            task_type=TaskType.PLANNING,
            confidence_score=0.95,
            result_data={"test": "data"},
            processing_time_ms=1500
        )
        
        assert result.task_id == "task-123"
        assert result.provider_used == "openai"
        assert result.confidence_score == 0.95
        assert result.task_type == TaskType.PLANNING


class TestAIProviderFactoryClient:
    """Test AI Provider Factory client integration"""
    
    @pytest.fixture
    def ai_client(self):
        """Create AI client instance for testing"""
        return AIProviderFactoryClient()
    
    def test_ai_client_initialization(self, ai_client):
        """Test AI client initialization"""
        assert ai_client.base_url is not None
        assert TaskType.PLANNING in ai_client.provider_configs
        assert TaskType.WRITING in ai_client.provider_configs
    
    def test_provider_configurations(self, ai_client):
        """Test AI provider configurations"""
        planning_configs = ai_client.provider_configs[TaskType.PLANNING]
        assert len(planning_configs) >= 3  # Should have primary, secondary, tertiary
        
        # Test first provider config
        primary_config = planning_configs[0]
        assert primary_config.provider_name == "vscode_lm"
        assert primary_config.model_name == "gpt-4o"
        assert primary_config.confidence_threshold > 0.8
    
    @pytest.mark.asyncio
    async def test_epic_breakdown_prompt_building(self, ai_client):
        """Test epic breakdown prompt generation"""
        project_spec = {
            "name": "Test Project",
            "description": "Test Description",
            "requirements": ["req1", "req2"],
            "constraints": ["constraint1"]
        }
        
        prompt = ai_client._build_epic_breakdown_prompt(project_spec)
        assert "Test Project" in prompt
        assert "Epic → Feature → Task" in prompt
        assert "business value mapping" in prompt
    
    @pytest.mark.asyncio
    async def test_issue_enhancement_prompt_building(self, ai_client):
        """Test issue enhancement prompt generation"""
        issue_data = {
            "title": "Test Issue",
            "description": "Test Description",
            "type": "feature"
        }
        
        prompt = ai_client._build_issue_enhancement_prompt(issue_data)
        assert "Test Issue" in prompt
        assert "acceptance criteria" in prompt
        assert "effort estimation" in prompt


class TestGovernanceEngineService:
    """Test Governance Engine Service"""
    
    @pytest.fixture
    def governance_service(self):
        """Create governance service instance for testing"""
        return GovernanceEngineService()
    
    def test_service_initialization(self, governance_service):
        """Test service initialization"""
        assert governance_service.service_name == "governance-engine"
        assert governance_service.version == "1.0.0"
        assert governance_service.start_time is not None
    
    def test_ai_governance_structure_parsing(self, governance_service):
        """Test AI governance structure parsing"""
        # Mock AI result
        ai_result = AIAnalysisResult(
            task_id="test-123",
            provider_used="openai",
            model_used="gpt-4",
            task_type=TaskType.PLANNING,
            confidence_score=0.9,
            result_data={
                "governance_structure": {
                    "epics": [{
                        "id": "epic-1",
                        "title": "Test Epic",
                        "description": "Test Epic Description",
                        "business_value": "High",
                        "features": [{
                            "id": "feature-1",
                            "title": "Test Feature",
                            "description": "Test Feature Description",
                            "tasks": [{
                                "id": "task-1",
                                "title": "Test Task",
                                "description": "Test Task Description",
                                "effort_estimate": "medium"
                            }]
                        }]
                    }]
                }
            },
            processing_time_ms=1000
        )
        
        governance_structure = governance_service._parse_ai_governance_structure(ai_result)
        
        assert "epics" in governance_structure
        assert len(governance_structure["epics"]) == 1
        assert governance_structure["epics"][0]["title"] == "Test Epic"
        assert len(governance_structure["epics"][0]["features"]) == 1
    
    @pytest.mark.asyncio
    async def test_governance_issue_creation(self, governance_service):
        """Test governance issue creation from structure"""
        governance_structure = {
            "epics": [{
                "id": "epic-1",
                "title": "Test Epic",
                "description": "Test Epic Description",
                "features": [{
                    "id": "feature-1",
                    "title": "Test Feature",
                    "description": "Test Feature Description",
                    "tasks": [{
                        "id": "task-1",
                        "title": "Test Task",
                        "description": "Test Task Description"
                    }]
                }]
            }]
        }
        
        ai_result = AIAnalysisResult(
            task_id="test-123",
            provider_used="openai",
            model_used="gpt-4",
            task_type=TaskType.PLANNING,
            confidence_score=0.9,
            result_data={},
            processing_time_ms=1000
        )
        
        issues = await governance_service._create_governance_issues(
            "project-123", governance_structure, ai_result
        )
        
        assert len(issues) == 3  # 1 epic + 1 feature + 1 task
        
        # Check epic
        epic_issue = next(issue for issue in issues if issue.issue_type == IssueType.EPIC)
        assert epic_issue.title == "Test Epic"
        assert len(epic_issue.children_ids) == 1
        
        # Check feature
        feature_issue = next(issue for issue in issues if issue.issue_type == IssueType.FEATURE)
        assert feature_issue.title == "Test Feature"
        assert feature_issue.parent_id == epic_issue.id
        
        # Check task
        task_issue = next(issue for issue in issues if issue.issue_type == IssueType.TASK)
        assert task_issue.title == "Test Task"
        assert task_issue.parent_id == feature_issue.id


class TestIssueGeneratorService:
    """Test Issue Generator Service"""
    
    @pytest.fixture
    def issue_service(self):
        """Create issue generator service instance for testing"""
        return IssueGeneratorService()
    
    def test_service_initialization(self, issue_service):
        """Test service initialization"""
        assert issue_service.service_name == "issue-generator"
        assert issue_service.version == "1.0.0"
    
    def test_issue_description_formatting(self, issue_service):
        """Test issue description formatting"""
        issue_data = {
            "description": "Base description",
            "ai_metadata": {
                "enhanced": True,
                "provider": "openai",
                "confidence": 0.95
            },
            "original_data": {
                "business_value": "High",
                "effort_estimate": "medium",
                "agent_assignment": "dev-agent"
            }
        }
        
        formatted_description = issue_service._format_issue_description(issue_data)
        
        assert "Base description" in formatted_description
        assert "AI Enhanced" in formatted_description
        assert "Business Value: High" in formatted_description
        assert "Effort Estimate: medium" in formatted_description
    
    @pytest.mark.asyncio
    async def test_ai_enhancement_fallback(self, issue_service):
        """Test AI enhancement with fallback behavior"""
        issue_data = {
            "title": "Test Issue",
            "description": "Test Description",
            "type": "task"
        }
        
        # Mock AI client to simulate failure
        with patch('src.shared.ai_client.ai_client.enhance_issue_description') as mock_enhance:
            mock_enhance.side_effect = Exception("AI service unavailable")
            
            enhanced_data = await issue_service._enhance_issue_with_ai(issue_data, "task")
            
            assert enhanced_data["title"] == "Test Issue"
            assert enhanced_data["ai_metadata"]["enhanced"] is False
            assert "error" in enhanced_data["ai_metadata"]


class TestEventMessage:
    """Test event messaging system"""
    
    def test_event_message_creation(self):
        """Test EventMessage creation and serialization"""
        event = EventMessage(
            event_id="event-123",
            event_type="governance_structure_generated",
            source_service="governance-engine",
            target_service="issue-generator",
            payload={"project_id": "project-123"},
            correlation_id="project-123"
        )
        
        assert event.event_id == "event-123"
        assert event.event_type == "governance_structure_generated"
        assert event.source_service == "governance-engine"
        
        # Test serialization
        event_dict = event.to_dict()
        assert event_dict["event_id"] == "event-123"
        assert "timestamp" in event_dict


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_governance_flow(self):
        """Test complete governance generation flow"""
        # This would be a comprehensive integration test
        # that validates the entire flow from specification to GitHub issues
        
        # Create project specification
        spec_request = ProjectSpecRequest(
            name="Integration Test Project",
            description="End-to-end test project",
            requirements=["requirement 1", "requirement 2"],
            constraints=["constraint 1"],
            stakeholders=["stakeholder 1"],
            priority="high"
        )
        
        # Mock database and AI services for integration test
        with patch('src.shared.database.db_manager') as mock_db:
            with patch('src.shared.ai_client.ai_client') as mock_ai:
                # Setup mocks
                mock_db.initialize_all_connections = AsyncMock()
                mock_db.get_mongodb.return_value.insert_document = AsyncMock(return_value="doc-123")
                mock_db.get_supabase.return_value.insert_record = Mock(return_value={"id": "record-123"})
                mock_db.get_redis.return_value.set_cache = Mock()
                mock_db.get_redis.return_value.publish_event = Mock()
                
                mock_ai.generate_epic_breakdown = AsyncMock(return_value=AIAnalysisResult(
                    task_id="ai-123",
                    provider_used="openai",
                    model_used="gpt-4",
                    task_type=TaskType.PLANNING,
                    confidence_score=0.9,
                    result_data={
                        "governance_structure": {
                            "epics": [{
                                "id": "epic-1",
                                "title": "Test Epic",
                                "description": "AI-generated epic",
                                "features": []
                            }]
                        }
                    },
                    processing_time_ms=2000
                ))
                
                # Test governance generation
                governance_service = GovernanceEngineService()
                await governance_service.initialize()
                
                result = await governance_service.process_project_specification(spec_request)
                
                assert result.status == "completed"
                assert "governance_structure" in result.governance_structure
                assert result.ai_analysis["provider_used"] == "openai"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
