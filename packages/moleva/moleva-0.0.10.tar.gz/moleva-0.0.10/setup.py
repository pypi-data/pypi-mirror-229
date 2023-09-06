from setuptools import setup, find_packages
from pathlib import Path

__version__ = "0.0.10"

dependencies = filter(lambda x: x.strip(), Path("requirements.txt").read_text().split())
dependencies = map(lambda x: x.strip(), dependencies)
dependencies = list(dependencies)

print("find_packages()", find_packages())

setup(
    name="moleva",
    version=__version__,
    description="evaluate molecule properties",
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=dependencies,
    include_package_data=True
)
