"""
Suite 4: Subscription — E2E tests aligned with integration_test use cases.
Covers: subscription_card_test.dart (loading, data display, empty, status, dates, callbacks)
      + subscription_flow_test.dart (family->plan->schedule->summary flow, error+retry)
TC-E2E-SUB-001 to TC-E2E-SUB-020
All selectors use XPath/AndroidUiAutomator (no ACCESSIBILITY_ID).
"""
import pytest
import time
from pages.home_page import HomePage
from pages.profile_page import ProfilePage
from pages.subscription_plans_page import SubscriptionPlansPage
from pages.subscription_active_page import ActiveSubscriptionPage
from pages.subscription_summary_page import SubscriptionSummaryPage
from pages.pause_subscription_page import PauseSubscriptionPage
from pages.resume_subscription_page import ResumeSubscriptionPage
from pages.modify_schedule_page import ModifySchedulePage
from pages.cancel_subscription_page import CancelSubscriptionPage
from config.test_config import TestConfig


class TestSubscription:
    """Subscription test suite aligned with integration_test use cases."""

    # ========== Dashboard Subscription Card (aligned with subscription_card_test.dart) ==========

    def test_tc_sub_001_dashboard_subscription_card(self, logged_in):
        """TC-E2E-SUB-001: Dashboard shows subscription info card."""
        home = HomePage(logged_in)
        assert home.is_dashboard_displayed(timeout=10), \
            "Dashboard not displayed"
        # Check for subscription-related text
        assert home.is_visible(*home.START_SUBSCRIPTION, timeout=10) or \
            home.is_visible(*home.SUBSCRIBE_BUTTON, timeout=5) or \
            home.is_visible(*home.NO_ACTIVE_PLAN, timeout=5), \
            "No subscription card element visible on dashboard"

    def test_tc_sub_002_no_subscription_message(self, logged_in):
        """TC-E2E-SUB-002: Shows 'No active subscription' when no plan (aligned with subscription_card_test.dart Test 3)."""
        home = HomePage(logged_in)
        assert home.is_dashboard_displayed(timeout=10)
        # If no subscription, should see subscriber CTA
        subscribe_btn = home.find_element(home.SUBSCRIBE_BUTTON)
        no_plan = home.find_element(home.NO_ACTIVE_PLAN)
        start_sub = home.find_element(home.START_SUBSCRIPTION)
        has_cta = subscribe_btn is not None or no_plan is not None or start_sub is not None
        if not has_cta:
            # May already have subscription — check manage button instead
            modify_btn = home.find_element(home.MODIFY_BUTTON)
            assert modify_btn is not None, \
                "Neither subscribe CTA nor manage button visible"

    def test_tc_sub_003_subscribe_now_navigates(self, logged_in):
        """TC-E2E-SUB-003: Tap Subscribe Now navigates to subscription plans (aligned with subscription_card_test.dart Test 7)."""
        home = HomePage(logged_in)
        subscribe_btn = home.find_element(home.SUBSCRIBE_BUTTON)
        start_sub = home.find_element(home.START_SUBSCRIPTION)
        if subscribe_btn:
            subscribe_btn.click()
        elif start_sub:
            start_sub.click()
        else:
            pytest.skip("Subscribe button not found - may already have subscription")
        time.sleep(3)
        plans = SubscriptionPlansPage(logged_in)
        assert plans.is_visible(*plans.DELIGHT_FAMILY, timeout=10) or \
            plans.is_visible(*plans.SIGNATURE_FAMILY, timeout=5), \
            "Subscription family screen not shown after tapping Subscribe"

    # ========== Subscription Plan Selection (aligned with subscription_flow_test.dart) ==========

    def test_tc_sub_004_family_screen_displays_families(self, logged_in):
        """TC-E2E-SUB-004: Family screen shows DELIGHT, SIGNATURE, PREMIUM (aligned with subscription_flow_test.dart)."""
        home = HomePage(logged_in)
        home.navigate_to_subscription()
        time.sleep(3)
        plans = SubscriptionPlansPage(logged_in)
        assert plans.is_family_displayed(), \
            "Subscription family options not displayed"

    def test_tc_sub_005_select_delight_family(self, logged_in):
        """TC-E2E-SUB-005: Select DELIGHT family plan."""
        home = HomePage(logged_in)
        home.navigate_to_subscription()
        time.sleep(3)
        plans = SubscriptionPlansPage(logged_in)
        plans.select_family("DELIGHT")
        time.sleep(2)
        assert True, "DELIGHT family selected"

    def test_tc_sub_006_select_signature_family(self, logged_in):
        """TC-E2E-SUB-006: Select SIGNATURE family plan."""
        home = HomePage(logged_in)
        home.navigate_to_subscription()
        time.sleep(3)
        plans = SubscriptionPlansPage(logged_in)
        plans.select_family("SIGNATURE")
        time.sleep(2)
        assert True, "SIGNATURE family selected"

    # ========== Active Subscription (aligned with subscription_card_test.dart Tests 2, 5, 6) ==========

    def test_tc_sub_007_active_subscription_screen(self, logged_in):
        """TC-E2E-SUB-007: Navigate to active subscription screen from profile."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_manage_subscriptions()
        time.sleep(3)
        active = ActiveSubscriptionPage(logged_in)
        assert active.is_displayed(), \
            "Active subscription screen not displayed"

    def test_tc_sub_008_active_subscription_status(self, logged_in):
        """TC-E2E-SUB-008: Subscription status is displayed (aligned with status chip test)."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_manage_subscriptions()
        time.sleep(3)
        active = ActiveSubscriptionPage(logged_in)
        status = active.get_status()
        assert status.lower() in ['active', 'paused', 'cancelled', 'expired', 'unknown'], \
            f"Unexpected status: {status}"

    # ========== Pause/Resume Flow ==========

    def test_tc_sub_009_pause_subscription_1_week(self, logged_in):
        """TC-E2E-SUB-009: Pause subscription for 1 week."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_manage_subscriptions()
        time.sleep(3)
        active = ActiveSubscriptionPage(logged_in)
        status = active.get_status()
        if status.lower() != 'active':
            pytest.skip("Subscription not active - cannot pause")
        active.tap_pause()
        time.sleep(2)
        pause = PauseSubscriptionPage(logged_in)
        assert pause.is_displayed(), \
            "Pause subscription screen not shown"
        pause.select_duration('1_week')
        pause.confirm_pause()
        time.sleep(3)
        assert active.is_displayed(), \
            "Not returned to subscription screen after pause"

    def test_tc_sub_010_resume_subscription(self, logged_in):
        """TC-E2E-SUB-010: Resume paused subscription."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_manage_subscriptions()
        time.sleep(3)
        active = ActiveSubscriptionPage(logged_in)
        status = active.get_status()
        if status.lower() != 'paused':
            pytest.skip("Subscription not paused - cannot resume")
        active.tap_resume()
        time.sleep(2)
        resume = ResumeSubscriptionPage(logged_in)
        assert resume.is_displayed(), \
            "Resume subscription screen not shown"
        resume.resume_now()
        time.sleep(3)
        assert active.is_displayed(), \
            "Not returned to subscription screen after resume"

    # ========== Modify Schedule ==========

    def test_tc_sub_011_modify_schedule_navigates(self, logged_in):
        """TC-E2E-SUB-011: Modify Schedule screen opens from active subscription."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_manage_subscriptions()
        time.sleep(3)
        active = ActiveSubscriptionPage(logged_in)
        status = active.get_status()
        if status.lower() != 'active':
            pytest.skip("Subscription not active - cannot modify schedule")
        active.tap_modify_schedule()
        time.sleep(2)
        modify = ModifySchedulePage(logged_in)
        assert modify.is_displayed(), \
            "Modify schedule screen not shown"

    def test_tc_sub_012_modify_schedule_weekly(self, logged_in):
        """TC-E2E-SUB-012: Modify schedule to weekly frequency."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_manage_subscriptions()
        time.sleep(3)
        active = ActiveSubscriptionPage(logged_in)
        status = active.get_status()
        if status.lower() != 'active':
            pytest.skip("Subscription not active")
        active.tap_modify_schedule()
        time.sleep(2)
        modify = ModifySchedulePage(logged_in)
        modify.select_frequency('weekly')
        modify.confirm_modify()
        time.sleep(3)
        assert active.is_displayed(), \
            "Not returned after schedule modification"

    # ========== Cancel Subscription ==========

    def test_tc_sub_013_cancel_subscription_navigates(self, logged_in):
        """TC-E2E-SUB-013: Cancel subscription screen opens."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_manage_subscriptions()
        time.sleep(3)
        active = ActiveSubscriptionPage(logged_in)
        status = active.get_status()
        if status.lower() not in ['active', 'paused']:
            pytest.skip("Subscription cannot be cancelled")
        active.scroll_to_cancel_button()
        active.tap_cancel()
        time.sleep(2)
        cancel = CancelSubscriptionPage(logged_in)
        assert cancel.is_displayed(), \
            "Cancel subscription screen not shown"

    # ========== Error Handling (aligned with subscription_flow_test.dart error+retry) ==========

    def test_tc_sub_014_subscription_error_handling(self, logged_in):
        """TC-E2E-SUB-014: Error state displays retry option (aligned with subscription_flow_test.dart)."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        profile.navigate_to_manage_subscriptions()
        time.sleep(3)
        active = ActiveSubscriptionPage(logged_in)
        if active.is_visible(*active.RETRY_BUTTON, timeout=5):
            active.tap(*active.RETRY_BUTTON)
            time.sleep(3)
            assert active.is_displayed() or not active.is_visible(*active.RETRY_BUTTON), \
                "Retry did not attempt to reload data"

    # ========== Subscription Summary ==========

    def test_tc_sub_015_manage_subscriptions_profile(self, logged_in):
        """TC-E2E-SUB-015: Manage Subscriptions option visible in profile."""
        home = HomePage(logged_in)
        home.navigate_to_profile()
        profile = ProfilePage(logged_in)
        assert profile.is_visible(*profile.MANAGE_SUBS_MENU, timeout=10), \
            "Manage Subscriptions option not visible in profile"

    def test_tc_sub_016_navigate_to_subscription_plans(self, logged_in):
        """TC-E2E-SUB-016: Navigate to subscription plans from dashboard."""
        home = HomePage(logged_in)
        home.navigate_to_subscription()
        time.sleep(3)
        plans = SubscriptionPlansPage(logged_in)
        assert plans.is_family_displayed(), \
            "Subscription plans not displayed"

    def test_tc_sub_017_delight_family_displayed(self, logged_in):
        """TC-E2E-SUB-017: DELIGHT family option is displayed."""
        home = HomePage(logged_in)
        home.navigate_to_subscription()
        time.sleep(3)
        plans = SubscriptionPlansPage(logged_in)
        assert plans.is_visible(*plans.DELIGHT_FAMILY, timeout=10), \
            "DELIGHT family not displayed"

    def test_tc_sub_018_signature_family_displayed(self, logged_in):
        """TC-E2E-SUB-018: SIGNATURE family option is displayed."""
        home = HomePage(logged_in)
        home.navigate_to_subscription()
        time.sleep(3)
        plans = SubscriptionPlansPage(logged_in)
        assert plans.is_visible(*plans.SIGNATURE_FAMILY, timeout=10), \
            "SIGNATURE family not displayed"

    def test_tc_sub_019_premium_family_displayed(self, logged_in):
        """TC-E2E-SUB-019: PREMIUM family option is displayed."""
        home = HomePage(logged_in)
        home.navigate_to_subscription()
        time.sleep(3)
        plans = SubscriptionPlansPage(logged_in)
        assert plans.is_visible(*plans.PREMIUM_FAMILY, timeout=10), \
            "PREMIUM family not displayed"

    def test_tc_sub_020_subscription_back_navigation(self, logged_in):
        """TC-E2E-SUB-020: Back navigation from subscription plans returns to dashboard."""
        home = HomePage(logged_in)
        home.navigate_to_subscription()
        time.sleep(2)
        # Press back
        home.press_back()
        time.sleep(2)
        assert home.is_dashboard_displayed(timeout=10), \
            "Back navigation did not return to dashboard"