import cplex
from cplex.callbacks import BranchCallback


class MyTooMuchEnvyCut(BranchCallback):

    """ Fathoms the current path if the number of unallocated items is less than
    the number of remaining envious agents (always infeasible in this case)
    """    
    def __call__(self):
        
        self.times_called += 1
        
        num_envious_agents = 0 
        num_remaining_items = 0


        # Don't explore this subtree if too few items to create E-F allocation
        # (Calling neither prune() nor make_branch() --> CPLEX branches normally)
        if num_envious_agents > num_remaining_items:
            self.prune()
        else:
            return



class MyBranchOnAvgItemValue(BranchCallback):

    """ Branches based on average item value (
    """    
    def __call__(self):
        
        self.times_called += 1
    
