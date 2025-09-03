"""
Phase 2 Function Tests
Tests for the 14 high-priority functions added in Phase 2
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from shared.github_client import GitHubAPIClient


@pytest.fixture
def github_client():
    """Create a test GitHub client instance"""
    return GitHubAPIClient(token="test-token")


@pytest.fixture
def mock_response():
    """Mock HTTP response"""
    mock = Mock()
    mock.status = 200
    mock.json = AsyncMock(return_value={"test": "data"})
    mock.text = AsyncMock(return_value='{"test": "data"}')
    return mock


class TestPhase2RepositoryOperations:
    """Test Phase 2 repository operations"""

    @pytest.mark.asyncio
    async def test_delete_repository(self, github_client, mock_response):
        """Test delete_repository function"""
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.status = 204  # DELETE returns 204
            
            await github_client.delete_repository("owner", "repo")
            
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "DELETE"
            assert "repos/owner/repo" in args[1]

    @pytest.mark.asyncio
    async def test_list_repository_forks(self, github_client, mock_response):
        """Test list_repository_forks function"""
        mock_forks = [{"id": 1, "name": "fork1"}, {"id": 2, "name": "fork2"}]
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_forks
            
            result = await github_client.list_repository_forks("owner", "repo", sort="newest")
            
            assert result == mock_forks
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/forks" in args[1]

    @pytest.mark.asyncio
    async def test_get_repository_activity(self, github_client, mock_response):
        """Test get_repository_activity function"""
        mock_events = [{"type": "PushEvent"}, {"type": "IssuesEvent"}]
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_events
            
            result = await github_client.get_repository_activity("owner", "repo")
            
            assert result == mock_events
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/events" in args[1]

    @pytest.mark.asyncio
    async def test_list_repository_topics(self, github_client, mock_response):
        """Test list_repository_topics function"""
        mock_topics = {"names": ["python", "api", "github"]}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_topics
            
            result = await github_client.list_repository_topics("owner", "repo")
            
            assert result == mock_topics
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/topics" in args[1]


class TestPhase2FileOperations:
    """Test Phase 2 file operations"""

    @pytest.mark.asyncio
    async def test_get_file_tree(self, github_client, mock_response):
        """Test get_file_tree function"""
        mock_tree = {
            "tree": [
                {"path": "file1.py", "type": "blob"},
                {"path": "dir1", "type": "tree"}
            ]
        }
        
        # Mock the repository info call first
        repo_mock = {"default_branch": "main"}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            # First call returns repo info, second returns tree
            mock_response.json.side_effect = [repo_mock, mock_tree]
            
            result = await github_client.get_file_tree("owner", "repo", recursive=True)
            
            assert result == mock_tree
            # Should make 2 calls: one for repo info, one for tree
            assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_search_code(self, github_client, mock_response):
        """Test search_code function"""
        mock_search_results = {
            "total_count": 1,
            "items": [{"name": "test.py", "repository": {"name": "test-repo"}}]
        }
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_search_results
            
            result = await github_client.search_code("test query", sort="indexed", order="desc")
            
            assert result == mock_search_results
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "search/code" in args[1]


class TestPhase2PullRequestOperations:
    """Test Phase 2 pull request operations"""

    @pytest.mark.asyncio
    async def test_close_pull_request(self, github_client, mock_response):
        """Test close_pull_request function"""
        mock_pr = {"state": "closed", "number": 123}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_pr
            
            result = await github_client.close_pull_request("owner", "repo", 123)
            
            assert result == mock_pr
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "PATCH"
            assert "repos/owner/repo/pulls/123" in args[1]

    @pytest.mark.asyncio
    async def test_list_pull_request_files(self, github_client, mock_response):
        """Test list_pull_request_files function"""
        mock_files = [{"filename": "test.py", "status": "modified"}]
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_files
            
            result = await github_client.list_pull_request_files("owner", "repo", 123)
            
            assert result == mock_files
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/pulls/123/files" in args[1]

    @pytest.mark.asyncio
    async def test_list_pull_request_commits(self, github_client, mock_response):
        """Test list_pull_request_commits function"""
        mock_commits = [{"sha": "abc123", "message": "Test commit"}]
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_commits
            
            result = await github_client.list_pull_request_commits("owner", "repo", 123)
            
            assert result == mock_commits
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/pulls/123/commits" in args[1]

    @pytest.mark.asyncio
    async def test_create_pull_request_review(self, github_client, mock_response):
        """Test create_pull_request_review function"""
        mock_review = {"id": 456, "state": "COMMENTED"}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_review
            
            result = await github_client.create_pull_request_review(
                "owner", "repo", 123, body="Good work!", event="APPROVE"
            )
            
            assert result == mock_review
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "POST"
            assert "repos/owner/repo/pulls/123/reviews" in args[1]


class TestPhase2BranchOperations:
    """Test Phase 2 branch operations"""

    @pytest.mark.asyncio
    async def test_delete_branch(self, github_client, mock_response):
        """Test delete_branch function"""
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.status = 204  # DELETE returns 204
            
            await github_client.delete_branch("owner", "repo", "feature-branch")
            
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "DELETE"
            assert "repos/owner/repo/git/refs/heads/feature-branch" in args[1]

    @pytest.mark.asyncio
    async def test_get_branch_protection(self, github_client, mock_response):
        """Test get_branch_protection function"""
        mock_protection = {"required_status_checks": {"strict": True}}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_protection
            
            result = await github_client.get_branch_protection("owner", "repo", "main")
            
            assert result == mock_protection
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/branches/main/protection" in args[1]

    @pytest.mark.asyncio
    async def test_update_branch_protection(self, github_client, mock_response):
        """Test update_branch_protection function"""
        protection_data = {"required_status_checks": {"strict": True}}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = protection_data
            
            result = await github_client.update_branch_protection("owner", "repo", "main", protection_data)
            
            assert result == protection_data
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "PUT"
            assert "repos/owner/repo/branches/main/protection" in args[1]

    @pytest.mark.asyncio
    async def test_compare_branches(self, github_client, mock_response):
        """Test compare_branches function"""
        mock_comparison = {"ahead_by": 3, "behind_by": 1, "files": []}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_comparison
            
            result = await github_client.compare_branches("owner", "repo", "main", "develop")
            
            assert result == mock_comparison
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/compare/main...develop" in args[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
