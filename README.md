# GitHub Governance Factory

**Enterprise AI-Powered Governance Automation Platform**  
🎯 **Status**: ✅ **ENHANCED** - 131 functions with complete GitHub Actions integration  
🚀 **Enterprise Ready**: Production-deployed platform with AI Factory integration

Transform your GitHub repositories into well-governed, AI-enhanced project management environments with automated issue generation, comprehensive GitHub API integration, enterprise-grade governance structures, and complete CI/CD workflow management.

## 🎉 Platform Enhanced - GitHub Actions Integration Complete

### ✅ **ALL PHASES COMPLETE + GITHUB ACTIONS** (September 2025)
- **131 API Functions** - Complete GitHub API coverage including GitHub Actions CI/CD
- **Enterprise Platform** - Complete microservices architecture with production deployment
- **AI Factory Ready** - Full integration capabilities for 17+ AI providers
- **GitHub Actions Analytics** - Workflow performance insights and optimization recommendations
- **Docker Validated** - Comprehensive testing suite with enhanced API coverage
- **Production Infrastructure** - Kubernetes-ready deployment with monitoring stack

### 🏆 **Final Implementation Summary**
- **GitHub Actions Integration**: 35 functions - Complete CI/CD API coverage ✅
- **Phase 1**: 21 functions - Foundation operations ✅
- **Phase 2**: 14 functions - Enhanced operations ✅  
- **Phase 3**: 10 functions - Enterprise features ✅
- **Phase 4**: 10 functions - Advanced capabilities ✅
- **Pre-existing**: 41 functions - Core functionality ✅

## 🚀 Key Features

### ✅ **Complete Implementation**
- **Comprehensive GitHub API Wrapper** - 131 functions with complete GitHub Actions integration
- **CI/CD Analytics** - Advanced workflow performance insights and optimization recommendations
- **Microservices Architecture** - Governance Engine + Issue Generator services  
- **AI Provider Factory Integration** - Clean API-only integration (no direct AI keys needed)
- **Multi-Database Support** - MongoDB, Supabase, Redis with connection pooling
- **Production-Ready CLI** - Complete command-line interface for all operations
- **Docker Containerization** - Full Docker Compose setup for easy deployment
- **Integration Testing** - Comprehensive test suite with real API validation

### 🎯 **Core Capabilities**
- **Repository Setup** - Automated governance label and milestone creation
- **AI-Enhanced Issue Generation** - Convert project specs into actionable GitHub issues
- **Batch Operations** - Efficient bulk GitHub operations with rate limiting
- **Real-time Monitoring** - Health checks, metrics, and observability
- **Enterprise Security** - Token-based auth, encrypted communications, audit logging

## 🏗️ Architecture

```
┌─────────────────────────┐
│   GitHub Governance     │
│       Factory           │
│                         │
│  ┌─────────────────────┐│
│  │ Governance Engine   ││  :8000
│  │ - Project Specs     ││
│  │ - Structure Gen     ││
│  │ - Health Monitoring ││
│  └─────────────────────┘│
│                         │
│  ┌─────────────────────┐│
│  │ Issue Generator     ││  :8001
│  │ - GitHub Issues     ││
│  │ - Repository Setup  ││
│  │ - GitHub API Client ││
│  └─────────────────────┘│
└─────────────────────────┘
            │
            │ API Integration
            ▼
┌─────────────────────────┐
│   AI Provider Factory   │  External Service
│   - 17+ AI Providers    │  
│   - 100+ Models         │
└─────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
```bash
# Required
git clone <repository>
cd github-governance-factory
pip install -r requirements.txt

# Environment Setup
cp .env.example .env
# Edit .env with your configuration
```

### Essential Configuration
```bash
# GitHub Integration (Required)
GITHUB_TOKEN=your_github_token_here

# AI Provider Factory (Required)
AI_PROVIDER_FACTORY_URL=http://localhost:8080
AI_PROVIDER_FACTORY_API_KEY=your_api_key_here

