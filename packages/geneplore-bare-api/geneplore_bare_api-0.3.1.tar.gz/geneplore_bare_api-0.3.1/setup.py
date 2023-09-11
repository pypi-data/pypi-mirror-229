from setuptools import setup

setup(
    name='geneplore_bare_api',
    version='0.3.1',
    install_requires=[
        'requests',
        'pandas',
        'tiktoken',
        'google-api-python-client',
        'google-api-core',
        'python-dotenv'
    ],
)