from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="morvba",
    version="2.0.0",
    author="Carlos Martins",
    author_email="c@tgrafi.co",
    description="A package providing VBA-like and other useful functions for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/masterofrisk/pythonvba",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.6',
    install_requires=[
        "chardet",
        "colorama",
        "configparser",
        "python-dateutil",
        "tiktoken"
    ],
    include_package_data=True,
)
