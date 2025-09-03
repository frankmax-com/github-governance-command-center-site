#!/usr/bin/env python3
"""
GitHub Governance Factory - Epic → Feature → Task Generator
Automatically generates GitHub Projects and Issues based on 
repository specifications and conversation history
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional

class GitHubGovernanceFactory:
    """Main class for GitHub governance automation"""
    
    def __init__(self, org_name: str = "frankmax-com", repo_name: str = "AI-DevOps-System"):
        self.org_name = org_name
        self.repo_name = repo_name
        self.repo_root = Path(__file__).parent.parent
        self.specs_dir = self.repo_root / ".specs"
        self.config_file = Path(__file__).parent / "governance-config.json"
        
        # Issue tracking
        self.created_issues = []
        self.failed_issues = []
        
    def validate_environment(self) -> bool:
        """Validate GitHub CLI and environment setup"""
        print("🔍 Validating environment...")
        
        # Check GitHub CLI authentication
        try:
            result = subprocess.run(["gh", "auth", "status"], 
                                  capture_output=True, text=True, check=True)
            print("✅ GitHub CLI authenticated")
        except subprocess.CalledProcessError:
            print("❌ ERROR: GitHub CLI not authenticated")
            print("Please run: gh auth login")
            return False
        
        # Check specs directory
        if not self.specs_dir.exists():
            print(f"❌ ERROR: Specs directory not found: {self.specs_dir}")
            return False
        
        print("✅ Environment validation complete")
        return True
    
    def load_configuration(self) -> Dict:
        """Load governance configuration from JSON file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ Configuration loaded: {config['governance']['version']}")
            return config['governance']
        except Exception as e:
            print(f"❌ ERROR: Failed to load configuration: {e}")
            return {}
    
    def create_project(self, project_config: Dict) -> bool:
        """Create a GitHub project based on configuration"""
        try:
            # For organization projects
            if self.org_name != "@me":
                cmd = [
                    "gh", "project", "create",
                    "--org", self.org_name,
                    "--title", project_config["name"],
                    "--body", project_config["description"]
                ]
                
                # Add template if specified
                if "template" in project_config:
                    cmd.extend(["--template", project_config["template"]])
            else:
                # For personal projects
                cmd = [
                    "gh", "project", "create",
                    "--title", project_config["name"],
                    "--body", project_config["description"]
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            project_url = result.stdout.strip()
            print(f"✅ Created project: {project_config['name']}")
            return True
            
        except subprocess.CalledProcessError as e:
            if "already exists" in str(e.stderr):
                print(f"ℹ️  Project already exists: {project_config['name']}")
                return True
            else:
                print(f"⚠️  Failed to create project: {project_config['name']} - {e.stderr}")
                return False
    
    def create_milestone(self, milestone_key: str, milestone_config: Dict) -> bool:
        """Create a GitHub milestone"""
        try:
            cmd = [
                "gh", "api",
                f"repos/{self.org_name}/{self.repo_name}/milestones",
                "--method", "POST",
                "--field", f"title={milestone_config['title']}",
                "--field", f"description={milestone_config['description']}",
                "--field", f"due_on={milestone_config['due_date']}T23:59:59Z",
                "--field", f"state={milestone_config.get('state', 'open')}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Created milestone: {milestone_config['title']}")
            return True
            
        except subprocess.CalledProcessError as e:
            if "already_exists" in str(e.stderr):
                print(f"ℹ️  Milestone already exists: {milestone_config['title']}")
                return True
            else:
                print(f"⚠️  Failed to create milestone: {milestone_config['title']}")
                return False
    
    def create_issue_with_hierarchy(self, issue_type: str, issue_key: str, issue_config: Dict, config: Dict) -> bool:
        """Create GitHub issue with proper hierarchy linking"""
        try:
            # Build issue body with hierarchy information
            body_parts = [issue_config["description"]]
            
            # Add parent linking for features and tasks
            if issue_type == "feature" and "parent_epic" in issue_config:
                epic_title = config["epics"][issue_config["parent_epic"]]["title"]
                body_parts.append(f"\n## 🔗 Parent Epic\nRelated to Epic: {epic_title}")
            
            if issue_type == "task" and "parent_feature" in issue_config:
                feature_title = config["features"][issue_config["parent_feature"]]["title"]
                body_parts.append(f"\n## 🔗 Parent Feature\nRelated to Feature: {feature_title}")
            
            # Add task list for epics and features
            if issue_type == "epic" and "features" in issue_config:
                body_parts.append("\n## 📋 Features")
                for feature_key in issue_config["features"]:
                    if feature_key in config.get("features", {}):
                        feature_title = config["features"][feature_key]["title"]
                        body_parts.append(f"- [ ] {feature_title}")
            
            if issue_type == "feature" and "tasks" in issue_config:
                body_parts.append("\n## 📋 Tasks")
                for task_key in issue_config["tasks"]:
                    body_parts.append(f"- [ ] {task_key.replace('-', ' ').title()}")
            
            # Add milestone information
            if "milestone" in issue_config and issue_config["milestone"] in config.get("milestones", {}):
                milestone_title = config["milestones"][issue_config["milestone"]]["title"]
                body_parts.append(f"\n## 🎯 Milestone\nTarget: {milestone_title}")
            
            # Add acceptance criteria and success metrics
            body_parts.append(f"\n## ✅ Definition of Done")
            if issue_type == "epic":
                body_parts.append("- All features completed and tested")
                body_parts.append("- Documentation updated")
                body_parts.append("- Performance metrics meet targets")
                body_parts.append("- Security review completed")
            elif issue_type == "feature":
                body_parts.append("- All tasks completed")
                body_parts.append("- Unit tests passing")
                body_parts.append("- Integration tests passing") 
                body_parts.append("- Code review approved")
                body_parts.append("- Documentation updated")
            
            full_body = "\n".join(body_parts)
            
            # Determine milestone for issue creation
            milestone_title = None
            if "milestone" in issue_config and issue_config["milestone"] in config.get("milestones", {}):
                milestone_title = config["milestones"][issue_config["milestone"]]["title"]
            
            # Create the issue
            return self.create_issue(
                title=issue_config["title"],
                body=full_body,
                labels=issue_config["labels"],
                milestone=milestone_title
            )
            
        except Exception as e:
            print(f"⚠️  Failed to create {issue_type}: {issue_config.get('title', issue_key)} - {e}")
            return False
    def create_issue(self, title: str, body: str, labels: List[str], assignee: str = "@me", milestone: str = None) -> bool:
        """Create a GitHub issue with error handling"""
        try:
            cmd = [
                "gh", "issue", "create",
                "--title", title,
                "--body", body,
                "--label", ",".join(labels),
                "--assignee", assignee,
                "--repo", f"{self.org_name}/{self.repo_name}"
            ]
            
            # Add milestone if specified
            if milestone:
                cmd.extend(["--milestone", milestone])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            issue_url = result.stdout.strip()
            self.created_issues.append({"title": title, "url": issue_url})
            print(f"✅ Created: {title}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.failed_issues.append({"title": title, "error": str(e)})
            print(f"⚠️  Failed to create: {title}")
            return False
    
    def generate_all_governance(self) -> None:
        """Generate complete governance structure from configuration"""
        print("🚀 GitHub Governance Factory - Configuration-Driven Generation")
        print("=" * 60)
        print(f"Repository: {self.repo_name}")
        print(f"Organization: {self.org_name}")
        print(f"Config File: {self.config_file}")
        print("=" * 60)
        
        # Validate environment
        if not self.validate_environment():
            sys.exit(1)
        
        # Load configuration
        config = self.load_configuration()
        if not config:
            print("❌ ERROR: Configuration loading failed")
            sys.exit(1)
        
        # Update org/repo from config if not overridden
        if hasattr(self, '_config_org'):
            self.org_name = config.get("organization", self.org_name)
            self.repo_name = config.get("repository", self.repo_name)
        
        print(f"📊 Configuration Summary:")
        print(f"  • Epics: {len(config.get('epics', {}))}")
        print(f"  • Features: {len(config.get('features', {}))}")
        print(f"  • Milestones: {len(config.get('milestones', {}))}")
        print(f"  • Projects: {len(config.get('project_templates', {}))}")
        print(f"  • Labels: {len(config.get('labels', {}))}")
        
        # Create milestones first
        print("\n🎯 Creating Milestones...")
        for milestone_key, milestone_config in config.get("milestones", {}).items():
            self.create_milestone(milestone_key, milestone_config)
        
        # Create GitHub Projects
        print("\n📊 Creating GitHub Projects...")
        for project_key, project_config in config.get("project_templates", {}).items():
            self.create_project(project_config)
        
        # Create Epics
        print("\n🏗️ Creating Epics...")
        for epic_key, epic_config in config.get("epics", {}).items():
            self.create_issue_with_hierarchy("epic", epic_key, epic_config, config)
        
        # Create Features
        print("\n🎯 Creating Features...")
        for feature_key, feature_config in config.get("features", {}).items():
            self.create_issue_with_hierarchy("feature", feature_key, feature_config, config)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self) -> None:
        """Print execution summary"""
        print("\n" + "=" * 50)
        print("🎉 GitHub Governance Factory Setup Complete!")
        print("=" * 50)
        print(f"\n📊 Issues Created: {len(self.created_issues)}")
        print(f"⚠️  Issues Failed: {len(self.failed_issues)}")
        
        if self.created_issues:
            print("\n✅ Successfully Created:")
            for issue in self.created_issues:
                print(f"  • {issue['title']}")
        
        if self.failed_issues:
            print("\n❌ Failed to Create:")
            for issue in self.failed_issues:
                print(f"  • {issue['title']}")
        
        print(f"\n🔗 Next Steps:")
        print(f"  1. Create individual task issues for each feature")
        print(f"  2. Link issues to project boards")
        print(f"  3. Setup milestone tracking")
        print(f"  4. Configure automation rules")
        print(f"\nView issues: https://github.com/{self.org_name}/{self.repo_name}/issues")
        print(f"View project: https://github.com/orgs/{self.org_name}/projects")
        print()

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='GitHub Governance Factory')
    parser.add_argument('--config', type=str, help='Path to governance configuration file')
    parser.add_argument('--org', type=str, default='frankmax-com', help='GitHub organization name')
    parser.add_argument('--repo', type=str, default='AI-DevOps-System', help='GitHub repository name')
    parser.add_argument('--execute', action='store_true', help='Execute governance creation')
    
    args = parser.parse_args()
    
    # Create and run governance factory
    factory = GitHubGovernanceFactory(args.org, args.repo)
    
    # Set custom config file if provided
    if args.config:
        factory.config_file = Path(args.config)
    
    if args.execute:
        factory.generate_all_governance()
    else:
        print("Use --execute flag to run governance creation")

if __name__ == "__main__":
    main()
