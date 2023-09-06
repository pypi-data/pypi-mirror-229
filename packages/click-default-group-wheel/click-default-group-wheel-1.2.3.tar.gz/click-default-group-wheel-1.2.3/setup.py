from setuptools import setup
import os

VERSION = "1.2.3"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="click-default-group-wheel",
    description="click-default-group-wheel is now click-default-group",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=VERSION,
    install_requires=["click-default-group"],
    classifiers=["Development Status :: 7 - Inactive"],
)
