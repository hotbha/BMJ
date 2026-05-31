"""
Subscription Summary Page Object — maps to subscription/subscription_summary_screen.dart
Uses text-based XPath selectors since Flutter Key() widgets are NOT exposed as content-desc.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class SubscriptionSummaryPage(BasePage):
    """Page object for subscription review/summary."""

    # Page title — typically shows from the route
    PAGE_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Summary" or @content-desc="Review"]')

    # Plan name — shown in summary card
    PLAN_NAME = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "Plan")]')

    # Frequency text
    FREQUENCY = (AppiumBy.XPATH, '//android.widget.TextView[contains(@content-desc, "Weekly") or contains(@content-desc, "Biweekly") or contains(@content-desc, "Monthly") or contains(@content-desc, "week") or contains(@content-desc, "month")]')

    # Total amount — contains ₹ symbol
    TOTAL = (AppiumBy.XPATH, '//android.widget.TextView[starts-with(@content-desc, "₹") or starts-with(@content-desc, "Rs")]')

    # Confirm button
    CONFIRM_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Confirm" or @content-desc="Confirm Subscription"] | //android.widget.TextView[@content-desc="Confirm" or @content-desc="Confirm Subscription"]')

    # Edit button
    EDIT_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Edit" or @content-desc="Change"] | //android.widget.TextView[@content-desc="Edit" or @content-desc="Change"]')

    def confirm_subscription(self):
        """Confirm and create subscription."""
        self.tap(*self.CONFIRM_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def get_plan_name(self) -> str:
        """Get the plan name from summary."""
        return self.get_text(*self.PLAN_NAME)

    def get_total(self) -> str:
        """Get the total amount text."""
        return self.get_text(*self.TOTAL)

    def is_displayed(self) -> bool:
        """Check if summary screen is displayed."""
        return self.is_visible(self.CONFIRM_BUTTON)

    def tap_edit(self):
        """Tap edit/change button."""
        self.tap(*self.EDIT_BUTTON)
        return self