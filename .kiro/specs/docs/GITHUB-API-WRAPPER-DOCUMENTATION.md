# GitHub API Wrapper Documentation

## Overview

The GitHub Governance Factory includes a comprehensive GitHub API wrapper (`src/shared/github_client.py`) that provides full coverage of GitHub's REST API v3/v4. This document catalogs all implemented functions and identifies pending functions that should be added.

## Current Implementation Status

### ✅ **FULLY IMPLEMENTED - Core Repository Operations**

#### Repository Management
```python
# Get repository information
async def get_repository(owner: str, repo: str) -> Dict[str, Any]

# List repositories for an owner
async def list_repositories(owner: str, type: str = "all") -> List[Dict[str, Any]]

# Create a new repository  
async def create_repository(name: str, description: str = "", private: bool = False, owner: Optional[str] = None) -> Dict[str, Any]
```

**Usage Example:**
```python
# Get repository details
repo_info = await github_client.get_repository("myorg", "myrepo")

# Create new repository
new_repo = await github_client.create_repository(
    name="new-project",
    description="A new project repository",
    private=False,
    owner="myorg"
)
```

### ✅ **FULLY IMPLEMENTED - Issue Management**

#### Core Issue Operations
```python
# Create a new issue
async def create_issue(owner: str, repo: str, title: str, body: str = "", 
                      labels: List[str] = None, assignees: List[str] = None,
                      milestone: Optional[int] = None) -> Dict[str, Any]

# Get specific issue
async def get_issue(owner: str, repo: str, issue_number: int) -> Dict[str, Any]

# List issues with filtering
async def list_issues(owner: str, repo: str, state: str = "open", 
                     labels: List[str] = None, assignee: str = None,
                     milestone: Union[str, int] = None) -> List[Dict[str, Any]]

# Update existing issue
async def update_issue(owner: str, repo: str, issue_number: int,
                      title: Optional[str] = None, body: Optional[str] = None,
                      state: Optional[str] = None, labels: List[str] = None,
                      assignees: List[str] = None) -> Dict[str, Any]

# Close/reopen issues
async def close_issue(owner: str, repo: str, issue_number: int) -> Dict[str, Any]
async def reopen_issue(owner: str, repo: str, issue_number: int) -> Dict[str, Any]
```

#### Issue Comments
```python
# Create issue comment
async def create_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]

# List issue comments
async def list_issue_comments(owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]

# Update issue comment
async def update_issue_comment(owner: str, repo: str, comment_id: int, body: str) -> Dict[str, Any]
```

**Usage Example:**
```python
# Create governance issue
issue = await github_client.create_issue(
    owner="myorg",
    repo="myrepo",
    title="Epic: User Authentication System",
    body="Comprehensive user authentication with OAuth 2.0...",
    labels=["epic", "high-priority", "governance"],
    assignees=["dev-lead"],
    milestone=1
)

# Add comment with updates
comment = await github_client.create_issue_comment(
    owner="myorg", 
    repo="myrepo",
    issue_number=issue["number"],
    body="Implementation progress: OAuth provider integration completed ✅"
)
```

### ✅ **FULLY IMPLEMENTED - Labels & Milestones**

#### Label Management
```python
# Create label
async def create_label(owner: str, repo: str, name: str, color: str, description: str = "") -> Dict[str, Any]

# List all labels
async def list_labels(owner: str, repo: str) -> List[Dict[str, Any]]

# Delete label
async def delete_label(owner: str, repo: str, name: str) -> bool
```

#### Milestone Management
```python
# Create milestone
async def create_milestone(owner: str, repo: str, title: str, description: str = "",
                          due_on: Optional[str] = None, state: str = "open") -> Dict[str, Any]

# List milestones
async def list_milestones(owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]

# Update milestone
async def update_milestone(owner: str, repo: str, milestone_number: int,
                          title: Optional[str] = None, description: Optional[str] = None,
                          state: Optional[str] = None) -> Dict[str, Any]
```

