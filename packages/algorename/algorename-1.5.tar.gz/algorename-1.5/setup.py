from setuptools import setup, find_packages

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='algorename',
    version='1.5',
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
    long_description=long_description,
    long_description_content_type='text/markdown',
)
