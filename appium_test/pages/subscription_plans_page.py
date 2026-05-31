"""
Subscription Plans Page Object — maps to subscription/subscription_family_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage


class SubscriptionPlansPage(BasePage):
    """Page object for subscription plan family selection."""

    # Family cards
    DELIGHT_FAMILY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="DELIGHT"]')
    SIGNATURE_FAMILY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="SIGNATURE"]')
    PREMIUM_FAMILY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="PREMIUM"]')

    # Plan selection - size/type options
    SIZE_200ML = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("200")')
    SIZE_300ML = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("300")')
    SIZE_500ML = (AppiumBy.ANDROID_UIAUTOMATOR,
        'new UiSelector().descriptionContains("500")')

    def select_family(self, family: str):
        """Select a subscription family."""
        locator = {
            'delight': self.DELIGHT_FAMILY,
            'signature': self.SIGNATURE_FAMILY,
            'premium': self.PREMIUM_FAMILY,
        }.get(family.lower())
        if locator:
            self.tap(*locator)
        return self

    def select_size(self, size: str):
        """Select plan size."""
        locator = {
            '200': self.SIZE_200ML,
            '300': self.SIZE_300ML,
            '500': self.SIZE_500ML,
        }.get(size)
        if locator:
            self.tap(*locator)
        return self

    def is_family_displayed(self, family: str) -> bool:
        locator = (AppiumBy.XPATH, f'//android.widget.TextView[@content-desc="{family.upper()}"]')
        return self.is_visible(*locator)