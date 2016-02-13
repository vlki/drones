# utility functions usable anywhere

import math

# returns distance between two given positions
def distance(a_pos, b_pos):
    return math.ceil(math.sqrt((a_pos[0] - b_pos[0]) ** 2 + (a_pos[1] - b_pos[1]) ** 2))

def find_closest_nonempty_warehouses(state, d):
    w_distances = [(w, distance(w.pos, d.pos)) for w in state.warehouses if w.is_not_empty()]
    w_distances.sort(key = lambda x: x[1])
    return [x[0] for x in w_distances]
