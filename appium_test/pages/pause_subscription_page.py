"""
Pause Subscription Page Object — maps to subscription/pause_subscription_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class PauseSubscriptionPage(BasePage):
    """Page object for pause subscription flow."""

    PAUSE_DURATION_DROPDOWN = (AppiumBy.ACCESSIBILITY_ID, 'pause_duration_dropdown')
    PAUSE_OPTION_1_WEEK = (AppiumBy.ACCESSIBILITY_ID, 'pause_option_1_week')
    PAUSE_OPTION_2_WEEKS = (AppiumBy.ACCESSIBILITY_ID, 'pause_option_2_weeks')
    PAUSE_OPTION_1_MONTH = (AppiumBy.ACCESSIBILITY_ID, 'pause_option_1_month')
    CONFIRM_PAUSE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'confirm_pause_button')
    CANCEL_PAUSE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'cancel_pause_button')

    def select_duration(self, duration: str):
        """Select pause duration."""
        self.tap(*self.PAUSE_DURATION_DROPDOWN)
        duration_map = {
            '1_week': self.PAUSE_OPTION_1_WEEK,
            '2_weeks': self.PAUSE_OPTION_2_WEEKS,
            '1_month': self.PAUSE_OPTION_1_MONTH,
        }
        locator = duration_map.get(duration)
        if locator:
            self.tap(*locator)
        return self

    def confirm_pause(self):
        self.tap(*self.CONFIRM_PAUSE_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def cancel_pause(self):
        self.tap(*self.CANCEL_PAUSE_BUTTON)
        return self