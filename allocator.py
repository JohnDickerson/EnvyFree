import cplex
from cplex.exceptions import CplexError

class DoesNotExistException(Exception):
    pass

def allocate(model):

    try:
        my_prob = cplex.Cplex()

    except CplexError, ex:
        print ex
        return


