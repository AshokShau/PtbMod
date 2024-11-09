import os
from typing import Dict

from setuptools import setup, find_packages

base_path = os.path.abspath(os.path.dirname(__file__))

about: Dict = {}

with open(
        os.path.join(
            base_path,
            'ptbmod',
            '__version__.py',
        ), encoding='utf-8',
) as f:
    exec(f.read(), about)

DESCRIPTION = 'Patch for python-telegram-bot providing decorator support for easy command handling and admin verification.'
with open("README.md", encoding="utf8") as readme:
    long_description = readme.read()

setup(
    name="ptbmod",
    version=about["__version__"],
    author="AshokShau (Ashok)",
    author_email="<abishnoi69@outlook.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
    ],
    extras_require={
        'all': [
            'python-telegram-bot[callback-data]',
        ],
    },
    keywords="telegram telegram-bot bot python-telegram-bot decorators command handling admin verification",
    url="https://github.com/AshokShau/ptbmod",
    download_url="https://github.com/AshokShau/ptbmod/releases/latest",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    project_urls={
        "Tracker": "https://github.com/AshokShau/ptbmod/issues",
        "Community": "https://t.me/GuardxSupport",
        "Source": "https://github.com/AshokShau/ptbmod",
        "Documentation": "https://t.me/GuardxSupport",
    },
    python_requires=">=3.8",
)
