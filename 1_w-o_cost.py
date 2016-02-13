#!/usr/bin/env python3

import itertools
import sys
import copy

from src.load_input import load_input
from src.util import distance

world, initial_state = load_input("inputs/busy_day.in")

def o_fulfilment_cost(o_fulfilment):
    cost = 0
    o, o_fulfilment = o_fulfilment

    # give me all the warehouse IDs from which this fulfilment would
    # get the product
    w_ids = [o_item_fulfilment[1] for o_item_fulfilment in o_fulfilment]

    for w_id in w_ids:
        cost += 2 * distance(initial_state.warehouses[w_id].pos, o.pos)

    return cost

def strategy_cost(strategy):
    cost = 0

    for oi, o_fulfilment in enumerate(strategy):
        o = initial_state.open_orders[oi]
        cost += o_fulfilment_cost((o, o_fulfilment))

    return cost

# first find the best allocation of items from warehouses to orders with
# intentionally ignoring drones
print("generating all the different fulfilments ...")
o_fulfilments_all = []
for oi, o in enumerate(initial_state.open_orders):
    print("starting with order " + str(oi))
    o_items_fulfilments = []

    # for every item in the order, find all of the warehouses from which
    # the item can be delivered (= fulfiled)
    temp_warehouses = copy.deepcopy(initial_state.warehouses)
    for o_item in o.items:
        o_item_fulfilments = []

        for w in temp_warehouses:
            # if the warehouse does not have any stock of that product type
            # do not add it
            if w.stock[o_item] > 0:
                o_item_fulfilments.append((o_item, w.id))
                w.stock[o_item] -= 1

        o_items_fulfilments.append(o_item_fulfilments)

    # now do cartesian product of all the item fulfilments which gives
    # us list of all the different combinations of item in order and warehouse
    # from which it will be delivered
    o_fulfilments = []
    for o_fulfilment in itertools.product(*o_items_fulfilments):
        # we need the order as first param for the cost function
        o_fulfilments.append((o, o_fulfilment))

    # now continue with not more than 5 fulfilments with the best cost,
    # because continuing with all the different combinations is too expensive
    # even for simple situations
    o_fulfilments = sorted(o_fulfilments, key=o_fulfilment_cost)
    o_fulfilments = o_fulfilments[:5]

    # print(str(oi))
    # print(str(len(o_fulfilments)))
    # for o_fulfilment in o_fulfilments:
    #     print(o_fulfilment_cost(o_fulfilment))
    #     print(o_fulfilment)

    # store just the list of fulfilments, now the order is not needed
    o_fulfilments_all.append([o_fulfilment[1] for o_fulfilment in o_fulfilments])


# and now we do cartesian product of all the different order fulfilments resulting
# in the list of all the available ways how to fulfil all the orders
print("filtering to only viable strategies ...")
viable_fulfilment_strategies = []
for fulfilment_strategy in itertools.product(*o_fulfilments_all):
    temp_warehouses = copy.deepcopy(initial_state.warehouses)
    is_viable = True

    # lets now check if the strategy is viable; because if there is
    # warehouse with 1 quantity of something, we can use it only for one order
    for oi, o_fulfilment in enumerate(fulfilment_strategy):
        for o_item_fulfilment in o_fulfilment:
            w = temp_warehouses[o_item_fulfilment[1]]

            if w.stock[o_item_fulfilment[0]] == 0:
                is_viable = False
                break

            w.stock[o_item_fulfilment[0]] -= 1

        if not is_viable:
            break

    if is_viable:
        viable_fulfilment_strategies.append(fulfilment_strategy)

# use the strategy with the minimal cost
viable_fulfilment_strategies = sorted(viable_fulfilment_strategies, key=strategy_cost)
strategy = viable_fulfilment_strategies[0]

print(strategy)
print(strategy_cost(strategy))

# execute strategy!
# print("simulating ...")
# state = initial_state
# for turn in range(world.turns):
#
#     idle_drones = [d for d in state.drones if d.turns_to_pos == 0]
#     for drone in idle_drones:
