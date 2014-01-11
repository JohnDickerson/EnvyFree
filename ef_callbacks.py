import cplex
from cplex.callbacks import BranchCallback, MIPInfoCallback


class MyTooMuchEnvyBranch(BranchCallback):

    """ Fathoms the current path if the number of unallocated items is less than
    the number of remaining envious agents (always infeasible in this case)
    """    
    def __call__(self):
        if should_fathom(self):
            self.times_used += 1
            self.prune()


    @staticmethod
    def should_fathom(branch):
        
        br_type = branch.get_branch_type()
        if br_type == branch.branch_type.SOS1 or br_type == branch.branch_type.SOS2:
            return False

        num_envious_agents = 0 
        num_remaining_items = 0

        
        # Don't explore this subtree if too few items to create E-F allocation
        # (Calling neither prune() nor make_branch() --> CPLEX branches normally)
        return num_envious_agents > num_remaining_items
        

class MyBranchOnAvgItemValue(BranchCallback):

    """ Branches based on average item value (
    """    
    def __call__(self):
        
        self.times_used += 1
        choose_branch(self)

    @staticmethod
    def choose_branch(branch):
        pass


class MyTooMuchEnvyAndBranchOnAvgItemValue(BranchCallback):

    """ Can only register one branching rule with CPLEX, so this first
    tries to prune a path based on too much envy (MyTooMuchEnvyBranch),
    and if this fails then branches on item value (MyBranchOnAvgItemValue)
    """
    def __call__(self):

        # Can we fathom this path?  If so, stop branching
        if MyTooMuchEnvyBranch.should_fathom(self):
            self.times_too_much_envy_used += 1
            self.prune()
            return

        # We have to keep branching; use average item value
        self.times_branch_on_avg_item_used += 1
        MyBranchOnAvgItemValue.choose_branch(self)

        return


class MyMIPInfo(MIPInfoCallback):
    """ Dummy class; this is the only way I could coerce CPLEX into returning
    the number of nodes in its B&C tree.
    """
    def __call__(self):

        self.num_nodes = self.get_num_nodes()
