"""
Pause Subscription Page Object — maps to subscription/pause_subscription_screen.dart
Uses text-based XPath selectors since Flutter Key() widgets are NOT exposed as content-desc.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class PauseSubscriptionPage(BasePage):
    """Page object for pause subscription flow."""

    # Page title
    PAGE_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Pause Subscription"]')

    # Duration options — text-based selectors
    PAUSE_DURATION_1_WEEK = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="1 Week" or @content-desc="1 week"] | //android.widget.RadioButton[@content-desc="1 Week" or @content-desc="1 week"]')
    PAUSE_DURATION_2_WEEKS = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="2 Weeks" or @content-desc="2 weeks"] | //android.widget.RadioButton[@content-desc="2 Weeks" or @content-desc="2 weeks"]')
    PAUSE_DURATION_1_MONTH = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="1 Month" or @content-desc="1 month"] | //android.widget.RadioButton[@content-desc="1 Month" or @content-desc="1 month"]')

    # Confirm pause button
    CONFIRM_PAUSE_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Pause" or @content-desc="Confirm Pause" or @content-desc="Confirm"] | //android.widget.TextView[@content-desc="Pause" or @content-desc="Confirm Pause" or @content-desc="Confirm"]')

    # Cancel button
    CANCEL_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Cancel" or @content-desc="Go Back"] | //android.widget.TextView[@content-desc="Cancel" or @content-desc="Go Back"]')

    def select_duration(self, duration: str):
        """Select pause duration by text match.

        Args:
            duration: One of '1_week', '2_weeks', '1_month'
        """
        duration_map = {
            '1_week': self.PAUSE_DURATION_1_WEEK,
            '2_weeks': self.PAUSE_DURATION_2_WEEKS,
            '1_month': self.PAUSE_DURATION_1_MONTH,
        }
        locator = duration_map.get(duration)
        if locator:
            self.tap(*locator)
        return self

    def confirm_pause(self):
        """Confirm and execute pause."""
        self.tap(*self.CONFIRM_PAUSE_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def cancel_pause(self):
        """Cancel the pause operation."""
        self.tap(*self.CANCEL_BUTTON)
        return self

    def is_displayed(self) -> bool:
        """Check if pause screen is displayed."""
        return self.is_visible(self.PAGE_TITLE) or self.is_visible(self.CONFIRM_PAUSE_BUTTON)