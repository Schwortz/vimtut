#!/usr/bin/env python3
"""
Main test runner for Vimtut tests.

Runs all unit tests from the internal test modules.

Usage:
    python tests/run_all_tests.py
    python -m tests.run_all_tests
"""

import os
import sys
import unittest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import all test modules
from tests.internal import test_lessons
from tests.internal import test_validation
from tests.internal import test_cleanup
from tests.internal import test_multiple_files
from tests.internal import test_split_windows
from tests.internal import test_marks


def create_test_suite():
    """Create a test suite containing all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add tests from each module
    suite.addTests(loader.loadTestsFromModule(test_lessons))
    suite.addTests(loader.loadTestsFromModule(test_validation))
    suite.addTests(loader.loadTestsFromModule(test_cleanup))
    suite.addTests(loader.loadTestsFromModule(test_multiple_files))
    suite.addTests(loader.loadTestsFromModule(test_split_windows))
    suite.addTests(loader.loadTestsFromModule(test_marks))

    return suite


def run_tests(verbosity=2):
    """Run all tests and return success status."""
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    print("=" * 70)
    print("VIMTUT TEST SUITE")
    print("=" * 70)
    print()

    success = run_tests()

    print()
    print("=" * 70)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 70)

    sys.exit(0 if success else 1)
