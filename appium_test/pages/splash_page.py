"""
Splash Page Object — maps to splash_page.dart
The splash screen auto-navigates to login after ~2 seconds, no user action needed.
"""
from appium.webdriver.common.appiumby import AppiumBy
from pages.base_page import BasePage
import time


class SplashPage(BasePage):
    """Page object for splash screen. Auto-navigates after 2s."""

    SPLASH_LOGO = (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().className("android.widget.Image")')

    def wait_for_splash(self, timeout: int = 10):
        """Wait for splash screen to appear, then wait for auto-navigation."""
        # Splash auto-navigates after ~2 seconds; just wait for the transition
        time.sleep(2.5)
        return self

    def navigate_to_login(self):
        """No button to tap — splash auto-navigates to login after ~2s."""
        # Wait for the splash duration + navigation to complete
        time.sleep(3)
        return self