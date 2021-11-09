
import re
import subprocess
from itertools import chain


class PytestCoverageRunner:
    """ Runs pytest with coverage and returns metrics. """
    CMD = "pytest"

    DEFAULT_OPTIONS = {
        # traceback print mode (auto/long/short/line/native/no)
        "--tb": "line",

        # one of: term, term-missing, annotate, html, xml (multi-allowed)
        "--cov-report": "term-missing",
    }

    # Can be in one of these formats:
    #     collecting ... collected 98 items
    #     collected 98 items
    NUM_TESTS_RE = re.compile(r'collected (\d+) items')

    # In this format:
    #     ========================== 98 passed in 2.79 seconds ===========================
    PASSED_IN_TIME_RE = re.compile(r'\=+ (\d+) passed in ([\d\.]+) seconds \=+')
    SOME_FAILED_IN_TIME_RE = re.compile(r'\=+ (\d+) failed, (\d+) passed in ([\d\.]+) seconds \=+')

    # In this format:
    #     TOTAL                                 462     58    87%
    COVERAGE_PERCENT_RE = re.compile(r'TOTAL\s+(\d+)\s+(\d+)\s+(\d+)\%')

    def __init__(self, coverage_dir, cmd=CMD, quiet=False):
        """
        Args:
            coverage_dir (str or Path): The path to calculate coverage on.
        """
        self.cmd = cmd.split() if isinstance(cmd, str) else cmd
        self.coverage_dir = coverage_dir
        self.quiet = quiet

    def run(self, *args):
        """ Run CMD using DEFAULT_OPTIONS and any additional args passed in here.


        Returns:
            (dict): A dictionary with 'metrics' (a dict with 'coverage' and
                'tests' dicts) and 'process' which is the CompletedProcess object
                with stdout and stderr attributes.
        """
        all_options = dict(self.DEFAULT_OPTIONS, **{"--cov": self.coverage_dir})
        flat_options = list(chain.from_iterable([[key, val] for key, val in all_options.items()]))
        full_cmd = self.cmd + flat_options + list(args)
        process = subprocess.run(full_cmd,  text=True, capture_output=True)

        if not self.quiet:
            print(process.stdout)

        if process.stderr:
            print("<< stderr >>")
            print(process.stderr)

        # To get real-time display and capture we want something like this:
        # (for some reason this is hanging, so just capturing text for now)
        # process = subprocess.Popen(full_cmd,  text=True, stdout=subprocess.PIPE)
        # Poll process.stdout to show stdout live
        # while True:
        #     output = process.stdout.readline()
        #     if process.poll() is not None:
        #         break
        #     if output:
        #         print(output.strip())
        # rc = process.poll()

        metrics = self._parse_metrics(process.stdout)
        return dict(
            metrics,
            process={
                'returncode': process.returncode,
                'object': process,
            }
        )

    def _parse_metrics(self, output):

        # below could easily be optimized

        # number of tests run
        match = self.NUM_TESTS_RE.search(output)
        num_run = int(match.group(1)) if match else None

        # number of tests passed in so many seconds
        match = self.PASSED_IN_TIME_RE.search(output)
        if match:
            num_passed_str, seconds_str = match.groups()
            num_failed = 0
            num_passed = int(num_passed_str)
            seconds = float(seconds_str)
        else:
            match = self.SOME_FAILED_IN_TIME_RE.search(output)
            num_failed_str, num_passed_str, seconds_str = match.groups()
            num_failed = int(num_failed_str)
            num_passed = int(num_passed_str)
            seconds = float(seconds_str)

        # coverage
        match = self.COVERAGE_PERCENT_RE.search(output)
        statements, missed, reported_coverage_percent = (int(val) for val in match.groups())

        return dict(
            coverage=dict(
                number_statements=statements,
                number_missed=missed,
                reported_percent=reported_coverage_percent,
            ),
            tests=dict(
                number_run=num_run,
                number_passed=num_passed,
                number_failed=num_failed,
                seconds=seconds,
            )
        )
