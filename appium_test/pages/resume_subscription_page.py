"""
Resume Subscription Page Object — maps to subscription/resume_subscription_screen.dart
Uses text-based XPath selectors since Flutter Key() widgets are NOT exposed as content-desc.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class ResumeSubscriptionPage(BasePage):
    """Page object for resume subscription flow."""

    # Page title
    PAGE_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Resume Subscription"]')

    # Resume now button
    RESUME_NOW_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Resume Now" or @content-desc="Resume"] | //android.widget.TextView[@content-desc="Resume Now" or @content-desc="Resume"]')

    # Resume on next cycle
    RESUME_NEXT_CYCLE_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Resume on Next Cycle" or @content-desc="Next Cycle"] | //android.widget.TextView[@content-desc="Resume on Next Cycle" or @content-desc="Next Cycle"]')

    # Confirm resume
    CONFIRM_RESUME_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Confirm" or @content-desc="Yes, Resume"] | //android.widget.TextView[@content-desc="Confirm" or @content-desc="Yes, Resume"]')

    # Cancel button
    CANCEL_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Cancel" or @content-desc="Go Back"] | //android.widget.TextView[@content-desc="Cancel" or @content-desc="Go Back"]')

    def resume_now(self):
        """Resume subscription immediately."""
        self.tap(*self.RESUME_NOW_BUTTON)
        # May show confirmation dialog
        if self.is_visible(self.CONFIRM_RESUME_BUTTON, timeout=3):
            self.tap(*self.CONFIRM_RESUME_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def resume_next_cycle(self):
        """Resume subscription on next billing cycle."""
        self.tap(*self.RESUME_NEXT_CYCLE_BUTTON)
        if self.is_visible(self.CONFIRM_RESUME_BUTTON, timeout=3):
            self.tap(*self.CONFIRM_RESUME_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def cancel_resume(self):
        """Cancel the resume operation."""
        self.tap(*self.CANCEL_BUTTON)
        return self

    def is_displayed(self) -> bool:
        """Check if resume screen is displayed."""
        return self.is_visible(self.PAGE_TITLE) or self.is_visible(self.RESUME_NOW_BUTTON)