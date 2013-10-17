import random

class Model:
    """Stores utility functions for each of N agents for M items"""

    def __init__(self, utilities, num_items):
        self.n = len(utilities)
        self.u = utilities
        self.m = num_items

    @staticmethod
    def generate(num_agents, num_items):

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
        
