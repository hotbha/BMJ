"""
Modify Schedule Page Object — maps to subscription/modify_schedule_screen.dart
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class ModifySchedulePage(BasePage):
    """Page object for modifying subscription schedule."""

    FREQUENCY_SELECTOR = (AppiumBy.ACCESSIBILITY_ID, 'modify_frequency_selector')
    FREQUENCY_WEEKLY = (AppiumBy.ACCESSIBILITY_ID, 'modify_frequency_weekly')
    FREQUENCY_BIWEEKLY = (AppiumBy.ACCESSIBILITY_ID, 'modify_frequency_biweekly')
    FREQUENCY_MONTHLY = (AppiumBy.ACCESSIBILITY_ID, 'modify_frequency_monthly')
    DAY_SELECTOR_MONDAY = (AppiumBy.ACCESSIBILITY_ID, 'modify_day_monday')
    DAY_SELECTOR_WEDNESDAY = (AppiumBy.ACCESSIBILITY_ID, 'modify_day_wednesday')
    DAY_SELECTOR_FRIDAY = (AppiumBy.ACCESSIBILITY_ID, 'modify_day_friday')
    CONFIRM_MODIFY_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'confirm_modify_button')
    CANCEL_MODIFY_BUTTON = (AppiumBy.ACCESSIBILITY_ID, 'cancel_modify_button')
    MODIFY_LOADING = (AppiumBy.ACCESSIBILITY_ID, 'modify_loading')

    def select_frequency(self, frequency: str):
        """Select new subscription frequency."""
        self.tap(*self.FREQUENCY_SELECTOR)
        freq_map = {
            'weekly': self.FREQUENCY_WEEKLY,
            'biweekly': self.FREQUENCY_BIWEEKLY,
            'monthly': self.FREQUENCY_MONTHLY,
        }
        locator = freq_map.get(frequency.lower())
        if locator:
            self.tap(*locator)
        return self

    def select_delivery_day(self, day: str):
        """Select delivery day."""
        day_map = {
            'monday': self.DAY_SELECTOR_MONDAY,
            'wednesday': self.DAY_SELECTOR_WEDNESDAY,
            'friday': self.DAY_SELECTOR_FRIDAY,
        }
        locator = day_map.get(day.lower())
        if locator:
            self.tap(*locator)
        return self

    def confirm_modify(self):
        """Confirm schedule modification."""
        self.tap(*self.CONFIRM_MODIFY_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def cancel_modify(self):
        """Cancel schedule modification."""
        self.tap(*self.CANCEL_MODIFY_BUTTON)
        return self