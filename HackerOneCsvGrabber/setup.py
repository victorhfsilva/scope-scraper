from setuptools import setup, find_packages

setup(
    name="HackerOneCsvGrabber",
    version="2.0.0",
    author="Victor Silva",
    description="A tool to extract and process in scope assets from Hacker One CSV files",
    packages=find_packages(include=["src", "src.*"]),
    py_modules=["h1_grabber"],
    package_dir={"": "."},
    install_requires=[],
    entry_points={
        "console_scripts": [
            "HackerOneCsvGrabber=h1_grabber:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)