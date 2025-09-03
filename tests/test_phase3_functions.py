"""
Phase 3 Function Tests
Tests for the 10 high-priority functions added in Phase 3
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


class TestPhase3AdvancedPROperations:
    """Test Phase 3 advanced pull request operations"""

    @pytest.mark.asyncio
    async def test_list_pull_request_reviews(self, github_client, mock_response):
        """Test list_pull_request_reviews function"""
        mock_reviews = [
            {"id": 1, "state": "APPROVED", "user": {"login": "reviewer1"}},
            {"id": 2, "state": "CHANGES_REQUESTED", "user": {"login": "reviewer2"}}
        ]
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_reviews
            
            result = await github_client.list_pull_request_reviews("owner", "repo", 123)
            
            assert result == mock_reviews
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/pulls/123/reviews" in args[1]

    @pytest.mark.asyncio
    async def test_get_pull_request_review(self, github_client, mock_response):
        """Test get_pull_request_review function"""
        mock_review = {"id": 456, "state": "APPROVED", "body": "Looks good!"}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_review
            
            result = await github_client.get_pull_request_review("owner", "repo", 123, 456)
            
            assert result == mock_review
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/pulls/123/reviews/456" in args[1]

    @pytest.mark.asyncio
    async def test_update_pull_request_review(self, github_client, mock_response):
        """Test update_pull_request_review function"""
        mock_updated_review = {"id": 456, "body": "Updated review"}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_updated_review
            
            result = await github_client.update_pull_request_review(
                "owner", "repo", 123, 456, "Updated review"
            )
            
            assert result == mock_updated_review
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "PUT"
            assert "repos/owner/repo/pulls/123/reviews/456" in args[1]

    @pytest.mark.asyncio
    async def test_dismiss_pull_request_review(self, github_client, mock_response):
        """Test dismiss_pull_request_review function"""
        mock_dismissed_review = {"id": 456, "state": "DISMISSED"}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_dismissed_review
            
            result = await github_client.dismiss_pull_request_review(
                "owner", "repo", 123, 456, "Outdated review"
            )
            
            assert result == mock_dismissed_review
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "PUT"
            assert "repos/owner/repo/pulls/123/reviews/456/dismissals" in args[1]

    @pytest.mark.asyncio
    async def test_submit_pull_request_review(self, github_client, mock_response):
        """Test submit_pull_request_review function"""
        mock_submitted_review = {"id": 456, "state": "APPROVED"}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_submitted_review
            
            result = await github_client.submit_pull_request_review(
                "owner", "repo", 123, 456, "APPROVE", "Approved!"
            )
            
            assert result == mock_submitted_review
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "POST"
            assert "repos/owner/repo/pulls/123/reviews/456/events" in args[1]

    @pytest.mark.asyncio
    async def test_request_pull_request_reviewers(self, github_client, mock_response):
        """Test request_pull_request_reviewers function"""
        mock_response_data = {"requested_reviewers": ["user1", "user2"]}
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_response_data
            
            result = await github_client.request_pull_request_reviewers(
                "owner", "repo", 123, reviewers=["user1", "user2"], team_reviewers=["team1"]
            )
            
            assert result == mock_response_data
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "POST"
            assert "repos/owner/repo/pulls/123/requested_reviewers" in args[1]


class TestPhase3RepositoryAnalytics:
    """Test Phase 3 repository analytics operations"""

    @pytest.mark.asyncio
    async def test_get_repository_languages(self, github_client, mock_response):
        """Test get_repository_languages function"""
        mock_languages = {
            "Python": 12345,
            "JavaScript": 8765,
            "HTML": 4321
        }
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_languages
            
            result = await github_client.get_repository_languages("owner", "repo")
            
            assert result == mock_languages
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "GET"
            assert "repos/owner/repo/languages" in args[1]

    @pytest.mark.asyncio
    async def test_get_repository_stats(self, github_client, mock_response):
        """Test get_repository_stats function"""
        mock_contributors = [{"author": {"login": "user1"}, "total": 50}]
        mock_repo_data = {
            "stargazers_count": 100,
            "forks_count": 25,
            "watchers_count": 80,
            "open_issues_count": 5,
            "size": 1024,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-12-31T23:59:59Z",
            "pushed_at": "2023-12-30T12:00:00Z"
        }
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            # First call returns contributors, second returns repo data
            mock_response.json.side_effect = [mock_contributors, mock_repo_data]
            
            result = await github_client.get_repository_stats("owner", "repo")
            
            assert result['contributors'] == mock_contributors
            assert result['repository_metrics']['stars'] == 100
            assert result['repository_metrics']['forks'] == 25
            # Should make 2 calls: one for contributors, one for repo info
            assert mock_request.call_count == 2


class TestPhase3BranchProtectionAdvanced:
    """Test Phase 3 advanced branch protection operations"""

    @pytest.mark.asyncio
    async def test_delete_branch_protection(self, github_client, mock_response):
        """Test delete_branch_protection function"""
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.status = 204  # DELETE returns 204
            
            await github_client.delete_branch_protection("owner", "repo", "main")
            
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "DELETE"
            assert "repos/owner/repo/branches/main/protection" in args[1]

    @pytest.mark.asyncio
    async def test_protect_branch(self, github_client, mock_response):
        """Test protect_branch function"""
        mock_protection = {
            "enforce_admins": True,
            "required_status_checks": {"strict": True, "contexts": []},
            "required_pull_request_reviews": {
                "required_approving_review_count": 2,
                "dismiss_stale_reviews": True
            }
        }
        
        with patch('aiohttp.ClientSession.request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value.__aenter__.return_value = mock_response
            mock_response.json.return_value = mock_protection
            
            result = await github_client.protect_branch(
                "owner", "repo", "main",
                required_status_checks={"strict": True, "contexts": ["ci/test"]},
                enforce_admins=True,
                required_pull_request_reviews={
                    "required_approving_review_count": 2,
                    "dismiss_stale_reviews": True,
                    "require_code_owner_reviews": True
                }
            )
            
            assert result == mock_protection
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "PUT"
            assert "repos/owner/repo/branches/main/protection" in args[1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
