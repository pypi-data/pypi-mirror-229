from setuptools import setup, find_packages

setup(
    name='data_to_snowflake',
    version='2.0.5',
    packages=find_packages(),
    install_requires=[
        # List any dependencies your package requires to run
        'snowflake-connector-python[pandas]',
        'python-dotenv',
        'pandas',
        'pygsheets',
    ],
)

