# utility functions usable anywhere

import math

# returns distance between two given positions
def distance(a_pos, b_pos):
    return math.ceil(math.sqrt((a_pos[0] - b_pos[0]) ** 2 + (a_pos[1] - b_pos[1]) ** 2))
