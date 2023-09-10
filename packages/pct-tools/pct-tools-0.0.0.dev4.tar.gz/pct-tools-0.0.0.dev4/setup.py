import sys
from glob import glob

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import find_packages, setup

__version__ = "0.0.0.dev4"


if sys.platform == "darwin":
    blosc_lib_path = "internal/blosc2/lib/libblosc2.a"
else:
    blosc_lib_path = "internal/blosc2/lib64/libblosc2.a"

ext_modules = [
    Pybind11Extension(
        "pct_tools_ext",
        sorted(glob("pct_tools_ext/src/*")),
        include_dirs=sorted(glob("pct_tools_ext/include"))
        + ["internal/eigen3/include/eigen3"]
        + ["internal/blosc2/include"],
        extra_compile_args=["-O3", "-std=c++11", "-fopenmp"],
        extra_link_args=["-fopenmp", "-lz"],
        extra_objects=[blosc_lib_path],
    ),
]

setup(
    name="pct-tools",
    version=__version__,
    author="Matthieu",
    author_email="m.hentz@outlook.com",
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=["numpy>=1.24.0", "scipy>=1.10.0"],
)