**Usage Example:**
```python
# Create governance labels
await github_client.create_label("myorg", "myrepo", "epic", "8B5CF6", "Epic-level work item")
await github_client.create_label("myorg", "myrepo", "feature", "3B82F6", "Feature-level work item")

# Create project milestone
milestone = await github_client.create_milestone(
    owner="myorg",
    repo="myrepo", 
    title="Q1 2025 Release",
    description="First quarter feature release",
    due_on="2025-03-31T23:59:59Z"
)
```

### ✅ **FULLY IMPLEMENTED - Pull Requests**

#### Pull Request Operations
```python
# Create pull request
async def create_pull_request(owner: str, repo: str, title: str, head: str, base: str,
                             body: str = "", draft: bool = False) -> Dict[str, Any]

# List pull requests
async def list_pull_requests(owner: str, repo: str, state: str = "open") -> List[Dict[str, Any]]

# Get specific pull request
async def get_pull_request(owner: str, repo: str, pull_number: int) -> Dict[str, Any]
```

### ✅ **FULLY IMPLEMENTED - Branch Management**

#### Branch Operations
```python
# List repository branches
async def list_branches(owner: str, repo: str) -> List[Dict[str, Any]]

# Get specific branch
async def get_branch(owner: str, repo: str, branch: str) -> Dict[str, Any]

# Create new branch
async def create_branch(owner: str, repo: str, branch: str, sha: str) -> Dict[str, Any]
```

### ✅ **FULLY IMPLEMENTED - Webhooks**

#### Webhook Management
```python
# Create webhook
async def create_webhook(owner: str, repo: str, config: Dict[str, Any],
                        events: List[str] = None, active: bool = True) -> Dict[str, Any]

# List webhooks
async def list_webhooks(owner: str, repo: str) -> List[Dict[str, Any]]

# Delete webhook
async def delete_webhook(owner: str, repo: str, hook_id: int) -> bool
```

### ✅ **FULLY IMPLEMENTED - Organization Operations**

#### Organization Management
```python
# Get organization info
async def get_organization(org: str) -> Dict[str, Any]

# List organization repositories
async def list_organization_repositories(org: str, type: str = "all") -> List[Dict[str, Any]]

# List organization members
async def list_organization_members(org: str) -> List[Dict[str, Any]]
```

### ✅ **FULLY IMPLEMENTED - User Operations**

#### User Management
```python
# Get user information
async def get_user(username: str = None) -> Dict[str, Any]

# List user repositories
async def list_user_repositories(username: str = None, type: str = "owner") -> List[Dict[str, Any]]
```

### ✅ **FULLY IMPLEMENTED - Search Operations**

#### Search Functions
```python
# Search repositories
async def search_repositories(query: str, sort: str = "stars", order: str = "desc") -> Dict[str, Any]

# Search issues and pull requests
async def search_issues(query: str, sort: str = "created", order: str = "desc") -> Dict[str, Any]

# Search users
async def search_users(query: str, sort: str = "followers", order: str = "desc") -> Dict[str, Any]
```

### ✅ **FULLY IMPLEMENTED - Project Management**

#### GitHub Projects
```python
# List repository projects
async def list_repository_projects(owner: str, repo: str) -> List[Dict[str, Any]]

# Create repository project
async def create_repository_project(owner: str, repo: str, name: str, body: str = "") -> Dict[str, Any]
```

### ✅ **FULLY IMPLEMENTED - Governance Batch Operations**

#### Automated Governance Setup
```python
# Create standard governance labels
async def create_governance_labels(owner: str, repo: str) -> List[Dict[str, Any]]

# Create governance milestones
async def create_governance_milestones(owner: str, repo: str, project_name: str) -> List[Dict[str, Any]]

# Complete repository governance setup
async def setup_governance_repository(owner: str, repo: str, project_name: str) -> Dict[str, Any]
```

**Usage Example:**
```python
# One-command repository setup
setup_result = await github_client.setup_governance_repository(
    owner="myorg",
    repo="myrepo", 
    project_name="My Amazing Project"
)

# Returns:
# {
#   'repository': {...},
#   'labels': [...],  # 8 governance labels created
#   'milestones': [...],  # 4 project milestones created
#   'errors': []
# }
```

### ✅ **FULLY IMPLEMENTED - Utility Functions**

