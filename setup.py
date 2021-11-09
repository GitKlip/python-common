import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="common",
    version="0.2.8",
    description="common stuff for 3plcentral",
    author="3plcentral",
    author_email="jprince@3plcentral",
    packages=setuptools.find_packages(exclude=["docs", "tests", ".gitignore", "README.md"]),
    # TODO: automate this from inspection of pyproject.toml file
    install_requires=[
        'pytz',
        'pyjwt',
    ]
)
