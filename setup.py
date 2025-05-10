from setuptools import setup, find_packages

setup(
    name="recursive-archive-extractor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.0.0",
        "tqdm>=4.65.0",
    ],
    entry_points={
        "console_scripts": [
            "extract-archives=archiver.cli:main",
        ],
    },
    author="ggfevans",
    author_email="admin@local.host",
    description="A tool for recursively extracting archives in directories",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ggfevans/recursive-archive-extractor",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
