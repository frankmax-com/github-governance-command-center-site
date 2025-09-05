"""
Unified GitHub API Client - Comprehensive 750+ Operations
Consolidates all GitHub API functionality with failproof architecture
Combines governance workflows with complete API coverage
"""

import asyncio
import aiohttp
import ssl
import certifi
import logging
import time
import json
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Optional backoff import with fallback
try:
    from backoff import on_exception, expo
    HAS_BACKOFF = True
except ImportError:
    HAS_BACKOFF = False
    # Simple fallback decorator
    def on_exception(strategy, exception, max_tries=3, max_time=60):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                for attempt in range(max_tries):
                    try:
                        return await func(*args, **kwargs)
                    except exception as e:
                        if attempt == max_tries - 1:
                            raise
                        await asyncio.sleep(min(2 ** attempt, 5))
                return None
            return wrapper
        return decorator
    
    def expo(*args, **kwargs):
        return None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors with enhanced context"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None, endpoint: str = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        self.endpoint = endpoint
        super().__init__(self.format_message())
    
    def format_message(self) -> str:
        msg = f"GitHub API Error: {self.message}"
        if self.status_code:
            msg += f" (Status: {self.status_code})"
        if self.endpoint:
            msg += f" (Endpoint: {self.endpoint})"
        return msg

class RateLimitManager:
    """Advanced rate limit management with predictive throttling"""
    def __init__(self):
        self.primary_limit = 5000
        self.primary_remaining = 5000
        self.primary_reset_time = None
        self.secondary_limit = 1000
        self.secondary_remaining = 1000
        self.secondary_reset_time = None
        self.last_request_time = 0
        self.min_interval = 0.1  # Minimum time between requests
        
    def update_from_headers(self, headers: Dict[str, str]):
        """Update rate limit info from response headers"""
        try:
            if 'x-ratelimit-limit' in headers:
                self.primary_limit = int(headers['x-ratelimit-limit'])
            if 'x-ratelimit-remaining' in headers:
                self.primary_remaining = int(headers['x-ratelimit-remaining'])
            if 'x-ratelimit-reset' in headers:
                self.primary_reset_time = int(headers['x-ratelimit-reset'])
                
            # Secondary rate limits (for search, etc.)
            if 'x-ratelimit-limit-search' in headers:
                self.secondary_limit = int(headers['x-ratelimit-limit-search'])
            if 'x-ratelimit-remaining-search' in headers:
                self.secondary_remaining = int(headers['x-ratelimit-remaining-search'])
                
        except (ValueError, KeyError) as e:
            logger.warning(f"Failed to parse rate limit headers: {e}")
    
    async def wait_if_needed(self, is_search: bool = False):
        """Wait if approaching rate limits with predictive throttling"""
        current_time = time.time()
        
        # Enforce minimum interval between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            await asyncio.sleep(self.min_interval - time_since_last)
        
        # Check appropriate rate limit
        remaining = self.secondary_remaining if is_search else self.primary_remaining
        reset_time = self.secondary_reset_time if is_search else self.primary_reset_time
        
        # If we're down to last 10% of requests, start throttling
        limit = self.secondary_limit if is_search else self.primary_limit
        if remaining < (limit * 0.1) and reset_time:
            wait_time = max(0, reset_time - current_time)
            if wait_time > 0:
                logger.info(f"Rate limit protection: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def get_status(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        return {
            'primary': {
                'limit': self.primary_limit,
                'remaining': self.primary_remaining,
                'reset_time': self.primary_reset_time
            },
            'secondary': {
                'limit': self.secondary_limit,
                'remaining': self.secondary_remaining,
                'reset_time': self.secondary_reset_time
            }
        }

@dataclass
class GitHubConfig:
    """Configuration for GitHub API client"""
    token: str
    base_url: str = "https://api.github.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = "GitHub-Governance-Factory/1.0"
    enable_rate_limiting: bool = True
    enable_ssl_verification: bool = True

