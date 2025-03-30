import random
import traceback

from kybra_simple_db import logger

class Tester:
    def __init__(self, test_class):
        self.test_instance = test_class()

    def run_tests(self):
        """Run all test methods in the test class and report results."""
        test_methods = [
            getattr(self.test_instance, func)
            for func in dir(self.test_instance)
            if callable(getattr(self.test_instance, func)) and func.startswith("test_")
        ]
        random.shuffle(test_methods)  # catch hidden dependencies among tests
        failed = 0
        for test in test_methods:
            try:
                # Call setUp if it exists
                if hasattr(self.test_instance, "setUp"):
                    self.test_instance.setUp()
                test()
                logger.info(f"{test.__name__} passed")  # Green for pass
            except Exception as e:
                logger.error(f"{test.__name__} failed: {e}")  # Red for fail
                logger.error(traceback.format_exc())
                failed += 1
        logger.info(
            f"\033[91m{failed} tests failed\033[0m"
            if failed > 0
            else "\033[92mAll tests passed\033[0m"
        )
        return failed

    @classmethod
    def assert_raises(cls, exception, func, *args, **kwargs):
        """Assert that a function raises a specific exception."""
        try:
            func(*args, **kwargs)
        except exception:
            logger.error(f"{func.__name__} raised {exception.__name__} as expected")
            return True
        except Exception as e:
            logger.error(f"{func.__name__} raised an unexpected exception: {e}")
            return False
        else:
            logger.error(f"{func.__name__} did not raise {exception.__name__}")
            return False
