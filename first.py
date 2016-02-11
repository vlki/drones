#!/usr/bin/env python3
import math
import itertools

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

# order items are sorted by increasing weight
orders_status = [(pos, sorted(o, key=lambda x: product_types_weights[x])) for (pos, o) in orders]

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
        warehouses_status[w_index][item] -= 1

def drone_is_idle(drone):
    # (position, left_moving_steps)
    return drone[1] == 0

def possible_moves(drones, orders, warehouses):
    for di, drone in enumerate([d for d in drones if drone_is_idle(d)]):
        for oi, order in enumerate(orders):
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

for turn in range(turns):
    print("-- starting turn " + str(turn))

    costs = []
    for di, oi, wi in possible_moves(drones_status, orders_status, warehouses_status):
        c = cost(orders_status[oi][0], orders_status[oi][1], drones_status[di][0], max_payload, warehouses_status[wi][0], warehouses_status[wi][1], product_types_weights)
        costs.append(((di, oi, wi), c))
        print(c)

    break


    for drone_index, drone_status in enumerate(drones_status):
        if drone_status[1] == 0:
            drone_turn_start_pos = drone_status[0]
            drone_turn_order_pos = order_pos[next_order]

            while True:
                drone_turn_order_items = order_items[next_order]
                closest_wh_index = find_closest_warehouse_with_items(drone_turn_start_pos, drone_turn_order_items)

                if closest_wh_index == None:
                    print("skipping order")
                    next_order += 1
                else:
                    break

            allocate_items_from_warehouse(closest_wh_index, items)

            closest_wh_pos = warehouse_pos[closest_wh_index]

            # get to closest warehouse and get stuff
            drone_turn_distance = distance(drone_turn_start_pos, closest_wh_pos)
            print("to wh: sending drone " + str(drone_index) + " from " + str(drone_turn_start_pos[0]) + "-" + str(drone_turn_start_pos[1]) + " to " + str(closest_wh_pos[0]) + "-" + str(closest_wh_pos[1]) + " (distance " + str(distance(drone_turn_start_pos, closest_wh_pos)) + ")")

            # load stuff in warehouse
            drone_turn_distance += 1

            # travel to order pos
            drone_turn_distance = distance(closest_wh_pos, drone_turn_order_pos)
            print("from wh: sending drone " + str(drone_index) + " from " + str(drone_turn_start_pos[0]) + "-" + str(closest_wh_pos[1]) + " to " + str(closest_wh_pos[0]) + "-" + str(drone_turn_order_pos[1]) + " (distance " + str(distance(closest_wh_pos, drone_turn_order_pos)) + ")")

            # set the end position and when can we expect drone there
            drones_status[drone_index] = (drone_turn_order_pos, drone_turn_distance)

            next_order += 1

            # do not plan next drone -> break
            if next_order == order_count:
                break

        drones_status[drone_index] = (drones_status[drone_index][0], drones_status[drone_index][1] - 1)

    # do not follow with any turns -> break
    if next_order == order_count:
        break




    # print(rows, cols, drones, turns, max_payload, product_types_count)
    # print()


# for line in open("busy_day.in").readlines():
#     line = line.strip()
#
#     print(line)