# Databases (MongoDB primary, others optional)
MONGODB_URL=mongodb://localhost:27017/governance
SUPABASE_URL=https://your-project.supabase.co
REDIS_URL=redis://localhost:6379
```

### Start Services

#### 🐳 **Docker Swagger Documentation (Recommended)**
```powershell
# PowerShell (Windows)
.\start-swagger-docker.ps1

# Linux/Mac
./start-swagger-docker.sh

# Manual Docker Compose
docker-compose -f docker-compose.swagger.yml up --build -d
```

**Access Points:**
- **Main API Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc  
- **Standalone Swagger UI**: http://localhost:8080
- **Standalone ReDoc**: http://localhost:8081
- **Health Check**: http://localhost:8000/health

#### 🔧 **Traditional Service Deployment**
```bash
# Option 1: CLI (Development)
python cli.py serve --service all

# Option 2: Production Docker Compose
docker-compose up -d

# Option 3: Individual Services
python cli.py serve --service governance-engine --port 8000
python cli.py serve --service issue-generator --port 8001
```

### Verify Installation
```bash
# Health check
python cli.py health-check

# Integration test
export GITHUB_TOKEN="your_token_here"
python test_integration.py
```

## 📋 Complete Usage Examples

### 1. Repository Setup
```bash
# Setup GitHub repository for governance automation
python cli.py setup-repository \
    --owner "myorg" \
    --repo "myrepo" \
    --project-name "My Amazing Project" \
    --github-token "$GITHUB_TOKEN"

# Output:
# ✓ Repository myorg/myrepo setup completed!
# ✓ Created 12 governance labels
# ✓ Created 4 project milestones
# ✅ Repository is ready for governance automation!
```

### 2. Generate Governance Structure
```bash
# Create comprehensive project governance
python cli.py generate-governance \
    --name "E-Commerce Platform" \
    --description "Modern e-commerce platform with microservices" \
    --requirements "User authentication" \
    --requirements "Payment processing" \
    --requirements "Inventory management" \
    --constraints "Launch in Q2 2024" \
    --constraints "Budget: $50,000" \
    --stakeholders "pm@company.com" \
    --stakeholders "dev-lead@company.com" \
    --priority "high" \
    --output governance.json
```

### 3. Generate GitHub Issues
```bash
# Convert governance structure to GitHub issues
python cli.py generate-issues \
    --project-id "ecommerce-q2-2024" \
    --governance-file governance.json \
    --github-owner "myorg" \
    --github-repo "ecommerce-platform" \
    --github-token "$GITHUB_TOKEN"

# Output:
# Generated 15/15 issues successfully!
# ✓ Epic: User Authentication System
# ✓ Epic: Payment Processing Integration  
# ✓ Epic: Inventory Management Service
# ✓ Story: OAuth 2.0 Implementation
# ✓ Story: Database Schema Design
# ... and more
```

## 🔧 API Documentation

### Governance Engine (Port 8000)

#### Generate Governance Structure
```http
POST /v1/governance/generate
Content-Type: application/json

{
  "name": "My Project",
  "description": "Project description",
  "requirements": ["OAuth integration", "Database setup"],
  "constraints": ["2 week timeline", "$5000 budget"],
  "stakeholders": ["pm@company.com"],
  "priority": "high"
}
```

**Response:**
```json
{
  "project_id": "project-abc123",
  "governance_structure": {
    "epics": [...],
    "stories": [...],
    "tasks": [...]
  },
  "ai_analysis": "AI-generated insights...",
  "status": "completed"
}
```

### Issue Generator (Port 8001)

#### Setup Repository
```http
POST /v1/repository/setup?owner=myorg&repo=myrepo&project_name=My%20Project
Authorization: token your_github_token
```

#### Generate Issues
```http
POST /v1/issues/generate
Content-Type: application/json

{
  "project_id": "project-abc123",
  "governance_structure": { ... },
  "github_config": {
    "repo_owner": "myorg",
    "repo_name": "myrepo", 
    "token": "your_github_token"
  }
}
```

#### GitHub Repository Info
```http
GET /v1/github/repositories/myorg/myrepo
Authorization: token your_github_token
```

## 🧪 Testing

### Run Integration Tests
```bash
# Set environment variables
export GITHUB_TOKEN="your_token_here"
export AI_PROVIDER_FACTORY_URL="http://localhost:8080"

