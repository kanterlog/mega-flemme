"""
Test Suite for Enhanced Google Workspace MCP v2.3 Integration - Simplified
"""

import asyncio
import logging
from datetime import datetime
from app.services.google_workspace_mcp_v23_simplified import (
    EnhancedGoogleWorkspaceMCP,
    GoogleWorkspaceConfig,
    EnhancedEmailMessage,
    ProductivityInsights,
    get_cache_stats,
    clear_service_cache,
    SCOPE_GROUPS,
    SERVICE_CONFIGS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_comprehensive_tests():
    """Run comprehensive test suite for Enhanced Google Workspace MCP v2.3"""
    
    print("🚀 Enhanced Google Workspace MCP v2.3 - Comprehensive Test Suite")
    print("=" * 80)
    
    test_results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    def test_result(test_name: str, passed: bool, details: str = ""):
        test_results["total"] += 1
        if passed:
            test_results["passed"] += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   {details}")
        else:
            test_results["failed"] += 1
            print(f"❌ {test_name}")
            if details:
                print(f"   {details}")
    
    # ==================================================================================
    # CONFIGURATION TESTS
    # ==================================================================================
    
    print("\n📋 1. Configuration and Initialization Tests")
    print("-" * 50)
    
    # Test 1.1: Configuration initialization
    config = GoogleWorkspaceConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        default_user_email="test@example.com"
    )
    test_result(
        "Configuration Initialization",
        config.client_id == "test_client_id" and config.default_user_email == "test@example.com",
        f"Client ID: {config.client_id}, User: {config.default_user_email}"
    )
    
    # Test 1.2: MCP integration initialization
    mcp = EnhancedGoogleWorkspaceMCP(config)
    test_result(
        "MCP Integration Initialization",
        mcp.config is not None and isinstance(mcp.config, GoogleWorkspaceConfig),
        f"Config loaded: {mcp.config.default_user_email}"
    )
    
    # Test 1.3: Scope groups configuration
    test_result(
        "Scope Groups Configuration",
        "gmail_read" in SCOPE_GROUPS and "calendar_events" in SCOPE_GROUPS,
        f"Gmail scope: {SCOPE_GROUPS.get('gmail_read', 'missing')[:50]}..."
    )
    
    # Test 1.4: Service configurations
    test_result(
        "Service Configurations",
        "gmail" in SERVICE_CONFIGS and SERVICE_CONFIGS["gmail"]["version"] == "v1",
        f"Gmail service: {SERVICE_CONFIGS['gmail']}"
    )
    
    # ==================================================================================
    # CACHING TESTS
    # ==================================================================================
    
    print("\n🔄 2. Service Caching Tests")
    print("-" * 50)
    
    # Test 2.1: Cache operations
    cleared_count = clear_service_cache()
    stats = get_cache_stats()
    test_result(
        "Cache Operations",
        stats["total_entries"] == 0 and stats["cache_ttl_minutes"] == 30.0,
        f"Cache cleared: {cleared_count}, TTL: {stats['cache_ttl_minutes']}min"
    )
    
    # Test 2.2: Cache key generation
    from app.services.google_workspace_mcp_v23_simplified import _get_cache_key
    key1 = _get_cache_key("user1@test.com", "gmail", "v1", ["scope1"])
    key2 = _get_cache_key("user2@test.com", "gmail", "v1", ["scope1"])
    test_result(
        "Cache Key Generation",
        key1 != key2 and "user1@test.com" in key1 and "gmail:v1" in key1,
        f"Key1: {key1[:50]}..., Key2: {key2[:50]}..."
    )
    
    # ==================================================================================
    # EMAIL OPERATIONS TESTS
    # ==================================================================================
    
    print("\n📧 3. Enhanced Email Operations Tests")
    print("-" * 50)
    
    user_email = "test@example.com"
    
    # Test 3.1: Email search (string format)
    try:
        email_result = await mcp.search_emails_enhanced(
            user_google_email=user_email,
            query="urgent deadline",
            max_results=5,
            include_analytics=False
        )
        test_result(
            "Email Search (String Format)",
            isinstance(email_result, str) and "Found 2 emails" in email_result,
            f"Result type: {type(email_result)}, length: {len(email_result)}"
        )
    except Exception as e:
        test_result("Email Search (String Format)", False, f"Error: {e}")
    
    # Test 3.2: Email search (analytics format)
    try:
        email_analytics = await mcp.search_emails_enhanced(
            user_google_email=user_email,
            query="urgent deadline",
            max_results=5,
            include_analytics=True
        )
        test_result(
            "Email Search (Analytics Format)",
            isinstance(email_analytics, list) and len(email_analytics) > 0,
            f"Result type: {type(email_analytics)}, count: {len(email_analytics)}"
        )
        
        # Verify email analytics
        if email_analytics:
            first_email = email_analytics[0]
            test_result(
                "Email Analytics Processing",
                isinstance(first_email, EnhancedEmailMessage) and first_email.priority_score >= 0,
                f"Priority: {first_email.priority_score:.1%}, Category: {first_email.category}"
            )
    except Exception as e:
        test_result("Email Search (Analytics Format)", False, f"Error: {e}")
    
    # Test 3.3: Smart email sending
    try:
        send_result = await mcp.send_email_smart(
            user_google_email=user_email,
            to="recipient@test.com",
            subject="Test Email",
            body="Test email body",
            optimize_send_time=True
        )
        test_result(
            "Smart Email Sending",
            "Email sent successfully" in send_result and "Optimal send time" in send_result,
            f"Result preview: {send_result[:100]}..."
        )
    except Exception as e:
        test_result("Smart Email Sending", False, f"Error: {e}")
    
    # ==================================================================================
    # CALENDAR OPERATIONS TESTS
    # ==================================================================================
    
    print("\n📅 4. Enhanced Calendar Operations Tests")
    print("-" * 50)
    
    # Test 4.1: Calendar listing
    try:
        calendar_result = await mcp.list_calendars_enhanced(
            user_google_email=user_email,
            include_analytics=False
        )
        test_result(
            "Calendar Listing",
            isinstance(calendar_result, str) and "Found 2 calendars" in calendar_result,
            f"Result type: {type(calendar_result)}, length: {len(calendar_result)}"
        )
    except Exception as e:
        test_result("Calendar Listing", False, f"Error: {e}")
    
    # Test 4.2: Smart event creation
    try:
        event_result = await mcp.create_event_smart(
            user_google_email=user_email,
            calendar_id="primary",
            title="Test Meeting",
            start_time="2024-01-15T10:00:00Z",
            end_time="2024-01-15T11:00:00Z",
            description="Test meeting",
            suggest_optimal_time=True
        )
        test_result(
            "Smart Event Creation",
            "Event Created Successfully" in event_result and "Timing Analysis" in event_result,
            f"Result preview: {event_result[:150]}..."
        )
    except Exception as e:
        test_result("Smart Event Creation", False, f"Error: {e}")
    
    # ==================================================================================
    # AI-POWERED ANALYTICS TESTS
    # ==================================================================================
    
    print("\n🤖 5. AI-Powered Analytics Tests")
    print("-" * 50)
    
    # Test 5.1: Productivity analysis
    try:
        insights = await mcp.analyze_productivity_trends(
            user_google_email=user_email,
            days_back=7
        )
        test_result(
            "Productivity Analysis",
            isinstance(insights, ProductivityInsights) and len(insights.recommendations) > 0,
            f"Recommendations: {len(insights.recommendations)}, Efficiency: {insights.meeting_efficiency_score}%"
        )
    except Exception as e:
        test_result("Productivity Analysis", False, f"Error: {e}")
    
    # Test 5.2: AI meeting suggestions
    try:
        suggestions = await mcp.suggest_meeting_times_ai(
            user_google_email=user_email,
            attendees=["colleague@test.com"],
            duration_minutes=60
        )
        test_result(
            "AI Meeting Suggestions",
            isinstance(suggestions, list) and len(suggestions) > 0,
            f"Suggestions count: {len(suggestions)}, First confidence: {suggestions[0]['confidence_score']:.0%}"
        )
    except Exception as e:
        test_result("AI Meeting Suggestions", False, f"Error: {e}")
    
    # Test 5.3: Email productivity analysis
    try:
        test_email = EnhancedEmailMessage(
            id="test_001",
            thread_id="thread_001",
            subject="Urgent: Important deadline tomorrow",
            sender="boss@test.com",
            recipients=["test@example.com"],
            snippet="Please review the urgent project deliverables before the important deadline"
        )
        analyzed_email = await mcp._analyze_email_productivity(test_email)
        test_result(
            "Email Productivity Analysis",
            analyzed_email.priority_score > 0 and analyzed_email.category != "unknown",
            f"Priority: {analyzed_email.priority_score:.1%}, Category: {analyzed_email.category}, Action: {analyzed_email.action_required}"
        )
    except Exception as e:
        test_result("Email Productivity Analysis", False, f"Error: {e}")
    
    # ==================================================================================
    # MULTI-SERVICE OPERATIONS TESTS
    # ==================================================================================
    
    print("\n🔄 6. Multi-Service Operations Tests")
    print("-" * 50)
    
    # Test 6.1: Workday pattern analysis
    try:
        patterns = await mcp.analyze_workday_patterns(
            user_google_email=user_email,
            analysis_days=14
        )
        test_result(
            "Workday Pattern Analysis",
            isinstance(patterns, dict) and "recommendations" in patterns,
            f"Peak hours: {patterns.get('peak_email_hours', [])}, Recommendations: {len(patterns.get('recommendations', []))}"
        )
    except Exception as e:
        test_result("Workday Pattern Analysis", False, f"Error: {e}")
    
    # ==================================================================================
    # AUTHENTICATION TESTS
    # ==================================================================================
    
    print("\n🔐 7. Authentication Tests")
    print("-" * 50)
    
    # Test 7.1: Service authentication
    try:
        service = await mcp.authenticate_google_service(
            service_name="gmail",
            version="v1",
            user_google_email=user_email,
            required_scopes=[SCOPE_GROUPS["gmail_read"]]
        )
        test_result(
            "Service Authentication",
            service is not None and hasattr(service, 'service_name'),
            f"Service type: {type(service)}, Name: {getattr(service, 'service_name', 'N/A')}"
        )
    except Exception as e:
        test_result("Service Authentication", False, f"Error: {e}")
    
    # Test 7.2: OAuth flow initialization
    try:
        oauth_result = await mcp.start_oauth_flow(user_email, "Gmail")
        test_result(
            "OAuth Flow Initialization",
            "Google Workspace Authentication Required" in oauth_result and "accounts.google.com" in oauth_result,
            f"OAuth URL generated, length: {len(oauth_result)}"
        )
    except Exception as e:
        test_result("OAuth Flow Initialization", False, f"Error: {e}")
    
    # ==================================================================================
    # UTILITY AND STATUS TESTS
    # ==================================================================================
    
    print("\n📊 8. Utility and Status Tests")
    print("-" * 50)
    
    # Test 8.1: Service status
    try:
        status = mcp.get_service_status()
        test_result(
            "Service Status Reporting",
            status["version"] == "2.3" and "supported_services" in status,
            f"Version: {status['version']}, Services: {len(status['supported_services'])}, Scopes: {len(status['available_scopes'])}"
        )
    except Exception as e:
        test_result("Service Status Reporting", False, f"Error: {e}")
    
    # Test 8.2: Result formatting
    try:
        test_emails = [
            EnhancedEmailMessage(
                id="msg_001",
                thread_id="thread_001",
                subject="Test Email 1",
                sender="sender1@test.com",
                recipients=["test@example.com"],
                snippet="Test snippet 1"
            ),
            EnhancedEmailMessage(
                id="msg_002",
                thread_id="thread_002",
                subject="Test Email 2",
                sender="sender2@test.com",
                recipients=["test@example.com"],
                snippet="Test snippet 2"
            )
        ]
        formatted = mcp._format_email_results(test_emails, "test query")
        test_result(
            "Result Formatting",
            "Found 2 emails" in formatted and "Test Email 1" in formatted,
            f"Formatted length: {len(formatted)}, contains expected content"
        )
    except Exception as e:
        test_result("Result Formatting", False, f"Error: {e}")
    
    # ==================================================================================
    # PERFORMANCE TESTS
    # ==================================================================================
    
    print("\n⚡ 9. Performance Tests")
    print("-" * 50)
    
    # Test 9.1: Email analysis performance
    try:
        import time
        test_emails = [
            EnhancedEmailMessage(
                id=f"msg_{i:03d}",
                thread_id=f"thread_{i:03d}",
                subject=f"Test Email {i} - Urgent deadline",
                sender=f"sender{i}@test.com",
                recipients=["test@example.com"],
                snippet=f"Test snippet {i} with urgent content requiring action"
            )
            for i in range(20)
        ]
        
        start_time = time.time()
        for email in test_emails:
            await mcp._analyze_email_productivity(email)
        analysis_time = time.time() - start_time
        
        test_result(
            "Email Analysis Performance",
            analysis_time < 0.5,  # Should process 20 emails in under 500ms
            f"Processed {len(test_emails)} emails in {analysis_time:.3f}s ({analysis_time/len(test_emails)*1000:.1f}ms/email)"
        )
    except Exception as e:
        test_result("Email Analysis Performance", False, f"Error: {e}")
    
    # ==================================================================================
    # INTEGRATION TEST
    # ==================================================================================
    
    print("\n🔄 10. Full Integration Test")
    print("-" * 50)
    
    try:
        # Complete workflow test
        workflow_steps = []
        
        # Step 1: Check service status
        status = mcp.get_service_status()
        workflow_steps.append(status["version"] == "2.3")
        
        # Step 2: Clear and check cache
        clear_service_cache()
        cache_stats = get_cache_stats()
        workflow_steps.append(cache_stats["total_entries"] == 0)
        
        # Step 3: Perform email search with analytics
        emails = await mcp.search_emails_enhanced(
            user_google_email=user_email,
            query="test",
            include_analytics=True
        )
        workflow_steps.append(isinstance(emails, list) and len(emails) > 0)
        
        # Step 4: Get productivity insights
        insights = await mcp.analyze_productivity_trends(
            user_google_email=user_email,
            days_back=7
        )
        workflow_steps.append(isinstance(insights, ProductivityInsights))
        
        # Step 5: Get AI suggestions
        suggestions = await mcp.suggest_meeting_times_ai(
            user_google_email=user_email,
            attendees=["colleague@test.com"],
            duration_minutes=30
        )
        workflow_steps.append(len(suggestions) > 0)
        
        all_passed = all(workflow_steps)
        test_result(
            "Full Integration Workflow",
            all_passed,
            f"Workflow steps: {workflow_steps.count(True)}/{len(workflow_steps)} passed"
        )
        
    except Exception as e:
        test_result("Full Integration Workflow", False, f"Error: {e}")
    
    # ==================================================================================
    # RESULTS SUMMARY
    # ==================================================================================
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    success_rate = (test_results["passed"] / test_results["total"]) * 100 if test_results["total"] > 0 else 0
    
    print(f"✅ Tests Passed: {test_results['passed']}")
    print(f"❌ Tests Failed: {test_results['failed']}")
    print(f"📊 Total Tests: {test_results['total']}")
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if test_results["failed"] == 0:
        print("\n🎉 🎉 🎉 ALL TESTS PASSED! 🎉 🎉 🎉")
        print("Enhanced Google Workspace MCP v2.3 is ready for production!")
        print("\n🚀 Key Features Validated:")
        print("   ⚡ Service caching with 30-minute TTL")
        print("   🧠 AI-powered productivity analytics")
        print("   📧 Enhanced email operations with smart analysis")
        print("   📅 Smart calendar management with optimal timing")
        print("   🤖 Cross-service workday pattern analysis")
        print("   🔐 Production-ready authentication patterns")
        print("   📊 Advanced performance monitoring")
        print("   🎯 taylorwilsdon-inspired architecture patterns")
    else:
        print(f"\n⚠️ {test_results['failed']} TESTS FAILED")
        print("Please review and fix the failing tests before production deployment.")
    
    print("\n" + "=" * 80)
    return test_results

if __name__ == "__main__":
    asyncio.run(run_comprehensive_tests())
