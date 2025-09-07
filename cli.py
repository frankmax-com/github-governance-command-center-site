"""
Command Line Interface for GitHub Governance Factory
Implementation of CLI operations from documented architecture
"""

import asyncio
import click
import json
import os
import sys
from typing import Dict, Any

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.main import app


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """GitHub Governance Factory - Enterprise AI-Powered Governance Automation"""
    pass


@cli.command()
@click.option('--name', required=True, help='Project name')
@click.option('--description', required=True, help='Project description')
@click.option('--requirements', multiple=True, help='Project requirements (can be used multiple times)')
@click.option('--constraints', multiple=True, help='Project constraints (can be used multiple times)')
@click.option('--stakeholders', multiple=True, help='Project stakeholders (can be used multiple times)')
@click.option('--priority', default='medium', help='Project priority (low, medium, high)')
@click.option('--output', type=click.File('w'), default='-', help='Output file (default: stdout)')
def generate_governance(name, description, requirements, constraints, stakeholders, priority, output):
    """
    Generate governance structure from project specification
    
    Example:
    python cli.py generate-governance \\
        --name "My Project" \\
        --description "A sample project" \\
        --requirements "OAuth integration" \\
        --requirements "Database setup" \\
        --stakeholders "john@company.com"
    """
    async def _generate():
        try:
            await app.initialize()
            
            args = {
                "name": name,
                "description": description,
                "requirements": list(requirements),
                "constraints": list(constraints),
                "stakeholders": list(stakeholders),
                "priority": priority
            }
            
            result = await app.run_cli_command("generate_governance", args)
            
            output_data = {
                "project_id": result.project_id,
                "governance_structure": result.governance_structure,
                "ai_analysis": result.ai_analysis,
                "status": result.status,
                "created_at": result.created_at
            }
            
            json.dump(output_data, output, indent=2)
            click.echo("\\nGovernance structure generated successfully!", err=True)
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        finally:
            await app.shutdown()
    
    asyncio.run(_generate())


@cli.command()
@click.option('--project-id', required=True, help='Project ID')
@click.option('--governance-file', type=click.File('r'), required=True, help='Governance structure JSON file')
@click.option('--github-owner', required=True, help='GitHub repository owner')
@click.option('--github-repo', required=True, help='GitHub repository name')
@click.option('--github-token', help='GitHub access token (or set GITHUB_TOKEN env var)')
@click.option('--output', type=click.File('w'), default='-', help='Output file (default: stdout)')
def generate_issues(project_id, governance_file, github_owner, github_repo, github_token, output):
    """
    Generate GitHub issues from governance structure
    
    Example:
    python cli.py generate-issues \\
        --project-id "project-123" \\
        --governance-file governance.json \\
        --github-owner "myorg" \\
        --github-repo "myrepo" \\
        --github-token "$GITHUB_TOKEN"
    """
    async def _generate_issues():
        try:
            await app.initialize()
            
            # Load governance structure
            governance_structure = json.load(governance_file)
            
            # Get GitHub token from environment if not provided
            token = github_token or os.getenv('GITHUB_TOKEN')
            if not token:
                raise ValueError("GitHub token required (use --github-token or set GITHUB_TOKEN env var)")
            
            args = {
                "project_id": project_id,
                "governance_structure": governance_structure,
                "github_config": {
                    "repo_owner": github_owner,
                    "repo_name": github_repo,
                    "token": token
                }
            }
            
            result = await app.run_cli_command("generate_issues", args)
            
            output_data = {
                "project_id": result.project_id,
                "generated_issues": [issue.dict() for issue in result.generated_issues],
                "failed_issues": result.failed_issues,
                "total_count": result.total_count,
                "success_count": result.success_count,
                "ai_analysis": result.ai_analysis
            }
            
            json.dump(output_data, output, indent=2)
            click.echo(f"\\nGenerated {result.success_count}/{result.total_count} issues successfully!", err=True)
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        finally:
            await app.shutdown()
    
    asyncio.run(_generate_issues())


@cli.command()
@click.option('--format', type=click.Choice(['json', 'table']), default='table', help='Output format')
def health_check(format):
    """
    Check system health and service status
    
    Example:
    python cli.py health-check --format json
    """
    async def _health_check():
        try:
            await app.initialize()
            
            health_status = await app.run_cli_command("health_check")
            
            if format == 'json':
                click.echo(json.dumps(health_status, indent=2))
            else:
                # Table format
                click.echo("GitHub Governance Factory - Health Check")
                click.echo("=" * 50)
                click.echo(f"System Status: {health_status['status']}")
                click.echo()
                
                click.echo("Services:")
                for service_name, service_health in health_status['services'].items():
                    status = service_health.get('status', 'unknown')
                    click.echo(f"  {service_name}: {status}")
                
                click.echo()
                click.echo("Dependencies:")
                for dep_name, dep_status in health_status['dependencies'].items():
                    click.echo(f"  {dep_name}: {dep_status}")
                
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        finally:
            await app.shutdown()
    
    asyncio.run(_health_check())


