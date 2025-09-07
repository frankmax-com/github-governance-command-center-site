# GitHub Governance Factory - AI Agent Instructions

## Project Overview
The **GitHub Governance Factory** is a universal, zero-hardcoded microservices platform that transforms ANY GitHub organization into a fully governed, enterprise-ready development ecosystem. This service eliminates organization-specific hardcoding and provides complete governance coverage across all GitHub domains.

## Architecture Context

### Microservices Structure
```
src/
├── main.py                    # Master orchestrator entry point
├── shared/
│   ├── github_client.py       # Comprehensive GitHub API wrapper (105 functions)
│   ├── ai_client.py           # AI Provider Factory integration
│   └── database.py           # Multi-database support (MongoDB, Supabase, Redis)
└── services/
    ├── governance_engine.py    # Core governance automation (Port 8000)
    └── issue_generator.py      # AI-powered issue creation (Port 8001)
```

### Key Design Patterns

**GitHub API Client Factory Pattern**:
```python
# Use factory function, NOT direct instantiation
from src.shared.github_client import get_github_client
client = get_github_client(token="github_token")
```

**Async-First Architecture**:
- All GitHub API operations use `async/await`
- Database connections are pooled and async
- Services communicate via HTTP async patterns

**Configuration-Driven, Not Hardcoded**:
- Environment variables for all credentials and endpoints
- `governance-config.json` for reusable templates
- No organization-specific code in the codebase

## Development Workflows

### Testing Strategy (Hybrid Approach)
```bash
# Unit tests with pytest (fast feedback)
python -m pytest tests/test_github_api_advanced.py -v

# Integration tests with Docker (end-to-end validation)
docker-compose -f docker-compose.test.yml up --build

# Combined testing (Windows)
.\run_tests.bat --verbose

# Combined testing (Linux/Mac) 
./run_tests.sh --verbose
```

### Service Development Pattern
When creating new microservices, follow the established pattern:
```python
# Each service needs:
# 1. FastAPI app with health endpoint
# 2. Async initialization with database connections
# 3. Integration with shared github_client factory
# 4. Proper error handling and logging
# 5. Docker containerization support
```

### GitHub API Implementation Standards
Current API coverage: **41/105 functions implemented (39%)**

**Phase 1 Priority Functions** (implement these first):
- Repository operations: `update_repository()`, `fork_repository()`, `get_repository_topics()`
- Issue management: `delete_issue_comment()`, `list_issue_events()`, `lock_issue()`
- Label operations: `update_label()`, `add_labels_to_issue()`
- File operations: `get_file_contents()`, `create_or_update_file()`
- Pull request operations: `update_pull_request()`, `merge_pull_request()`

## Critical Integration Points

### AI Provider Factory Integration
```python
# Never import AI libraries directly - use factory service
ai_response = await ai_client.generate_issues(
    project_spec=spec,
    provider="openai",  # or anthropic, google, etc.
    model="gpt-4"
)
```

### Multi-Database Pattern
```python
# Support all three database types
if database_type == "mongodb":
    await mongodb_client.create_governance_record()
elif database_type == "supabase":
    await supabase_client.create_governance_record()
elif database_type == "redis":
    await redis_client.cache_governance_data()
```

### GitHub Factory Execution Authority
**CRITICAL**: All GitHub governance actions MUST go through the factory automation:
- ❌ Never create Projects/Issues manually in GitHub UI
- ✅ Always use `governance-config.json` configuration
- ✅ All changes tracked in git commit history
- ✅ Factory generates complete Epic → Feature → Task hierarchies

## Project-Specific Conventions

### Environment Variables Pattern
```bash
# GitHub Configuration (required)
GITHUB_TOKEN=ghp_...
GITHUB_ORG=mycompany
GITHUB_REPO=myproject

# AI Provider Factory (optional)
AI_PROVIDER_FACTORY_URL=http://ai-provider-factory:8000

# Database Configuration (choose one)
MONGODB_URI=mongodb://...
SUPABASE_URL=postgresql://...
REDIS_URI=redis://...
```

### Error Handling Standards
```python
# GitHub API operations should handle rate limits and retries
async def _make_request(self, method: str, url: str, **kwargs):
    async with aiohttp.ClientSession(timeout=self.timeout) as session:
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status >= 400:
                    error_msg = f"GitHub API error {response.status}: {response_data.get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {e}")
            raise
```

### Docker Development
```bash
# Test environment startup
docker-compose -f docker-compose.test.yml up -d

# Production environment
docker-compose up --build

# Service-specific debugging
docker-compose logs governance-engine
docker-compose logs issue-generator
```

## Important Files to Reference

- `docs/GITHUB-API-WRAPPER-DOCUMENTATION.md` - Complete API function catalog
- `docs/GITHUB-API-IMPLEMENTATION-TRACKING.md` - Implementation roadmap and priorities
- `specs/MICROSERVICES-ARCHITECTURE.md` - Detailed microservices design
- `specs/functional/requirements.md` - Core functional requirements
- `EXECUTION-AUTHORITY.md` - Factory governance principles

## Quality Standards

**Testing Requirements**:
- All new GitHub API functions need unit tests with mocks
- Integration tests for service communication
- Docker container health checks
- 85%+ code coverage for core functionality

**Code Conventions**:
- Use `get_github_client()` factory, never direct `GitHubAPIClient()` instantiation
- Async/await for all I/O operations
- Comprehensive error handling with proper logging
- Type hints for better IDE support
- Follow existing naming patterns for consistency

## Deployment Context

This service is part of the larger AI DevOps ecosystem:
- **Parent Repository**: Part of `frankmax-com/AI DevOps` monorepo
- **Distribution**: Standalone git repository + Docker containers
- **Integration**: Works with orchestrator-service, dev-agent-service, etc.
- **Environment**: Supports personal accounts to Fortune 500 enterprises
