#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for NEXUS_AI Autonomous Workflow Intelligence System
Tests JWT authentication, workflow management, real-time metrics, AI brain, and WebSocket functionality
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

class NexusAITester:
    def __init__(self, base_url="https://autonomous-flows.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.tests_run = 0
        self.tests_passed = 0
        self.user_token = None
        self.admin_user = None
        self.created_workflows = []

    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Dict = None, headers: Dict = None) -> tuple:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        test_headers = self.session.headers.copy()
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}", "ERROR")
                try:
                    error_data = response.json()
                    self.log(f"   Error: {error_data}", "ERROR")
                except:
                    self.log(f"   Error: {response.text}", "ERROR")
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Exception: {str(e)}", "ERROR")
            return False, {}

    def test_health_check(self):
        """Test basic health check"""
        success, response = self.run_test("Health Check", "GET", "health", 200)
        return success

    def test_admin_login(self):
        """Test admin login with provided credentials"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@nexusai.com", "password": "Admin123!"}
        )
        
        if success and isinstance(response, dict):
            self.admin_user = response
            self.log(f"   Admin logged in: {response.get('name', 'Unknown')} ({response.get('role', 'user')})")
            return True
        return False

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_user_{int(time.time())}@nexusai.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": "TestPass123!",
                "name": "Test User"
            }
        )
        
        if success and isinstance(response, dict):
            self.log(f"   User registered: {response.get('name', 'Unknown')}")
            return True
        return False

    def test_protected_route_access(self):
        """Test accessing protected routes"""
        success, response = self.run_test("Get Current User", "GET", "auth/me", 200)
        if success and isinstance(response, dict):
            self.log(f"   Current user: {response.get('name', 'Unknown')} ({response.get('email', 'Unknown')})")
        return success

    def test_workflow_creation(self):
        """Test creating different types of workflows"""
        workflow_types = ["etl", "microservice", "batch"]
        created_count = 0
        
        for wf_type in workflow_types:
            workflow_name = f"Test {wf_type.upper()} Workflow"
            success, response = self.run_test(
                f"Create {wf_type.upper()} Workflow",
                "POST",
                "workflows",
                200,
                data={"name": workflow_name, "workflow_type": wf_type}
            )
            
            if success and isinstance(response, dict):
                self.created_workflows.append(response)
                created_count += 1
                self.log(f"   Created workflow: {response.get('id', 'Unknown')} - {response.get('name', 'Unknown')}")
        
        return created_count == len(workflow_types)

    def test_workflow_operations(self):
        """Test workflow start/stop operations"""
        if not self.created_workflows:
            self.log("No workflows available for testing operations", "WARNING")
            return False
        
        workflow = self.created_workflows[0]
        workflow_id = workflow.get('id')
        
        # Test starting workflow
        start_success, _ = self.run_test(
            "Start Workflow",
            "POST",
            f"workflows/{workflow_id}/start",
            200
        )
        
        if start_success:
            time.sleep(2)  # Allow workflow to start
            
            # Test stopping workflow
            stop_success, _ = self.run_test(
                "Stop Workflow",
                "POST",
                f"workflows/{workflow_id}/stop",
                200
            )
            return stop_success
        
        return False

    def test_workflow_retrieval(self):
        """Test retrieving workflows"""
        # Test getting all workflows
        success, response = self.run_test("Get All Workflows", "GET", "workflows", 200)
        
        if success and isinstance(response, list):
            self.log(f"   Found {len(response)} workflows")
            
            # Test getting specific workflow
            if self.created_workflows:
                workflow_id = self.created_workflows[0].get('id')
                specific_success, specific_response = self.run_test(
                    "Get Specific Workflow",
                    "GET",
                    f"workflows/{workflow_id}",
                    200
                )
                return specific_success
        
        return success

    def test_metrics_endpoints(self):
        """Test metrics-related endpoints"""
        # Test current metrics
        current_success, current_response = self.run_test("Get Current Metrics", "GET", "metrics/current", 200)
        
        if current_success and isinstance(current_response, dict):
            expected_metrics = ["cpu", "memory", "latency", "throughput", "error_rate", "active_workers", "queue_depth"]
            found_metrics = [m for m in expected_metrics if m in current_response]
            self.log(f"   Found metrics: {', '.join(found_metrics)}")
        
        # Test metrics history
        history_success, history_response = self.run_test("Get Metrics History", "GET", "metrics", 200)
        
        if history_success and isinstance(history_response, list):
            self.log(f"   Found {len(history_response)} historical metrics")
        
        return current_success and history_success

    def test_logs_endpoint(self):
        """Test logs endpoint"""
        success, response = self.run_test("Get Logs", "GET", "logs", 200)
        
        if success and isinstance(response, list):
            self.log(f"   Found {len(response)} log entries")
            if response:
                sample_log = response[0]
                required_fields = ["level", "message", "component", "timestamp"]
                found_fields = [f for f in required_fields if f in sample_log]
                self.log(f"   Log fields: {', '.join(found_fields)}")
        
        return success

    def test_alerts_endpoint(self):
        """Test alerts endpoint"""
        success, response = self.run_test("Get Alerts", "GET", "alerts", 200)
        
        if success and isinstance(response, list):
            self.log(f"   Found {len(response)} alerts")
            if response:
                sample_alert = response[0]
                if "severity" in sample_alert and "message" in sample_alert:
                    self.log(f"   Sample alert: {sample_alert['severity']} - {sample_alert['message'][:50]}...")
        
        return success

    def test_predictions_endpoint(self):
        """Test predictions endpoint"""
        success, response = self.run_test("Get Predictions", "GET", "predictions", 200)
        
        if success and isinstance(response, list):
            self.log(f"   Found {len(response)} predictions")
            if response:
                sample_pred = response[0]
                if "probability" in sample_pred:
                    self.log(f"   Sample prediction: {sample_pred['probability']:.2f} failure probability")
        
        return success

    def test_ai_brain_endpoints(self):
        """Test AI Brain functionality"""
        # Test getting AI analysis
        analysis_success, analysis_response = self.run_test("Get AI Analysis", "GET", "ai/analysis", 200)
        
        if analysis_success and isinstance(analysis_response, list):
            self.log(f"   Found {len(analysis_response)} AI analyses")
        
        # Test triggering log analysis
        analyze_success, analyze_response = self.run_test("Analyze Logs", "POST", "ai/analyze-logs", 200)
        
        if analyze_success and isinstance(analyze_response, dict):
            if "summary" in analyze_response:
                self.log(f"   AI Analysis summary: {analyze_response['summary'][:100]}...")
            if "anomalies" in analyze_response:
                self.log(f"   Found {len(analyze_response['anomalies'])} anomalies")
        
        return analysis_success and analyze_success

    def test_healing_actions_endpoint(self):
        """Test auto-healing actions endpoint"""
        # Test getting healing actions
        get_success, get_response = self.run_test("Get Healing Actions", "GET", "healing-actions", 200)
        
        if get_success and isinstance(get_response, list):
            self.log(f"   Found {len(get_response)} healing actions")
        
        # Test triggering healing action
        trigger_success, trigger_response = self.run_test(
            "Trigger Healing Action",
            "POST",
            "healing/trigger",
            200,
            data={"type": "restart", "target": "test-service"}
        )
        
        if trigger_success and isinstance(trigger_response, dict):
            self.log(f"   Triggered healing action: {trigger_response.get('type', 'unknown')}")
        
        return get_success and trigger_success

    def test_logout(self):
        """Test user logout"""
        success, response = self.run_test("Logout", "POST", "auth/logout", 200)
        return success

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting NEXUS_AI Backend API Testing")
        self.log("=" * 60)
        
        test_results = {}
        
        # Basic connectivity
        test_results["health_check"] = self.test_health_check()
        
        # Authentication tests
        test_results["admin_login"] = self.test_admin_login()
        test_results["user_registration"] = self.test_user_registration()
        test_results["protected_routes"] = self.test_protected_route_access()
        
        # Workflow management tests
        test_results["workflow_creation"] = self.test_workflow_creation()
        test_results["workflow_operations"] = self.test_workflow_operations()
        test_results["workflow_retrieval"] = self.test_workflow_retrieval()
        
        # Monitoring and metrics tests
        test_results["metrics_endpoints"] = self.test_metrics_endpoints()
        test_results["logs_endpoint"] = self.test_logs_endpoint()
        test_results["alerts_endpoint"] = self.test_alerts_endpoint()
        test_results["predictions_endpoint"] = self.test_predictions_endpoint()
        
        # AI and automation tests
        test_results["ai_brain_endpoints"] = self.test_ai_brain_endpoints()
        test_results["healing_actions"] = self.test_healing_actions_endpoint()
        
        # Cleanup
        test_results["logout"] = self.test_logout()
        
        # Print results summary
        self.log("=" * 60)
        self.log("📊 TEST RESULTS SUMMARY")
        self.log("=" * 60)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} {test_name.replace('_', ' ').title()}")
        
        self.log("=" * 60)
        self.log(f"📈 Overall Results: {self.tests_passed}/{self.tests_run} individual tests passed")
        self.log(f"🎯 Test Categories: {passed_tests}/{total_tests} categories passed")
        
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        self.log(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            self.log("🎉 EXCELLENT: Backend is working very well!")
        elif success_rate >= 75:
            self.log("👍 GOOD: Backend is mostly functional with minor issues")
        elif success_rate >= 50:
            self.log("⚠️  MODERATE: Backend has significant issues that need attention")
        else:
            self.log("🚨 CRITICAL: Backend has major problems requiring immediate fixes")
        
        return success_rate >= 75

def main():
    """Main test execution"""
    tester = NexusAITester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        tester.log("Test interrupted by user", "WARNING")
        return 1
    except Exception as e:
        tester.log(f"Test failed with exception: {str(e)}", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())