#!/usr/bin/env python3
import math
import itertools

with open("busy_day.in") as f:
    rows, cols, drone_count, turns, max_payload = [int(x) for x in f.readline().split()]

    product_types_count = int(f.readline())
    product_types_weights = [int(x) for x in f.readline().split()]
    assert(len(product_types_weights) == product_types_count)

    warehouse_count = int(f.readline())
    warehouse_pos = []
    warehouse_stock = []

    for wi in range(warehouse_count):
        x, y = [int(x) for x in f.readline().split()]
        warehouse_pos.append((x, y))

        stocks = [int(x) for x in f.readline().split()]
        warehouse_stock.append(stocks)

    order_count = int(f.readline())
    order_pos = []
    order_items = []

    for ci in range(order_count):
        x, y = [int(x) for x in f.readline().split()]
        order_pos.append((x, y))

        # not using this :)
        order_items_count = int(f.readline())

        order_items.append([int(x) for x in f.readline().split()])
        assert(len(order_items[ci]) == order_items_count)

    assert(len(order_pos) == order_count)
    assert(len(order_items) == order_count)

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
start_pos = warehouse_pos[0]
# print(start_pos)
for di in range(drone_count):
    # second param is number of turns in which drones gets to the position in first param
    status = (start_pos, 0)
    drones_status.append(status)

warehouses_status = warehouse_stock[:]
next_order = 0
#
# def find_closest_warehouse_with_items(origin, items):
#     for warehouse_index, warehouse_status in enumerate(warehouses_status):
#         wh_has_items = true
#         wh_distance = distance(warehouse_pos, warehouse_status)
#         for items

def drone_is_idle(drone):
    # (position, left_moving_steps)
    return drone[1] == 0

def possible_moves(drones, orders, warehouses):
    for di, drone in enumerate([d for d in drones if drone_is_idle(d)]):
        for oi, order in enumerate(orders):
            for wi, warehouse in enumerate(warehouses):
                yield (di, oi, wi)

for turn in range(turns):
    print("-- starting turn " + str(turn))
    for drone_index, drone_status in enumerate(drones_status):
        if drone_status[1] == 0:
            drone_turn_start_pos = drone_status[0]
            drone_turn_order_pos = order_pos[next_order]

            # drone_turn_order_items = order_items[next_order]
            # find_closest_warehouse_with_items(drone_turn_start_pos, drone_turn_order_items)

            # TODO: find warehouse where to get stuff
            drone_turn_distance = 0

            # load stuff in warehouse
            drone_turn_distance += 1

            # travel to order pos
            drone_turn_distance = distance(drone_turn_start_pos, drone_turn_order_pos)
            print("sending drone " + str(drone_index) + " from " + str(drone_turn_start_pos[0]) + "-" + str(drone_turn_start_pos[1]) + " to " + str(drone_turn_order_pos[0]) + "-" + str(drone_turn_order_pos[1]) + " (distance " + str(drone_turn_distance) + ")")

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
