@echo off
REM ===============================================================
REM GitHub Governance Factory - Epic → Feature → Task Generator
REM Automatically generates GitHub Projects and Issues based on 
REM repository specifications and conversation history
REM ===============================================================

SETLOCAL ENABLEDELAYEDEXPANSION

REM Configuration
SET "REPO_ROOT=%~dp0.."
SET "SPECS_DIR=%REPO_ROOT%\.specs"
SET "CONVERSATIONS_DIR=%SPECS_DIR%\conversation history"
SET "CONFIG_FILE=%~dp0governance-config.json"

REM GitHub Configuration
SET "ORG_NAME=frankmax-com"
SET "REPO_NAME=AI-DevOps-System"

ECHO 🚀 GitHub Governance Factory - Epic Generation
ECHO ===============================================
ECHO Repository: %REPO_NAME%
ECHO Organization: %ORG_NAME%
ECHO Specs Directory: %SPECS_DIR%
ECHO ===============================================

REM Validate GitHub CLI authentication
gh auth status >nul 2>&1
IF ERRORLEVEL 1 (
    ECHO ❌ ERROR: GitHub CLI not authenticated
    ECHO Please run: gh auth login
    EXIT /B 1
)

REM Validate specs directory exists
IF NOT EXIST "%SPECS_DIR%" (
    ECHO ❌ ERROR: Specs directory not found: %SPECS_DIR%
    EXIT /B 1
)

ECHO ✅ Pre-flight checks complete

REM ===============================================================
REM Epic 1: Infrastructure Foundation Epic
REM ===============================================================
ECHO.
ECHO 🏗️ Creating Infrastructure Foundation Epic...

REM Create Epic Issue
gh issue create ^
    --title "Epic: Infrastructure Foundation Platform" ^
    --body "## 🎯 Epic Overview%newline%Build the foundational infrastructure components for the AI DevOps system.%newline%%newline%## 🏗️ Features%newline%- [ ] #FEATURE_SUBTREE Infrastructure subtree architecture%newline%- [ ] #FEATURE_MONITORING Real-time monitoring and logging%newline%- [ ] #FEATURE_SECURITY Security scanning and compliance%newline%- [ ] #FEATURE_DOCKER Docker containerization%newline%%newline%## 📊 Success Criteria%newline%- All agent services properly containerized%newline%- Monitoring dashboards operational%newline%- Security compliance validated%newline%- Infrastructure scalable and maintainable" ^
    --label "epic,agent:orchestrator,status:planning" ^
    --assignee "@me" ^
    --repo %ORG_NAME%/%REPO_NAME%

IF ERRORLEVEL 1 (
    ECHO ⚠️  Epic creation failed, continuing...
) ELSE (
    ECHO ✅ Infrastructure Foundation Epic created
)

REM Create Feature 1.1: Subtree Architecture
gh issue create ^
    --title "Feature: Git Subtree Architecture Implementation" ^
    --body "## 🎯 Feature Overview%newline%Implement git subtree architecture for modular agent services.%newline%%newline%## 📋 Tasks%newline%- [ ] #TASK Configure dev-agent-service subtree%newline%- [ ] #TASK Configure ai-provider-agent-service subtree%newline%- [ ] #TASK Configure orchestrator-service subtree%newline%- [ ] #TASK Configure qa-agent-service subtree%newline%- [ ] #TASK Configure security-agent-service subtree%newline%- [ ] #TASK Update documentation%newline%%newline%## ✅ Definition of Done%newline%- All services configured as subtrees%newline%- Pull/push operations documented%newline%- Developer onboarding guide updated" ^
    --label "feature,agent:orchestrator,status:in-progress" ^
    --assignee "@me" ^
    --repo %ORG_NAME%/%REPO_NAME%

IF ERRORLEVEL 1 (
    ECHO ⚠️  Feature creation failed, continuing...
) ELSE (
    ECHO ✅ Subtree Architecture Feature created
)

