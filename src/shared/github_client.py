"""
GitHub API Client for GitHub Governance Factory
Comprehensive GitHub API wrapper for all governance operations
"""

import os
import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class GitHubAPIClient:
    """
    Comprehensive GitHub API client for governance operations
    Implements all GitHub API functions needed for issue management, project governance, and automation
    """
    
    def __init__(self, token: Optional[str] = None, api_url: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.api_url = api_url or os.getenv('GITHUB_API_URL', 'https://api.github.com')
        
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass token parameter.")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Governance-Factory/1.0.0'
        }
        
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    # =============================================================================
    # REPOSITORY OPERATIONS
    # =============================================================================
    
    async def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        url = f"{self.api_url}/repos/{owner}/{repo}"
        return await self._make_request('GET', url)
    
    async def list_repositories(self, owner: str, type: str = "all") -> List[Dict[str, Any]]:
        """List repositories for an owner"""
        url = f"{self.api_url}/users/{owner}/repos"
        params = {'type': type, 'per_page': 100}
        return await self._make_request('GET', url, params=params)
    
    async def create_repository(self, name: str, description: str = "", private: bool = False, owner: Optional[str] = None) -> Dict[str, Any]:
        """Create a new repository"""
        url = f"{self.api_url}/user/repos"
        if owner:
            url = f"{self.api_url}/orgs/{owner}/repos"
        
        data = {
            'name': name,
            'description': description,
            'private': private,
            'auto_init': True,
            'gitignore_template': 'Python'
        }
        return await self._make_request('POST', url, json=data)
    
    # =============================================================================
    # ISSUE OPERATIONS
    # =============================================================================
    
    async def create_issue(self, owner: str, repo: str, title: str, body: str = "", 
                          labels: List[str] = None, assignees: List[str] = None,
                          milestone: Optional[int] = None) -> Dict[str, Any]:
        """Create a new issue"""
        url = f"{self.api_url}/repos/{owner}/{repo}/issues"
        
        data = {
            'title': title,
            'body': body,
            'labels': labels or [],
            'assignees': assignees or []
        }
        
        if milestone:
            data['milestone'] = milestone
        
        return await self._make_request('POST', url, json=data)
    
    async def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Get a specific issue"""
        url = f"{self.api_url}/repos/{owner}/{repo}/issues/{issue_number}"
        return await self._make_request('GET', url)
    
    async def list_issues(self, owner: str, repo: str, state: str = "open", 
                         labels: List[str] = None, assignee: str = None,
                         milestone: Union[str, int] = None) -> List[Dict[str, Any]]:
        """List issues for a repository"""
        url = f"{self.api_url}/repos/{owner}/{repo}/issues"
        
        params = {
            'state': state,
            'per_page': 100
        }
        
        if labels:
            params['labels'] = ','.join(labels)
        if assignee:
            params['assignee'] = assignee
        if milestone:
            params['milestone'] = milestone
        
        return await self._make_request('GET', url, params=params)
    
    async def update_issue(self, owner: str, repo: str, issue_number: int,
                          title: Optional[str] = None, body: Optional[str] = None,
                          state: Optional[str] = None, labels: List[str] = None,
                          assignees: List[str] = None) -> Dict[str, Any]:
        """Update an existing issue"""
        url = f"{self.api_url}/repos/{owner}/{repo}/issues/{issue_number}"
        
        data = {}
        if title is not None:
            data['title'] = title
        if body is not None:
            data['body'] = body
        if state is not None:
            data['state'] = state
        if labels is not None:
            data['labels'] = labels
        if assignees is not None:
            data['assignees'] = assignees
        
        return await self._make_request('PATCH', url, json=data)
    
    async def close_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Close an issue"""
        return await self.update_issue(owner, repo, issue_number, state='closed')
    
    async def reopen_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """Reopen an issue"""
        return await self.update_issue(owner, repo, issue_number, state='open')
    
    # =============================================================================
    # ISSUE COMMENTS
    # =============================================================================
    
    async def create_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
        """Create a comment on an issue"""
        url = f"{self.api_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        data = {'body': body}
        return await self._make_request('POST', url, json=data)
    
    async def list_issue_comments(self, owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]:
        """List comments on an issue"""
        url = f"{self.api_url}/repos/{owner}/{repo}/issues/{issue_number}/comments"
        return await self._make_request('GET', url)
    
    async def update_issue_comment(self, owner: str, repo: str, comment_id: int, body: str) -> Dict[str, Any]:
        """Update an issue comment"""
        url = f"{self.api_url}/repos/{owner}/{repo}/issues/comments/{comment_id}"
        data = {'body': body}
        return await self._make_request('PATCH', url, json=data)
    
    # =============================================================================
    # LABELS
    # =============================================================================
    
    async def create_label(self, owner: str, repo: str, name: str, color: str, description: str = "") -> Dict[str, Any]:
        """Create a label"""
        url = f"{self.api_url}/repos/{owner}/{repo}/labels"
        data = {
            'name': name,
            'color': color.lstrip('#'),  # Remove # if present
            'description': description
        }
        return await self._make_request('POST', url, json=data)
    
    async def list_labels(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List all labels in a repository"""
        url = f"{self.api_url}/repos/{owner}/{repo}/labels"
        return await self._make_request('GET', url)
    
    async def delete_label(self, owner: str, repo: str, name: str) -> bool:
        """Delete a label"""
        url = f"{self.api_url}/repos/{owner}/{repo}/labels/{name}"
        try:
            await self._make_request('DELETE', url)
            return True
        except Exception:
            return False
    
    # =============================================================================
    # MILESTONES
    # =============================================================================
    
    async def create_milestone(self, owner: str, repo: str, title: str, description: str = "",
                              due_on: Optional[str] = None, state: str = "open") -> Dict[str, Any]:
        """Create a milestone"""
        url = f"{self.api_url}/repos/{owner}/{repo}/milestones"
        data = {
            'title': title,
            'description': description,
            'state': state
        }
        if due_on:
            data['due_on'] = due_on
        
        return await self._make_request('POST', url, json=data)
    
    async def list_milestones(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """List milestones in a repository"""
        url = f"{self.api_url}/repos/{owner}/{repo}/milestones"
        params = {'state': state}
        return await self._make_request('GET', url, params=params)
    
    async def update_milestone(self, owner: str, repo: str, milestone_number: int,
                              title: Optional[str] = None, description: Optional[str] = None,
                              state: Optional[str] = None) -> Dict[str, Any]:
        """Update a milestone"""
        url = f"{self.api_url}/repos/{owner}/{repo}/milestones/{milestone_number}"
        
        data = {}
        if title is not None:
            data['title'] = title
        if description is not None:
            data['description'] = description
        if state is not None:
            data['state'] = state
        
        return await self._make_request('PATCH', url, json=data)
    
    # =============================================================================
    # PROJECTS (GitHub Projects v2)
    # =============================================================================
    
    async def list_repository_projects(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List projects for a repository"""
        url = f"{self.api_url}/repos/{owner}/{repo}/projects"
        headers = {**self.headers, 'Accept': 'application/vnd.github.inertia-preview+json'}
        return await self._make_request('GET', url, headers=headers)
    
    async def create_repository_project(self, owner: str, repo: str, name: str, body: str = "") -> Dict[str, Any]:
        """Create a project for a repository"""
        url = f"{self.api_url}/repos/{owner}/{repo}/projects"
        headers = {**self.headers, 'Accept': 'application/vnd.github.inertia-preview+json'}
        data = {
            'name': name,
            'body': body
        }
        return await self._make_request('POST', url, json=data, headers=headers)
    
    # =============================================================================
    # PULL REQUESTS
    # =============================================================================
    
    async def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str,
                                 body: str = "", draft: bool = False) -> Dict[str, Any]:
        """Create a pull request"""
        url = f"{self.api_url}/repos/{owner}/{repo}/pulls"
        data = {
            'title': title,
            'head': head,
            'base': base,
            'body': body,
            'draft': draft
        }
        return await self._make_request('POST', url, json=data)
    
    async def list_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]:
        """List pull requests"""
        url = f"{self.api_url}/repos/{owner}/{repo}/pulls"
        params = {'state': state, 'per_page': 100}
        return await self._make_request('GET', url, params=params)
    
    async def get_pull_request(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """Get a specific pull request"""
        url = f"{self.api_url}/repos/{owner}/{repo}/pulls/{pull_number}"
        return await self._make_request('GET', url)
    
    # =============================================================================
    # BRANCHES
    # =============================================================================
    
    async def list_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List branches in a repository"""
        url = f"{self.api_url}/repos/{owner}/{repo}/branches"
        return await self._make_request('GET', url)
    
    async def get_branch(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """Get a specific branch"""
        url = f"{self.api_url}/repos/{owner}/{repo}/branches/{branch}"
        return await self._make_request('GET', url)
    
    async def create_branch(self, owner: str, repo: str, branch: str, sha: str) -> Dict[str, Any]:
        """Create a new branch"""
        url = f"{self.api_url}/repos/{owner}/{repo}/git/refs"
        data = {
            'ref': f'refs/heads/{branch}',
            'sha': sha
        }
        return await self._make_request('POST', url, json=data)
    
    # =============================================================================
    # WEBHOOKS
    # =============================================================================
    
    async def create_webhook(self, owner: str, repo: str, config: Dict[str, Any],
                           events: List[str] = None, active: bool = True) -> Dict[str, Any]:
        """Create a webhook"""
        url = f"{self.api_url}/repos/{owner}/{repo}/hooks"
        data = {
            'name': 'web',
            'config': config,
            'events': events or ['push', 'issues', 'pull_request'],
            'active': active
        }
        return await self._make_request('POST', url, json=data)
    
    async def list_webhooks(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """List webhooks for a repository"""
        url = f"{self.api_url}/repos/{owner}/{repo}/hooks"
        return await self._make_request('GET', url)
    
    async def delete_webhook(self, owner: str, repo: str, hook_id: int) -> bool:
        """Delete a webhook"""
        url = f"{self.api_url}/repos/{owner}/{repo}/hooks/{hook_id}"
        try:
            await self._make_request('DELETE', url)
            return True
        except Exception:
            return False
    
    # =============================================================================
    # ORGANIZATIONS
    # =============================================================================
    
    async def get_organization(self, org: str) -> Dict[str, Any]:
        """Get organization information"""
        url = f"{self.api_url}/orgs/{org}"
        return await self._make_request('GET', url)
    
    async def list_organization_repositories(self, org: str, type: str = "all") -> List[Dict[str, Any]]:
        """List repositories for an organization"""
        url = f"{self.api_url}/orgs/{org}/repos"
        params = {'type': type, 'per_page': 100}
        return await self._make_request('GET', url, params=params)
    
    async def list_organization_members(self, org: str) -> List[Dict[str, Any]]:
        """List organization members"""
        url = f"{self.api_url}/orgs/{org}/members"
        return await self._make_request('GET', url)
    
    # =============================================================================
    # USER OPERATIONS
    # =============================================================================
    
    async def get_user(self, username: str = None) -> Dict[str, Any]:
        """Get user information (current user if username not provided)"""
        url = f"{self.api_url}/user" if username is None else f"{self.api_url}/users/{username}"
        return await self._make_request('GET', url)
    
    async def list_user_repositories(self, username: str = None, type: str = "owner") -> List[Dict[str, Any]]:
        """List repositories for a user"""
        if username is None:
            url = f"{self.api_url}/user/repos"
        else:
            url = f"{self.api_url}/users/{username}/repos"
        
        params = {'type': type, 'per_page': 100}
        return await self._make_request('GET', url, params=params)
    
    # =============================================================================
    # SEARCH OPERATIONS
    # =============================================================================
    
    async def search_repositories(self, query: str, sort: str = "stars", order: str = "desc") -> Dict[str, Any]:
        """Search repositories"""
        url = f"{self.api_url}/search/repositories"
        params = {'q': query, 'sort': sort, 'order': order}
        return await self._make_request('GET', url, params=params)
    
    async def search_issues(self, query: str, sort: str = "created", order: str = "desc") -> Dict[str, Any]:
        """Search issues and pull requests"""
        url = f"{self.api_url}/search/issues"
        params = {'q': query, 'sort': sort, 'order': order}
        return await self._make_request('GET', url, params=params)
    
    async def search_users(self, query: str, sort: str = "followers", order: str = "desc") -> Dict[str, Any]:
        """Search users"""
        url = f"{self.api_url}/search/users"
        params = {'q': query, 'sort': sort, 'order': order}
        return await self._make_request('GET', url, params=params)
    
    # =============================================================================
    # BATCH OPERATIONS FOR GOVERNANCE
    # =============================================================================
    
    async def create_governance_labels(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Create standard governance labels"""
        governance_labels = [
            {'name': 'epic', 'color': '8B5CF6', 'description': 'Epic-level work item'},
            {'name': 'feature', 'color': '3B82F6', 'description': 'Feature-level work item'},
            {'name': 'task', 'color': '10B981', 'description': 'Task-level work item'},
            {'name': 'governance', 'color': 'F59E0B', 'description': 'Governance-related item'},
            {'name': 'ai-generated', 'color': 'EC4899', 'description': 'Generated by AI'},
            {'name': 'high-priority', 'color': 'EF4444', 'description': 'High priority item'},
            {'name': 'medium-priority', 'color': 'F97316', 'description': 'Medium priority item'},
            {'name': 'low-priority', 'color': '84CC16', 'description': 'Low priority item'}
        ]
        
        created_labels = []
        for label in governance_labels:
            try:
                created_label = await self.create_label(owner, repo, **label)
                created_labels.append(created_label)
            except Exception as e:
                logger.warning(f"Failed to create label {label['name']}: {e}")
        
        return created_labels
    
    async def create_governance_milestones(self, owner: str, repo: str, project_name: str) -> List[Dict[str, Any]]:
        """Create standard governance milestones"""
        milestones = [
            {
                'title': f'{project_name} - Planning Phase',
                'description': 'Initial project planning and requirements gathering'
            },
            {
                'title': f'{project_name} - Development Phase',
                'description': 'Core development and implementation'
            },
            {
                'title': f'{project_name} - Testing Phase',
                'description': 'Quality assurance and testing'
            },
            {
                'title': f'{project_name} - Release Phase',
                'description': 'Final preparation and release'
            }
        ]
        
        created_milestones = []
        for milestone in milestones:
            try:
                created_milestone = await self.create_milestone(owner, repo, **milestone)
                created_milestones.append(created_milestone)
            except Exception as e:
                logger.warning(f"Failed to create milestone {milestone['title']}: {e}")
        
        return created_milestones
    
    async def setup_governance_repository(self, owner: str, repo: str, project_name: str) -> Dict[str, Any]:
        """Setup a repository for governance with labels, milestones, and basic structure"""
        setup_results = {
            'repository': None,
            'labels': [],
            'milestones': [],
            'webhooks': [],
            'errors': []
        }
        
        try:
            # Get repository info
            setup_results['repository'] = await self.get_repository(owner, repo)
            
            # Create governance labels
            setup_results['labels'] = await self.create_governance_labels(owner, repo)
            
            # Create governance milestones
            setup_results['milestones'] = await self.create_governance_milestones(owner, repo, project_name)
            
            logger.info(f"Successfully setup governance for repository {owner}/{repo}")
            
        except Exception as e:
            setup_results['errors'].append(str(e))
            logger.error(f"Failed to setup governance repository: {e}")
        
        return setup_results
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    
    async def _make_request(self, method: str, url: str, params: Dict[str, Any] = None,
                           json: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Any:
        """Make an HTTP request to GitHub API"""
        request_headers = headers or self.headers
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.request(
                    method, url, params=params, json=json, headers=request_headers
                ) as response:
                    if response.status == 204:  # No Content
                        return {}
                    
                    response_data = await response.json()
                    
                    if response.status >= 400:
                        error_msg = f"GitHub API error {response.status}: {response_data.get('message', 'Unknown error')}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    return response_data
                    
            except aiohttp.ClientError as e:
                logger.error(f"HTTP client error: {e}")
                raise
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise
    
    async def test_connection(self) -> bool:
        """Test GitHub API connection"""
        try:
            await self.get_user()
            return True
        except Exception as e:
            logger.error(f"GitHub API connection test failed: {e}")
            return False


# Global GitHub client instance
github_client = GitHubAPIClient()
