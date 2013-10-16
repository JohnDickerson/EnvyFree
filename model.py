import random

class Model:
    """Stores utility functions for each of N agents for M items"""

    def __init__(self, utilities, num_items):
        self.n = len(utilities)
        self.u = utilities
        self.m = num_items

    @staticmethod
    def generate(num_agents, num_items):
        
        # Generate random utility functions for each agent
        utilities = []
        for _ in range(num_agents):
            
            # Sample some integer values
            u = []
            
            # Randomly distribute the sampled values to items
            random.shuffle(u)

            utilities.append(u)


        return Model(utilities, num_items)
        
