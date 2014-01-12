import random        # for uniform random
import copy          # for urn sampling
import numpy as np   # for Zipf sampling

class DupValues:
    allowed, disallowed, disallowed_max = range(3)

class DistTypes:
    urand_int, urand_real, zipf_real, polya_urn_real, correlated_real = range(5)

class ObjType:
    feasibility, social_welfare_max = range(2)

class Model:
    """Stores utility functions for each of N agents for M items"""

    def __init__(self, utilities, num_items, dist_type, dup_values):
        # raw utilities
        self.n = len(utilities)
        self.u = utilities
        self.m = num_items
        
        # Precompute statistics for branching heuristics
        self.m_avg_vals = [None]*self.m
        for j in xrange(self.m):
            item_avg = 0
            for u_list in self.u:
                item_avg += u_list[j]
            self.m_avg_vals[j] = item_avg / self.m

        # properties/settings
        self.dist_type = dist_type
        self.dup_values = dup_values
        self.obj_type = ObjType.feasibility


    @staticmethod
    def __legal_wrt_duplicates(u, dup_values):
        if dup_values == DupValues.allowed:
            # No rules on duplication; done
            return True
        elif dup_values == DupValues.disallowed:
            # No duplicate valuations AT ALL; set is all unique elements
            if len(u) == len(set(u)):
                return True
        else:
            # Only need to make sure top and second-to-top elements
            # have different valuations
            descending = sorted(u, reverse=True)
            if len(descending) > 1 and descending[0] != descending[1]:
                return True

        return False

    @staticmethod
    def generate_urand_int(num_agents, num_items, dup_values = DupValues.allowed):
        """Generates a random set of ints that sum to 10*num_items
        as utilities for num_agents agents"""

        # Each agent is given a budget of max_pts valuation points
        max_pts = 10*num_items

        # Generate random utility functions for each agent
        utilities = []
        for _ in xrange(num_agents):

            while(True):
            
                # Sample some integer values
                u = [0]
                for _ in xrange(num_items-1):
                    u.append( random.randint(0,max_pts) )
                u.append(max_pts)

                # Make sampled integer values sum to max_pts
                u = sorted(u)
                for idx, val in enumerate(u):
                    if idx==0:
                        continue
                    else:
                        u[idx-1] = u[idx]-u[idx-1]
                del u[-1]

                # Randomly distribute the sampled values to items
                random.shuffle(u)

                # Make sure utilities align with duplicate valuation allowance
                if Model.__legal_wrt_duplicates(u, dup_values):
                    break

            # Legal utility vector for agent created; record and continue
            utilities.append(u)
            


        return Model(utilities, num_items, DistTypes.urand_int, dup_values)
        

    @staticmethod
    def generate_urand_real(num_agents, num_items, dup_values = DupValues.allowed):
        """Generates a random set of reals (variable sum) as utilities
        for num_agents agents"""

        # Generate random utility functions for each agent
        utilities = []
        for _ in xrange(num_agents):
            
            while(True):
                # Sample some real [0,1] values
                u = [random.random() for _ in xrange(num_items)]

                if Model.__legal_wrt_duplicates(u, dup_values):
                    break

            utilities.append(u)
             
        return Model(utilities, num_items, DistTypes.urand_real, dup_values)
        

    @staticmethod
    def generate_zipf_real(num_agents, num_items, alpha, dup_values = DupValues.allowed):
        """Pulls real-valued utilities from a Zipf distribution with 
        parameter alpha for each of the num_agents agents"""
        
        utilities = []

        for _ in xrange(num_agents):
        
            while(True):
                # Draws num_items valuations from Zipf with parameter alpha
                u = np.random.zipf(alpha, num_items).tolist()   # Need list, not np.array for CPLEX
                if Model.__legal_wrt_duplicates(u, dup_values):
                    break

            utilities.append(u)

        return Model(utilities, num_items, DistTypes.zipf_real, dup_values)


    @staticmethod
    def generate_polya_urn_real(num_agents, num_items, param_r, param_a, add_noise = False):
        """Adapted Polya-Eggenberger urn sampling model for
        drawing correlated utility profiles
        param_r: number of "RANDOM" balls in urn at start
        param_a: number of repeat balls to add to urn at each sample"""

        # (1)  start with an urn containing a single ball called "Random".
        # (2)  For each agent, draw a ball:
        # (3.i)   If that ball is "Random": the agent's utility profile u_i is chosen u.a.r. and add the "Random" ball back into the urn along with A copies of u_i
        # (3.ii)  Else: the agent's utility profile is the ball and replace that ball and A copies of the ball.
        # We can still use the problem size-independent parameterization used by Walsh (which looks to be taken from a 2006 paper in "Group Decision and Negotiation").

        # Initially, the urn contains the single distinguished "random" ball
        random_ball = "RANDOM"
        urn = [random_ball]

        # Store chosen utility profiles for each of the agents
        utilities = []
        for _ in xrange(num_agents):

            ball = random.choice(urn)
            if ball == random_ball:
                # if the ball is random, choose a random utility profile
                u = [random.random() for _ in xrange(num_items)]

            else:
                # otherwise, the ball is our agent's utility profile
                u = copy.deepcopy(ball)
            utilities.append(u)

            # Add param_a new copies of u to the urn (possibly with some noise)
            numpy_u = np.array(u)
            for _ in xrange(param_a):
                
                if add_noise:
                    # Add u=0, stdev=noise to u, then cap utilities to min 0 and max 1
                    noisy_u = numpy_u + np.random.normal(0, 0.01, num_items)
                    noisy_u[noisy_u < 0] = 0
                    noisy_u[noisy_u > 1] = 1
                    urn.append( noisy_u.tolist() )
                else:
                    urn.append( numpy_u.tolist() )
            
        return Model(utilities, num_items, DistTypes.polya_urn_real, True)


    @staticmethod
    def generate_correlated_real(num_agents, num_items):
        """Samples a base value for each item in [0.4, 0.6], and then
        samples a value per item per agent from some normal around that
        base value for the item, with variance propto value of item"""

        # Sample means for the normal values of each item
        # means in [0.4, 0.6], stdevs from 0.2 (for u=0.4) to 0.3 (for u=0.6)
        min_mean = 0.4
        max_mean = 0.6
        min_stdev = 0.2
        max_stdev = 0.3
        base_means = []
        base_stdevs = []
        for _ in xrange(num_items):
            mu = min_mean + (max_mean-min_mean)*random.random()
            sigma = min_stdev + (max_stdev-min_stdev)*( 1.0-((max_mean-mu)/(max_mean-min_mean)) ) 
            base_means.append(mu)
            base_stdevs.append(sigma)
        base_means=np.array(base_means)
        base_stdevs=np.array(base_stdevs)
        

        # Store chosen utility profiles for each of the agents
        utilities = []
        for _ in xrange(num_agents):

            # Sample from each item's intrinsic normal, truncating utilities to [0,1]
            u = np.random.normal(base_means, base_stdevs)
            u[u < 0] = 0
            u[u > 1] = 1
            
            utilities.append(u.tolist())

        return Model(utilities, num_items, DistTypes.correlated_real, True)