#### Helper Methods
```python
# Test API connection
async def test_connection() -> bool

# Make raw HTTP request to GitHub API
async def _make_request(method: str, url: str, params: Dict[str, Any] = None,
                       json: Dict[str, Any] = None, headers: Dict[str, str] = None) -> Any
```

---

## 🚧 **PENDING IMPLEMENTATION - Additional GitHub API Functions**

The following GitHub API functions should be added to provide complete coverage:

### 📋 **High Priority - Missing Core Functions**

#### Repository Advanced Operations
```python
# UPDATE A REPOSITORY
async def update_repository(owner: str, repo: str, name: str = None, description: str = None,
                           private: bool = None, default_branch: str = None) -> Dict[str, Any]

# DELETE A REPOSITORY (dangerous operation)
async def delete_repository(owner: str, repo: str) -> bool

# FORK A REPOSITORY
async def fork_repository(owner: str, repo: str, organization: str = None) -> Dict[str, Any]

# LIST REPOSITORY FORKS
async def list_repository_forks(owner: str, repo: str) -> List[Dict[str, Any]]

# GET REPOSITORY TOPICS
async def get_repository_topics(owner: str, repo: str) -> List[str]

# UPDATE REPOSITORY TOPICS
async def update_repository_topics(owner: str, repo: str, topics: List[str]) -> Dict[str, Any]
```

#### Issue Advanced Operations
```python
# DELETE AN ISSUE COMMENT
async def delete_issue_comment(owner: str, repo: str, comment_id: int) -> bool

# LIST ISSUE EVENTS (activity timeline)
async def list_issue_events(owner: str, repo: str, issue_number: int) -> List[Dict[str, Any]]

# LOCK/UNLOCK ISSUE
async def lock_issue(owner: str, repo: str, issue_number: int, lock_reason: str = None) -> bool
async def unlock_issue(owner: str, repo: str, issue_number: int) -> bool

# TRANSFER ISSUE TO ANOTHER REPOSITORY
async def transfer_issue(owner: str, repo: str, issue_number: int, new_owner: str, new_repo: str) -> Dict[str, Any]
```

#### Label Advanced Operations
```python
# UPDATE LABEL
async def update_label(owner: str, repo: str, current_name: str, new_name: str = None,
                      color: str = None, description: str = None) -> Dict[str, Any]

# ADD LABELS TO ISSUE
async def add_labels_to_issue(owner: str, repo: str, issue_number: int, labels: List[str]) -> List[Dict[str, Any]]

# REMOVE LABELS FROM ISSUE
async def remove_labels_from_issue(owner: str, repo: str, issue_number: int, labels: List[str]) -> bool

# REMOVE ALL LABELS FROM ISSUE
async def remove_all_labels_from_issue(owner: str, repo: str, issue_number: int) -> bool
```

#### Milestone Advanced Operations
```python
# DELETE MILESTONE
async def delete_milestone(owner: str, repo: str, milestone_number: int) -> bool

# GET MILESTONE
async def get_milestone(owner: str, repo: str, milestone_number: int) -> Dict[str, Any]
```

### 📋 **Medium Priority - Pull Request Advanced Functions**

#### Pull Request Advanced Operations
```python
# UPDATE PULL REQUEST
async def update_pull_request(owner: str, repo: str, pull_number: int, title: str = None,
                             body: str = None, state: str = None, base: str = None) -> Dict[str, Any]

# MERGE PULL REQUEST
async def merge_pull_request(owner: str, repo: str, pull_number: int, commit_title: str = None,
                            commit_message: str = None, merge_method: str = "merge") -> Dict[str, Any]

# LIST PULL REQUEST FILES
async def list_pull_request_files(owner: str, repo: str, pull_number: int) -> List[Dict[str, Any]]

# LIST PULL REQUEST COMMITS
async def list_pull_request_commits(owner: str, repo: str, pull_number: int) -> List[Dict[str, Any]]

# CREATE PULL REQUEST REVIEW
async def create_pull_request_review(owner: str, repo: str, pull_number: int, body: str = None,
                                    event: str = "COMMENT", comments: List[Dict] = None) -> Dict[str, Any]

# LIST PULL REQUEST REVIEWS
async def list_pull_request_reviews(owner: str, repo: str, pull_number: int) -> List[Dict[str, Any]]

# REQUEST PULL REQUEST REVIEWERS
async def request_pull_request_reviewers(owner: str, repo: str, pull_number: int,
                                       reviewers: List[str] = None, team_reviewers: List[str] = None) -> Dict[str, Any]
```

