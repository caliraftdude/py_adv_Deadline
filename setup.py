from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="deadline-if",
    version="1.0.0",
    author="Python Port Team",
    description="Deadline Interactive Fiction - Python 3.13 Port",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/deadline-python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "deadline": ["data/*.json"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.13",
    install_requires=[
        "typing-extensions>=4.8.0",
        "dataclasses-json>=0.6.1",
        "prompt-toolkit>=3.0.39",
        "colorama>=0.4.6",
        "rich>=13.5.0",
    ],
    entry_points={
        "console_scripts": [
            "deadline=deadline.main:main",
        ],
    },
)