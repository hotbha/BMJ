"""
Resume Subscription Page Object — maps to subscription/resume_subscription_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class ResumeSubscriptionPage(BasePage):
    """Page object for resume subscription flow."""

    RESUME_NOW_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'resume_now_button')
    RESUME_ON_NEXT_CYCLE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'resume_on_next_cycle_button')
    CONFIRM_RESUME_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'confirm_resume_button')
    CANCEL_RESUME_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'cancel_resume_button')

    def resume_now(self):
        """Resume subscription immediately."""
        self.tap(*self.RESUME_NOW_BUTTON)
        self.tap(*self.CONFIRM_RESUME_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self