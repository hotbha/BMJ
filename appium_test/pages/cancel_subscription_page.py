"""
Cancel Subscription Page Object — maps to subscription/cancel_subscription_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class CancelSubscriptionPage(BasePage):
    """Page object for cancel subscription flow."""

    CANCEL_REASON_DROPDOWN = (AppiumBy.ACCESSIBILITY_ID, 'cancel_reason_dropdown')
    CANCEL_REASON_EXPENSIVE = (AppiumBy.ACCESSIBILITY_ID, 'cancel_reason_expensive')
    CANCEL_REASON_NOT_NEEDED = (AppiumBy.ACCESSIBILITY_ID, 'cancel_reason_not_needed')
    CANCEL_REASON_OTHER = (AppiumBy.ACCESSIBILITY_ID, 'cancel_reason_other')
    FEEDBACK_FIELD = (AppiumBy.ACCESSIBILITY_ID, 'cancel_feedback_field')
    CONFIRM_CANCEL_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'confirm_cancel_button')
    CANCEL_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'cancel_cancel_button')

    def select_reason(self, reason: str):
        """Select cancellation reason."""
        self.tap(*self.CANCEL_REASON_DROPDOWN)
        reason_map = {
            'expensive': self.CANCEL_REASON_EXPENSIVE,
            'not_needed': self.CANCEL_REASON_NOT_NEEDED,
            'other': self.CANCEL_REASON_OTHER,
        }
        locator = reason_map.get(reason.lower())
        if locator:
            self.tap(*locator)
        return self

    def confirm_cancel(self):
        self.tap(*self.CONFIRM_CANCEL_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self