
def max_contested_feasible(model):
    """If for each item $j \in [M'] \subseteq [M]$ there are $k_j > 0$ agents 
    who want it the most, then any envy-free allocation needs at least 
    $\sum_j (2k_j-1) < 2N$ items assigned to the $M'$ agents.  This leads to 
    a very loose sufficient criterion for infeasibility: 
    if $M < \sum_j (2k_j-1)$, then no envy-free allocation exists."""

    conflict_counts = {}

    # Determine contested items, and how many agents contest each item
    for u in model.u:
        max_idx = max(enumerate(u),key=lambda idx_val_pair: idx_val_pair[1])[0]
        if max_idx not in conflict_counts:
            conflict_counts[max_idx] = 1
        else:
            conflict_counts[max_idx] += 1

    # \sum_j 2k_j - 1     for any item j with k_j > 1 conflicts
    min_item_ct = 0
    for item, conflict_count in conflict_counts.items():
        min_item_ct += 2*conflict_count - 1   # works for k_j = 1, too
    
    #print "#Items: {0}, #Min Items: {1}".format(model.m, min_item_ct)

    # If we don't have enough items to go around, no E-F solution can exist
    if model.m < min_item_ct:
        return False

    return True