### 📋 **Medium Priority - File & Content Operations**

#### Repository Content Management
```python
# GET FILE CONTENTS
async def get_file_contents(owner: str, repo: str, path: str, ref: str = None) -> Dict[str, Any]

# CREATE OR UPDATE FILE
async def create_or_update_file(owner: str, repo: str, path: str, message: str, content: str,
                               sha: str = None, branch: str = None) -> Dict[str, Any]

# DELETE FILE
async def delete_file(owner: str, repo: str, path: str, message: str, sha: str, branch: str = None) -> Dict[str, Any]

# LIST DIRECTORY CONTENTS
async def list_directory_contents(owner: str, repo: str, path: str = "", ref: str = None) -> List[Dict[str, Any]]

# GET REPOSITORY README
async def get_repository_readme(owner: str, repo: str, ref: str = None) -> Dict[str, Any]
```

### 📋 **Medium Priority - Git Operations**

#### Git References & Trees
```python
# LIST GIT REFERENCES
async def list_git_references(owner: str, repo: str, namespace: str = None) -> List[Dict[str, Any]]

# GET GIT REFERENCE
async def get_git_reference(owner: str, repo: str, ref: str) -> Dict[str, Any]

# CREATE GIT REFERENCE
async def create_git_reference(owner: str, repo: str, ref: str, sha: str) -> Dict[str, Any]

# UPDATE GIT REFERENCE
async def update_git_reference(owner: str, repo: str, ref: str, sha: str, force: bool = False) -> Dict[str, Any]

# DELETE GIT REFERENCE
async def delete_git_reference(owner: str, repo: str, ref: str) -> bool

# GET GIT COMMIT
async def get_git_commit(owner: str, repo: str, commit_sha: str) -> Dict[str, Any]

# CREATE GIT COMMIT
async def create_git_commit(owner: str, repo: str, message: str, tree: str, parents: List[str]) -> Dict[str, Any]

# GET GIT TREE
async def get_git_tree(owner: str, repo: str, tree_sha: str, recursive: bool = False) -> Dict[str, Any]

# CREATE GIT TREE
async def create_git_tree(owner: str, repo: str, tree: List[Dict], base_tree: str = None) -> Dict[str, Any]
```

### 📋 **Medium Priority - Branch Advanced Operations**

#### Branch Protection & Rules
```python
# GET BRANCH PROTECTION
async def get_branch_protection(owner: str, repo: str, branch: str) -> Dict[str, Any]

# UPDATE BRANCH PROTECTION
async def update_branch_protection(owner: str, repo: str, branch: str, protection_config: Dict) -> Dict[str, Any]

# DELETE BRANCH PROTECTION
async def delete_branch_protection(owner: str, repo: str, branch: str) -> bool

# DELETE BRANCH
async def delete_branch(owner: str, repo: str, branch: str) -> bool

# COMPARE BRANCHES
async def compare_branches(owner: str, repo: str, base: str, head: str) -> Dict[str, Any]
```

### 📋 **Low Priority - Advanced Features**

#### Releases & Tags
```python
# LIST RELEASES
async def list_releases(owner: str, repo: str) -> List[Dict[str, Any]]

# GET LATEST RELEASE
async def get_latest_release(owner: str, repo: str) -> Dict[str, Any]

# GET RELEASE BY TAG
async def get_release_by_tag(owner: str, repo: str, tag: str) -> Dict[str, Any]

# CREATE RELEASE
async def create_release(owner: str, repo: str, tag_name: str, name: str = None,
                        body: str = None, draft: bool = False, prerelease: bool = False) -> Dict[str, Any]

# UPDATE RELEASE
async def update_release(owner: str, repo: str, release_id: int, tag_name: str = None,
                        name: str = None, body: str = None, draft: bool = None, prerelease: bool = None) -> Dict[str, Any]

# DELETE RELEASE
async def delete_release(owner: str, repo: str, release_id: int) -> bool

# LIST TAGS
async def list_tags(owner: str, repo: str) -> List[Dict[str, Any]]

# GET TAG
async def get_tag(owner: str, repo: str, tag_sha: str) -> Dict[str, Any]

# CREATE TAG
async def create_tag(owner: str, repo: str, tag: str, message: str, object: str, type: str) -> Dict[str, Any]
```

