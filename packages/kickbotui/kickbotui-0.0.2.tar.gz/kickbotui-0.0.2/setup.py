from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='kickbotui',
    version='0.0.2',
    description='Basic User-Interface for interacting with the kickbot package',
    packages=find_packages(),
    package_data={'kickbotui': ['static/*', 'templates/*']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'kickbotui = kickbotui.app:main',
        ],
    },
)
