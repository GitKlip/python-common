
import logging

from common.logging_utils import setup_as_console_handler


class TestSetupAsConsoleHandler:

    def test_default_logging_behavior(self, capsys):
        """ Default logger won't log info or debug levels (why we want console handler in first place!). """
        logger = logging.getLogger("default_behavior")
        logger.setLevel(logging.DEBUG)
        logger.debug("hiya!")
        self._assert_stderr(capsys, '')

    def test_basic_usage(self, capsys):
        """ Sends info level to stderr by default. """
        logger = setup_as_console_handler(logger=logging.getLogger("basic_usage"))
        logger.info("hiya!")
        logger.debug("will not show!")
        self._assert_stderr(capsys, 'hiya!\n')

    def test_debug_level(self, capsys):
        """ Can specify the logger's log level. """
        logger = setup_as_console_handler(logger=logging.getLogger("debug_level"), log_level=logging.DEBUG)
        logger.debug("will show!")
        self._assert_stderr(capsys, 'will show!\n')

    def test_format_string(self, capsys):
        fmt_str = '%(name)s - %(levelname)s - %(message)s'
        EXPECTED = "format_string - INFO - hiya!\n"

        logger = setup_as_console_handler(logger=logging.getLogger("format_string"), format_str=fmt_str)
        logger.setLevel(logging.DEBUG)
        logger.info("hiya!")
        self._assert_stderr(capsys, EXPECTED)

    @staticmethod
    def _assert_stderr(capsys_, expected):
        captured = capsys_.readouterr()
        assert not captured.out
        assert captured.err == expected