#### Repository Statistics & Insights
```python
# GET REPOSITORY STATISTICS
async def get_repository_statistics(owner: str, repo: str) -> Dict[str, Any]

# GET COMMIT ACTIVITY
async def get_commit_activity(owner: str, repo: str) -> List[Dict[str, Any]]

# GET CODE FREQUENCY
async def get_code_frequency(owner: str, repo: str) -> List[List[int]]

# GET CONTRIBUTOR STATISTICS
async def get_contributor_statistics(owner: str, repo: str) -> List[Dict[str, Any]]

# GET REPOSITORY TRAFFIC
async def get_repository_traffic(owner: str, repo: str) -> Dict[str, Any]

# GET REPOSITORY CLONES
async def get_repository_clones(owner: str, repo: str, per: str = "day") -> Dict[str, Any]

# GET POPULAR CONTENT
async def get_popular_content(owner: str, repo: str) -> Dict[str, Any]
```

#### Repository Settings & Configuration
```python
# LIST REPOSITORY COLLABORATORS
async def list_repository_collaborators(owner: str, repo: str) -> List[Dict[str, Any]]

# ADD REPOSITORY COLLABORATOR
async def add_repository_collaborator(owner: str, repo: str, username: str, permission: str = "push") -> bool

# REMOVE REPOSITORY COLLABORATOR
async def remove_repository_collaborator(owner: str, repo: str, username: str) -> bool

# GET REPOSITORY PERMISSIONS
async def get_repository_permissions(owner: str, repo: str, username: str) -> Dict[str, Any]

# LIST REPOSITORY LANGUAGES
async def list_repository_languages(owner: str, repo: str) -> Dict[str, int]

# LIST REPOSITORY TEAMS (for organization repos)
async def list_repository_teams(owner: str, repo: str) -> List[Dict[str, Any]]
```

#### Notifications & Subscriptions
```python
# GET REPOSITORY SUBSCRIPTION
async def get_repository_subscription(owner: str, repo: str) -> Dict[str, Any]

# SET REPOSITORY SUBSCRIPTION
async def set_repository_subscription(owner: str, repo: str, subscribed: bool = True,
                                     ignored: bool = False) -> Dict[str, Any]

# DELETE REPOSITORY SUBSCRIPTION
async def delete_repository_subscription(owner: str, repo: str) -> bool

# LIST REPOSITORY NOTIFICATIONS
async def list_repository_notifications(owner: str, repo: str, all: bool = False,
                                       participating: bool = False, since: str = None) -> List[Dict[str, Any]]

# MARK REPOSITORY NOTIFICATIONS AS READ
async def mark_repository_notifications_as_read(owner: str, repo: str, last_read_at: str = None) -> bool
```

#### Security & Vulnerability Management
```python
# LIST SECURITY ADVISORIES
async def list_security_advisories(owner: str, repo: str) -> List[Dict[str, Any]]

# GET SECURITY ADVISORY
async def get_security_advisory(owner: str, repo: str, advisory_id: str) -> Dict[str, Any]

# LIST VULNERABILITY ALERTS
async def list_vulnerability_alerts(owner: str, repo: str) -> List[Dict[str, Any]]

# ENABLE VULNERABILITY ALERTS
async def enable_vulnerability_alerts(owner: str, repo: str) -> bool

# DISABLE VULNERABILITY ALERTS
async def disable_vulnerability_alerts(owner: str, repo: str) -> bool
```

---

## 🎯 **Implementation Priority Recommendations**

### **Priority 1: Core Missing Functions (Implement First)**
1. **Repository Operations**: `update_repository`, `fork_repository`, `get_repository_topics`
2. **Issue Advanced**: `delete_issue_comment`, `list_issue_events`, `lock_issue`
3. **Label Management**: `update_label`, `add_labels_to_issue`, `remove_labels_from_issue`
4. **Milestone Advanced**: `delete_milestone`, `get_milestone`