# Run comprehensive test suite
python test_integration.py

# Test specific components
python -m pytest tests/ -v
```

### Test Coverage
- ✅ Service health checks
- ✅ GitHub API wrapper operations
- ✅ Repository setup automation
- ✅ Governance structure generation
- ✅ Issue creation and management
- ✅ AI Provider Factory integration
- ✅ Database connectivity
- ✅ Error handling and recovery

## 📦 Dependencies

### Core Framework (Streamlined)
```txt
fastapi==0.104.1          # Modern async web framework
uvicorn[standard]==0.24.0 # ASGI server
pydantic==2.5.0           # Data validation
aiohttp==3.9.1            # Async HTTP client
PyGithub==1.59.1          # GitHub API client
```

### Database Integration
```txt
motor==3.3.2              # MongoDB async driver
redis==5.0.1              # Redis client
supabase==2.0.4           # Supabase client
```

### Security & Utils
```txt
python-jose[cryptography]==3.3.0  # JWT handling
passlib[bcrypt]==1.7.4             # Password hashing
python-dotenv==1.0.0               # Environment management
click==8.1.7                       # CLI framework
```

## 🔒 Security

### Authentication
- **GitHub Token**: Repository and API access
- **AI Provider Factory API Key**: AI service integration
- **Service-to-Service**: Secure internal communication

### Data Protection
- Environment variable encryption
- Token rotation support
- Audit logging for compliance
- Secure HTTPS communication

## 📊 Monitoring

### Health Endpoints
```bash
# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health

# Validate configuration
python cli.py validate-config --fix
```

### Metrics & Logging
- Structured JSON logging
- Request/response tracking
- GitHub API rate limit monitoring
- Database performance metrics
- Error tracking and alerting

## 🚀 Deployment

### Development
```bash
# Start all services locally
python cli.py serve --service all
```

### Production with Docker
```bash
# Build and deploy
docker-compose up -d

# Scale services
docker-compose up -d --scale governance-engine=3 --scale issue-generator=2

# Monitor logs
docker-compose logs -f
```

### Cloud Deployment
- Kubernetes manifests available
- Environment-specific configuration
- Load balancing and auto-scaling
- Monitoring and alerting setup

## 🔄 Architecture Benefits

### Clean Service Separation
- **GitHub Governance Factory**: Handles all GitHub operations
- **AI Provider Factory**: Manages AI integrations (external service)
- **No Direct AI Dependencies**: Clean API-only integration pattern

### Comprehensive GitHub Integration
- **Full API Coverage**: Complete GitHub API v4 wrapper
- **Batch Operations**: Efficient bulk operations with rate limiting
- **Real-time Events**: Webhook support for live updates
- **Enterprise Features**: Advanced security and monitoring

### Production-Ready
- **Microservices Architecture**: Scalable and maintainable
- **Multi-Database Support**: MongoDB, Supabase, Redis
- **Container-Ready**: Full Docker and Kubernetes support
- **Comprehensive Testing**: Integration and unit test coverage

## 📚 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete technical architecture
- **[GitHub API Wrapper Documentation](./docs/GITHUB-API-WRAPPER-DOCUMENTATION.md)** - Complete GitHub API function catalog
- **[GitHub API Quick Reference](./docs/GITHUB-API-QUICK-REFERENCE.md)** - Implementation status and usage examples
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)
- **[CLI Reference](./cli.py)** - Command-line interface documentation
- **[Testing Guide](./test_integration.py)** - Comprehensive testing examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

MIT License - see [LICENSE](./LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/yourorg/github-governance-factory/issues)
- **Documentation**: [Architecture Guide](./ARCHITECTURE.md)
- **Community**: [Discussions](https://github.com/yourorg/github-governance-factory/discussions)

---

**Built with ❤️ for enterprise-grade GitHub governance automation**
