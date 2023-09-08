from setuptools import setup, find_packages

setup(
    name="foreqast-client",
    packages=find_packages(),
    version="0.1.0",
    description="Python client for requests to the ForeQast API.",
    author="Qiyuan Cai",
    author_email="astral@foreqast.ai",
    install_requires=[
        "pandas",
        "requests"
    ],
)