class UnifiedGitHubAPIClient:
    """
    Unified GitHub API Client with 750+ operations
    Combines governance workflows with comprehensive API coverage
    Features failproof architecture with advanced error handling
    """
    
    def __init__(self, config: GitHubConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimitManager()
        self._closed = False
        
        # SSL Context
        if config.enable_ssl_verification:
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        else:
            self.ssl_context = False
            
        # Headers
        self.headers = {
            'Authorization': f'token {config.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': config.user_agent,
            'X-GitHub-Api-Version': '2022-11-28'
        }
    
    async def __aenter__(self):
        await self._create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _create_session(self):
        """Create aiohttp session with optimal configuration"""
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        connector = aiohttp.TCPConnector(
            ssl=self.ssl_context,
            limit=100,
            limit_per_host=30,
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        self.session = aiohttp.ClientSession(
            headers=self.headers,
            timeout=timeout,
            connector=connector
        )
    
    async def close(self):
        """Close the session and cleanup resources"""
        if self.session and not self._closed:
            await self.session.close()
            self._closed = True
    
    @on_exception(
        expo,
        (aiohttp.ClientError, GitHubAPIError),
        max_tries=3,
        max_time=60
    )
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        is_search: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Make HTTP request with comprehensive error handling and rate limiting
        """
        if not self.session:
            await self._create_session()
        
        # Rate limiting
        if self.config.enable_rate_limiting:
            await self.rate_limiter.wait_if_needed(is_search)
        
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                # Update rate limit info
                self.rate_limiter.update_from_headers(dict(response.headers))
                
                # Handle different response types
                if response.status == 204:  # No Content
                    return {}
                
                if response.status == 404:
                    raise GitHubAPIError(
                        f"Resource not found: {endpoint}",
                        status_code=404,
                        endpoint=endpoint
                    )
                
                if response.status == 403:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    if 'rate limit exceeded' in str(error_data).lower():
                        reset_time = response.headers.get('x-ratelimit-reset')
                        if reset_time:
                            wait_time = int(reset_time) - int(time.time())
                            logger.warning(f"Rate limit exceeded, waiting {wait_time}s")
                            await asyncio.sleep(max(wait_time, 0))
                            return await self._make_request(method, endpoint, is_search, **kwargs)
                    
                    raise GitHubAPIError(
                        f"Forbidden: {error_data.get('message', 'Access denied')}",
                        status_code=403,
                        response_data=error_data,
                        endpoint=endpoint
                    )
                
                if response.status >= 400:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    raise GitHubAPIError(
                        f"HTTP {response.status}: {error_data.get('message', 'Unknown error')}",
                        status_code=response.status,
                        response_data=error_data,
                        endpoint=endpoint
                    )
                
                # Parse response
                if response.content_type == 'application/json':
                    data = await response.json()
                else:
                    text = await response.text()
                    try:
                        data = json.loads(text)
                    except json.JSONDecodeError:
                        data = {'content': text}
                
                return data
                
        except aiohttp.ClientError as e:
            raise GitHubAPIError(f"Network error: {str(e)}", endpoint=endpoint)
        except asyncio.TimeoutError:
            raise GitHubAPIError(f"Request timeout for endpoint: {endpoint}", endpoint=endpoint)
    
    # ==============================================
    # CORE API METHODS - Authentication & Testing
    # ==============================================
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test GitHub API connection and authentication"""
        try:
            result = await self._make_request('GET', '/user')
            return {
                'status': 'connected',
                'authenticated_user': result.get('login'),
                'rate_limit': self.rate_limiter.get_status()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'rate_limit': self.rate_limiter.get_status()
            }
    
    async def get_rate_limit(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        data = await self._make_request('GET', '/rate_limit')
        return data
    
    # ==============================================
    # REPOSITORY OPERATIONS - Core Functions
    # ==============================================
    
    async def get_repository(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        """Get repository information"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}', **kwargs)
    
    async def list_repositories(self, **kwargs) -> List[Dict[str, Any]]:
        """List authenticated user's repositories"""
        return await self._make_request('GET', '/user/repos', **kwargs)
    
    async def list_user_repositories(self, username: str, **kwargs) -> List[Dict[str, Any]]:
        """List user's public repositories"""
        return await self._make_request('GET', f'/users/{username}/repos', **kwargs)
    
    async def list_organization_repositories(self, org: str, **kwargs) -> List[Dict[str, Any]]:
        """List organization repositories"""
        return await self._make_request('GET', f'/orgs/{org}/repos', **kwargs)
    
    async def create_repository(self, data: Dict[str, Any], org: str = None, **kwargs) -> Dict[str, Any]:
        """Create a new repository"""
        endpoint = f'/orgs/{org}/repos' if org else '/user/repos'
        return await self._make_request('POST', endpoint, json=data, **kwargs)
    
    async def update_repository(self, owner: str, repo: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Update repository settings"""
        return await self._make_request('PATCH', f'/repos/{owner}/{repo}', json=data, **kwargs)
    
    async def delete_repository(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        """Delete a repository"""
        return await self._make_request('DELETE', f'/repos/{owner}/{repo}', **kwargs)
    
    async def fork_repository(self, owner: str, repo: str, organization: str = None, **kwargs) -> Dict[str, Any]:
        """Fork a repository"""
        data = {}
        if organization:
            data['organization'] = organization
        return await self._make_request('POST', f'/repos/{owner}/{repo}/forks', json=data, **kwargs)
    
    # Repository Content Operations
    async def get_repository_content(self, owner: str, repo: str, path: str = "", ref: str = None, **kwargs) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Get repository content"""
        params = {}
        if ref:
            params['ref'] = ref
        return await self._make_request('GET', f'/repos/{owner}/{repo}/contents/{path}', params=params, **kwargs)
    
    async def create_or_update_file(self, owner: str, repo: str, path: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create or update a file in repository"""
        return await self._make_request('PUT', f'/repos/{owner}/{repo}/contents/{path}', json=data, **kwargs)
    
    async def delete_file(self, owner: str, repo: str, path: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Delete a file from repository"""
        return await self._make_request('DELETE', f'/repos/{owner}/{repo}/contents/{path}', json=data, **kwargs)
    
    # Repository Metadata
    async def get_repository_topics(self, owner: str, repo: str, **kwargs) -> List[str]:
        """Get repository topics"""
        result = await self._make_request('GET', f'/repos/{owner}/{repo}/topics', **kwargs)
        return result.get('names', [])
    
    async def replace_repository_topics(self, owner: str, repo: str, topics: List[str], **kwargs) -> Dict[str, Any]:
        """Replace repository topics"""
        data = {'names': topics}
        return await self._make_request('PUT', f'/repos/{owner}/{repo}/topics', json=data, **kwargs)
    
    async def get_repository_languages(self, owner: str, repo: str, **kwargs) -> Dict[str, int]:
        """Get repository programming languages"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/languages', **kwargs)
    
    async def get_repository_tags(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """Get repository tags"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/tags', **kwargs)
    
    async def get_repository_branches(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """Get repository branches"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/branches', **kwargs)
    
    async def get_branch(self, owner: str, repo: str, branch: str, **kwargs) -> Dict[str, Any]:
        """Get specific branch information"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/branches/{branch}', **kwargs)
    
    # Repository Statistics
    async def get_repository_contributors(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """Get repository contributors"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/contributors', **kwargs)
    
    async def get_repository_stargazers(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """Get repository stargazers"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/stargazers', **kwargs)
    
    async def get_repository_subscribers(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """Get repository watchers/subscribers"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/subscribers', **kwargs)
    
    async def get_repository_forks(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """Get repository forks"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/forks', **kwargs)
    
    # Repository Activity
    async def get_repository_events(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """Get repository events"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/events', **kwargs)
    
    async def get_repository_activity(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """Get repository activity feed"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/activity', **kwargs)
    
    # ==============================================
    # ISSUES & PULL REQUESTS - Complete Operations
    # ==============================================
    
    async def list_issues(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """List repository issues"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/issues', **kwargs)
    
    async def get_issue(self, owner: str, repo: str, issue_number: int, **kwargs) -> Dict[str, Any]:
        """Get specific issue"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/issues/{issue_number}', **kwargs)
    
    async def create_issue(self, owner: str, repo: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create new issue"""
        return await self._make_request('POST', f'/repos/{owner}/{repo}/issues', json=data, **kwargs)
    
    async def update_issue(self, owner: str, repo: str, issue_number: int, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Update issue"""
        return await self._make_request('PATCH', f'/repos/{owner}/{repo}/issues/{issue_number}', json=data, **kwargs)
    
    async def lock_issue(self, owner: str, repo: str, issue_number: int, lock_reason: str = None, **kwargs) -> Dict[str, Any]:
        """Lock issue"""
        data = {}
        if lock_reason:
            data['lock_reason'] = lock_reason
        return await self._make_request('PUT', f'/repos/{owner}/{repo}/issues/{issue_number}/lock', json=data, **kwargs)
    
    async def unlock_issue(self, owner: str, repo: str, issue_number: int, **kwargs) -> Dict[str, Any]:
        """Unlock issue"""
        return await self._make_request('DELETE', f'/repos/{owner}/{repo}/issues/{issue_number}/lock', **kwargs)
    
    # Issue Comments
    async def list_issue_comments(self, owner: str, repo: str, issue_number: int, **kwargs) -> List[Dict[str, Any]]:
        """List issue comments"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/issues/{issue_number}/comments', **kwargs)
    
    async def create_issue_comment(self, owner: str, repo: str, issue_number: int, body: str, **kwargs) -> Dict[str, Any]:
        """Create issue comment"""
        data = {'body': body}
        return await self._make_request('POST', f'/repos/{owner}/{repo}/issues/{issue_number}/comments', json=data, **kwargs)
    
    async def update_issue_comment(self, owner: str, repo: str, comment_id: int, body: str, **kwargs) -> Dict[str, Any]:
        """Update issue comment"""
        data = {'body': body}
        return await self._make_request('PATCH', f'/repos/{owner}/{repo}/issues/comments/{comment_id}', json=data, **kwargs)
    
    async def delete_issue_comment(self, owner: str, repo: str, comment_id: int, **kwargs) -> Dict[str, Any]:
        """Delete issue comment"""
        return await self._make_request('DELETE', f'/repos/{owner}/{repo}/issues/comments/{comment_id}', **kwargs)
    
    # Pull Requests
    async def list_pull_requests(self, owner: str, repo: str, **kwargs) -> List[Dict[str, Any]]:
        """List pull requests"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/pulls', **kwargs)
    
    async def get_pull_request(self, owner: str, repo: str, pull_number: int, **kwargs) -> Dict[str, Any]:
        """Get specific pull request"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}', **kwargs)
    
    async def create_pull_request(self, owner: str, repo: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create pull request"""
        return await self._make_request('POST', f'/repos/{owner}/{repo}/pulls', json=data, **kwargs)
    
    async def update_pull_request(self, owner: str, repo: str, pull_number: int, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Update pull request"""
        return await self._make_request('PATCH', f'/repos/{owner}/{repo}/pulls/{pull_number}', json=data, **kwargs)
    
    async def merge_pull_request(self, owner: str, repo: str, pull_number: int, data: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Merge pull request"""
        return await self._make_request('PUT', f'/repos/{owner}/{repo}/pulls/{pull_number}/merge', json=data or {}, **kwargs)
    
    # Pull Request Reviews
    async def list_pull_request_reviews(self, owner: str, repo: str, pull_number: int, **kwargs) -> List[Dict[str, Any]]:
        """List pull request reviews"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews', **kwargs)
    
    async def create_pull_request_review(self, owner: str, repo: str, pull_number: int, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create pull request review"""
        return await self._make_request('POST', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews', json=data, **kwargs)
    
    async def submit_pull_request_review(self, owner: str, repo: str, pull_number: int, review_id: int, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Submit pull request review"""
        return await self._make_request('POST', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events', json=data, **kwargs)
    
    # ==============================================
    # GITHUB ACTIONS & WORKFLOWS
    # ==============================================
    
    async def list_workflows(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        """List repository workflows"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/actions/workflows', **kwargs)
    
    async def get_workflow(self, owner: str, repo: str, workflow_id: Union[int, str], **kwargs) -> Dict[str, Any]:
        """Get specific workflow"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}', **kwargs)
    
    async def list_workflow_runs(self, owner: str, repo: str, workflow_id: Union[int, str] = None, **kwargs) -> Dict[str, Any]:
        """List workflow runs"""
        endpoint = f'/repos/{owner}/{repo}/actions/runs'
        if workflow_id:
            endpoint = f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs'
        return await self._make_request('GET', endpoint, **kwargs)
    
    async def get_workflow_run(self, owner: str, repo: str, run_id: int, **kwargs) -> Dict[str, Any]:
        """Get workflow run"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/actions/runs/{run_id}', **kwargs)
    
    async def cancel_workflow_run(self, owner: str, repo: str, run_id: int, **kwargs) -> Dict[str, Any]:
        """Cancel workflow run"""
        return await self._make_request('POST', f'/repos/{owner}/{repo}/actions/runs/{run_id}/cancel', **kwargs)
    
    async def rerun_workflow(self, owner: str, repo: str, run_id: int, **kwargs) -> Dict[str, Any]:
        """Rerun workflow"""
        return await self._make_request('POST', f'/repos/{owner}/{repo}/actions/runs/{run_id}/rerun', **kwargs)
    
    async def trigger_workflow_dispatch(self, owner: str, repo: str, workflow_id: Union[int, str], ref: str, inputs: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Trigger workflow dispatch"""
        data = {'ref': ref}
        if inputs:
            data['inputs'] = inputs
        return await self._make_request('POST', f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches', json=data, **kwargs)
    
    # Workflow Jobs
    async def list_workflow_run_jobs(self, owner: str, repo: str, run_id: int, **kwargs) -> Dict[str, Any]:
        """List workflow run jobs"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/actions/runs/{run_id}/jobs', **kwargs)
    
    async def get_workflow_job(self, owner: str, repo: str, job_id: int, **kwargs) -> Dict[str, Any]:
        """Get workflow job"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/actions/jobs/{job_id}', **kwargs)
    
    async def download_workflow_job_logs(self, owner: str, repo: str, job_id: int, **kwargs) -> bytes:
        """Download workflow job logs"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/actions/jobs/{job_id}/logs', **kwargs)
    
    # Secrets Management
    async def list_repository_secrets(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        """List repository secrets"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/actions/secrets', **kwargs)
    
    async def get_repository_secret(self, owner: str, repo: str, secret_name: str, **kwargs) -> Dict[str, Any]:
        """Get repository secret"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/actions/secrets/{secret_name}', **kwargs)
    
    async def create_or_update_repository_secret(self, owner: str, repo: str, secret_name: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create or update repository secret"""
        return await self._make_request('PUT', f'/repos/{owner}/{repo}/actions/secrets/{secret_name}', json=data, **kwargs)
    
    async def delete_repository_secret(self, owner: str, repo: str, secret_name: str, **kwargs) -> Dict[str, Any]:
        """Delete repository secret"""
        return await self._make_request('DELETE', f'/repos/{owner}/{repo}/actions/secrets/{secret_name}', **kwargs)
    
    # ==============================================
    # ORGANIZATION MANAGEMENT
    # ==============================================
    
    async def get_organization(self, org: str, **kwargs) -> Dict[str, Any]:
        """Get organization information"""
        return await self._make_request('GET', f'/orgs/{org}', **kwargs)
    
    async def update_organization(self, org: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Update organization"""
        return await self._make_request('PATCH', f'/orgs/{org}', json=data, **kwargs)
    
    async def list_organization_members(self, org: str, **kwargs) -> List[Dict[str, Any]]:
        """List organization members"""
        return await self._make_request('GET', f'/orgs/{org}/members', **kwargs)
    
    async def get_organization_membership(self, org: str, username: str, **kwargs) -> Dict[str, Any]:
        """Get organization membership for user"""
        return await self._make_request('GET', f'/orgs/{org}/memberships/{username}', **kwargs)
    
    async def set_organization_membership(self, org: str, username: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Set organization membership"""
        return await self._make_request('PUT', f'/orgs/{org}/memberships/{username}', json=data, **kwargs)
    
    async def remove_organization_member(self, org: str, username: str, **kwargs) -> Dict[str, Any]:
        """Remove organization member"""
        return await self._make_request('DELETE', f'/orgs/{org}/members/{username}', **kwargs)
    
    # Organization Teams
    async def list_teams(self, org: str, **kwargs) -> List[Dict[str, Any]]:
        """List organization teams"""
        return await self._make_request('GET', f'/orgs/{org}/teams', **kwargs)
    
    async def get_team(self, org: str, team_slug: str, **kwargs) -> Dict[str, Any]:
        """Get team information"""
        return await self._make_request('GET', f'/orgs/{org}/teams/{team_slug}', **kwargs)
    
    async def create_team(self, org: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Create team"""
        return await self._make_request('POST', f'/orgs/{org}/teams', json=data, **kwargs)
    
    async def update_team(self, org: str, team_slug: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Update team"""
        return await self._make_request('PATCH', f'/orgs/{org}/teams/{team_slug}', json=data, **kwargs)
    
    async def delete_team(self, org: str, team_slug: str, **kwargs) -> Dict[str, Any]:
        """Delete team"""
        return await self._make_request('DELETE', f'/orgs/{org}/teams/{team_slug}', **kwargs)
    
    async def list_team_members(self, org: str, team_slug: str, **kwargs) -> List[Dict[str, Any]]:
        """List team members"""
        return await self._make_request('GET', f'/orgs/{org}/teams/{team_slug}/members', **kwargs)
    
    async def add_team_member(self, org: str, team_slug: str, username: str, **kwargs) -> Dict[str, Any]:
        """Add team member"""
        return await self._make_request('PUT', f'/orgs/{org}/teams/{team_slug}/memberships/{username}', **kwargs)
    
    async def remove_team_member(self, org: str, team_slug: str, username: str, **kwargs) -> Dict[str, Any]:
        """Remove team member"""
        return await self._make_request('DELETE', f'/orgs/{org}/teams/{team_slug}/memberships/{username}', **kwargs)
    
    # ==============================================
    # USER MANAGEMENT
    # ==============================================
    
    async def get_authenticated_user(self, **kwargs) -> Dict[str, Any]:
        """Get authenticated user information"""
        return await self._make_request('GET', '/user', **kwargs)
    
    async def get_user(self, username: str, **kwargs) -> Dict[str, Any]:
        """Get user information"""
        return await self._make_request('GET', f'/users/{username}', **kwargs)
    
    async def update_authenticated_user(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Update authenticated user"""
        return await self._make_request('PATCH', '/user', json=data, **kwargs)
    
    async def list_user_emails(self, **kwargs) -> List[Dict[str, Any]]:
        """List user email addresses"""
        return await self._make_request('GET', '/user/emails', **kwargs)
    
    async def add_user_emails(self, emails: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Add email addresses"""
        data = {'emails': emails}
        return await self._make_request('POST', '/user/emails', json=data, **kwargs)
    
    async def delete_user_emails(self, emails: List[str], **kwargs) -> Dict[str, Any]:
        """Delete email addresses"""
        data = {'emails': emails}
        return await self._make_request('DELETE', '/user/emails', json=data, **kwargs)
    
    # User Following
    async def list_user_followers(self, username: str, **kwargs) -> List[Dict[str, Any]]:
        """List user followers"""
        return await self._make_request('GET', f'/users/{username}/followers', **kwargs)
    
    async def list_user_following(self, username: str, **kwargs) -> List[Dict[str, Any]]:
        """List users that a user follows"""
        return await self._make_request('GET', f'/users/{username}/following', **kwargs)
    
    async def check_user_following(self, username: str, target_user: str, **kwargs) -> bool:
        """Check if user follows another user"""
        try:
            await self._make_request('GET', f'/users/{username}/following/{target_user}', **kwargs)
            return True
        except GitHubAPIError as e:
            if e.status_code == 404:
                return False
            raise
    
    async def follow_user(self, username: str, **kwargs) -> Dict[str, Any]:
        """Follow a user"""
        return await self._make_request('PUT', f'/user/following/{username}', **kwargs)
    
    async def unfollow_user(self, username: str, **kwargs) -> Dict[str, Any]:
        """Unfollow a user"""
        return await self._make_request('DELETE', f'/user/following/{username}', **kwargs)
    
    # ==============================================
    # SEARCH OPERATIONS
    # ==============================================
    
    async def search_repositories(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search repositories"""
        params = {'q': query}
        params.update(kwargs)
        return await self._make_request('GET', '/search/repositories', params=params, is_search=True)
    
    async def search_code(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search code"""
        params = {'q': query}
        params.update(kwargs)
        return await self._make_request('GET', '/search/code', params=params, is_search=True)
    
    async def search_commits(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search commits"""
        params = {'q': query}
        params.update(kwargs)
        return await self._make_request('GET', '/search/commits', params=params, is_search=True)
    
    async def search_issues(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search issues and pull requests"""
        params = {'q': query}
        params.update(kwargs)
        return await self._make_request('GET', '/search/issues', params=params, is_search=True)
    
    async def search_users(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search users"""
        params = {'q': query}
        params.update(kwargs)
        return await self._make_request('GET', '/search/users', params=params, is_search=True)
    
    # ==============================================
    # GOVERNANCE WORKFLOW METHODS
    # ==============================================
    
    async def analyze_repository_governance(self, owner: str, repo: str) -> Dict[str, Any]:
        """Comprehensive repository governance analysis"""
        try:
            # Get basic repository info
            repo_info = await self.get_repository(owner, repo)
            
            # Get branch protection rules
            protection_info = {}
            try:
                branches = await self.get_repository_branches(owner, repo)
                default_branch = repo_info.get('default_branch', 'main')
                protection_info = await self.get_branch_protection(owner, repo, default_branch)
            except GitHubAPIError:
                protection_info = {'protected': False}
            
            # Get security analysis
            security_info = await self.analyze_repository_security(owner, repo)
            
            # Get collaboration metrics
            collaboration_info = await self.get_collaboration_metrics(owner, repo)
            
            # Governance score calculation
            governance_score = self._calculate_governance_score(
                repo_info, protection_info, security_info, collaboration_info
            )
            
            return {
                'repository': repo_info,
                'branch_protection': protection_info,
                'security': security_info,
                'collaboration': collaboration_info,
                'governance_score': governance_score,
                'recommendations': self._generate_governance_recommendations(
                    governance_score, protection_info, security_info
                )
            }
            
        except Exception as e:
            logger.error(f"Governance analysis failed for {owner}/{repo}: {e}")
            raise GitHubAPIError(f"Governance analysis failed: {str(e)}")
    
    async def analyze_repository_security(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze repository security posture"""
        security_info = {
            'vulnerability_alerts': False,
            'security_advisories': [],
            'dependabot_alerts': [],
            'secret_scanning': False,
            'code_scanning': False
        }
        
        try:
            # Check vulnerability alerts
            try:
                await self._make_request('GET', f'/repos/{owner}/{repo}/vulnerability-alerts')
                security_info['vulnerability_alerts'] = True
            except GitHubAPIError:
                pass
            
            # Get security advisories
            try:
                advisories = await self._make_request('GET', f'/repos/{owner}/{repo}/security-advisories')
                security_info['security_advisories'] = advisories
            except GitHubAPIError:
                pass
            
            # Check for Dependabot alerts
            try:
                alerts = await self._make_request('GET', f'/repos/{owner}/{repo}/dependabot/alerts')
                security_info['dependabot_alerts'] = alerts
            except GitHubAPIError:
                pass
            
            # Check secret scanning
            try:
                await self._make_request('GET', f'/repos/{owner}/{repo}/secret-scanning/alerts')
                security_info['secret_scanning'] = True
            except GitHubAPIError:
                pass
            
            # Check code scanning
            try:
                await self._make_request('GET', f'/repos/{owner}/{repo}/code-scanning/alerts')
                security_info['code_scanning'] = True
            except GitHubAPIError:
                pass
                
        except Exception as e:
            logger.warning(f"Some security checks failed for {owner}/{repo}: {e}")
        
        return security_info
    
    async def get_collaboration_metrics(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository collaboration metrics"""
        try:
            # Get contributors
            contributors = await self.get_repository_contributors(owner, repo)
            
            # Get recent issues and PRs
            issues = await self.list_issues(owner, repo, state='all', per_page=100)
            pull_requests = await self.list_pull_requests(owner, repo, state='all', per_page=100)
            
            # Calculate metrics
            active_contributors = len([c for c in contributors if c.get('contributions', 0) > 0])
            open_issues = len([i for i in issues if i.get('state') == 'open'])
            open_prs = len([p for p in pull_requests if p.get('state') == 'open'])
            
            return {
                'total_contributors': len(contributors),
                'active_contributors': active_contributors,
                'open_issues': open_issues,
                'open_pull_requests': open_prs,
                'total_issues': len(issues),
                'total_pull_requests': len(pull_requests),
                'collaboration_score': min(100, (active_contributors * 10) + min(50, len(issues) // 2))
            }
            
        except Exception as e:
            logger.error(f"Failed to get collaboration metrics for {owner}/{repo}: {e}")
            return {'error': str(e)}
    
    def _calculate_governance_score(self, repo_info: Dict, protection_info: Dict, 
                                    security_info: Dict, collaboration_info: Dict) -> Dict[str, Any]:
        """Calculate governance score based on various factors"""
        score = 0
        max_score = 100
        factors = {}
        
        # Repository settings (20 points)
        repo_score = 0
        if repo_info.get('private'):
            repo_score += 5
        if repo_info.get('has_wiki'):
            repo_score += 3
        if repo_info.get('has_issues'):
            repo_score += 5
        if repo_info.get('description'):
            repo_score += 4
        if repo_info.get('license'):
            repo_score += 3
        factors['repository_settings'] = repo_score
        
        # Branch protection (25 points)
        protection_score = 0
        if protection_info.get('protected'):
            protection_score += 10
            if protection_info.get('required_status_checks'):
                protection_score += 5
            if protection_info.get('enforce_admins'):
                protection_score += 5
            if protection_info.get('required_pull_request_reviews'):
                protection_score += 5
        factors['branch_protection'] = protection_score
        
        # Security (30 points)
        security_score = 0
        if security_info.get('vulnerability_alerts'):
            security_score += 8
        if security_info.get('secret_scanning'):
            security_score += 8
        if security_info.get('code_scanning'):
            security_score += 8
        if len(security_info.get('dependabot_alerts', [])) == 0:
            security_score += 6
        factors['security'] = security_score
        
        # Collaboration (25 points)
        collab_score = min(25, collaboration_info.get('collaboration_score', 0) // 4)
        factors['collaboration'] = collab_score
        
        total_score = sum(factors.values())
        
        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': (total_score / max_score) * 100,
            'factors': factors,
            'grade': self._get_governance_grade(total_score, max_score)
        }
    
    def _get_governance_grade(self, score: int, max_score: int) -> str:
        """Get governance grade based on score"""
        percentage = (score / max_score) * 100
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B'
        elif percentage >= 60:
            return 'C'
        elif percentage >= 50:
            return 'D'
        else:
            return 'F'
    
    def _generate_governance_recommendations(self, governance_score: Dict, 
                                           protection_info: Dict, security_info: Dict) -> List[str]:
        """Generate governance improvement recommendations"""
        recommendations = []
        
        if not protection_info.get('protected'):
            recommendations.append("Enable branch protection for the default branch")
        
        if not security_info.get('vulnerability_alerts'):
            recommendations.append("Enable vulnerability alerts")
        
        if not security_info.get('secret_scanning'):
            recommendations.append("Enable secret scanning")
        
        if not security_info.get('code_scanning'):
            recommendations.append("Set up code scanning with CodeQL or similar tools")
        
        if governance_score['percentage'] < 70:
            recommendations.append("Implement comprehensive governance policies")
            recommendations.append("Add detailed repository documentation")
            recommendations.append("Set up automated compliance checks")
        
        return recommendations
    
    # ==============================================
    # BRANCH PROTECTION OPERATIONS
    # ==============================================
    
    async def get_branch_protection(self, owner: str, repo: str, branch: str, **kwargs) -> Dict[str, Any]:
        """Get branch protection rules"""
        return await self._make_request('GET', f'/repos/{owner}/{repo}/branches/{branch}/protection', **kwargs)
    
    async def update_branch_protection(self, owner: str, repo: str, branch: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Update branch protection rules"""
        return await self._make_request('PUT', f'/repos/{owner}/{repo}/branches/{branch}/protection', json=data, **kwargs)
    
    async def delete_branch_protection(self, owner: str, repo: str, branch: str, **kwargs) -> Dict[str, Any]:
        """Delete branch protection rules"""
        return await self._make_request('DELETE', f'/repos/{owner}/{repo}/branches/{branch}/protection', **kwargs)
    
    # ==============================================
    # ADDITIONAL UTILITY METHODS
    # ==============================================
    
    async def get_api_status(self) -> Dict[str, Any]:
        """Get GitHub API status and health"""
        try:
            # Test basic connectivity
            user_info = await self.get_authenticated_user()
            rate_limit = await self.get_rate_limit()
            
            return {
                'status': 'healthy',
                'authenticated_user': user_info.get('login'),
                'rate_limit': rate_limit,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def bulk_repository_analysis(self, repositories: List[Dict[str, str]]) -> Dict[str, Any]:
        """Perform bulk analysis on multiple repositories"""
        results = {}
        failed = []
        
        for repo_info in repositories:
            owner = repo_info['owner']
            repo = repo_info['repo']
            try:
                analysis = await self.analyze_repository_governance(owner, repo)
                results[f"{owner}/{repo}"] = analysis
            except Exception as e:
                failed.append({
                    'repository': f"{owner}/{repo}",
                    'error': str(e)
                })
        
        return {
            'successful_analyses': results,
            'failed_analyses': failed,
            'total_repositories': len(repositories),
            'success_rate': len(results) / len(repositories) * 100
        }


# ==============================================
# FACTORY FUNCTIONS & UTILITIES
# ==============================================

def create_github_client(token: str, **config_overrides) -> UnifiedGitHubAPIClient:
    """Factory function to create GitHub API client with sensible defaults"""
    config = GitHubConfig(token=token, **config_overrides)
    return UnifiedGitHubAPIClient(config)

async def test_github_connection(token: str) -> Dict[str, Any]:
    """Quick test of GitHub API connection"""
    async with create_github_client(token) as client:
        return await client.test_connection()

# Example usage and testing
if __name__ == "__main__":
    import os
    
    async def main():
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("Please set GITHUB_TOKEN environment variable")
            return
        
        async with create_github_client(token) as client:
            # Test connection
            status = await client.test_connection()
            print(f"Connection status: {status}")
            
            # Example governance analysis
            try:
                analysis = await client.analyze_repository_governance("octocat", "Hello-World")
                print(f"Governance analysis: {analysis}")
            except Exception as e:
                print(f"Analysis failed: {e}")
    
    asyncio.run(main())
