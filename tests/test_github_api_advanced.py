"""
Tests for new GitHub API wrapper functions
Testing the Phase 1 high-priority implementations
"""

import asyncio
import pytest
import os
from unittest.mock import AsyncMock, patch

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.shared.github_client import GitHubAPIClient


class TestRepositoryAdvanced:
    """Test advanced repository operations"""
    
    @pytest.fixture
    def github_client(self):
        return GitHubAPIClient(token="test_token")
    
    @pytest.mark.asyncio
    async def test_update_repository(self, github_client):
        """Test repository update functionality"""
        mock_response = {
            "id": 123,
            "name": "updated-repo",
            "description": "Updated description",
            "private": False
        }
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.update_repository(
                owner="testowner",
                repo="testrepo", 
                name="updated-repo",
                description="Updated description",
                private=False
            )
            
            mock_request.assert_called_once_with(
                'PATCH',
                'https://api.github.com/repos/testowner/testrepo',
                json={
                    'name': 'updated-repo',
                    'description': 'Updated description', 
                    'private': False
                }
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_fork_repository(self, github_client):
        """Test repository forking"""
        mock_response = {"id": 456, "full_name": "testowner/forked-repo"}
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.fork_repository(
                owner="originalowner",
                repo="originalrepo",
                organization="testorg"
            )
            
            mock_request.assert_called_once_with(
                'POST',
                'https://api.github.com/repos/originalowner/originalrepo/forks',
                json={'organization': 'testorg'}
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_get_repository_topics(self, github_client):
        """Test getting repository topics"""
        mock_response = {"names": ["python", "automation", "governance"]}
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.get_repository_topics("testowner", "testrepo")
            
            mock_request.assert_called_once()
            assert result == ["python", "automation", "governance"]
    
    @pytest.mark.asyncio
    async def test_update_repository_topics(self, github_client):
        """Test updating repository topics"""
        mock_response = {"names": ["python", "automation", "governance", "new-topic"]}
        topics = ["python", "automation", "governance", "new-topic"]
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.update_repository_topics("testowner", "testrepo", topics)
            
            mock_request.assert_called_once_with(
                'PUT',
                'https://api.github.com/repos/testowner/testrepo/topics',
                json={'names': topics},
                headers={**github_client.headers, 'Accept': 'application/vnd.github.mercy-preview+json'}
            )
            assert result == mock_response


class TestIssueAdvanced:
    """Test advanced issue operations"""
    
    @pytest.fixture
    def github_client(self):
        return GitHubAPIClient(token="test_token")
    
    @pytest.mark.asyncio
    async def test_delete_issue_comment(self, github_client):
        """Test deleting issue comment"""
        with patch.object(github_client, '_make_request', return_value={}) as mock_request:
            result = await github_client.delete_issue_comment("testowner", "testrepo", 123)
            
            mock_request.assert_called_once_with(
                'DELETE',
                'https://api.github.com/repos/testowner/testrepo/issues/comments/123'
            )
            assert result is True
    
    @pytest.mark.asyncio
    async def test_list_issue_events(self, github_client):
        """Test listing issue events"""
        mock_response = [
            {"id": 1, "event": "labeled", "label": {"name": "bug"}},
            {"id": 2, "event": "assigned", "assignee": {"login": "developer"}}
        ]
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.list_issue_events("testowner", "testrepo", 456)
            
            mock_request.assert_called_once_with(
                'GET',
                'https://api.github.com/repos/testowner/testrepo/issues/456/events'
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_lock_issue(self, github_client):
        """Test locking an issue"""
        with patch.object(github_client, '_make_request', return_value={}) as mock_request:
            result = await github_client.lock_issue("testowner", "testrepo", 789, "resolved")
            
            mock_request.assert_called_once_with(
                'PUT',
                'https://api.github.com/repos/testowner/testrepo/issues/789/lock',
                json={'lock_reason': 'resolved'}
            )
            assert result is True
    
    @pytest.mark.asyncio
    async def test_unlock_issue(self, github_client):
        """Test unlocking an issue"""
        with patch.object(github_client, '_make_request', return_value={}) as mock_request:
            result = await github_client.unlock_issue("testowner", "testrepo", 789)
            
            mock_request.assert_called_once_with(
                'DELETE',
                'https://api.github.com/repos/testowner/testrepo/issues/789/lock'
            )
            assert result is True


class TestLabelAdvanced:
    """Test advanced label operations"""
    
    @pytest.fixture
    def github_client(self):
        return GitHubAPIClient(token="test_token")
    
    @pytest.mark.asyncio
    async def test_update_label(self, github_client):
        """Test updating a label"""
        mock_response = {
            "name": "new-label-name",
            "color": "ff0000", 
            "description": "Updated description"
        }
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.update_label(
                owner="testowner",
                repo="testrepo",
                current_name="old-label",
                new_name="new-label-name",
                color="#ff0000",
                description="Updated description"
            )
            
            mock_request.assert_called_once_with(
                'PATCH',
                'https://api.github.com/repos/testowner/testrepo/labels/old-label',
                json={
                    'name': 'new-label-name',
                    'color': 'ff0000',
                    'description': 'Updated description'
                }
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_add_labels_to_issue(self, github_client):
        """Test adding labels to an issue"""
        mock_response = [
            {"name": "bug", "color": "d73a4a"},
            {"name": "feature", "color": "a2eeef"}
        ]
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.add_labels_to_issue(
                "testowner", "testrepo", 123, ["bug", "feature"]
            )
            
            mock_request.assert_called_once_with(
                'POST',
                'https://api.github.com/repos/testowner/testrepo/issues/123/labels',
                json={'labels': ['bug', 'feature']}
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_remove_labels_from_issue(self, github_client):
        """Test removing specific labels from an issue"""
        with patch.object(github_client, '_make_request', return_value={}) as mock_request:
            result = await github_client.remove_labels_from_issue(
                "testowner", "testrepo", 123, ["bug", "feature"]
            )
            
            # Should make multiple DELETE calls
            assert mock_request.call_count == 2
            assert result is True


class TestFileOperations:
    """Test file and content operations"""
    
    @pytest.fixture
    def github_client(self):
        return GitHubAPIClient(token="test_token")
    
    @pytest.mark.asyncio
    async def test_get_file_contents(self, github_client):
        """Test getting file contents"""
        mock_response = {
            "name": "README.md",
            "content": "VGVzdCBjb250ZW50",  # base64 encoded "Test content"
            "encoding": "base64"
        }
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.get_file_contents("testowner", "testrepo", "README.md")
            
            mock_request.assert_called_once_with(
                'GET',
                'https://api.github.com/repos/testowner/testrepo/contents/README.md',
                params={}
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_create_or_update_file(self, github_client):
        """Test creating or updating a file"""
        mock_response = {
            "content": {"name": "test.txt", "path": "test.txt"},
            "commit": {"sha": "abc123"}
        }
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.create_or_update_file(
                owner="testowner",
                repo="testrepo",
                path="test.txt",
                message="Add test file",
                content="Test content"
            )
            
            # Verify the content was base64 encoded
            call_args = mock_request.call_args
            assert 'content' in call_args[1]['json']
            assert call_args[1]['json']['message'] == "Add test file"
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_list_directory_contents(self, github_client):
        """Test listing directory contents"""
        mock_response = [
            {"name": "file1.py", "type": "file"},
            {"name": "subdir", "type": "dir"}
        ]
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.list_directory_contents("testowner", "testrepo", "src")
            
            mock_request.assert_called_once_with(
                'GET',
                'https://api.github.com/repos/testowner/testrepo/contents/src',
                params={}
            )
            assert result == mock_response


class TestPullRequestAdvanced:
    """Test advanced pull request operations"""
    
    @pytest.fixture
    def github_client(self):
        return GitHubAPIClient(token="test_token")
    
    @pytest.mark.asyncio
    async def test_update_pull_request(self, github_client):
        """Test updating a pull request"""
        mock_response = {
            "number": 123,
            "title": "Updated PR title",
            "body": "Updated description"
        }
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.update_pull_request(
                owner="testowner",
                repo="testrepo",
                pull_number=123,
                title="Updated PR title",
                body="Updated description"
            )
            
            mock_request.assert_called_once_with(
                'PATCH',
                'https://api.github.com/repos/testowner/testrepo/pulls/123',
                json={
                    'title': 'Updated PR title',
                    'body': 'Updated description'
                }
            )
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_merge_pull_request(self, github_client):
        """Test merging a pull request"""
        mock_response = {
            "sha": "abc123def456",
            "merged": True,
            "message": "Pull Request successfully merged"
        }
        
        with patch.object(github_client, '_make_request', return_value=mock_response) as mock_request:
            result = await github_client.merge_pull_request(
                owner="testowner",
                repo="testrepo",
                pull_number=123,
                commit_title="Merge feature branch",
                merge_method="squash"
            )
            
            mock_request.assert_called_once_with(
                'PUT',
                'https://api.github.com/repos/testowner/testrepo/pulls/123/merge',
                json={
                    'merge_method': 'squash',
                    'commit_title': 'Merge feature branch'
                }
            )
            assert result == mock_response


if __name__ == "__main__":
    # Run specific test
    pytest.main([__file__, "-v"])
