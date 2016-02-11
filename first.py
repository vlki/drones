#!/usr/bin/env python3
import math
import itertools

out = []

def out_action(action, a, b, c, d):
    out.append(str(a) + " " + action + " " + str(b) + " " + str(c) + " " + str(d))

def out_load(d_id, w_id, p_id, p_qty):
    out_action("L", d_id, w_id, p_id, p_qty)

def out_unload(d_id, w_id, p_id, p_qty):
    out_action("U", d_id, w_id, p_id, p_qty)

def out_deliver(d_id, o_id, p_id, p_qty):
    out_action("D", d_id, o_id, p_id, p_qty)

def out_wait(d_id, turns):
    out.append(str(d_id) + " W " + str(turns))

with open("busy_day.in") as f:
    rows, cols, drone_count, turns, max_payload = [int(x) for x in f.readline().split()]

    product_types_count = int(f.readline())
    product_types_weights = [int(x) for x in f.readline().split()]
    assert(len(product_types_weights) == product_types_count)

    warehouse_count = int(f.readline())
    warehouses = []

    for wi in range(warehouse_count):
        x, y = [int(x) for x in f.readline().split()]
        # warehouse_pos.append((x, y))

        stocks = [int(x) for x in f.readline().split()]
        # warehouse_stock.append(stocks)

        warehouses.append(((x, y), stocks))

    order_count = int(f.readline())
    # order_pos = []
    # order_items = []
    orders = []

    for ci in range(order_count):
        x, y = [int(x) for x in f.readline().split()]
        # order_pos.append((x, y))

        # not using this :)
        order_items_count = int(f.readline())

        items = [int(x) for x in f.readline().split()]
        # order_items.append([int(x) for x in f.readline().split()])
        orders.append(((x, y), items))
        # assert(len(order_items[ci]) == order_items_count)

    # assert(len(order_pos) == order_count)
    # assert(len(order_items) == order_count)

    print("drone_count: " + str(drone_count))
    print("warehouse_count: " + str(warehouse_count))
    print("order_count: " + str(order_count))

def distance(origin, dest):
    return math.ceil(math.sqrt((origin[0] - dest[0]) ** 2 + (origin[1] - dest[1]) ** 2))


def cost(o_pos, o_items, d_pos, d_load, w_pos, w_stock, p_weights):
    c = 0
    stock_punishment = 10
    weight_punishment = 10

    o_w_dist = distance(o_pos, w_pos)
    d_w_dist = distance(d_pos, w_pos)

    o_weight = 0
    for o_item in o_items:
        o_weight += p_weights[o_item]

    if o_weight > d_load:
        c += weight_punishment * (o_weight / d_load)

    w_stock_working = w_stock[:]
    for o_item in o_items:
        if w_stock_working[o_item] > 0:
            w_stock_working[o_item] -= 1
        else:
            c += stock_punishment

    return c + o_w_dist + d_w_dist

# print(distance((2, 1), (2, 2)))

drones_status = []
start_pos = warehouses[0][0]
# print(start_pos)
for di in range(drone_count):
    # second param is number of turns in which drones gets to the position in first param
    status = (start_pos, 0)
    drones_status.append(status)

warehouses_status = warehouses[:]

orders_status = []
# order items are sorted by increasing weight
for pos, items in [(pos, sorted(o, key=lambda x: product_types_weights[x])) for (pos, o) in orders]:
    orders_status.append((pos, items, False))

next_order = 0

def find_closest_warehouse_with_items(origin, items):
    min_distance = math.inf
    min_distance_wh_index = None
    for warehouse_index, warehouse_status in enumerate(warehouses_status):
        wh_has_items = True
        wh_distance = distance(origin, warehouse_pos[warehouse_index])

        temp_warehouse_status = warehouse_status[:]
        for item in items:
            temp_warehouse_status[item] -= 1

        for item_stock in temp_warehouse_status:
            if item_stock < 0:
                wh_has_items = False

        if wh_has_items and wh_distance < min_distance:
            min_distance = wh_distance
            min_distance_wh_index = warehouse_index

    # if min_distance_wh_index == None:
    #     print(str(items))
    # assert(min_distance_wh_index != None)
    return min_distance_wh_index

def allocate_items_from_warehouse(w_index, o_items):
    for item in o_items:
        warehouses_status[w_index][1][item] -= 1

