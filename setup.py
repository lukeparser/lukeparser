import codecs
import os
import re
import sys
import shutil
from pathlib import Path

from setuptools import setup, find_packages, Extension


###################################################################

NAME = "lukeparser"
PACKAGES = find_packages(where="src")
META_PATH = Path("src") / "luke" / "__init__.py"
KEYWORDS = ["markdown", "html", "latex", "parser"]
CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Natural Language :: English",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    "Programming Language :: Python",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Text Processing"
]
INSTALL_REQUIRES = [
    "pybison",
    "watchdog",
    "six",
    "tqdm",
    "tornado",
    "livereload"
]

###################################################################

HERE = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read(META_PATH)


def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__\s+=\s+['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))


# Compile the parser
# ==================
# add source root to PYTHONPATH
sys.path.insert(0, "src")

# rebuild the extension again
from luke.parser.markdown import MarkdownParser
parser = MarkdownParser(buildDirectory="build/", _buildOnlyCFiles=True, verbose=True, debug=True)
buildDir = parser.buildDirectory

extension_module = Extension(
    'luke.parser.markdown_parser',
    sources=[
        f"{buildDir}/tmp.tab.c",
        f"{buildDir}/lex.yy.c"
    ],
    headers=[
        f"{buildDir}/tmp.tab.h",
        f"{buildDir}/lex.yy.h"
    ]
)


if __name__ == "__main__":
    setup(
        name=NAME,
        description=find_meta("description"),
        license=find_meta("license"),
        url=find_meta("url"),
        version=find_meta("version"),
        author=find_meta("author"),
        maintainer=find_meta("author"),
        project_urls={
            'Documentation': find_meta('documentation'),
            'Source': find_meta("source"),
            'Tracker': find_meta("tracker"),
        },
        keywords=KEYWORDS,
        long_description_content_type="text/markdown",
        long_description=read("README.md"),
        packages=PACKAGES,
        package_dir={"": "src"},
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        entry_points={
            'console_scripts': [
                'luke = luke.luke_cli:main',
                'luke-server = luke.luke_server:main'
            ],
        },
        include_package_data=True,
        ext_modules=[extension_module],
        python_requires='>=3.7',
    )
