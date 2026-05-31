"""
Active Subscription Page Object — maps to subscription/active_subscription_screen.dart
Uses text-based XPath selectors since Flutter Key() widgets are NOT exposed as content-desc.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class ActiveSubscriptionPage(BasePage):
    """Page object for active subscription details."""

    # AppBar title
    MY_SUBSCRIPTION_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="My Subscription"]')
    # Back button — arrow icon in AppBar
    BACK_BUTTON = (AppiumBy.XPATH, '//android.widget.ImageButton[@content-desc="Navigate up" or @content-desc="Back"]')
    # Loading indicator
    LOADING_INDICATOR = (AppiumBy.XPATH, '//android.widget.ProgressIndicator | //android.widget.ProgressBar')

    # Plan name — displayed in plan summary card (large bold text)
    # The plan name is the first bold text in the content area
    PLAN_NAME = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.view.View").instance(1)')

    # Status chip — colored container with status text like "ACTIVE", "PAUSED"
    STATUS_CHIP = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="ACTIVE" or @content-desc="PAUSED" or @content-desc="CANCELLED" or @content-desc="EXPIRED" or @content-desc="active" or @content-desc="paused" or @content-desc="cancelled" or @content-desc="expired" or @content-desc="Active" or @content-desc="Paused" or @content-desc="Cancelled"][last()]')

    # Info row labels
    STARTED_LABEL = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Started"]')
    NEXT_RENEWAL_LABEL = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Next Renewal"]')
    AMOUNT_LABEL = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Amount"]')

    # Schedule card
    SCHEDULE_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Schedule"]')

    # Action buttons — status-dependent
    MODIFY_SCHEDULE_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Modify Schedule"] | //android.widget.TextView[@content-desc="Modify Schedule"]')
    PAUSE_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Pause"] | //android.widget.TextView[@content-desc="Pause"]')
    RESUME_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Resume"] | //android.widget.TextView[@content-desc="Resume"]')
    CANCEL_SUBSCRIPTION_BUTTON = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Cancel Subscription"] | //android.widget.Button[@content-desc="Cancel Subscription"]')
    RESUBSCRIBE_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Resubscribe"] | //android.widget.TextView[@content-desc="Resubscribe"]')

    # Retry button on error
    RETRY_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Retry"] | //android.widget.TextView[@content-desc="Retry"]')

    def get_status(self) -> str:
        """Get current subscription status text."""
        try:
            el = self.wait_for_element(self.STATUS_CHIP, timeout=5)
            return el.text
        except Exception:
            return 'unknown'

    def is_displayed(self) -> bool:
        """Check if active subscription screen is displayed."""
        return self.is_visible(self.MY_SUBSCRIPTION_TITLE)

    def is_loading(self) -> bool:
        """Check if loading indicator is shown."""
        return self.is_visible(self.LOADING_INDICATOR)

    def tap_pause(self):
        """Tap Pause button (available when status is 'active')."""
        self.tap(*self.PAUSE_BUTTON)
        return self

    def tap_resume(self):
        """Tap Resume button (available when status is 'paused')."""
        self.tap(*self.RESUME_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def tap_cancel(self):
        """Tap Cancel Subscription button."""
        el = self.find_element(self.CANCEL_SUBSCRIPTION_BUTTON)
        self.scroll_to_element(el)
        self.tap(*self.CANCEL_SUBSCRIPTION_BUTTON)
        return self

    def tap_modify_schedule(self):
        """Tap Modify Schedule button (available when status is 'active')."""
        el = self.find_element(self.MODIFY_SCHEDULE_BUTTON)
        self.scroll_to_element(el)
        self.tap(*self.MODIFY_SCHEDULE_BUTTON)
        return self

    def tap_resubscribe(self):
        """Tap Resubscribe button (available when status is 'cancelled')."""
        self.tap(*self.RESUBSCRIBE_BUTTON)
        return self

    def go_back(self):
        """Navigate back."""
        self.tap(*self.BACK_BUTTON)
        return self

    def get_plan_name(self) -> str:
        """Get subscription plan name text."""
        return self.get_text(*self.PLAN_NAME)

    def scroll_to_cancel_button(self):
        """Scroll to find cancel subscription button."""
        self.scroll_to_text("Cancel Subscription")
        return self

    def wait_for_data_loaded(self, timeout: int = 15):
        """Wait for subscription data to load (loading indicator gone, plan name visible)."""
        self.wait_for_loading_gone(timeout)
        return self