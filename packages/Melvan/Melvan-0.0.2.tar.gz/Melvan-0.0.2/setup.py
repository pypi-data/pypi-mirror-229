import re
from sys import argv

import setuptools


from compiler.api import compiler as api_compiler
from compiler.errors import compiler as errors_compiler


with open("requirements.txt", encoding="utf-8") as r:
    requirements = [i.strip() for i in r]

# requirements = ["redis", "hiredis", "python-decouple", "python-dotenv", "setuptools"]

with open("melvan/__init__.py", "rt", encoding="utf8") as x:
    version = re.search(r'__version__ = "(.*?)"', x.read()).group(1)

with open("melvan/__init__.py", "rt", encoding="utf8") as x:
    license = re.search(r'__license__ = "(.*?)"', x.read()).group(1)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

if len(argv) > 1 and argv[1] in ["bdist_wheel", "install", "develop"]:
    api_compiler.start()
    errors_compiler.start()


name = "Melvan"
author = "MelvanTeam"
author_email = "melvanteam@gmail.com"
description = "Melvan - Telegram MTProto API Client Library for Python."
url = "https://github.com/MelvanTeam/melvan"
project_urls = {
    "Bug Tracker": "https://github.com/MelvanTeam/melvan/issues",
    "Documentation": "https://melvanteam.tech",
    "Source Code": "https://github.com/MelvanTeam/melvan",
}
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
]

setuptools.setup(
    name=name,
    version=version,
    author=author,
    author_email=author_email,
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=url,
    project_urls=project_urls,
    license=license,
    package_data={
        "melvan": ["py.typed"],
    },
    packages=setuptools.find_packages(exclude=["compiler*", "tests*"]),
    install_requires=requirements,
    classifiers=classifiers,
    python_requires="~=3.7",
    zip_safe=False,
)
