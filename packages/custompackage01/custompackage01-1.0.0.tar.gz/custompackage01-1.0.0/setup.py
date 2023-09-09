import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "custompackage01",
    version = "1.0.0",
    author="Ananth S S",
    description =  "Custom python module",
    long_description = long_description,
    packages= setuptools.find_packages(),
    py_modules=["custom"],
    package_dir={"": "custompackage01/src"}
)