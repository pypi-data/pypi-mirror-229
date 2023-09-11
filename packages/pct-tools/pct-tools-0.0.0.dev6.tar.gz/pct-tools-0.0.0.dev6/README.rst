=================
pct-tools — Tools for proton CT image reconstruction
=================

|PyPI package|

This Python package contains tools used in proton CT image reconstructions. They may come in handy when dealing with very large and sparse system matrices.

It consists of two parts: `pct-tools` is a Python wrapper around the C++ extension `pct-tools-ext` built using pybind11_.



=================
Installation
=================
The package is pre-built for several platforms and available via PyPI_: ::

   pip install pct-tools


If the package isn't available for your platform, follow the steps below to compile locally after cloning the repository.

-----------------
Build c-blosc2
-----------------
::

   git clone https://github.com/Blosc/c-blosc2
   cd c-blosc2
   mkdir build
   cd build
   cmake -DCMAKE_INSTALL_PREFIX=path/to/pct-tools/internal/blosc2 ..
   cmake --build . --parallel 8
   ctest
   cmake --build . --target install  --parallel 8

-----------------
Build pct-tools
-----------------
::

   pip install -r dev-requirements.txt
   pip install .


.. |PyPI package| image:: https://img.shields.io/pypi/v/pct-tools.svg
   :target: https://pypi.org/project/pct-tools/

.. _pybind11: https://pybind11.readthedocs.io/en/stable
.. _PyPI: https://pypi.org/project/pct-tools