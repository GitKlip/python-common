import logging

from common.commandline.verbose_argument_parser import VerboseArgumentParser

ROOT_LOGGER = logging.getLogger()
INIT_ROOT_LEVEL = ROOT_LOGGER.level


class TestVerboseArgumentParser:
    """ Should properly set the root logger level. """

    EXPECTED = {
        tuple(): (logging.WARN, 0),
        ("-v",): (logging.INFO, 1),
        ("-vv",): (logging.DEBUG, 2),
    }

    def setup_method(self):
        self.parser = VerboseArgumentParser()
        self.parser.add_argument("file")
        ROOT_LOGGER.setLevel(INIT_ROOT_LEVEL)

    def teardown_method(self):
        ROOT_LOGGER.setLevel(INIT_ROOT_LEVEL)

    def test_no_logger(self):
        """ Should set root log level and verbose appropriately. """
        self._test_logger()

    def test_with_logger(self):
        """ Should set the given log level and verbose appropriately and not mess with root. """
        this_file_logger = logging.getLogger(__name__)
        self._test_logger(logger=this_file_logger)

    def _test_logger(self, **kwargs):
        for verbose_args, (log_level, verbose_level) in self.EXPECTED.items():
            parse_args = ["myfile"] + list(verbose_args)
            args = self.parser.parse_args(parse_args, **kwargs)
            logger = kwargs.get('logger')
            if logger:
                assert ROOT_LOGGER.level == INIT_ROOT_LEVEL
                assert logger.level == log_level
            else:
                assert ROOT_LOGGER.level == log_level

            assert args.verbose == verbose_level
