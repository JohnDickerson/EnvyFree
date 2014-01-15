import numpy as np

# Maps column indices to the data they hold
class Col:
    (seed, 
     num_threads, 
     num_agents, 
     num_items, 
     alternate_IP_model_on,
     dist_type, 
     N, 
     obj_type, 
     fathom_too_much_envy_on, fathom_too_much_envy_ct,
     branch_avg_value_on, branch_avg_value_ct,
     branch_sos1_envy_on, branch_sos1_envy_ct,
     prioritize_avg_value_on,
     feasible, 
     mip_node_count,
     build_s, 
     solve_s,
     obj_val) = range(20)


class IOUtil:
    obj_type_map = {0: "Existence", 1: "Social Welfare Max"}
    dist_type_map = {1: "U[0,1]", 4: "Correlated"}
    
    # Converts "True" or "False" to 1 or 0 integral, respectively
    @staticmethod
    def get_boolean_from_string(s):
        s.strip
        if s.upper() == "TRUE" or s.upper() == "T":
            return 1.
        else:
            return 0.  # If we can't understand it, return false

    @staticmethod
    def load(filename_data):
        # Load all the data at once
        print 'Loading data from ' + filename_data
        data = np.genfromtxt(filename_data, 
                             delimiter=',', 
                             skiprows=0,
                             converters={
                Col.alternate_IP_model_on: IOUtil.get_boolean_from_string,
                Col.feasible: IOUtil.get_boolean_from_string,
                Col.fathom_too_much_envy_on: IOUtil.get_boolean_from_string,
                Col.branch_avg_value_on: IOUtil.get_boolean_from_string,
                Col.branch_sos1_envy_on: IOUtil.get_boolean_from_string,
                Col.prioritize_avg_value_on: IOUtil.get_boolean_from_string,
                                         }, 
                             )
        print 'Loaded ' + str(len(data)) + ' rows of data.'
        return data
