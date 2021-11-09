from distutils.util import strtobool


def to_bool(value):
    """ Returns True or False given anything boolean like.

    Note: Uses distutils.util.strtobool function under the hood

    Args:
        value (object): accepts strings or objects that are true-ish or false-ish
            True: True, 1, 'y', 'yes', 't', 'true', 'on', '1'
            False: False, 0, 'n', 'no', 'f', 'false', 'off', '0'

    Raises:
        (ValueError): if value is anything not specified above
    """
    return bool(strtobool(str(value).lower()))
