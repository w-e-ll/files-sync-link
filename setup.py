import os
from setuptools import setup, find_packages

from glob import glob


def read(*r_names):
    return open(os.path.join(os.path.dirname(__file__), *r_names)).read()


version = '1.0'

long_description = (
    read('README.md')
)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(name="files_sync_link",
      description="Fetch files over sftp and copy fetched file to multiple sources",
      version=version,
      license="",
      long_description=long_description,
      author="Valentin Sheboldaev",
      author_email="",
      url="",
      packages=find_packages(),
      data_files=[("", glob("README.md"))],
      include_package_data=True,
      platforms=["Any"],
      zip_safe=False,
      install_requires=[
            'asyncio',
            'asyncssh',
            'PyYAML',
      ],
)
