Running on Blacklight
=====================

I've installed NumPy for Python 2.7.3, and we use the argparse library for options parsing, so we need at least Python 2.7.  Run:

    module load python/2.7.3

The NumPy install needs to be added to PYTHONPATH, too, like CPLEX:
    
    export PYTHONPATH=/usr/users/0/jpdicker/ILOG/CPLEX_Studio_AcademicResearch122/cplex/python/x86-64_sles10_4.1          
    export PYTHONPATH="${PYTHONPATH}:/usr/users/0/jpdicker/num-1.7.2/lib/python2.7/site-packages"

