
# World contains all the static information which does not change
# during the simulation
class World:
    def __init__(self):
        self.rows = None
        self.cols = None
        self.turns = None
        self.d_count = None
        self.d_max_payload = None
        self.pt_count = None
        self.pt_weights = None
        self.w_count = None

    def __str__(self):
        return """World:
    rows: %s
    cols: %s
    turns: %s
    d_count: %s
    d_max_payload: %s
    pt_count: %s
    pt_weights: %s
    w_count: %s""" % (
        self.rows,
        self.cols,
        self.turns,
        self.d_count,
        self.d_max_payload,
        self.pt_count,
        self.pt_weights,
        self.w_count)

# State contains all the information which changes during simulation
class State:
    def __init__(self):
        self.turn = 0
        self.warehouses = None
        self.open_orders = None
        self.drones = None

    def __str__(self):
        return """State:
    turn: {}
    warehouses:
        {}
    open_orders:
        {}
    drones:
        {}""".format(
        self.turn,
        [str(w) for w in self.warehouses],
        [str(o) for o in self.open_orders],
        [str(d) for d in self.drones])

class Warehouse:
    def __init__(self):
        self.pos = None
        self.stock = None

    def __str__(self):
        return "w%s%s" % (self.pos, self.stock)

class Order:
    def __init__(self):
        self.pos = None
        self.items = None

    def __str__(self):
        return "o%s%s" % (self.pos, self.items)

class Drone:
    def __init__(self):
        self.pos = None
        self.turns_to_pos = None

    def __str__(self):
        return "d%s(%s)" % (self.pos, self.turns_to_pos)
