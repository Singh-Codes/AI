from setuptools import setup, find_packages

setup(
    name="windsurf_ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pytest>=7.0.0",
        "hypothesis>=6.0.0",
    ],
    python_requires=">=3.8",
)
