import sys

from invoke import Collection

from common.licenses import tasks as license_tasks

# add tasks here (needs to be before Collection logic below):
...

namespace = Collection.from_module(sys.modules[__name__])
namespace.add_collection(license_tasks, name="license")
