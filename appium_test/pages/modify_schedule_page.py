"""
Modify Schedule Page Object — maps to subscription/modify_schedule_screen.dart
Uses text-based XPath selectors since Flutter Key() widgets are NOT exposed as content-desc.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
from config.test_config import TestConfig


class ModifySchedulePage(BasePage):
    """Page object for modifying subscription schedule."""

    # Page title
    PAGE_TITLE = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Modify Schedule" or @content-desc="Schedule"]')

    # Frequency selectors
    FREQUENCY_WEEKLY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Weekly" or @content-desc="Every Week"] | //android.widget.RadioButton[@content-desc="Weekly" or @content-desc="Every Week"]')
    FREQUENCY_BIWEEKLY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Biweekly" or @content-desc="Every 2 Weeks" or @content-desc="Fortnightly"] | //android.widget.RadioButton[@content-desc="Biweekly" or @content-desc="Every 2 Weeks" or @content-desc="Fortnightly"]')
    FREQUENCY_MONTHLY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Monthly" or @content-desc="Every Month"] | //android.widget.RadioButton[@content-desc="Monthly" or @content-desc="Every Month"]')

    # Day selectors
    DAY_MONDAY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Monday" or @content-desc="Mon"]')
    DAY_TUESDAY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Tuesday" or @content-desc="Tue"]')
    DAY_WEDNESDAY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Wednesday" or @content-desc="Wed"]')
    DAY_THURSDAY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Thursday" or @content-desc="Thu"]')
    DAY_FRIDAY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Friday" or @content-desc="Fri"]')
    DAY_SATURDAY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Saturday" or @content-desc="Sat"]')
    DAY_SUNDAY = (AppiumBy.XPATH, '//android.widget.TextView[@content-desc="Sunday" or @content-desc="Sun"]')

    # Confirm modify button
    CONFIRM_MODIFY_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Confirm" or @content-desc="Save Changes" or @content-desc="Update"] | //android.widget.TextView[@content-desc="Confirm" or @content-desc="Save Changes" or @content-desc="Update"]')

    # Cancel button
    CANCEL_BUTTON = (AppiumBy.XPATH, '//android.widget.Button[@content-desc="Cancel" or @content-desc="Go Back"] | //android.widget.TextView[@content-desc="Cancel" or @content-desc="Go Back"]')

    def select_frequency(self, frequency: str):
        """Select new subscription frequency.

        Args:
            frequency: 'weekly', 'biweekly', or 'monthly'
        """
        freq_map = {
            'weekly': self.FREQUENCY_WEEKLY,
            'biweekly': self.FREQUENCY_BIWEEKLY,
            'fortnightly': self.FREQUENCY_BIWEEKLY,
            'monthly': self.FREQUENCY_MONTHLY,
        }
        locator = freq_map.get(frequency.lower())
        if locator:
            self.tap(*locator)
        return self

    def select_delivery_day(self, day: str):
        """Select delivery day of week.

        Args:
            day: 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
        """
        day_map = {
            'monday': self.DAY_MONDAY,
            'tuesday': self.DAY_TUESDAY,
            'wednesday': self.DAY_WEDNESDAY,
            'thursday': self.DAY_THURSDAY,
            'friday': self.DAY_FRIDAY,
            'saturday': self.DAY_SATURDAY,
            'sunday': self.DAY_SUNDAY,
        }
        locator = day_map.get(day.lower())
        if locator:
            # Scroll to day if not visible — may be in horizontal/vertical list
            try:
                self.tap(*locator)
            except Exception:
                self.scroll_to_text(day.capitalize())
                self.tap(*locator)
        return self

    def confirm_modify(self):
        """Confirm schedule modification."""
        self.tap(*self.CONFIRM_MODIFY_BUTTON)
        self.wait_for_loading_gone(TestConfig.API_WAIT)
        return self

    def cancel_modify(self):
        """Cancel schedule modification."""
        self.tap(*self.CANCEL_BUTTON)
        return self

    def is_displayed(self) -> bool:
        """Check if modify schedule screen is displayed."""
        return self.is_visible(self.PAGE_TITLE) or self.is_visible(self.FREQUENCY_WEEKLY)