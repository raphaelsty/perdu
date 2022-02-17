import io
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="perdu",
    version="0.0.3",
    author="Raphael Sourty",
    author_email="raphael.sourty@gmail.com",
    description="Minimalist search engine for python code and notebooks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD-3",
    url="https://github.com/raphaelsty/perdu",
    package_data={"perdu": ["web/styles/*.css", "web/highlight.pack.js", "web/perdu.html"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["perdu=perdu:start"],
    },
)
