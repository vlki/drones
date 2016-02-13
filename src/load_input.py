from .classes import World, State, Warehouse, Order, Drone

def load_input(input_file_path):
    world = World()

    initial_state = State()
    initial_state.turn = 0
    initial_state.warehouses = []
    initial_state.open_orders = []
    initial_state.drones = []

    with open(input_file_path) as f:
        # 1 line - general info
        world.rows, world.cols, world.d_count, world.turns, world.d_max_payload = [int(x) for x in f.readline().split()]

        # 1 line - product types count
        world.pt_count = int(f.readline())

        # 1 line - product types weights
        world.pt_weights = [int(x) for x in f.readline().split()]

        # 1 line - warehouses count
        world.w_count = int(f.readline())

        # pairs of lines - warehouses positions & stock
        for wi in range(world.w_count):
            w = Warehouse()
            w.id = wi

            x, y = [int(x) for x in f.readline().split()]
            w.pos = (x, y)

            w.stock = [int(x) for x in f.readline().split()]

            initial_state.warehouses.append(w)

        # init drones
        for di in range(world.d_count):
            d = Drone()

            # drones start at the first warehouse
            d.pos = initial_state.warehouses[0].pos

            # and they are already there, therefore they needs zero turns
            # to get to that position
            d.turns_to_pos = 0

            initial_state.drones.append(d)

        # 1 line - orders count
        o_count = int(f.readline())

        # 3 lines per order - order position, items count & items
        for ci in range(o_count):
            o = Order()

            x, y = [int(x) for x in f.readline().split()]
            o.pos = (x, y)

            # this line contains items count, we don't need that information
            # so just read the line and trash the output
            f.readline()

            o.items = [int(x) for x in f.readline().split()]

            initial_state.open_orders.append(o)

    return (world, initial_state)
