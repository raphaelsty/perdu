import io
import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, "perdu", "__version__.py")) as f:
    exec(f.read(), about)

setup(
    name="perdu",
    version=about["__version__"],
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
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["perdu=perdu:start"],
    },
    install_requires=[
        "Flask>=2.0.0",
        "Flask-Cors>=3.0.10",
        "elasticsearch>=7.12.1",
        "nbformat>=5.1.2",
        "regex>=2021.3.17",
        "requests>=2.25.1",
    ],
)
