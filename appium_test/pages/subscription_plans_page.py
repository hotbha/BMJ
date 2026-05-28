"""
Subscription Plans Page Object — maps to subscription/ files
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class SubscriptionPlansPage(BasePage):
    """Page object for subscription plan selection."""

    PLAN_CARD = (AppiumBy.ACCESSIBILITY_ID, 'subscription_plan_card')
    CONFIRM_PLAN_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'confirm_plan_button')
    PLAN_NAME = (AppiumBy.ACCESSIBILITY_ID, 'subscription_plan_name')
    PLAN_PRICE = (AppiumBy.ACCESSIBILITY_ID, 'subscription_plan_price')
    PLAN_SELECTOR = (AppiumBy.ACCESSIBILITY_ID, 'plan_selector')

    # Family selection
    FAMILY_DELIGHT = (AppiumBy.ACCESSIBILITY_ID, 'family_delight')
    FAMILY_PREMIUM = (AppiumBy.ACCESSIBILITY_ID, 'family_premium')

    # Frequency
    FREQUENCY_WEEKLY = (AppiumBy.ACCESSIBILITY_ID, 'frequency_weekly')
    FREQUENCY_BIWEEKLY = (AppiumBy.ACCESSIBILITY_ID, 'frequency_biweekly')
    FREQUENCY_MONTHLY = (AppiumBy.ACCESSIBILITY_ID, 'frequency_monthly')

    # Schedule
    SCHEDULE_DAY = (AppiumBy.ACCESSIBILITY_ID, 'schedule_day_monday')
    REVIEW_ORDER_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'review_order_button')
    START_SUBSCRIPTION_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'start_subscription_button')

    def select_family(self, family: str):
        """Select a product family."""
        family_map = {
            'delight': self.FAMILY_DELIGHT,
            'premium': self.FAMILY_PREMIUM,
        }
        locator = family_map.get(family.lower())
        if locator:
            self.tap(*locator)
        self.wait_for_loading_gone()
        return self

    def confirm_plan(self):
        self.tap(*self.CONFIRM_PLAN_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def select_frequency(self, frequency: str):
        """Select subscription frequency."""
        freq_map = {
            'weekly': self.FREQUENCY_WEEKLY,
            'biweekly': self.FREQUENCY_BIWEEKLY,
            'monthly': self.FREQUENCY_MONTHLY,
        }
        locator = freq_map.get(frequency.lower())
        if locator:
            self.tap(*locator)
        return self

    def start_subscription(self):
        self.tap(*self.START_SUBSCRIPTION_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def get_plan_name(self) -> str:
        return self.get_text(*self.PLAN_NAME)

    def get_plan_price(self) -> str:
        return self.get_text(*self.PLAN_PRICE)