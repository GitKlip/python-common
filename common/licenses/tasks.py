import json

from invoke import task

from common.config_utils import get_project_name
from common.licenses.constants import APPROVED
from common.licenses.constants import LICENSES_USED_FILE
from common.licenses.constants import LICENSES_USED_FORMAT


def _core_pip_licenses_cmd():
    project_name = get_project_name()
    common_project_name = get_project_name(__file__)
    ignore_packages = list(set([project_name, common_project_name]))
    return str(
        f"pip-licenses --from=mixed "
        f"--ignore-packages {' '.join(ignore_packages)} "
    )


@task
def write_table(context, outfile=LICENSES_USED_FILE, format=LICENSES_USED_FORMAT):
    print(f"Writing: {outfile}")
    options = f"--order=license --with-urls --format={format} "
    if outfile != '-':
        options += f" > {outfile}"

    context.run(
        _core_pip_licenses_cmd() + options
    )


@task
def unapproved_licenses(context):
    result = context.run(_core_pip_licenses_cmd() + "--format=json", hide='stdout')
    licenses = json.loads(result.stdout)
    for license_info in licenses:
        if license_info["License"] not in APPROVED:
            print(' '.join(license_info[key] for key in ['Name', 'Version', 'License']))
