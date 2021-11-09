
import subprocess
from pathlib import Path
from unittest.mock import patch

from common.ci_cd.pytest_coverage_runner import PytestCoverageRunner

THIS_DIR = Path(__file__).resolve().parent
PASSING_TESTS_BASE_FILENAME = "passing_tests.txt"
FAILING_TESTS_BASE_FILENAME = "failing_tests.txt"

PASSING_TEST_STR = open(THIS_DIR / PASSING_TESTS_BASE_FILENAME).read()
FAILING_TEST_STR = open(THIS_DIR / FAILING_TESTS_BASE_FILENAME).read()


class TestPytestCoverageRunner:
    """ Test PytestCoverageRunner. """

    @patch('subprocess.run')
    def test_passing_tests(self, subprocess_run_mock):
        completed_process = subprocess.CompletedProcess(args=[], returncode=0, stdout=PASSING_TEST_STR, stderr='')
        expected = {
            'coverage': {'number_statements': 461, 'number_missed': 57, 'reported_percent': 88},
            'tests': {'number_run': 99, 'number_passed': 99, 'number_failed': 0, 'seconds': 2.69},
            'process': {
                'returncode': 0,
                'object': completed_process,
            }
        }

        subprocess_run_mock.return_value = completed_process
        runner = PytestCoverageRunner(coverage_dir="common", quiet=True)

        # pick any test but this one to run to avoid infinite loop!
        response = runner.run()
        assert response == expected

    @patch('subprocess.run')
    def test_failing_tests(self, subprocess_run_mock):
        completed_process = subprocess.CompletedProcess(args=[], returncode=1, stdout=FAILING_TEST_STR, stderr='')
        expected = {
            'coverage': {'number_statements': 468, 'number_missed': 42, 'reported_percent': 91},
            'tests': {'number_run': 100, 'number_passed': 99, 'number_failed': 1, 'seconds': 2.74},
            'process': {
                'returncode': 1,
                'object': completed_process,
            }
        }

        subprocess_run_mock.return_value = completed_process
        runner = PytestCoverageRunner(coverage_dir="common", quiet=True)

        # pick any test but this one to run to avoid infinite loop!
        response = runner.run()
        assert response == expected
