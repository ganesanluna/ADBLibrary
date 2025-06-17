from setuptools import setup, find_packages

setup(
    name="robotframework-adblibrary",
    version="0.1.1",
    author="Ganesan Selvaraj",
    author_email="ganesanluna@yahoo.in",
    description="Robot Framework library for Android ADB interaction",
    long_description=open("README.md", encoding="utf-8").read(),
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
        "robotframework>=5.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Robot Framework",
        "Framework :: Robot Framework :: Library",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["robotframework", "adb", "android", "automation", "testing"],
    python_requires='>=3.6',
)
