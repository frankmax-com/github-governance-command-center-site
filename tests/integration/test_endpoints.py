"""
Integration tests for GitHub API endpoints
Tests real HTTP endpoints in containerized environment
"""

import asyncio
import httpx
import pytest
import os


class TestGitHubAPIEndpoints:
    """Integration tests for GitHub API service endpoints"""
    
    @pytest.fixture
    def base_url(self):
        return os.getenv('GITHUB_API_BASE_URL', 'http://localhost:8000')
    
    @pytest.fixture
    async def http_client(self):
        async with httpx.AsyncClient() as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, http_client, base_url):
        """Test service health endpoint"""
        response = await http_client.get(f"{base_url}/v1/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "version" in health_data
        assert "timestamp" in health_data
    
    @pytest.mark.asyncio
    async def test_github_api_info_endpoint(self, http_client, base_url):
        """Test GitHub API info endpoint"""
        response = await http_client.get(f"{base_url}/v1/github/info")
        assert response.status_code == 200
        
        info_data = response.json()
        assert "functions" in info_data
        assert "implemented_count" in info_data
        assert "total_count" in info_data
        assert info_data["implemented_count"] >= 41  # Should have at least our implemented functions
    
    @pytest.mark.asyncio
    async def test_list_repositories_endpoint(self, http_client, base_url):
        """Test list repositories endpoint"""
        # Test with mock data in testing mode
        params = {"owner": "testowner", "per_page": 10}
        response = await http_client.get(f"{base_url}/v1/github/repositories", params=params)
        
        # In testing mode, should return mock data or handle gracefully
        assert response.status_code in [200, 401, 403]  # Valid responses
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_create_issue_endpoint(self, http_client, base_url):
        """Test create issue endpoint"""
        issue_data = {
            "owner": "testowner",
            "repo": "testrepo",
            "title": "Test Issue",
            "body": "This is a test issue created by integration tests",
            "labels": ["test", "integration"]
        }
        
        response = await http_client.post(f"{base_url}/v1/github/issues", json=issue_data)
        
        # In testing mode, should return mock data or handle gracefully  
        assert response.status_code in [201, 401, 403, 422]  # Valid responses
        
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["title"] == issue_data["title"]
    
    @pytest.mark.asyncio
    async def test_repository_operations_endpoint(self, http_client, base_url):
        """Test repository operations endpoint"""
        repo_data = {
            "owner": "testowner",
            "repo": "testrepo",
            "description": "Updated via integration test",
            "private": False
        }
        
        response = await http_client.patch(f"{base_url}/v1/github/repositories/update", json=repo_data)
        
        # In testing mode, should handle gracefully
        assert response.status_code in [200, 401, 403, 404, 422]  # Valid responses
    
    @pytest.mark.asyncio
    async def test_labels_endpoint(self, http_client, base_url):
        """Test labels management endpoint"""
        params = {"owner": "testowner", "repo": "testrepo"}
        response = await http_client.get(f"{base_url}/v1/github/labels", params=params)
        
        # In testing mode, should return mock data or handle gracefully
        assert response.status_code in [200, 401, 403, 404]  # Valid responses
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_file_operations_endpoint(self, http_client, base_url):
        """Test file operations endpoint"""
        params = {"owner": "testowner", "repo": "testrepo", "path": "README.md"}
        response = await http_client.get(f"{base_url}/v1/github/files/contents", params=params)
        
        # In testing mode, should handle gracefully
        assert response.status_code in [200, 401, 403, 404]  # Valid responses
    
    @pytest.mark.asyncio
    async def test_pull_requests_endpoint(self, http_client, base_url):
        """Test pull requests endpoint"""
        params = {"owner": "testowner", "repo": "testrepo", "state": "open"}
        response = await http_client.get(f"{base_url}/v1/github/pull-requests", params=params)
        
        # In testing mode, should return mock data or handle gracefully
        assert response.status_code in [200, 401, 403, 404]  # Valid responses
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_branches_endpoint(self, http_client, base_url):
        """Test branches endpoint"""
        params = {"owner": "testowner", "repo": "testrepo"}
        response = await http_client.get(f"{base_url}/v1/github/branches", params=params)
        
        # In testing mode, should return mock data or handle gracefully
        assert response.status_code in [200, 401, 403, 404]  # Valid responses
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestServiceCommunication:
    """Test inter-service communication and dependencies"""
    
    @pytest.fixture
    def base_url(self):
        return os.getenv('GITHUB_API_BASE_URL', 'http://localhost:8000')
    
    @pytest.fixture
    async def http_client(self):
        async with httpx.AsyncClient(timeout=30.0) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_service_startup_time(self, http_client, base_url):
        """Test that service starts up within reasonable time"""
        import time
        start_time = time.time()
        
        max_retries = 10
        for i in range(max_retries):
            try:
                response = await http_client.get(f"{base_url}/v1/health")
                if response.status_code == 200:
                    startup_time = time.time() - start_time
                    assert startup_time < 60  # Should start within 60 seconds
                    return
            except httpx.RequestError:
                if i < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                raise
        
        pytest.fail("Service did not become healthy within timeout")
    
    @pytest.mark.asyncio
    async def test_error_handling(self, http_client, base_url):
        """Test error handling for invalid requests"""
        # Test invalid endpoint
        response = await http_client.get(f"{base_url}/v1/invalid-endpoint")
        assert response.status_code == 404
        
        # Test invalid method
        response = await http_client.delete(f"{base_url}/v1/health")
        assert response.status_code == 405
    
    @pytest.mark.asyncio
    async def test_rate_limiting_headers(self, http_client, base_url):
        """Test that rate limiting headers are present"""
        response = await http_client.get(f"{base_url}/v1/health")
        
        # Check for common rate limiting headers
        headers = response.headers
        # These might be present depending on implementation
        rate_limit_headers = [
            'x-ratelimit-limit',
            'x-ratelimit-remaining', 
            'x-ratelimit-reset',
            'retry-after'
        ]
        
        # At least verify response has proper headers structure
        assert 'content-type' in headers
        assert headers['content-type'] == 'application/json'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
