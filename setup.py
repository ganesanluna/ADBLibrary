"""
Setup script for the Robot Framework ADB library.
Handles packaging and distribution via setuptools.
"""

import pathlib
from setuptools import setup, find_packages

# Read README.md for long_description
this_dir = pathlib.Path(__file__).parent.resolve()
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="robotframework-adblibrary",
    version="0.1.3",
    author="Ganesan Selvaraj",
    author_email="ganesanluna@yahoo.in",
    description="Robot Framework library for Android ADB interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ganesanluna/ADBLibrary",
    project_urls={
        "Documentation": "https://github.com/ganesanluna/ADBLibrary#readme",
        "Source": "https://github.com/ganesanluna/ADBLibrary",
        "Tracker": "https://github.com/ganesanluna/ADBLibrary/issues",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "robotframework>=7.0",
        "ipaddress>=1.0.23",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Library",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["robotframework", "adb", "android", "automation", "testing"],
    python_requires=">=3.10",
)
