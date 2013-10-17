EnvyFree
========

Computes envy-free allocations of items to agents.


External Dependencies
=====================
The `allocator` module uses [CPLEX](http://www-01.ibm.com/software/commerce/optimization/cplex-optimizer/), so you will need to install it.  IBM offers a free license via its [Academic Initiative](http://www-03.ibm.com/ibm/university/academic/pub/page/academic_initiative).


Troubleshooting
===============

If you receive a `no module named cplex` error, set the `PYTHONPATH` environmental variable to search for CPLEX in your install directory.  For example:

    export PYTHONPATH="/my/path/to/CPLEX/cplex/python/x86_darwin9_gcc4.0:$PYTHONPATH"

If you are running Mac OS X 10.6+, you need to run Python as a 32-bit application (as opposed to the default 64-bit version), since the CPLEX Python connector currently only exists in 32-bit.  Try running the following:

    VERSIONER_PYTHON_PREFER_32_BIT=yes python driver.py
