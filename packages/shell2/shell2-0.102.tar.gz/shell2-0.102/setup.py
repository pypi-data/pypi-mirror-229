from setuptools import setup, find_packages
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='shell2',
    version='0.102',
    packages=find_packages(),
    install_requires=[
        'requests',
        #'google-cloud-firestore',
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
