from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

setup(
    name='kickbotui',
    version='0.0.6',
    description='Basic User-Interface for interacting with the kickbot package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lukemvc/kickbotui",
    packages=find_packages(),
    package_data={'kickbotui': ['static/*', 'templates/*']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'kickbotui = kickbotui.app:main',
        ],
    },
)
