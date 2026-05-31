"""
Notification Centre Page Object — maps to notification_centre_screen.dart
Uses text-based selectors (no ACCESSIBILITY_ID).
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class NotificationCentrePage(BasePage):
    """Page object for notification centre."""

    # Screen title
    NOTIFICATION_TITLE = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("Notifications")')
    # Empty state
    EMPTY_NOTIFICATION = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("No notifications")')
    # Back button — XPath for ImageButton (arrow back)
    BACK_BUTTON = (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Navigate up" or @content-desc="Back"]')
    # Notification list container
    NOTIFICATION_LIST = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().className("android.widget.ListView")')
    # Mark all as read button
    MARK_ALL_READ = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Mark all read" or @content-desc="Mark All Read"]')
    # Notification bell in home
    NOTIFICATION_BELL = (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Notifications"] | //android.widget.ImageView[@content-desc="Notifications"]')

    def is_empty(self) -> bool:
        """Check if notification list is empty."""
        return self.is_visible(*self.EMPTY_NOTIFICATION)

    def go_back(self):
        """Navigate back from notifications."""
        self.tap(*self.BACK_BUTTON)
        return self

    def get_notification_count(self) -> int:
        """Count visible notification items."""
        els = self.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.view.View")'
        )
        return len(els)

    def tap_notification(self, index: int = 0):
        """Tap a notification by index."""
        els = self.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().className("android.view.View")'
        )
        if index < len(els):
            els[index].click()
        return self

    def mark_all_read(self):
        """Tap mark all as read."""
        if self.is_visible(*self.MARK_ALL_READ, timeout=3):
            self.tap(*self.MARK_ALL_READ)
        return self