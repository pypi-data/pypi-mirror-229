from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tqueue",
    version="0.0.2",
    author="Hai Cao",
    author_email="",
    description="Threading Queue",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haiz/tqueue",
    project_urls={
        "Bug Tracker": "https://github.com/haiz/tqueue/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    package_dir={'': "src"},
    packages=find_packages("src"),
    python_requires=">=3.6",
    entry_points={}
)
