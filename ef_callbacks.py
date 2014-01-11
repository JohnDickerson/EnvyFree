import cplex
from cplex.callbacks import BranchCallback, MIPInfoCallback


class MyTooMuchEnvyBranch(BranchCallback):

    """ Fathoms the current path if the number of unallocated items is less than
    the number of remaining envious agents (always infeasible in this case)
    """
    def __call__(self):
        if MyTooMuchEnvyBranch.should_fathom(self):
            self.times_used += 1
            self.prune()


    @staticmethod
    def should_fathom(branch):
        
        br_type = branch.get_branch_type()
        if br_type == branch.branch_type.SOS1 or br_type == branch.branch_type.SOS2:
            return False

        x = branch.get_values()
        model = branch.model

        # TBD: This is a heavyweight computation for now; look at CPLEX API
        # to figure out how to count violated constraints, since we have one
        # constraint per pairwise possible envy between two agents.
        num_envious_agents = 0
        
        # For each allocation A_i to agent i, and each allocation A_j to agent j,
        # make sure agent i values A_i at least as much as she values A_j
        for a_i in xrange(model.n):
            
            a_i_envious = False

            # Check A_i's valuation for her current allocation 
            i_indices = [a_i*model.m + j for j in xrange(model.m)]
            i_values = model.u[a_i]
            a_i_allocation_val = 0
            for item_idx, i_index in enumerate(i_indices):
                a_i_allocation_val += x[i_index] * i_values[item_idx]


            # Check if agent A_i is envious of any other agent A_j
            for a_j in xrange(model.n):

                # Agent i is not envious of her own allocation
                if a_i == a_j:
                    continue

                # Calculate A_i's valuation for A_j's current bundle
                a_j_allocation_val = 0
                j_indices = [a_j*model.m + j for j in xrange(model.m)]
                for item_idx, j_index in enumerate(j_indices):
                    a_j_allocation_val += x[j_index] * i_values[item_idx]

                # Does A_i value A_j's allocation more than her own?
                if a_i_allocation_val < a_j_allocation_val:
                    a_i_envious = True
                    break

            # If this agent is envious, count it exactly once and move on
            # to see if other agents are envious, too
            if a_i_envious:
                num_envious_agents += 1
                continue
        
        # Unallocated items = M - \sum_{all binaries}
        num_remaining_items = model.m - sum(x)

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
        
        br_type = branch.get_branch_type()
        if br_type == branch.branch_type.SOS1 or br_type == branch.branch_type.SOS2:
            return

        objval = branch.get_objective_value()

        # Branching on binary, so we force a var=1 branch with lower bound "L"=1,
        # and we force a var=0 branch with upper bound "U"=0
        #branch.make_branch(objval, variables = [(var, "L", 1)])
        #branch.make_branch(objval, variables = [(var, "U", 0)])


class MyBranchSOS1Envy(BranchCallback):
    """TBD
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


class MyTooMuchEnvyAndBranchSOS1Envy(BranchCallback):

    """ Can only register one branching rule with CPLEX, so this first
    tries to prune a path based on too much envy (MyTooMuchEnvyBranch),
    and if this fails then SOS1 branches on envious agent (MyBranchSOS1Envy)
    """
    def __call__(self):

        # Can we fathom this path?  If so, stop branching
        if MyTooMuchEnvyBranch.should_fathom(self):
            self.times_too_much_envy_used += 1
            self.prune()
            return

        # We have to keep branching; use average item value
        self.times_sos1_envy_used += 1
        MyBranchSOS1Envy.choose_branch(self)

        return



class MyMIPInfo(MIPInfoCallback):
    """ Dummy class; this is the only way I could coerce CPLEX into returning
    the number of nodes in its B&C tree.
    """
    def __call__(self):

        self.num_nodes = self.get_num_nodes()
