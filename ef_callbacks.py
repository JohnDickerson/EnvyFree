import cplex
from cplex.callbacks import BranchCallback, MIPInfoCallback
import sys

# General note [C API vs. Python API]:
# Are we indexing into the original model or the reduced/presolved model?
# "In the C++, Java, .NET, Python, and MATLAB APIs of CPLEX, only the original model is available to callbacks."
# Source: http://pic.dhe.ibm.com/infocenter/cosinfoc/v12r2/index.jsp?topic=/ilog.odms.cplex.help/Content/Optimization/Documentation/CPLEX/_pubskel/CPLEX980.html


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
        #if br_type == branch.branch_type.SOS1 or br_type == branch.branch_type.SOS2:
        #    return False
        if br_type != branch.branch_type.variable:
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
                a_i_allocation_val += (x[i_index]==1.0) * i_values[item_idx]


            # Check if agent A_i is envious of any other agent A_j
            for a_j in xrange(model.n):

                # Agent i is not envious of her own allocation
                if a_i == a_j:
                    continue

                # Calculate A_i's valuation for A_j's current bundle
                a_j_allocation_val = 0
                j_indices = [a_j*model.m + j for j in xrange(model.m)]
                for item_idx, j_index in enumerate(j_indices):
                    a_j_allocation_val += (x[j_index]==1.0) * i_values[item_idx]

                # Does A_i value A_j's allocation more than her own?
                # (CPLEX's minimum constraint violation allowance is 1e-9)
                if (a_i_allocation_val + 1e-9) < a_j_allocation_val:
                    a_i_envious = True
                    break

            # If this agent is envious, count it exactly once and move on
            # to see if other agents are envious, too
            if a_i_envious:
                num_envious_agents += 1
                continue
        
        # Unallocated items = M - \sum_{all binaries}
        allocated_items = sum([1 for assgn in x if assgn == 1.0])
        num_remaining_items = model.m - allocated_items

        fathom_subtree = (num_envious_agents > num_remaining_items)
        if fathom_subtree:
            print "Model.m={0}, sum(x)={1}, int(round(sum(x)))={2}, envy_ct={3}, firing={4}".format(model.m, sum(x), allocated_items, num_envious_agents, (num_envious_agents > num_remaining_items))

        # Don't explore this subtree if too few items to create E-F allocation
        # (Call neither prune() nor make_branch() --> CPLEX branches normally)
        return fathom_subtree
        

class MyBranchOnAvgItemValue(BranchCallback):

    """ Branches based on average item value (pick the item with the highest
    average value that isn't allocated, then branch on giving it to the agent
    that currently wants it the most.
    """    
    def __call__(self):
        
        self.times_used += 1
        MyBranchOnAvgItemValue.choose_branch(self)

    @staticmethod
    def choose_branch(branch):
        
        br_type = branch.get_branch_type()
        if br_type == branch.branch_type.SOS1 or br_type == branch.branch_type.SOS2:
            return

        objval = branch.get_objective_value()
        x = branch.get_values()

        # Get the highest average value remaining unallocated item, and branch
        # on giving that item to the agent who values it the most
        # Todo: drop from O(nm) to something lower via priority queues (maybe not worth it)
        #       or if we're SOS1ing items maybe check for inactive constraints
        max_avg_item_val = -sys.maxint - 1
        branch_var = -1
        for item_j in xrange(branch.model.m):
            
            # Figure out if item_j is allocated; if it's not allocated,
            # determine which agent_i wants it the most
            allocated = False
            max_agent_val = -sys.maxint - 1
            max_agent_cand = -1
            for agent_i in xrange(branch.model.n):            
                if int(round(x[agent_i * branch.model.n + item_j])) != 0:
                    allocated = True
                    break
                elif branch.model.u[agent_i][item_j] > max_agent_val:
                    max_agent_val = branch.model.u[agent_i][item_j]
                    max_agent_cand = agent_i

            # Branch candidate!  Is this the highest avg value unallocated item?
            if not allocated:
                if branch.model.m_avg_vals[item_j] > max_avg_item_val:
                    branch_var = max_agent_cand*branch.model.m + item_j
                    max_avg_item_val = branch.model.m_avg_vals[item_j]


        # Branching on binary, so we force a var=1 branch with lower bound "L"=1,
        # and we force a var=0 branch with upper bound "U"=0
        if branch_var >= 0:
            branch.make_branch(objval, variables = [(branch_var, "L", 1)])
            branch.make_branch(objval, variables = [(branch_var, "U", 0)])


class MyBranchSOS1Envy(BranchCallback):
    """TBD
    """

    def __call__(self):
        self.times_used += 1
        choose_branch(self)

    @staticmethod
    def choose_branch(branch):

        br_type = branch.get_branch_type()
        if br_type == branch.branch_type.SOS1 or br_type == branch.branch_type.SOS2:
            return

        # Do some stuff here someday...
        return


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
