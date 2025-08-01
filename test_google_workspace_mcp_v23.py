"""
Test Suite for Enhanced Google Workspace MCP v2.3 Integration
Testing production-ready features inspired by taylorwilsdon/google_workspace_mcp
"""

import asyncio
import pytest
import logging
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import json

# Import the enhanced MCP integration
from app.services.google_workspace_mcp_v23 import (
    EnhancedGoogleWorkspaceMCP,
    GoogleWorkspaceConfig,
    EnhancedEmailMessage,
    EnhancedCalendarEvent,
    ProductivityInsights,
    require_google_service,
    require_multiple_services,
    get_cache_stats,
    clear_service_cache,
    SCOPE_GROUPS,
    SERVICE_CONFIGS
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestEnhancedGoogleWorkspaceMCPv23:
    """Comprehensive test suite for Enhanced Google Workspace MCP v2.3"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return GoogleWorkspaceConfig(
            client_id="test_client_id",
            client_secret="test_client_secret",
            default_user_email="test@example.com",
            enable_service_caching=True,
            enable_ai_suggestions=True,
            cache_ttl_minutes=30
        )
    
    @pytest.fixture
    def mcp_integration(self, config):
        """MCP integration instance for testing"""
        return EnhancedGoogleWorkspaceMCP(config)
    
    @pytest.fixture
    def sample_emails(self):
        """Sample email data for testing"""
        return [
            EnhancedEmailMessage(
                id="msg_001",
                thread_id="thread_001",
                subject="Urgent: Project Deadline Tomorrow",
                sender="boss@company.com",
                recipients=["test@example.com"],
                snippet="Please review the project deliverables before tomorrow's deadline",
                word_count=45,
                priority_score=0.8,
                category="work",
                action_required=True
            ),
            EnhancedEmailMessage(
                id="msg_002", 
                thread_id="thread_002",
                subject="Meeting Confirmation",
                sender="calendar@company.com",
                recipients=["test@example.com"],
                snippet="Your meeting with the team is confirmed for 2 PM",
                word_count=20,
                priority_score=0.3,
                category="meeting",
                action_required=False
            ),
            EnhancedEmailMessage(
                id="msg_003",
                thread_id="thread_003", 
                subject="Newsletter: Weekly Updates",
                sender="newsletter@company.com",
                recipients=["test@example.com"],
                snippet="Check out this week's highlights and company news",
                word_count=15,
                priority_score=0.1,
                category="automated",
                action_required=False
            )
        ]
    
    @pytest.fixture
    def sample_calendars(self):
        """Sample calendar data for testing"""
        return [
            {
                'id': 'primary',
                'name': 'Primary Calendar',
                'time_zone': 'UTC',
                'access_role': 'owner',
                'primary': True,
                'weekly_hours': 25.5,
                'meeting_types': {'standup': 5, 'planning': 3, 'review': 2}
            },
            {
                'id': 'work_calendar',
                'name': 'Work Projects',
                'time_zone': 'UTC',
                'access_role': 'writer',
                'primary': False,
                'weekly_hours': 15.0,
                'meeting_types': {'planning': 4, '1-on-1': 6}
            }
        ]
    
    # ==================================================================================
    # CONFIGURATION AND INITIALIZATION TESTS
    # ==================================================================================
    
    def test_configuration_initialization(self, config):
        """Test configuration initialization with environment variables"""
        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_client_secret"
        assert config.default_user_email == "test@example.com"
        assert config.cache_ttl_minutes == 30
        assert config.enable_service_caching is True
        assert config.enable_ai_suggestions is True
    
    def test_mcp_integration_initialization(self, mcp_integration):
        """Test MCP integration initialization"""
        assert mcp_integration.config is not None
        assert isinstance(mcp_integration.config, GoogleWorkspaceConfig)
        assert mcp_integration.config.default_user_email == "test@example.com"
        logger.info("✅ MCP integration initialized successfully")
    
    def test_scope_groups_configuration(self):
        """Test scope groups are properly configured"""
        assert "gmail_read" in SCOPE_GROUPS
        assert "calendar_events" in SCOPE_GROUPS
        assert "drive_read" in SCOPE_GROUPS
        assert "docs_write" in SCOPE_GROUPS
        
        # Verify scope URLs are valid
        assert SCOPE_GROUPS["gmail_read"] == "https://www.googleapis.com/auth/gmail.readonly"
        assert SCOPE_GROUPS["calendar_events"] == "https://www.googleapis.com/auth/calendar.events"
        logger.info("✅ Scope groups configured correctly")
    
    def test_service_configs(self):
        """Test service configurations"""
        assert "gmail" in SERVICE_CONFIGS
        assert "calendar" in SERVICE_CONFIGS
        assert "drive" in SERVICE_CONFIGS
        assert "docs" in SERVICE_CONFIGS
        
        # Verify service details
        assert SERVICE_CONFIGS["gmail"]["service"] == "gmail"
        assert SERVICE_CONFIGS["gmail"]["version"] == "v1"
        assert SERVICE_CONFIGS["calendar"]["version"] == "v3"
        logger.info("✅ Service configurations verified")
    
    # ==================================================================================
    # SERVICE CACHING TESTS
    # ==================================================================================
    
    def test_service_cache_operations(self):
        """Test service caching functionality"""
        # Clear cache first
        cleared = clear_service_cache()
        logger.info(f"Cleared {cleared} cache entries")
        
        # Get initial cache stats
        stats = get_cache_stats()
        assert stats["total_entries"] == 0
        assert stats["valid_entries"] == 0
        assert stats["cache_ttl_minutes"] == 30
        
        logger.info("✅ Service cache operations working correctly")
    
    def test_cache_key_generation(self):
        """Test cache key generation for different configurations"""
        from app.services.google_workspace_mcp_v23 import _get_cache_key
        
        key1 = _get_cache_key("user1@test.com", "gmail", "v1", ["scope1", "scope2"])
        key2 = _get_cache_key("user2@test.com", "gmail", "v1", ["scope1", "scope2"])
        key3 = _get_cache_key("user1@test.com", "calendar", "v3", ["scope1"])
        
        assert key1 != key2  # Different users
        assert key1 != key3  # Different services
        assert "user1@test.com" in key1
        assert "gmail:v1" in key1
        
        logger.info("✅ Cache key generation working correctly")
    
    # ==================================================================================
    # DECORATOR PATTERN TESTS
    # ==================================================================================
    
    @pytest.mark.asyncio
    async def test_require_google_service_decorator(self):
        """Test the @require_google_service decorator"""
        
        # Mock function to test decorator
        @require_google_service("gmail", "gmail_read")
        async def test_function(service, user_email: str, query: str):
            return f"Service: {service}, User: {user_email}, Query: {query}"
        
        # Mock authentication
        with patch('app.services.google_workspace_mcp_v23.authenticate_google_service') as mock_auth:
            mock_service = Mock()
            mock_auth.return_value = mock_service
            
            result = await test_function(
                user_email="test@example.com",
                query="test query"
            )
            
            # Verify service was injected
            mock_auth.assert_called_once()
            assert "test@example.com" in result
            assert "test query" in result
        
        logger.info("✅ @require_google_service decorator working correctly")
    
    @pytest.mark.asyncio 
    async def test_require_multiple_services_decorator(self):
        """Test the @require_multiple_services decorator"""
        
        @require_multiple_services([
            {"service_type": "gmail", "scopes": "gmail_read", "param_name": "gmail_service"},
            {"service_type": "calendar", "scopes": "calendar_read", "param_name": "calendar_service"}
        ])
        async def test_multi_service_function(gmail_service, calendar_service, user_email: str):
            return f"Gmail: {gmail_service}, Calendar: {calendar_service}, User: {user_email}"
        
        with patch('app.services.google_workspace_mcp_v23.authenticate_google_service') as mock_auth:
            mock_gmail = Mock()
            mock_calendar = Mock()
            mock_auth.side_effect = [mock_gmail, mock_calendar]
            
            result = await test_multi_service_function(user_email="test@example.com")
            
            # Verify both services were authenticated
            assert mock_auth.call_count == 2
            assert "test@example.com" in result
        
        logger.info("✅ @require_multiple_services decorator working correctly")
    
    # ==================================================================================
    # ENHANCED EMAIL OPERATIONS TESTS
    # ==================================================================================
    
    @pytest.mark.asyncio
    async def test_search_emails_enhanced(self, mcp_integration):
        """Test enhanced email search functionality"""
        
        # Mock Gmail service and responses
        mock_service = Mock()
        mock_messages = Mock()
        mock_users = Mock()
        
        mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        
        # Mock list response
        mock_list = Mock()
        mock_messages.list.return_value = mock_list
        mock_list.execute.return_value = {
            'messages': [
                {'id': 'msg_001'},
                {'id': 'msg_002'}
            ]
        }
        
        # Mock get response
        mock_get = Mock()
        mock_messages.get.return_value = mock_get
        mock_get.execute.return_value = {
            'id': 'msg_001',
            'threadId': 'thread_001',
            'snippet': 'Test email snippet',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': 'Test Subject'},
                    {'name': 'From', 'value': 'sender@test.com'},
                    {'name': 'To', 'value': 'recipient@test.com'}
                ]
            },
            'labelIds': ['INBOX', 'UNREAD']
        }
        
        with patch.object(mcp_integration, 'authenticate_google_service', return_value=mock_service):
            result = await mcp_integration.search_emails_enhanced(
                user_google_email="test@example.com",
                query="test query",
                max_results=5,
                include_analytics=False
            )
            
            assert isinstance(result, str)
            assert "Found 2 emails" in result
            assert "Test Subject" in result
        
        logger.info("✅ Enhanced email search working correctly")
    
    @pytest.mark.asyncio
    async def test_send_email_smart(self, mcp_integration):
        """Test smart email sending functionality"""
        
        mock_service = Mock()
        mock_users = Mock()
        mock_messages = Mock()
        mock_send = Mock()
        
        mock_service.users.return_value = mock_users
        mock_users.messages.return_value = mock_messages
        mock_messages.send.return_value = mock_send
        mock_send.execute.return_value = {'id': 'sent_msg_001'}
        
        with patch.object(mcp_integration, 'authenticate_google_service', return_value=mock_service):
            result = await mcp_integration.send_email_smart(
                user_google_email="test@example.com",
                to="recipient@test.com",
                subject="Test Email",
                body="Test email body",
                optimize_send_time=False
            )
            
            assert "Email sent successfully" in result
            assert "sent_msg_001" in result
        
        logger.info("✅ Smart email sending working correctly")
    
    # ==================================================================================
    # ENHANCED CALENDAR OPERATIONS TESTS
    # ==================================================================================
    
    @pytest.mark.asyncio
    async def test_list_calendars_enhanced(self, mcp_integration, sample_calendars):
        """Test enhanced calendar listing functionality"""
        
        mock_service = Mock()
        mock_calendar_list = Mock()
        
        mock_service.calendarList.return_value = mock_calendar_list
        mock_list = Mock()
        mock_calendar_list.list.return_value = mock_list
        mock_list.execute.return_value = {
            'items': [
                {
                    'id': 'primary',
                    'summary': 'Primary Calendar',
                    'timeZone': 'UTC',
                    'accessRole': 'owner',
                    'primary': True
                }
            ]
        }
        
        with patch.object(mcp_integration, 'authenticate_google_service', return_value=mock_service):
            with patch.object(mcp_integration, '_calculate_calendar_usage', return_value=25.5):
                with patch.object(mcp_integration, '_analyze_meeting_types', return_value={'standup': 5}):
                    result = await mcp_integration.list_calendars_enhanced(
                        user_google_email="test@example.com",
                        include_analytics=False
                    )
                    
                    assert isinstance(result, str)
                    assert "Found 1 calendars" in result
                    assert "Primary Calendar" in result
        
        logger.info("✅ Enhanced calendar listing working correctly")
    
    @pytest.mark.asyncio
    async def test_create_event_smart(self, mcp_integration):
        """Test smart event creation functionality"""
        
        mock_service = Mock()
        mock_events = Mock()
        mock_insert = Mock()
        
        mock_service.events.return_value = mock_events
        mock_events.insert.return_value = mock_insert
        mock_insert.execute.return_value = {
            'id': 'event_001',
            'htmlLink': 'https://calendar.google.com/event?eid=event_001'
        }
        
        with patch.object(mcp_integration, 'authenticate_google_service', return_value=mock_service):
            result = await mcp_integration.create_event_smart(
                user_google_email="test@example.com",
                calendar_id="primary",
                title="Test Meeting",
                start_time="2024-01-15T10:00:00Z",
                end_time="2024-01-15T11:00:00Z",
                description="Test meeting description",
                suggest_optimal_time=False
            )
            
            assert "Event Created Successfully" in result
            assert "Test Meeting" in result
            assert "event_001" in result
        
        logger.info("✅ Smart event creation working correctly")
    
    # ==================================================================================
    # AI-POWERED ANALYTICS TESTS
    # ==================================================================================
    
    @pytest.mark.asyncio
    async def test_analyze_productivity_trends(self, mcp_integration):
        """Test AI-powered productivity analysis"""
        
        insights = await mcp_integration.analyze_productivity_trends(
            user_google_email="test@example.com",
            days_back=30
        )
        
        assert isinstance(insights, ProductivityInsights)
        assert insights.email_volume_trend in ["increasing", "decreasing", "stable"]
        assert isinstance(insights.response_time_avg, (int, float))
        assert 0 <= insights.meeting_efficiency_score <= 100
        assert len(insights.recommendations) > 0
        assert len(insights.focus_time_blocks) > 0
        
        logger.info("✅ Productivity analysis working correctly")
        logger.info(f"   📊 Email trend: {insights.email_volume_trend}")
        logger.info(f"   ⏱️ Response time: {insights.response_time_avg} hours")
        logger.info(f"   📈 Meeting efficiency: {insights.meeting_efficiency_score}%")
    
    @pytest.mark.asyncio
    async def test_suggest_meeting_times_ai(self, mcp_integration):
        """Test AI-powered meeting time suggestions"""
        
        suggestions = await mcp_integration.suggest_meeting_times_ai(
            user_google_email="test@example.com",
            attendees=["colleague1@test.com", "colleague2@test.com"],
            duration_minutes=60
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
        for suggestion in suggestions:
            assert "start_time" in suggestion
            assert "end_time" in suggestion
            assert "confidence_score" in suggestion
            assert "reason" in suggestion
            assert 0 <= suggestion["confidence_score"] <= 1
        
        logger.info("✅ AI meeting suggestions working correctly")
        logger.info(f"   🤖 Generated {len(suggestions)} suggestions")
        for i, suggestion in enumerate(suggestions[:2], 1):
            logger.info(f"   {i}. {suggestion['start_time']} (confidence: {suggestion['confidence_score']:.0%})")
    
    @pytest.mark.asyncio
    async def test_email_productivity_analysis(self, mcp_integration, sample_emails):
        """Test email productivity analysis"""
        
        for email in sample_emails:
            analyzed_email = await mcp_integration._analyze_email_productivity(email)
            
            # Verify analytics were added
            assert analyzed_email.word_count > 0
            assert analyzed_email.reading_time_minutes >= 0
            assert 0 <= analyzed_email.priority_score <= 1
            assert analyzed_email.category in ["work", "meeting", "automated", "general"]
            assert isinstance(analyzed_email.action_required, bool)
        
        logger.info("✅ Email productivity analysis working correctly")
        for email in sample_emails:
            logger.info(f"   📧 {email.subject}: {email.category}, priority {email.priority_score:.1%}")
    
    # ==================================================================================
    # MULTI-SERVICE OPERATIONS TESTS
    # ==================================================================================
    
    @pytest.mark.asyncio
    async def test_analyze_workday_patterns(self, mcp_integration):
        """Test cross-service workday pattern analysis"""
        
        mock_gmail_service = Mock()
        mock_calendar_service = Mock()
        
        with patch.object(mcp_integration, 'authenticate_google_service') as mock_auth:
            mock_auth.side_effect = [mock_gmail_service, mock_calendar_service]
            
            patterns = await mcp_integration.analyze_workday_patterns(
                user_google_email="test@example.com",
                analysis_days=14
            )
            
            assert isinstance(patterns, dict)
            assert "peak_email_hours" in patterns
            assert "meeting_density" in patterns
            assert "focus_time_availability" in patterns
            assert "recommendations" in patterns
            
            # Verify structure
            assert isinstance(patterns["peak_email_hours"], list)
            assert isinstance(patterns["meeting_density"], dict)
            assert len(patterns["recommendations"]) > 0
        
        logger.info("✅ Workday pattern analysis working correctly")
        logger.info(f"   📊 Peak email hours: {patterns['peak_email_hours']}")
        logger.info(f"   📅 Busiest day: {max(patterns['meeting_density'], key=patterns['meeting_density'].get)}")
    
    # ==================================================================================
    # ERROR HANDLING TESTS
    # ==================================================================================
    
    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, mcp_integration):
        """Test authentication error handling"""
        
        from app.services.google_workspace_mcp_v23 import AuthenticationError
        
        with patch.object(mcp_integration, 'authenticate_google_service') as mock_auth:
            mock_auth.side_effect = Exception("Authentication failed")
            
            with pytest.raises(AuthenticationError):
                await mcp_integration.search_emails_enhanced(
                    user_google_email="invalid@example.com",
                    query="test",
                    max_results=5
                )
        
        logger.info("✅ Authentication error handling working correctly")
    
    @pytest.mark.asyncio
    async def test_service_configuration_validation(self, mcp_integration):
        """Test service configuration validation"""
        
        from app.services.google_workspace_mcp_v23 import require_google_service
        
        # Test invalid service type
        with pytest.raises(ValueError, match="Unknown service type"):
            @require_google_service("invalid_service", "gmail_read")
            async def invalid_function(service, user_email: str):
                pass
        
        logger.info("✅ Service configuration validation working correctly")
    
    # ==================================================================================
    # UTILITY AND STATUS TESTS
    # ==================================================================================
    
    def test_service_status(self, mcp_integration):
        """Test service status reporting"""
        
        status = mcp_integration.get_service_status()
        
        assert isinstance(status, dict)
        assert status["version"] == "2.3"
        assert "config" in status
        assert "cache_statistics" in status
        assert "supported_services" in status
        assert "available_scopes" in status
        
        # Verify configuration
        config = status["config"]
        assert isinstance(config["cache_enabled"], bool)
        assert isinstance(config["cache_ttl_minutes"], int)
        
        # Verify supported services
        assert "gmail" in status["supported_services"]
        assert "calendar" in status["supported_services"]
        
        logger.info("✅ Service status reporting working correctly")
        logger.info(f"   📊 Version: {status['version']}")
        logger.info(f"   🔧 Services: {len(status['supported_services'])}")
        logger.info(f"   🔑 Scopes: {len(status['available_scopes'])}")
    
    def test_result_formatting(self, mcp_integration, sample_emails, sample_calendars):
        """Test result formatting for MCP responses"""
        
        # Test email formatting
        email_result = mcp_integration._format_email_results(sample_emails, "test query")
        assert isinstance(email_result, str)
        assert "Found 3 emails" in email_result
        assert "Urgent: Project Deadline" in email_result
        
        # Test calendar formatting
        calendar_result = mcp_integration._format_calendar_results(sample_calendars)
        assert isinstance(calendar_result, str)
        assert "Found 2 calendars" in calendar_result
        assert "Primary Calendar" in calendar_result
        
        logger.info("✅ Result formatting working correctly")
    
    # ==================================================================================
    # INTEGRATION TEST
    # ==================================================================================
    
    @pytest.mark.asyncio
    async def test_full_integration_workflow(self, mcp_integration):
        """Test complete integration workflow"""
        
        logger.info("🚀 Starting full integration workflow test")
        
        user_email = "integration.test@example.com"
        
        # Mock all services
        mock_service = Mock()
        
        with patch.object(mcp_integration, 'authenticate_google_service', return_value=mock_service):
            
            # 1. Test service status
            status = mcp_integration.get_service_status()
            assert status["version"] == "2.3"
            logger.info("   ✅ Service status check passed")
            
            # 2. Test cache operations
            clear_service_cache()
            stats = get_cache_stats()
            assert stats["total_entries"] == 0
            logger.info("   ✅ Cache operations passed")
            
            # 3. Test productivity analysis
            insights = await mcp_integration.analyze_productivity_trends(
                user_google_email=user_email,
                days_back=7
            )
            assert isinstance(insights, ProductivityInsights)
            logger.info("   ✅ Productivity analysis passed")
            
            # 4. Test AI suggestions
            suggestions = await mcp_integration.suggest_meeting_times_ai(
                user_google_email=user_email,
                attendees=["colleague@test.com"],
                duration_minutes=30
            )
            assert len(suggestions) > 0
            logger.info("   ✅ AI suggestions passed")
        
        logger.info("🎉 Full integration workflow completed successfully!")

# ==================================================================================
# PERFORMANCE BENCHMARKS
# ==================================================================================

class TestPerformanceBenchmarks:
    """Performance benchmark tests for v2.3 features"""
    
    @pytest.mark.asyncio
    async def test_service_caching_performance(self):
        """Benchmark service caching performance"""
        
        import time
        from app.services.google_workspace_mcp_v23 import (
            _cache_service, _get_cached_service, _get_cache_key
        )
        
        # Clear cache
        clear_service_cache()
        
        # Benchmark cache operations
        mock_service = Mock()
        user_email = "benchmark@test.com"
        
        # Cache write performance
        start_time = time.time()
        for i in range(100):
            cache_key = _get_cache_key(f"{user_email}_{i}", "gmail", "v1", ["scope1"])
            _cache_service(cache_key, mock_service, f"{user_email}_{i}")
        cache_write_time = time.time() - start_time
        
        # Cache read performance
        start_time = time.time()
        for i in range(100):
            cache_key = _get_cache_key(f"{user_email}_{i}", "gmail", "v1", ["scope1"])
            result = _get_cached_service(cache_key)
            assert result is not None
        cache_read_time = time.time() - start_time
        
        logger.info(f"⚡ Cache Performance Benchmark:")
        logger.info(f"   Write: {cache_write_time:.4f}s for 100 operations ({cache_write_time/100*1000:.2f}ms/op)")
        logger.info(f"   Read: {cache_read_time:.4f}s for 100 operations ({cache_read_time/100*1000:.2f}ms/op)")
        
        # Verify performance thresholds
        assert cache_write_time < 0.1  # Should be under 100ms for 100 operations
        assert cache_read_time < 0.05  # Should be under 50ms for 100 operations
    
    @pytest.mark.asyncio
    async def test_email_analysis_performance(self):
        """Benchmark email analysis performance"""
        
        from app.services.google_workspace_mcp_v23 import EnhancedGoogleWorkspaceMCP
        
        mcp = EnhancedGoogleWorkspaceMCP()
        
        # Create test emails
        test_emails = []
        for i in range(50):
            email = EnhancedEmailMessage(
                id=f"msg_{i:03d}",
                thread_id=f"thread_{i:03d}",
                subject=f"Test Email {i} - Urgent deadline tomorrow",
                sender=f"sender{i}@test.com",
                recipients=["recipient@test.com"],
                snippet=f"This is test email {i} with some urgent content that requires action"
            )
            test_emails.append(email)
        
        # Benchmark analysis
        import time
        start_time = time.time()
        
        analyzed_emails = []
        for email in test_emails:
            analyzed_email = await mcp._analyze_email_productivity(email)
            analyzed_emails.append(analyzed_email)
        
        analysis_time = time.time() - start_time
        
        logger.info(f"⚡ Email Analysis Performance Benchmark:")
        logger.info(f"   Analyzed {len(test_emails)} emails in {analysis_time:.4f}s")
        logger.info(f"   Average: {analysis_time/len(test_emails)*1000:.2f}ms per email")
        
        # Verify all emails were analyzed
        assert len(analyzed_emails) == len(test_emails)
        for email in analyzed_emails:
            assert email.word_count > 0
            assert email.priority_score >= 0
        
        # Performance threshold: should process 50 emails in under 1 second
        assert analysis_time < 1.0

# ==================================================================================
# MAIN TEST RUNNER
# ==================================================================================

async def run_all_tests():
    """Run all tests manually (for non-pytest environments)"""
    
    print("🚀 Enhanced Google Workspace MCP v2.3 - Comprehensive Test Suite")
    print("=" * 80)
    
    # Initialize test instances
    config = GoogleWorkspaceConfig(
        client_id="test_client_id",
        client_secret="test_client_secret",
        default_user_email="test@example.com"
    )
    mcp = EnhancedGoogleWorkspaceMCP(config)
    
    test_results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    tests = [
        ("Configuration Initialization", lambda: config.client_id == "test_client_id"),
        ("MCP Integration Initialization", lambda: mcp.config is not None),
        ("Scope Groups Configuration", lambda: "gmail_read" in SCOPE_GROUPS),
        ("Service Configurations", lambda: "gmail" in SERVICE_CONFIGS),
        ("Service Cache Operations", lambda: get_cache_stats()["cache_ttl_minutes"] == 30),
    ]
    
    for test_name, test_func in tests:
        test_results["total"] += 1
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}")
                test_results["passed"] += 1
            else:
                print(f"❌ {test_name}")
                test_results["failed"] += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            test_results["failed"] += 1
    
    # Async tests
    async_tests = [
        ("Productivity Analysis", mcp.analyze_productivity_trends("test@example.com", 7)),
        ("AI Meeting Suggestions", mcp.suggest_meeting_times_ai("test@example.com", ["colleague@test.com"], 30)),
    ]
    
    for test_name, test_coro in async_tests:
        test_results["total"] += 1
        try:
            result = await test_coro
            if result:
                print(f"✅ {test_name}")
                test_results["passed"] += 1
            else:
                print(f"❌ {test_name}")
                test_results["failed"] += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            test_results["failed"] += 1
    
    print("\n" + "=" * 80)
    print(f"📊 Test Results: {test_results['passed']}/{test_results['total']} passed")
    print(f"✅ Success Rate: {test_results['passed']/test_results['total']*100:.1f}%")
    
    if test_results["failed"] == 0:
        print("🎉 All tests passed! Enhanced Google Workspace MCP v2.3 is ready for production!")
    else:
        print(f"⚠️ {test_results['failed']} tests failed. Please review and fix issues.")
    
    return test_results

if __name__ == "__main__":
    # Run tests directly
    asyncio.run(run_all_tests())
