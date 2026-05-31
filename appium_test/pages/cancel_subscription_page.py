"""
Cancel Subscription Page Object — maps to subscription/cancel_subscription_screen.dart
Uses text-based XPath selectors since Flutter Key() widgets are NOT exposed as content-desc.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class CancelSubscriptionPage(BasePage):
    """Page object for cancel subscription flow."""

    # Page title
    PAGE_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Cancel Subscription"]')

    # Reason options — text-based
    CANCEL_REASON_EXPENSIVE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Too expensive"] | //android.widget.RadioButton[@content-desc="Too expensive"]')
    CANCEL_REASON_NOT_NEEDED = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="No longer needed" or @content-desc="Not needed"] | //android.widget.RadioButton[@content-desc="No longer needed" or @content-desc="Not needed"]')
    CANCEL_REASON_OTHER = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Other reason" or @content-desc="Other"] | //android.widget.RadioButton[@content-desc="Other reason" or @content-desc="Other"]')

    # Feedback text field
    FEEDBACK_FIELD = (AppiumBy.XPATH, '//android.widget.EditText[contains(@content-desc, "feedback") or contains(@content-desc, "Feedback") or contains(@hint, "feedback") or contains(@hint, "Feedback") or contains(@hint, "reason")]')

    # Confirm cancel button
    CONFIRM_CANCEL_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Confirm" or @content-desc="Cancel Subscription" or @content-desc="Yes, Cancel"] | //android.widget.TextView[@content-desc="Confirm" or @content-desc="Cancel Subscription" or @content-desc="Yes, Cancel"]')

    # Go back button
    CANCEL_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Go Back" or @content-desc="Keep Subscription" or @content-desc="No"] | //android.widget.TextView[@content-desc="Go Back" or @content-desc="Keep Subscription" or @content-desc="No"]')

    def select_reason(self, reason: str):
        """Select cancellation reason.

        Args:
            reason: 'expensive', 'not_needed', or 'other'
        """
        reason_map = {
            'expensive': self.CANCEL_REASON_EXPENSIVE,
            'too_expensive': self.CANCEL_REASON_EXPENSIVE,
            'not_needed': self.CANCEL_REASON_NOT_NEEDED,
            'no_longer_needed': self.CANCEL_REASON_NOT_NEEDED,
            'other': self.CANCEL_REASON_OTHER,
        }
        locator = reason_map.get(reason.lower())
        if locator:
            self.tap(*locator)
        return self

    def enter_feedback(self, text: str):
        """Enter cancellation feedback text."""
        try:
            el = self.find_element(self.FEEDBACK_FIELD)
            if el:
                el.clear()
                el.send_keys(text)
        except Exception:
            pass  # Feedback field may not exist
        return self

    def confirm_cancel(self):
        """Confirm and execute cancellation."""
        self.tap(*self.CONFIRM_CANCEL_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def go_back(self):
        """Go back without cancelling."""
        self.tap(*self.CANCEL_BUTTON)
        return self

    def is_displayed(self) -> bool:
        """Check if cancel screen is displayed."""
        return self.is_visible(self.PAGE_TITLE) or self.is_visible(self.CONFIRM_CANCEL_BUTTON)