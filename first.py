#!/usr/bin/env python3
import math

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

print(distance((2, 1), (2, 2)))

drones_status = []
start_pos = warehouse_pos[0]
# print(start_pos)
for di in range(drone_count):
    # second param is number of turns in which drones gets to the position in first param
    status = (start_pos, 0)
    drones_status.append(status)

warehouse_status = warehouse_stock[:]
next_order = 0

# for turn in range(turns):
#     for drone_status in drones_status:
#         if drone_status[1] == 0:
#




    # print(rows, cols, drones, turns, max_payload, product_types_count)
    # print()


# for line in open("busy_day.in").readlines():
#     line = line.strip()
#
#     print(line)
