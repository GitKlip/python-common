import os
import subprocess


class TestTasks:
    """ Test that the tasks work with invoke. """
    CMD_KWARGS = dict(
        capture_output=True,
        encoding="utf-8",
        shell=True,
        env=os.environ.copy(),
    )

    def test_unapproved_licenses(self):
        """ Should emit table of unapproved licenses. """
        reply = subprocess.run("poetry run invoke license.unapproved-licenses", **self.CMD_KWARGS)
        output = reply.stdout
        # assumes we require pylint and pylint is GPL and that's on our unapproved list
        assert "pylint" in output
        assert "GNU General Public License" in output

    def test_write_table(self):
        """ Should emit a table of licenses used. """
        reply = subprocess.run("poetry run invoke license.write-table --outfile='-'", **self.CMD_KWARGS)
        output = reply.stdout
        # assumes we require coverage and at least one package we depend on is Apache licensed
        assert 'coverage' in output
        assert 'Apache Software License' in output
