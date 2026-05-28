"""
Notification Centre Page Object — maps to notification_centre_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class NotificationCentrePage(BasePage):
    """Page object for notification centre."""

    NOTIFICATION_LIST = (AppiumBy.ACCESSIBILITY_ID, 'notification_list')
    EMPTY_NOTIFICATION_TEXT = (AppiumBy.ACCESSIBILITY_ID, 'empty_notification_text')
    MARK_ALL_READ_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'mark_all_read_button')
    BACK_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'notification_back_button')

    def get_notification_count(self) -> int:
        """Get number of visible notifications."""
        els = self.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionContains("notification_item_")',
            timeout=5
        )
        return len(els)

    def tap_notification(self, index: int = 0):
        """Tap a notification by index."""
        els = self.find_elements(
            AppiumBy.ANDROID_UIAUTOMATOR,
            'new UiSelector().descriptionContains("notification_item_")',
            timeout=5
        )
        if els and len(els) > index:
            els[index].click()
        return self

    def mark_all_read(self):
        self.tap(*self.MARK_ALL_READ_BUTTON)
        self.wait_for_loading_gone()
        return self

    def is_empty(self) -> bool:
        return self.is_visible(*self.EMPTY_NOTIFICATION_TEXT, timeout=5)

    def go_back(self):
        self.tap(*self.BACK_BUTTON)
        return self