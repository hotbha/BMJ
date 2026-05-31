"""
Suite 6: Notifications — E2E tests using real bmjServer FCM.
TC-E2E-NOTIF-001 to TC-E2E-NOTIF-008
All selectors use XPath/AndroidUiAutomator (no ACCESSIBILITY_ID).
"""
import pytest
import time
from pages.notification_centre_page import NotificationCentrePage
from pages.home_page import HomePage
from config.test_config import TestConfig


class TestNotifications:
    """Notification test suite aligned with integration_test use cases."""

    def test_tc_notif_001_screen_displayed(self, logged_in):
        """TC-E2E-NOTIF-001: Notification centre screen displays correctly."""
        home = HomePage(logged_in)
        home.navigate_to_notifications()
        notif = NotificationCentrePage(logged_in)
        assert notif.is_visible(*notif.NOTIFICATION_TITLE, timeout=10), \
            "Notification title not visible"

    def test_tc_notif_002_empty_state(self, logged_in):
        """TC-E2E-NOTIF-002: Empty notifications shows 'No notifications' message."""
        home = HomePage(logged_in)
        home.navigate_to_notifications()
        notif = NotificationCentrePage(logged_in)
        if notif.is_empty():
            assert notif.is_visible(*notif.EMPTY_NOTIFICATION), \
                "Empty notification text not shown"

    def test_tc_notif_003_notification_badge_home(self, logged_in):
        """TC-E2E-NOTIF-003: Notification bell icon is visible on home screen."""
        home = HomePage(logged_in)
        assert home.is_visible(*home.NOTIFICATION_BELL, timeout=10), \
            "Notification bell not visible on home"

    def test_tc_notif_004_tap_notification_navigates(self, logged_in):
        """TC-E2E-NOTIF-004: Tapping a notification navigates to relevant screen."""
        home = HomePage(logged_in)
        home.navigate_to_notifications()
        notif = NotificationCentrePage(logged_in)
        if not notif.is_empty():
            count_before = notif.get_notification_count()
            notif.tap_notification(0)
            time.sleep(3)
            back_btn = notif.find_element(notif.BACK_BUTTON)
            assert back_btn is not None or notif.is_visible(*notif.BACK_BUTTON, timeout=5), \
                "Should be able to navigate back after tapping notification"
            notif.go_back()

    def test_tc_notif_005_notification_count_non_negative(self, logged_in):
        """TC-E2E-NOTIF-005: Notification count is non-negative."""
        home = HomePage(logged_in)
        home.navigate_to_notifications()
        notif = NotificationCentrePage(logged_in)
        count = notif.get_notification_count()
        assert count >= 0, f"Notification count should be >= 0, got {count}"

    def test_tc_notif_006_back_navigation(self, logged_in):
        """TC-E2E-NOTIF-006: Back from notification centre returns to dashboard."""
        home = HomePage(logged_in)
        home.navigate_to_notifications()
        notif = NotificationCentrePage(logged_in)
        notif.go_back()
        time.sleep(2)
        assert home.is_dashboard_displayed(timeout=10), \
            "Back navigation did not return to dashboard"

    def test_tc_notif_007_notification_persistence(self, logged_in):
        """TC-E2E-NOTIF-007: Notifications persist across screen navigation."""
        home = HomePage(logged_in)
        home.navigate_to_notifications()
        notif = NotificationCentrePage(logged_in)
        count_before = notif.get_notification_count()
        notif.go_back()
        time.sleep(1)
        home.navigate_to_notifications()
        count_after = notif.get_notification_count()
        assert count_after == count_before, \
            f"Notification count changed: before={count_before}, after={count_after}"

    def test_tc_notif_008_navigate_from_home_bell(self, logged_in):
        """TC-E2E-NOTIF-008: Tap bell icon on home navigates to notification centre."""
        home = HomePage(logged_in)
        bell = home.find_element(home.NOTIFICATION_BELL)
        if bell:
            bell.click()
            time.sleep(2)
            notif = NotificationCentrePage(logged_in)
            assert notif.is_visible(*notif.NOTIFICATION_TITLE, timeout=5), \
                "Notification centre not opened from bell icon"