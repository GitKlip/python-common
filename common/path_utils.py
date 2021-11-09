from contextlib import contextmanager
import os


@contextmanager
def chdir(newdir):
    """ context manager for changing directories.

    Example:
        with chdir("/home/user/whatevs"):
            # now in "/home/user/whatevs"
            ...
            raise Exception("something went wrong!")
        # now you are back to wherever you were before!

    Modified from public domain https://stackoverflow.com/a/24176022/422075
    """
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)
