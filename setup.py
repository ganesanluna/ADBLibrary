from setuptools import setup, find_packages

setup(
    name="robotframework-adblibrary",
    version="0.1.0",
    author="Ganesan Selvaraj",
    author_email="ganesanluna@yahoo.in",
    description="Robot Framework library for Android ADB interaction",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ganesanluna/ADBLibrary",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "robotframework>=5.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Robot Framework",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

