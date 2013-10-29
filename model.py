import random        # for uniform random
import numpy as np   # for Zipf sampling

class Model:
    """Stores utility functions for each of N agents for M items"""

    def __init__(self, utilities, num_items):
        self.n = len(utilities)
        self.u = utilities
        self.m = num_items

    @staticmethod
    def generate_urand_int(num_agents, num_items):
        """Generates a random set of ints that sum to 10*num_items
        as utilities for num_agents agents"""

        # Each agent is given a budget of max_pts valuation points
        max_pts = 10*num_items

        # Generate random utility functions for each agent
        utilities = []
        for _ in xrange(num_agents):
            
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
            
            utilities.append(u)
             

        return Model(utilities, num_items)
        

    @staticmethod
    def generate_urand_real(num_agents, num_items):
        """Generates a random set of reals (variable sum) as utilities
        for num_agents agents"""

        # Generate random utility functions for each agent
        utilities = []
        for _ in xrange(num_agents):
            
            # Sample some integer values
            u = [random.random() for _ in xrange(num_items)]            
            utilities.append(u)
             
        return Model(utilities, num_items)
        

    @staticmethod
    def generate_zipf_real(num_agents, num_items, alpha):
        """Pulls real-valued utilities from a Zipf distribution with 
        parameter alpha for each of the num_agents agents"""
        
        utilities = []

        for _ in xrange(num_agents):
        
            # Draws num_items valuations from Zipf with parameter alpha
            u = np.random.zipf(alpha, num_items).tolist()   # Need list, not np.array for CPLEX

            utilities.append(u)

        return Model(utilities, num_items)