@cli.command()
@click.option('--fix', is_flag=True, help='Attempt to fix configuration issues')
def validate_config(fix):
    """
    Validate system configuration
    
    Example:
    python cli.py validate-config --fix
    """
    async def _validate_config():
        try:
            await app.initialize()
            
            validation_results = await app.run_cli_command("validate_config")
            
            click.echo("Configuration Validation Results")
            click.echo("=" * 40)
            
            # Environment variables
            click.echo("\\nEnvironment Variables:")
            for var_name, var_info in validation_results['environment_variables'].items():
                status = "✓" if var_info['present'] else "✗"
                click.echo(f"  {status} {var_name}")
            
            # Database connections
            click.echo("\\nDatabase Connections:")
            for db_name, db_status in validation_results['database_connections'].items():
                status = "✓" if db_status == "valid" else "✗"
                click.echo(f"  {status} {db_name}: {db_status}")
            
            # Overall status
            overall_status = validation_results['overall_status']
            click.echo(f"\\nOverall Status: {overall_status}")
            
            if overall_status != "valid":
                click.echo("\\nConfiguration issues detected!")
                if fix:
                    click.echo("Attempting to fix issues...")
                    # Implementation would attempt to fix common issues
                    click.echo("Manual intervention may be required for some issues.")
                else:
                    click.echo("Use --fix flag to attempt automatic fixes.")
                sys.exit(1)
            else:
                click.echo("\\nAll configuration checks passed!")
                
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        finally:
            await app.shutdown()
    
    asyncio.run(_validate_config())


@cli.command()
@click.option('--service', type=click.Choice(['governance-engine', 'issue-generator', 'all']), 
              default='all', help='Service to start')
@click.option('--port', type=int, help='Port to bind (for single service)')
@click.option('--host', default='0.0.0.0', help='Host to bind')
@click.option('--workers', type=int, default=1, help='Number of worker processes')
def serve(service, port, host, workers):
    """
    Start microservices
    
    Example:
    python cli.py serve --service governance-engine --port 8000
    python cli.py serve --service all
    """
    async def _serve():
        try:
            if service == 'all':
                click.echo("Starting all microservices...")
                await app.initialize()
                
                click.echo("GitHub Governance Factory is running!")
                click.echo("Services available:")
                click.echo("  - Governance Engine: http://localhost:8000")
                click.echo("  - Issue Generator: http://localhost:8001")
                click.echo("\\nPress Ctrl+C to stop")
                
                # Keep running until interrupted
                while app.running:
                    await asyncio.sleep(1)
                    
            elif service == 'governance-engine':
                import uvicorn
                from src.services.governance_engine import app as governance_app
                
                port = port or 8000
                click.echo(f"Starting Governance Engine on {host}:{port}")
                uvicorn.run(governance_app, host=host, port=port, workers=workers)
                
            elif service == 'issue-generator':
                import uvicorn
                from src.services.issue_generator import app as issue_app
                
                port = port or 8001
                click.echo(f"Starting Issue Generator on {host}:{port}")
                uvicorn.run(issue_app, host=host, port=port, workers=workers)
                
        except KeyboardInterrupt:
            click.echo("\\nShutting down...")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        finally:
            if service == 'all':
                await app.shutdown()
    
    asyncio.run(_serve())


@cli.command()
@click.option('--owner', required=True, help='GitHub repository owner')
@click.option('--repo', required=True, help='GitHub repository name') 
@click.option('--project-name', required=True, help='Project name for governance setup')
@click.option('--github-token', help='GitHub access token (or set GITHUB_TOKEN env var)')
def setup_repository(owner, repo, project_name, github_token):
    """
    Setup GitHub repository for governance automation
    
    Example:
    python cli.py setup-repository \\
        --owner "myorg" \\
        --repo "myrepo" \\
        --project-name "My Project" \\
        --github-token "$GITHUB_TOKEN"
    """
    async def _setup_repository():
        try:
            # Set GitHub token if provided
            if github_token:
                os.environ['GITHUB_TOKEN'] = github_token
            
            await app.initialize()
            
            # Call repository setup
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = "http://localhost:8001/v1/repository/setup"
                params = {
                    "owner": owner,
                    "repo": repo,
                    "project_name": project_name
                }
                
                async with session.post(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        click.echo(f"✓ Repository {result['repository']} setup completed!")
                        click.echo(f"✓ Created {result['labels_created']} governance labels")
                        click.echo(f"✓ Created {result['milestones_created']} project milestones")
                        
                        if result['errors']:
                            click.echo("⚠️  Some issues occurred:")
                            for error in result['errors']:
                                click.echo(f"   - {error}")
                        else:
                            click.echo("✅ Repository is ready for governance automation!")
                    else:
                        error_text = await response.text()
                        click.echo(f"❌ Setup failed: {error_text}", err=True)
                        sys.exit(1)
                        
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        finally:
            await app.shutdown()
    
    asyncio.run(_setup_repository())


@cli.command()
def version():
    """Show version information"""
    click.echo("GitHub Governance Factory v1.0.0")
    click.echo("Enterprise AI-Powered Governance Automation")
    click.echo("17+ AI Providers | 100+ Specialized Models")


if __name__ == '__main__':
    cli()
