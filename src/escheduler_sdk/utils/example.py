import sys
import os

# To make this example runnable, add the 'src' directory to Python's path
# This allows us to import 'escheduler_sdk' as a top-level package
# __file__ is the path to the current script.
# os.path.dirname(__file__) is '.../src/escheduler_sdk/utils'
# os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) is '.../src'
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, src_dir)

from escheduler_sdk.utils.test_logger import test_logger, log_test_exception

def run_example():
    """A simple function to demonstrate the usage of test_logger."""
    test_logger.debug("This is a debug message from the example in utils.")
    test_logger.info("This is an info message.")
    test_logger.warning("This is a warning message.")

    try:
        # Simulate an operation that will cause an exception
        x = 1 / 0
    except ZeroDivisionError:
        # Use log_test_exception to record the full exception information
        test_logger.error("An error occurred during calculation!")
        log_test_exception()  # This will automatically capture and log the current exception stack

    test_logger.info("Example execution finished.")

if __name__ == "__main__":
    print("Starting logger example from utils...")
    run_example()
    # The logger now creates a unique timestamped file for each run.
    log_dir = os.path.join(src_dir, 'logs', 'test')
    print("\nExample execution complete.")
    print(f"Please check the 'logs/test' directory for the newly created log file: '{log_dir}'")
