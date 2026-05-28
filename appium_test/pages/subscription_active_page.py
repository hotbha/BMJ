"""
Active Subscription Page Object — maps to subscription/active_subscription_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class ActiveSubscriptionPage(BasePage):
    """Page object for active subscription details."""

    STATUS_CHIP = (AppiumBy.ACCESSIBILITY_ID, 'subscription_status_chip')
    PAUSE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'pause_subscription_button')
    RESUME_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'resume_subscription_button')
    CANCEL_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'cancel_subscription_button')
    MODIFY_SCHEDULE_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'modify_schedule_button')
    SUBSCRIPTION_PLAN_NAME = (AppiumBy.ACCESSIBILITY_ID, 'active_subscription_plan_name')
    NEXT_DELIVERY_DATE = (AppiumBy.ACCESSIBILITY_ID, 'next_delivery_date')
    BACK_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'active_subscription_back')

    def get_status(self) -> str:
        return self.get_text(*self.STATUS_CHIP)

    def tap_pause(self):
        self.tap(*self.PAUSE_BUTTON)
        return self

    def tap_resume(self):
        self.tap(*self.RESUME_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def tap_cancel(self):
        self.tap(*self.CANCEL_BUTTON)
        return self

    def tap_modify_schedule(self):
        self.tap(*self.MODIFY_SCHEDULE_BUTTON)
        return self

    def go_back(self):
        self.tap(*self.BACK_BUTTON)
        return self