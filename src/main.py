"""
Main Application Entry Point for GitHub Governance Factory
Implementation of microservices orchestration from MICROSERVICES-ARCHITECTURE.md
"""

import asyncio
import logging
import signal
import sys
import os
from typing import Dict, Any

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.shared.database import db_manager
from src.shared.ai_client import ai_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GitHubGovernanceFactory:
    """
    Main GitHub Governance Factory Application
    Orchestrates all microservices for enterprise governance automation
    """
    
    def __init__(self):
        self.services = {}
        self.running = False
        
    async def initialize(self):
        """Initialize all microservices and dependencies"""
        try:
            logger.info("Initializing GitHub Governance Factory...")
            
            # Initialize database connections
            await db_manager.initialize_all_connections()
            logger.info("Database connections initialized")
            
            # Initialize AI Provider Factory client
            # ai_client initialization happens automatically
            logger.info("AI Provider Factory client initialized")
            
            # Start microservices
            await self._start_microservices()
            
            self.running = True
            logger.info("GitHub Governance Factory initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize GitHub Governance Factory: {e}")
            raise
    
    async def _start_microservices(self):
        """Start all microservices"""
        try:
            # Import and start Governance Engine Service
            from src.services.governance_engine import governance_service, app as governance_app
            await governance_service.initialize()
            self.services["governance-engine"] = governance_service
            logger.info("Governance Engine Service started")
            
            # Import and start Issue Generator Service
            from src.services.issue_generator import issue_generator_service, app as issue_app
            await issue_generator_service.initialize()
            self.services["issue-generator"] = issue_generator_service
            logger.info("Issue Generator Service started")
            
            # Additional services would be started here
            # Each service runs on its own port and can be scaled independently
            
        except Exception as e:
            logger.error(f"Failed to start microservices: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown of all services"""
        try:
            logger.info("Shutting down GitHub Governance Factory...")
            
            # Stop microservices
            for service_name, service in self.services.items():
                try:
                    if hasattr(service, 'shutdown'):
                        await service.shutdown()
                    logger.info(f"Stopped {service_name}")
                except Exception as e:
                    logger.error(f"Error stopping {service_name}: {e}")
            
            # Close database connections
            await db_manager.close_all_connections()
            
            self.running = False
            logger.info("GitHub Governance Factory shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Overall system health check"""
        health_status = {
            "system": "github-governance-factory",
            "status": "healthy" if self.running else "unhealthy",
            "services": {},
            "dependencies": {}
        }
        
        # Check service health
        for service_name, service in self.services.items():
            try:
                if hasattr(service, 'health_check'):
                    service_health = await service.health_check()
                    health_status["services"][service_name] = service_health
                else:
                    health_status["services"][service_name] = {"status": "unknown"}
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check database dependencies
        try:
            await db_manager.mongodb.client.admin.command('ping')
            health_status["dependencies"]["mongodb"] = "healthy"
        except Exception as e:
            health_status["dependencies"]["mongodb"] = f"unhealthy: {e}"
        
        try:
            db_manager.redis.client.ping()
            health_status["dependencies"]["redis"] = "healthy"
        except Exception as e:
            health_status["dependencies"]["redis"] = f"unhealthy: {e}"
        
        try:
            db_manager.supabase.client.table("health_check").select("*").limit(1).execute()
            health_status["dependencies"]["supabase"] = "healthy"
        except Exception as e:
            health_status["dependencies"]["supabase"] = f"unhealthy: {e}"
        
        return health_status
    
    async def run_cli_command(self, command: str, args: Dict[str, Any] = None):
        """
        Run CLI commands for governance operations
        Implementation of documented CLI interface patterns
        """
        try:
            if command == "generate_governance":
                return await self._cli_generate_governance(args or {})
            elif command == "generate_issues":
                return await self._cli_generate_issues(args or {})
            elif command == "health_check":
                return await self.health_check()
            elif command == "validate_config":
                return await self._cli_validate_config()
            else:
                raise ValueError(f"Unknown command: {command}")
                
        except Exception as e:
            logger.error(f"CLI command '{command}' failed: {e}")
            raise
    
    async def _cli_generate_governance(self, args: Dict[str, Any]):
        """CLI command to generate governance structure"""
        if "governance-engine" not in self.services:
            raise RuntimeError("Governance Engine Service not available")
        
        governance_service = self.services["governance-engine"]
        
        # Create project specification from args
        from src.services.governance_engine import ProjectSpecRequest
        spec_request = ProjectSpecRequest(
            name=args.get("name", "CLI Project"),
            description=args.get("description", "Project created via CLI"),
            requirements=args.get("requirements", []),
            constraints=args.get("constraints", []),
            stakeholders=args.get("stakeholders", []),
            priority=args.get("priority", "medium")
        )
        
        result = await governance_service.process_project_specification(spec_request)
        return result
    
    async def _cli_generate_issues(self, args: Dict[str, Any]):
        """CLI command to generate GitHub issues"""
        if "issue-generator" not in self.services:
            raise RuntimeError("Issue Generator Service not available")
        
        issue_service = self.services["issue-generator"]
        
        # Create issue generation request from args
        from src.services.issue_generator import IssueGenerationRequest
        request = IssueGenerationRequest(
            project_id=args["project_id"],
            governance_structure=args["governance_structure"],
            github_config=args["github_config"]
        )
        
        result = await issue_service.generate_issues_from_governance(request)
        return result
    
    async def _cli_validate_config(self):
        """Validate system configuration"""
        validation_results = {
            "environment_variables": {},
            "database_connections": {},
            "ai_provider_config": {},
            "overall_status": "valid"
        }
        
        # Check environment variables
        required_env_vars = [
            "MONGODB_CONNECTION_STRING",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY",
            "REDIS_HOST",
            "AI_PROVIDER_FACTORY_URL"
        ]
        
        for var in required_env_vars:
            value = os.getenv(var)
            validation_results["environment_variables"][var] = {
                "present": value is not None,
                "value": "***" if value else None
            }
            if not value:
                validation_results["overall_status"] = "invalid"
        
        # Test database connections
        try:
            await db_manager.mongodb.client.admin.command('ping')
            validation_results["database_connections"]["mongodb"] = "valid"
        except Exception as e:
            validation_results["database_connections"]["mongodb"] = f"invalid: {e}"
            validation_results["overall_status"] = "invalid"
        
        try:
            db_manager.redis.client.ping()
            validation_results["database_connections"]["redis"] = "valid"
        except Exception as e:
            validation_results["database_connections"]["redis"] = f"invalid: {e}"
            validation_results["overall_status"] = "invalid"
        
        try:
            db_manager.supabase.client.table("health_check").select("*").limit(1).execute()
            validation_results["database_connections"]["supabase"] = "valid"
        except Exception as e:
            validation_results["database_connections"]["supabase"] = f"invalid: {e}"
            validation_results["overall_status"] = "invalid"
        
        return validation_results


# Global application instance
app = GitHubGovernanceFactory()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(app.shutdown())


async def main():
    """Main application entry point"""
    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize and run the application
        await app.initialize()
        
        logger.info("GitHub Governance Factory is running...")
        logger.info("Available services:")
        for service_name in app.services.keys():
            logger.info(f"  - {service_name}")
        
        # Keep the application running
        while app.running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise
    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
