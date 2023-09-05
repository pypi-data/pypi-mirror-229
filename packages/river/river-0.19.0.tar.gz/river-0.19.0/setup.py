from __future__ import annotations

import io
import os
import platform
import subprocess
import sys

import setuptools  # type: ignore
from setuptools_rust import Binding, RustExtension  # type: ignore

try:
    from numpy import __version__ as numpy_version
    from numpy import get_include
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    from numpy import __version__ as numpy_version
    from numpy import get_include

try:
    from Cython.Build import cythonize
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Cython"])
    from Cython.Build import cythonize  # type: ignore

NAME = "river"
DESCRIPTION = "Online machine learning in Python"
LONG_DESCRIPTION_CONTENT_TYPE = "text/markdown"
URL = "https://github.com/online-ml/river"
EMAIL = "maxhalford25@gmail.com"
AUTHOR = "Max Halford"
REQUIRES_PYTHON = ">=3.8.0"

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

about: dict = {}
with open(os.path.join(here, NAME, "__version__.py")) as f:
    exec(f.read(), about)

setuptools.setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=setuptools.find_packages(exclude=("tests",)),
    install_requires=(base_packages := [f"numpy>={numpy_version}", "scipy>=1.5", "pandas>=1.3"]),
    extras_require={
        "dev": base_packages
        + [
            "black>=22.1.0",
            "graphviz>=0.10.1",
            "gym>=0.26.1",
            "matplotlib>=3.0.2",
            "mypy>=0.980",
            "pre-commit>=2.9.2",
            "pytest>=4.5.0",
            "ruff>=0.0.213",
            "scikit-learn>=1.0.1",
            "sqlalchemy>=2.0.0",
            "sympy>=1.10.1",
        ],
        "compat": base_packages
        + [
            "scikit-learn",
            "sqlalchemy>=2.0.0",
            "vaex",
        ],
        "docs": base_packages
        + [
            "dominate",
            "flask",
            "ipykernel",
            "jupyter-client",
            "mike",
            "mkdocs",
            "mkdocs-awesome-pages-plugin",
            "mkdocs-charts-plugin",
            "mkdocs-material",
            "nbconvert",
            "numpydoc",
            "python-slugify",
            "spacy",
            "tabulate",
            "watermark",
        ],
        "extra": ["river_extra"],
        "deep": ["deep-river"],
        "torch": ["river_torch"],
        "benchmark": base_packages
        + [
            "scikit-learn==1.1.2",
            "scipy==1.9.3",
            "torch==1.13.0",
            "vowpalwabbit==9.6.0",
            "torch==1.13.0",
            "dominate==2.7.0",
            "slugify==0.0.1",
            "watermark==2.3.1",
            "river-torch==0.1.2",
        ],
        ":python_version == '3.6'": ["dataclasses"],
    },
    include_package_data=True,
    license="BSD-3",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    ext_modules=cythonize(
        module_list=[
            setuptools.Extension(
                "*",
                sources=["**/*.pyx"],
                include_dirs=[get_include()],
                libraries=[] if platform.system() == "Windows" else ["m"],
                define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
            )
        ],
        compiler_directives={
            "language_level": 3,
            "binding": True,
            "embedsignature": True,
        },
    ),
    rust_extensions=[RustExtension("river.stats._rust_stats", binding=Binding.PyO3)],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)
