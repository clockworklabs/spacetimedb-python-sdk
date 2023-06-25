from setuptools import setup, find_packages

setup(
    name='spacetimedb_python_sdk',
    version='1.0.3',
    description='The spacetimedb_python_sdk is a software development kit (SDK) designed to facilitate the creation of client applications that interact with SpacetimeDB modules.',
    author='Clockwork Labs',
    author_email='derek@clockworklabs.io',
    packages=find_packages(),
    install_requires=[
        'websocket-client',
        'configparser',
    ],
)