### **Priority 2: Content & File Management**
1. **File Operations**: `get_file_contents`, `create_or_update_file`, `delete_file`
2. **Directory Listing**: `list_directory_contents`, `get_repository_readme`

### **Priority 3: Pull Request Enhancement**
1. **PR Advanced**: `update_pull_request`, `merge_pull_request`, `list_pull_request_files`
2. **PR Reviews**: `create_pull_request_review`, `list_pull_request_reviews`

### **Priority 4: Git Operations**
1. **Git References**: `list_git_references`, `get_git_reference`, `create_git_reference`
2. **Branch Protection**: `get_branch_protection`, `update_branch_protection`

### **Priority 5: Advanced Features**
1. **Releases**: `list_releases`, `create_release`, `get_latest_release`
2. **Statistics**: `get_repository_statistics`, `get_commit_activity`
3. **Security**: `list_security_advisories`, `enable_vulnerability_alerts`

---

## 📚 **Usage Patterns in Current Implementation**

### **Governance Automation Workflow**
```python
# 1. Setup repository for governance
setup_result = await github_client.setup_governance_repository(
    owner="myorg", repo="myrepo", project_name="My Project"
)

# 2. Create governance issues
epic_issue = await github_client.create_issue(
    owner="myorg", repo="myrepo",
    title="Epic: User Authentication", 
    body="Comprehensive authentication system...",
    labels=["epic", "high-priority"], 
    milestone=setup_result['milestones'][0]['number']
)

# 3. Add progress comments
await github_client.create_issue_comment(
    owner="myorg", repo="myrepo",
    issue_number=epic_issue["number"],
    body="✅ OAuth provider integration completed"
)
```

### **Repository Management Workflow**
```python
# 1. Get repository information
repo_info = await github_client.get_repository("myorg", "myrepo")

# 2. List all issues for analysis
issues = await github_client.list_issues(
    owner="myorg", repo="myrepo",
    state="all", labels=["epic", "feature"]
)

# 3. Create project milestones
milestone = await github_client.create_milestone(
    owner="myorg", repo="myrepo",
    title="Q1 2025 Release",
    description="First quarter deliverables"
)
```

### **Search & Discovery Workflow**
```python
# 1. Search for governance-related issues
governance_issues = await github_client.search_issues(
    query="repo:myorg/myrepo label:governance state:open"
)

# 2. Find repositories with specific topics
related_repos = await github_client.search_repositories(
    query="topic:governance topic:automation"
)
```

---

## 🔧 **Integration with Issue Generator Service**

The GitHub API wrapper is actively used in the Issue Generator service (`src/services/issue_generator.py`):

```python
# Current usage pattern in _create_github_issue method:
github_issue = await github_client.create_issue(
    owner=repo_owner,
    repo=repo_name, 
    title=issue_data["title"],
    body=self._format_issue_description(issue_data),
    labels=issue_data.get("labels", []),
    assignees=issue_data.get("assignees", [])
)
```

The service also uses the repository setup endpoint:
```python
# Repository setup endpoint
@app.post("/v1/repository/setup")
async def setup_repository(owner: str, repo: str, project_name: str):
    setup_result = await github_client.setup_governance_repository(owner, repo, project_name)
    return {
        "repository": f"{owner}/{repo}",
        "labels_created": len(setup_result.get('labels', [])),
        "milestones_created": len(setup_result.get('milestones', [])),
        "errors": setup_result.get('errors', [])
    }
```

---

## 📋 **Next Steps for Implementation**

1. **Review and prioritize** missing functions based on governance automation needs
2. **Implement Priority 1 functions** to complete core API coverage
3. **Add comprehensive error handling** for all new functions
4. **Update integration tests** to cover new API functions
5. **Enhance batch operations** for efficiency in governance workflows
6. **Add rate limiting management** for large-scale operations

This documentation serves as a comprehensive reference for the current GitHub API wrapper implementation and provides a clear roadmap for completing full GitHub API coverage in the GitHub Governance Factory.
