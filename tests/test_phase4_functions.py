"""
Test suite for Phase 4 GitHub API functions
Tests 10 functions for blob operations, repository lifecycle, collaboration, workflows, and security
"""

import pytest
import aiohttp
from unittest.mock import AsyncMock, patch, MagicMock
import base64
import json

from src.shared.github_client import GitHubClient


@pytest.fixture
def mock_session():
    """Mock aiohttp session"""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def github_client(mock_session):
    """GitHub client with mocked session"""
    client = GitHubClient("fake_token")
    client.session = mock_session
    return client


class TestBlobOperations:
    """Test blob operation functions"""
    
    @pytest.mark.asyncio
    async def test_get_blob(self, github_client, mock_session):
        """Test get_blob function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'content': base64.b64encode(b'file content').decode('utf-8'),
            'encoding': 'base64',
            'sha': 'abc123',
            'size': 12
        }
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        result = await github_client.get_blob('owner', 'repo', 'abc123')
        
        assert result['content'] == base64.b64encode(b'file content').decode('utf-8')
        assert result['encoding'] == 'base64'
        mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_blob(self, github_client, mock_session):
        """Test create_blob function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = {
            'sha': 'new_blob_sha',
            'url': 'https://api.github.com/repos/owner/repo/git/blobs/new_blob_sha'
        }
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        result = await github_client.create_blob('owner', 'repo', 'file content', 'utf-8')
        
        assert result['sha'] == 'new_blob_sha'
        mock_session.request.assert_called_once()


class TestRepositoryLifecycle:
    """Test repository lifecycle management"""
    
    @pytest.mark.asyncio
    async def test_archive_repository(self, github_client, mock_session):
        """Test archive_repository function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'archived': True,
            'full_name': 'owner/repo'
        }
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        result = await github_client.archive_repository('owner', 'repo')
        
        assert result['archived'] is True
        mock_session.request.assert_called_once()


class TestBranchManagement:
    """Test advanced branch management"""
    
    @pytest.mark.asyncio
    async def test_get_branch_merge_methods(self, github_client, mock_session):
        """Test get_branch_merge_methods function"""
        # Mock get_repository call
        with patch.object(github_client, 'get_repository') as mock_get_repo:
            mock_get_repo.return_value = {
                'allow_merge_commit': True,
                'allow_squash_merge': False,
                'allow_rebase_merge': True,
                'allow_auto_merge': False,
                'delete_branch_on_merge': True
            }
            
            result = await github_client.get_branch_merge_methods('owner', 'repo')
            
            assert result['allow_merge_commit'] is True
            assert result['allow_squash_merge'] is False
            assert result['delete_branch_on_merge'] is True
            mock_get_repo.assert_called_once_with('owner', 'repo')


class TestCollaborationManagement:
    """Test collaboration management functions"""
    
    @pytest.mark.asyncio
    async def test_list_collaborators(self, github_client, mock_session):
        """Test list_collaborators function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = [
            {'login': 'user1', 'permissions': {'admin': True}},
            {'login': 'user2', 'permissions': {'push': True}}
        ]
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        result = await github_client.list_collaborators('owner', 'repo')
        
        assert len(result) == 2
        assert result[0]['login'] == 'user1'
        mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_collaborator(self, github_client, mock_session):
        """Test add_collaborator function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = {
            'login': 'newuser',
            'permissions': {'push': True}
        }
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        result = await github_client.add_collaborator('owner', 'repo', 'newuser', 'push')
        
        assert result['login'] == 'newuser'
        mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_remove_collaborator(self, github_client, mock_session):
        """Test remove_collaborator function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 204
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        result = await github_client.remove_collaborator('owner', 'repo', 'username')
        
        assert result is True
        mock_session.request.assert_called_once()


class TestWorkflowAutomation:
    """Test GitHub Actions workflow automation"""
    
    @pytest.mark.asyncio
    async def test_list_workflow_runs(self, github_client, mock_session):
        """Test list_workflow_runs function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'workflow_runs': [
                {'id': 123, 'status': 'completed', 'conclusion': 'success'},
                {'id': 124, 'status': 'in_progress', 'conclusion': None}
            ]
        }
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        result = await github_client.list_workflow_runs('owner', 'repo')
        
        assert len(result) == 2
        assert result[0]['status'] == 'completed'
        mock_session.request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_trigger_workflow(self, github_client, mock_session):
        """Test trigger_workflow function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 204
        mock_response.json.return_value = {}
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        inputs = {'environment': 'production', 'version': '1.0.0'}
        result = await github_client.trigger_workflow('owner', 'repo', 'deploy.yml', 'main', inputs)
        
        mock_session.request.assert_called_once()


class TestSecurityFeatures:
    """Test security and vulnerability features"""
    
    @pytest.mark.asyncio
    async def test_list_repository_vulnerabilities(self, github_client, mock_session):
        """Test list_repository_vulnerabilities function"""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = [
            {
                'package': {'name': 'lodash'},
                'severity': 'high',
                'advisory': {'summary': 'Prototype pollution vulnerability'}
            }
        ]
        mock_session.request.return_value.__aenter__.return_value = mock_response
        
        result = await github_client.list_repository_vulnerabilities('owner', 'repo')
        
        assert len(result) == 1
        assert result[0]['severity'] == 'high'
        mock_session.request.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
