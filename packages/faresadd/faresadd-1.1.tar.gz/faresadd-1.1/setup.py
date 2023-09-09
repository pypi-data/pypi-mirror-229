import pathlib
import setuptools

setuptools.setup(
    name="faresadd",
    version='1.1',
    description="A package from me to add and sub easy ",
    long_description=pathlib.Path("README.md").read_text(),
    packages=setuptools.find_packages(exclude=("tests", "data"))
)