def drone_is_idle(drone):
    # (position, left_moving_steps)
    return drone[1] == 0

def possible_moves(drones, orders, warehouses):
    for di, drone in enumerate([d for d in drones_status if drone_is_idle(d)]):
        for oi, order in enumerate([o for o in orders if (o[2] == False)]):
            for wi, warehouse in enumerate(warehouses):
                yield (di, oi, wi)

# split order, take as many items as possible
# expected items are in increasing weight order
def split_order(order, warehouse):
    o_pos, o_items = order
    w_pos, w_items = warehouse
    w_items = w_items[:]

    # select available items that will fit in

    total = 0
    take = []
    keep = []

    for ii in o_items:
        ii_weight = product_types_weights[ii]
        if ii in w_items and (total + ii_weight <= max_payload):
            total += ii_weight
            w_items.remove(ii)
            take.append(ii)
        else:
            keep.append(ii)

    return ((o_pos, take), (o_pos, keep))

def is_executable(drone, order, warehouse):
    o_items = order[1]
    w_stock = warehouse[1]

    o_weight = 0
    for o_item in o_items:
        o_weight += product_types_weights[o_item]

        if o_weight > max_payload:
            return False

    # TODO: maybe just one loop
    w_stock_working = w_stock[:]
    for o_item in o_items:
        if w_stock_working[o_item] > 0:
            w_stock_working[o_item] -= 1
        else:
            return False

    return True

for turn in range(turns):
    print("-- starting turn " + str(turn))

    costs = []
    for di, oi, wi in possible_moves(drones_status, orders_status, warehouses_status):
        c = cost(orders_status[oi][0], orders_status[oi][1], drones_status[di][0], max_payload, warehouses_status[wi][0], warehouses_status[wi][1], product_types_weights)
        costs.append((di, oi, wi, c))

    print("costs len: " + str(len(costs)))

    costs.sort(key=lambda cc: cc[3])

    for di, oi, wi, c in costs:
        if is_executable(drones_status[di], orders_status[oi], warehouses_status[wi]) and drones_status[di][1] == 0 and orders_status[oi][2] == False:
            drone = drones_status[di]
            order = orders_status[oi]
            warehouse = warehouses_status[wi]

            # get to closest warehouse and get stuff
            drone_turn_distance = distance(drone[0], warehouse[0])
            print("to wh: sending drone " + str(di) + " from " + str(drone[0][0]) + "-" + str(drone[0][1]) + " to " + str(warehouse[0][0]) + "-" + str(warehouse[0][1]) + " (distance " + str(distance(drone[0], warehouse[0])) + ")")

            for p_id in order[1]:
                out_load(di, wi, p_id, 1)

            # load stuff in warehouse
            drone_turn_distance += 1

            for p_id in order[1]:
                out_deliver(di, wi, p_id, 1)

            # travel to order pos
            drone_turn_distance = distance(warehouse[0], order[0])
            print("from wh: sending drone " + str(di) + " from " + str(warehouse[0][0]) + "-" + str(warehouse[0][1]) + " to " + str(order[0][0]) + "-" + str(order[0][1]) + " (distance " + str(distance(warehouse[0], order[0])) + ")")

            # set the end position and when can we expect drone there
            drones_status[di] = (order[0], drone_turn_distance)

            allocate_items_from_warehouse(wi, order[1])
            orders_status[oi] = (orders_status[oi][0], orders_status[oi][1], True)

    break;

    for di, drone in enumerate(drones_status):
        if drones_status[di][1] == 0:
            # means that there was no executable action for this drone, wait at this location
            print("boo")
        else:
            drones_status[di] = (drones_status[di][0], drones_status[di][1] - 1)

        print("drone " + str(di) + ", time to target " + str(drones_status[di][1]))




    # print(rows, cols, drones, turns, max_payload, product_types_count)
    # print()


# for line in open("busy_day.in").readlines():
#     line = line.strip()
#
#     print(line)

# out_load(1, 2, 3, 1)
# out_unload(1, 2, 3, 1)
# out_deliver(1, 2, 3, 1)
# out_wait(1, 2)

with open("busy_day.out", "w") as f:
    out.insert(0, str(len(out)))
    f.write("\n".join(out))
