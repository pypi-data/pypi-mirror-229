import setuptools
from pathlib import Path

long_desc = Path("Readme.md").read_text()
setuptools.setup(
    name="EkkoTrueDamage",
    version="0.0.1",
    long_description=long_desc,
    packages=setuptools.find_packages(
        exclude=["mocks", "tests"]
    )
)
