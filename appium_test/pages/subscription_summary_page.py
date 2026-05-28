"""
Subscription Summary Page Object — maps to subscription/subscription_summary_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class SubscriptionSummaryPage(BasePage):
    """Page object for subscription review/summary."""

    SUMMARY_TITLE = (AppiumBy.ACCESSIBILITY_ID, 'subscription_summary_title')
    SUMMARY_PLAN_NAME = (AppiumBy.ACCESSIBILITY_ID, 'summary_plan_name')
    SUMMARY_FREQUENCY = (AppiumBy.ACCESSIBILITY_ID, 'summary_frequency')
    SUMMARY_TOTAL = (AppiumBy.ACCESSIBILITY_ID, 'summary_total')
    CONFIRM_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'summary_confirm_button')
    EDIT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'summary_edit_button')

    def confirm_subscription(self):
        """Confirm and create subscription."""
        self.tap(*self.CONFIRM_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def get_plan_name(self) -> str:
        return self.get_text(*self.SUMMARY_PLAN_NAME)

    def get_total(self) -> str:
        return self.get_text(*self.SUMMARY_TOTAL)