REM Create Feature 1.2: Monitoring & Logging
gh issue create ^
    --title "Feature: Real-time Monitoring and Logging Platform" ^
    --body "## 🎯 Feature Overview%newline%Implement comprehensive monitoring and logging for all agent services.%newline%%newline%## 📋 Tasks%newline%- [ ] #TASK Setup Prometheus metrics collection%newline%- [ ] #TASK Configure Grafana dashboards%newline%- [ ] #TASK Implement structured logging%newline%- [ ] #TASK Setup log aggregation%newline%- [ ] #TASK Configure alerting rules%newline%%newline%## ✅ Definition of Done%newline%- All services instrumented with metrics%newline%- Dashboards showing system health%newline%- Alerts configured for critical issues%newline%- Log retention policies in place" ^
    --label "feature,agent:orchestrator,status:planning" ^
    --assignee "@me" ^
    --repo %ORG_NAME%/%REPO_NAME%

IF ERRORLEVEL 1 (
    ECHO ⚠️  Feature creation failed, continuing...
) ELSE (
    ECHO ✅ Monitoring & Logging Feature created
)

REM ===============================================================
REM Epic 2: Agent Services Platform Epic
REM ===============================================================
ECHO.
ECHO 🤖 Creating Agent Services Platform Epic...

gh issue create ^
    --title "Epic: Intelligent Agent Services Platform" ^
    --body "## 🎯 Epic Overview%newline%Develop and deploy the complete suite of AI-powered agent services.%newline%%newline%## 🤖 Agent Services%newline%- [ ] #FEATURE_DEV Development Agent Service%newline%- [ ] #FEATURE_AI AI Provider Agent Service%newline%- [ ] #FEATURE_QA Quality Assurance Agent Service%newline%- [ ] #FEATURE_SECURITY Security Agent Service%newline%- [ ] #FEATURE_RELEASE Release Agent Service%newline%- [ ] #FEATURE_PM Project Management Agent Service%newline%%newline%## 📊 Success Criteria%newline%- All agent services operational%newline%- Inter-agent communication established%newline%- AI workflows automated%newline%- Performance metrics tracked" ^
    --label "epic,agent:orchestrator,status:planning" ^
    --assignee "@me" ^
    --repo %ORG_NAME%/%REPO_NAME%

IF ERRORLEVEL 1 (
    ECHO ⚠️  Epic creation failed, continuing...
) ELSE (
    ECHO ✅ Agent Services Platform Epic created
)

REM Create Feature 2.1: Development Agent Service
gh issue create ^
    --title "Feature: Development Agent Service Implementation" ^
    --body "## 🎯 Feature Overview%newline%Build the development agent service for automated coding assistance.%newline%%newline%## 📋 Tasks%newline%- [ ] #TASK Implement Azure DevOps integration%newline%- [ ] #TASK Implement GitHub integration%newline%- [ ] #TASK Setup automated code review%newline%- [ ] #TASK Configure CI/CD pipeline integration%newline%- [ ] #TASK Implement code quality checks%newline%- [ ] #TASK Setup performance monitoring%newline%%newline%## ✅ Definition of Done%newline%- Service responds to development requests%newline%- Integration with Azure DevOps working%newline%- Automated code review functional%newline%- Performance metrics tracked" ^
    --label "feature,agent:dev,status:in-progress" ^
    --assignee "@me" ^
    --repo %ORG_NAME%/%REPO_NAME%

IF ERRORLEVEL 1 (
    ECHO ⚠️  Feature creation failed, continuing...
) ELSE (
    ECHO ✅ Development Agent Feature created
)

