from setuptools import setup, find_packages
setup(
    name='shell2',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'google-cloud-firestore',
    ],
)