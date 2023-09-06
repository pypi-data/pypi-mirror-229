from setuptools import setup, find_packages

setup(
    name='algorename',
    version='1.4',
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'pytest'
    ],
    entry_points={
        'console_scripts': [
            'algorename=algorename.main:main',
        ],
    },
    author='Mario Nascimento',
    author_email='mario@whitehathacking.tech',
    description='A utility to change file names based on algorithms.',
)
