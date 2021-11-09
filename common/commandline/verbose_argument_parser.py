import logging
from argparse import ArgumentParser


class VerboseArgumentParser(ArgumentParser):
    """ An ArgumentParser whose verbosity works closely with logging levels.

    Basic Example:
        parser = VerboseArgumentParser()
        parser.add_argument("blah", help="something")

        # root loglevel set to logging.INFO
        args = parser.parse_args(["-v"])

        # root loglevel set to logging.DEBUG
        args = parser.parse_args(["-vv"])

    Special logger:
        args = parser.parse_args(["-v"], logger=my_logger)
    """

    # correspond to verbose values by index, 0, 1, 2
    LOG_LEVELS = [logging.WARN, logging.INFO, logging.DEBUG]

    # modified slightly from https://stackoverflow.com/a/21981107/422075, which is public domain
    VERBOSE_ARGS = ["-v", "--verbose"]
    VERBOSE_KWARGS = dict(
        action="count",
        default=0,
        help="verbosity; no flag -> warn, '-v' -> info, '-vv' -> debug.",
    )

    @classmethod
    def add_verbose(cls, parser):
        parser.add_argument(*cls.VERBOSE_ARGS, **cls.VERBOSE_KWARGS)

    @classmethod
    def set_log_level(cls, args, logger):
        logger.setLevel(cls.LOG_LEVELS[args.verbose])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__class__.add_verbose(self)

    def parse_args(self, *args, logger=None, **kwargs):
        """ Parses the args and sets logging level based on verbosity on logger or root logger. """
        args = super().parse_args(*args, **kwargs)
        if logger is None:
            logger = logging.getLogger()
        self.__class__.set_log_level(args, logger)
        return args
