import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))


class TestConfig:
    SERVER_URL = os.getenv('BMJ_SERVER_URL')
    TEST_EMAIL = os.getenv('TEST_EMAIL')
    TEST_PASSWORD = os.getenv('TEST_PASSWORD')
    CHARGEBEE_API_KEY = os.getenv('CHARGEBEE_TEST_API_KEY')
    FIREBASE_API_KEY = os.getenv('FIREBASE_WEB_API_KEY')

    PINCODE_VALID = '110001'
    PINCODE_INVALID = '400001'
    SEARCH_HIT = 'mango'
    SEARCH_MISS = 'xyzabc123'

    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 15
    API_WAIT = 30  # real API calls take longer

    # App package for device operations
    APP_PACKAGE = 'com.bookmyjuice.lush'

    # Chargebee site
    CHARGEBEE_SITE = 'bookmyjuice-test'

    @classmethod
    def validate(cls):
        missing = [k for k, v in {
            'BMJ_SERVER_URL': cls.SERVER_URL,
            'TEST_EMAIL': cls.TEST_EMAIL,
            'TEST_PASSWORD': cls.TEST_PASSWORD,
            'CHARGEBEE_TEST_API_KEY': cls.CHARGEBEE_API_KEY,
            'FIREBASE_WEB_API_KEY': cls.FIREBASE_API_KEY,
        }.items() if not v]
        if missing:
            raise EnvironmentError(
                f"Missing .env values: {missing}\n"
                f"Copy .env.example to .env and fill all values.")


TestConfig.validate()