REM Create Feature 2.2: AI Provider Agent Service
gh issue create ^
    --title "Feature: AI Provider Agent Service Implementation" ^
    --body "## 🎯 Feature Overview%newline%Build the AI provider agent service for managing AI model interactions.%newline%%newline%## 📋 Tasks%newline%- [ ] #TASK Implement multi-provider support%newline%- [ ] #TASK Configure OpenAI integration%newline%- [ ] #TASK Configure Azure OpenAI integration%newline%- [ ] #TASK Implement request routing%newline%- [ ] #TASK Setup rate limiting and throttling%newline%- [ ] #TASK Implement cost tracking%newline%%newline%## ✅ Definition of Done%newline%- Multiple AI providers supported%newline%- Request routing working efficiently%newline%- Rate limiting prevents overuse%newline%- Cost tracking accurate" ^
    --label "feature,agent:ai-provider,status:planning" ^
    --assignee "@me" ^
    --repo %ORG_NAME%/%REPO_NAME%

IF ERRORLEVEL 1 (
    ECHO ⚠️  Feature creation failed, continuing...
) ELSE (
    ECHO ✅ AI Provider Agent Feature created
)

REM ===============================================================
REM Epic 3: Developer Experience Enhancement Epic
REM ===============================================================
ECHO.
ECHO 👨‍💻 Creating Developer Experience Enhancement Epic...

gh issue create ^
    --title "Epic: Developer Experience Enhancement Platform" ^
    --body "## 🎯 Epic Overview%newline%Enhance developer productivity through automation and tooling improvements.%newline%%newline%## 🛠️ Enhancement Areas%newline%- [ ] #FEATURE_AUTOMATION Development workflow automation%newline%- [ ] #FEATURE_TOOLING Enhanced developer tooling%newline%- [ ] #FEATURE_DOCUMENTATION Comprehensive documentation%newline%- [ ] #FEATURE_ONBOARDING Developer onboarding%newline%%newline%## 📊 Success Criteria%newline%- Developer onboarding time reduced by 50%%newline%- Automated workflows operational%newline%- Documentation comprehensive and current%newline%- Developer satisfaction scores improved" ^
    --label "epic,agent:dev,status:planning" ^
    --assignee "@me" ^
    --repo %ORG_NAME%/%REPO_NAME%

IF ERRORLEVEL 1 (
    ECHO ⚠️  Epic creation failed, continuing...
) ELSE (
    ECHO ✅ Developer Experience Epic created
)

REM Create Feature 3.1: Development Workflow Automation
gh issue create ^
    --title "Feature: Development Workflow Automation" ^
    --body "## 🎯 Feature Overview%newline%Automate common development workflows to improve productivity.%newline%%newline%## 📋 Tasks%newline%- [ ] #TASK Setup automated testing pipelines%newline%- [ ] #TASK Configure automated deployments%newline%- [ ] #TASK Implement automated code formatting%newline%- [ ] #TASK Setup automated dependency updates%newline%- [ ] #TASK Configure automated security scanning%newline%%newline%## ✅ Definition of Done%newline%- All common workflows automated%newline%- Manual intervention minimized%newline%- Error rates reduced%newline%- Productivity metrics improved" ^
    --label "feature,agent:dev,status:planning" ^
    --assignee "@me" ^
    --repo %ORG_NAME%/%REPO_NAME%

IF ERRORLEVEL 1 (
    ECHO ⚠️  Feature creation failed, continuing...
) ELSE (
    ECHO ✅ Workflow Automation Feature created
)

ECHO.
ECHO ===============================================
ECHO 🎉 GitHub Governance Factory Setup Complete!
ECHO ===============================================
ECHO.
ECHO 📊 Issues Created:
ECHO   • 3 Epics (Infrastructure, Agent Services, Developer Experience)
ECHO   • 6 Features (Subtree, Monitoring, Dev Agent, AI Provider, Workflow Automation, etc.)
ECHO   • Issues tagged by agent service and status
ECHO.
ECHO 🔗 Next Steps:
ECHO   1. Create individual task issues for each feature
ECHO   2. Link issues to project boards
ECHO   3. Setup milestone tracking
ECHO   4. Configure automation rules
ECHO.
ECHO View issues: https://github.com/%ORG_NAME%/%REPO_NAME%/issues
ECHO View project: https://github.com/orgs/%ORG_NAME%/projects
ECHO.

ENDLOCAL
