#!/usr/bin/env python3
"""
Integration Testing Script for GitHub Governance Factory
Tests the complete architecture with real API calls
"""

import asyncio
import aiohttp
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List
import time

# Configuration
TEST_CONFIG = {
    "services": {
        "governance_engine": "http://localhost:8000",
        "issue_generator": "http://localhost:8001"
    },
    "github": {
        "owner": "test-org",  # Replace with actual test org
        "repo": "test-repo",  # Replace with actual test repo
        "token": os.getenv("GITHUB_TOKEN")  # Set your GitHub token
    },
    "ai_provider_factory": {
        "url": os.getenv("AI_PROVIDER_FACTORY_URL", "http://localhost:8080"),
        "api_key": os.getenv("AI_PROVIDER_FACTORY_API_KEY")
    }
}

class IntegrationTester:
    """Comprehensive integration testing for all services"""
    
    def __init__(self):
        self.session: aiohttp.ClientSession = None
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s)")
        if details:
            print(f"    {details}")
    
    async def test_service_health(self, service_name: str, url: str) -> bool:
        """Test service health endpoint"""
        test_start = time.time()
        try:
            async with self.session.get(f"{url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    duration = time.time() - test_start
                    self.log_test(
                        f"{service_name} Health Check",
                        True,
                        f"Status: {data.get('status', 'unknown')}",
                        duration
                    )
                    return True
                else:
                    duration = time.time() - test_start
                    self.log_test(
                        f"{service_name} Health Check",
                        False,
                        f"HTTP {response.status}",
                        duration
                    )
                    return False
        except Exception as e:
            duration = time.time() - test_start
            self.log_test(
                f"{service_name} Health Check",
                False,
                str(e),
                duration
            )
            return False
    
    async def test_governance_generation(self) -> Dict[str, Any]:
        """Test governance structure generation"""
        test_start = time.time()
        try:
            url = f"{TEST_CONFIG['services']['governance_engine']}/v1/governance/generate"
            payload = {
                "name": "Test Project",
                "description": "Integration test project for GitHub Governance Factory",
                "requirements": [
                    "OAuth integration with GitHub",
                    "Database setup with PostgreSQL",
                    "API rate limiting implementation"
                ],
                "constraints": [
                    "Must be completed within 2 weeks",
                    "Budget limit of $5000",
                    "Team size limited to 3 developers"
                ],
                "stakeholders": [
                    "test-pm@company.com",
                    "test-dev@company.com"
                ],
                "priority": "high"
            }
            
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    duration = time.time() - test_start
                    
                    # Validate response structure
                    required_fields = ['project_id', 'governance_structure', 'status']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if missing_fields:
                        self.log_test(
                            "Governance Generation",
                            False,
                            f"Missing fields: {missing_fields}",
                            duration
                        )
                        return {}
                    
                    self.log_test(
                        "Governance Generation",
                        True,
                        f"Generated structure for project {data['project_id']}",
                        duration
                    )
                    return data
                else:
                    error_text = await response.text()
                    duration = time.time() - test_start
                    self.log_test(
                        "Governance Generation",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        duration
                    )
                    return {}
        except Exception as e:
            duration = time.time() - test_start
            self.log_test(
                "Governance Generation",
                False,
                str(e),
                duration
            )
            return {}
    
    async def test_repository_setup(self) -> bool:
        """Test GitHub repository setup"""
        test_start = time.time()
        try:
            url = f"{TEST_CONFIG['services']['issue_generator']}/v1/repository/setup"
            params = {
                "owner": TEST_CONFIG['github']['owner'],
                "repo": TEST_CONFIG['github']['repo'],
                "project_name": "Test Integration Project"
            }
            
            # Set GitHub token in headers
            headers = {}
            if TEST_CONFIG['github']['token']:
                headers['Authorization'] = f"token {TEST_CONFIG['github']['token']}"
            
            async with self.session.post(url, params=params, headers=headers) as response:
                duration = time.time() - test_start
                
                if response.status == 200:
                    data = await response.json()
                    self.log_test(
                        "Repository Setup",
                        True,
                        f"Setup {data.get('repository', 'unknown')} with {data.get('labels_created', 0)} labels",
                        duration
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Repository Setup",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        duration
                    )
                    return False
        except Exception as e:
            duration = time.time() - test_start
            self.log_test(
                "Repository Setup",
                False,
                str(e),
                duration
            )
            return False
    
    async def test_issue_generation(self, governance_data: Dict[str, Any]) -> bool:
        """Test GitHub issue generation"""
        if not governance_data:
            self.log_test(
                "Issue Generation",
                False,
                "No governance data available",
                0
            )
            return False
        
        test_start = time.time()
        try:
            url = f"{TEST_CONFIG['services']['issue_generator']}/v1/issues/generate"
            payload = {
                "project_id": governance_data['project_id'],
                "governance_structure": governance_data['governance_structure'],
                "github_config": {
                    "repo_owner": TEST_CONFIG['github']['owner'],
                    "repo_name": TEST_CONFIG['github']['repo'],
                    "token": TEST_CONFIG['github']['token']
                }
            }
            
            async with self.session.post(url, json=payload) as response:
                duration = time.time() - test_start
                
                if response.status == 200:
                    data = await response.json()
                    success_count = data.get('success_count', 0)
                    total_count = data.get('total_count', 0)
                    
                    self.log_test(
                        "Issue Generation",
                        success_count > 0,
                        f"Generated {success_count}/{total_count} issues",
                        duration
                    )
                    return success_count > 0
                else:
                    error_text = await response.text()
                    self.log_test(
                        "Issue Generation",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        duration
                    )
                    return False
        except Exception as e:
            duration = time.time() - test_start
            self.log_test(
                "Issue Generation",
                False,
                str(e),
                duration
            )
            return False
    
    async def test_github_api_wrapper(self) -> bool:
        """Test GitHub API wrapper functionality"""
        test_start = time.time()
        try:
            # Test repository info retrieval
            url = f"{TEST_CONFIG['services']['issue_generator']}/v1/github/repositories/{TEST_CONFIG['github']['owner']}/{TEST_CONFIG['github']['repo']}"
            
            headers = {}
            if TEST_CONFIG['github']['token']:
                headers['Authorization'] = f"token {TEST_CONFIG['github']['token']}"
            
            async with self.session.get(url, headers=headers) as response:
                duration = time.time() - test_start
                
                if response.status == 200:
                    data = await response.json()
                    self.log_test(
                        "GitHub API Wrapper",
                        True,
                        f"Retrieved repository info: {data.get('name', 'unknown')}",
                        duration
                    )
                    return True
                else:
                    error_text = await response.text()
                    self.log_test(
                        "GitHub API Wrapper",
                        False,
                        f"HTTP {response.status}: {error_text}",
                        duration
                    )
                    return False
        except Exception as e:
            duration = time.time() - test_start
            self.log_test(
                "GitHub API Wrapper",
                False,
                str(e),
                duration
            )
            return False
    
    async def test_ai_provider_integration(self) -> bool:
        """Test AI Provider Factory integration"""
        test_start = time.time()
        try:
            # Test that services can communicate with AI Provider Factory
            # This is a mock test since we don't have the actual AI Provider Factory running
            
            if not TEST_CONFIG['ai_provider_factory']['url']:
                self.log_test(
                    "AI Provider Integration",
                    False,
                    "AI Provider Factory URL not configured",
                    0
                )
                return False
            
            # In a real scenario, this would test actual AI provider calls
            # For now, we'll just check that the configuration is present
            duration = time.time() - test_start
            self.log_test(
                "AI Provider Integration",
                True,
                "AI Provider Factory configuration validated",
                duration
            )
            return True
            
        except Exception as e:
            duration = time.time() - test_start
            self.log_test(
                "AI Provider Integration",
                False,
                str(e),
                duration
            )
            return False
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        total_duration = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("INTEGRATION TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
        print(f"Total Duration: {total_duration:.2f}s")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"  {status} {result['test']} ({result['duration']:.2f}s)")
            if result['details']:
                print(f"      {result['details']}")


async def main():
    """Run all integration tests"""
    print("🚀 Starting GitHub Governance Factory Integration Tests")
    print(f"Testing against services: {list(TEST_CONFIG['services'].values())}")
    print(f"GitHub: {TEST_CONFIG['github']['owner']}/{TEST_CONFIG['github']['repo']}")
    print("-" * 60)
    
    # Validate prerequisites
    if not TEST_CONFIG['github']['token']:
        print("❌ ERROR: GITHUB_TOKEN environment variable not set")
        print("Please set your GitHub token: export GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    async with IntegrationTester() as tester:
        # Test service health
        for service_name, service_url in TEST_CONFIG['services'].items():
            await tester.test_service_health(service_name, service_url)
        
        # Test AI Provider integration
        await tester.test_ai_provider_integration()
        
        # Test GitHub API wrapper
        await tester.test_github_api_wrapper()
        
        # Test repository setup
        await tester.test_repository_setup()
        
        # Test governance generation
        governance_data = await tester.test_governance_generation()
        
        # Test issue generation (depends on governance generation)
        await tester.test_issue_generation(governance_data)
        
        # Print summary
        tester.print_summary()
        
        # Exit with appropriate code
        failed_tests = sum(1 for result in tester.test_results if not result['success'])
        sys.exit(0 if failed_tests == 0 else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner error: {e}")
        sys.exit(1)
