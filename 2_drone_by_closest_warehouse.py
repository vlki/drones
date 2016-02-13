#!/usr/bin/env python3

import itertools
import sys
import copy
import math

from src.load_input import load_input
from src.util import distance, find_closest_nonempty_warehouses
from src.output import Output

if len(sys.argv) != 3:
    print("invalid number of params")
    print("run as: ./script input_file.in output_file.out")
    sys.exit(1)

world, initial_state = load_input(sys.argv[1])


# this is the function which is called anytime drone is idle and
# it decides what the drone will do next
#
# the idea behind this implementation is to find closest non-empty
# warehouse to drone which can deliver something for any order
# and find order which can be ideally fully
# delivered from this warehouse or order for which the drone can
# be fully loaded
def find_drone_action(state, d):
    if len(state.warehouses) == 1:
        # optimalization for scenario when there is just one warehouse
        closest_warehouses = state.warehouses[:]
    else:
        closest_warehouses = find_closest_nonempty_warehouses(state, d)

    for w in closest_warehouses:
        action = find_drone_action_for_warehouse(state, d, w)
        if action != None:
            return action

    return None

def find_drone_action_for_warehouse(state, d, w):
    o_deliverable_fully = []
    o_other = []

    for o in state.open_orders:
        if o.delivered():
            continue

        o_deliverable_weight = 0
        o_deliverable_items = []
        o_undeliverable_weight = 0

        # lets create copy of warehouse so we can check that the stock
        # is enough
        temp_w = copy.deepcopy(w)

        for item in o.items:
            if o.delivered():
                continue

            if item.delivered:
                continue

            pt_weight = world.pt_weights[item.pt_id]

            if temp_w.stock[item.pt_id] > 0:
                # item in warehouse stock
                temp_w.stock[item.pt_id] -= 1
                o_deliverable_weight += pt_weight
                o_deliverable_items.append(item)
            else:
                # item not in warehouse stock
                o_undeliverable_weight += pt_weight

        # print('@')
        # print(str(o.id))
        # print(str(o_deliverable_weight))
        # print((o_undeliverable_weight == 0 and o_deliverable_weight < world.d_max_payload))

        if o_deliverable_weight == 0:
            # nothing in this warehouse for the order
            pass
        elif o_undeliverable_weight == 0 and o_deliverable_weight < world.d_max_payload:
            # lets log orders which we can fully deliver from this warehouse
            # by just one drone flight
            o_deliverable_fully.append(o)
        else:
            o_other.append((o, o_deliverable_items, o_deliverable_weight, o_undeliverable_weight))

    # if there are some orders which can be delivered fully, do that!
    if len(o_deliverable_fully) > 0:
        o_deliverable_fully.sort(key = lambda o: distance(o.pos, d.pos))
        o = o_deliverable_fully[0]
        return (w, o, [i for i in o.items if not i.delivered])

    if len(o_other) == 0:
        # there is no order, we got it all!
        return None

    # otherwise find the order with lowest deliverable weight
    o_other.sort(key = lambda x: x[2])
    o, o_deliverable_items, a, b = o_other[0]

    # and limit the number of items based on max payload
    deliver_items = []
    deliver_weight = 0
    for item in o_deliverable_items:
        pt_weight = world.pt_weights[item.pt_id]
        if (deliver_weight + pt_weight) <= world.d_max_payload:
            deliver_items.append(item)
            deliver_weight += pt_weight

    return (w, o, deliver_items)

output = Output(sys.argv[2])
state = copy.deepcopy(initial_state)
for turn in range(world.turns):
    print("-- starting turn " + str(turn))

    idle_drones = [d for d in state.drones if d.turns_to_pos == 0]

    for d in idle_drones:
        # find action to do
        action = find_drone_action(state, d)

        if action == None:
            continue

        w, o, items_to_deliver = action

        # print("  # action")
        # print(items_to_deliver)

        turns_till_idle_again = 0

        # drone has to get to the warehouse first
        turns_till_idle_again += distance(d.pos, w.pos)
        print("  * sending drone " + str(d.id) + " to warehouse " + str(w.id) +  " at " + str(w.pos[0]) + "-" + str(w.pos[1]) + " (distance: " + str(distance(d.pos, w.pos)) + ")")

        # load stuff from warehouse
        for item in items_to_deliver:
            output.load(d.id, w.id, item.pt_id, 1)
            print("  * loading drone " + str(d.id) + " with product " + str(item.pt_id))

            # every load command takes one turn
            turns_till_idle_again += 1

        # drone has to get to order
        turns_till_idle_again += distance(w.pos, o.pos)
        print("  * sending drone " + str(d.id) + " to order " + str(o.id) + " pos " + str(o.pos[0]) + "-" + str(o.pos[1]) + " (distance: " + str(distance(w.pos, o.pos)) + ")")

        # drone has to unload
        for item in items_to_deliver:
            output.deliver(d.id, o.id, item.pt_id, 1)
            print("  * unloading drone " + str(d.id) + " with product " + str(item.pt_id))

            # every deliver command takes one turn
            turns_till_idle_again += 1

            item.delivered = True

        if o.delivered():
            delivered_orders = [o for o in state.open_orders if o.delivered()]
            print("  # delivered " + str(len(delivered_orders)) + " out of " + str(len(state.open_orders)) + " orders")

            if len(delivered_orders) == len(state.open_orders):
                print("end, no more orders!")
                output.write_to_file()
                sys.exit(0)

        d.pos = copy.deepcopy(o.pos)
        d.turns_to_pos = turns_till_idle_again

    for d in state.drones:
        if d.turns_to_pos > 0:
            d.turns_to_pos = d.turns_to_pos - 1

print("end, no more turns!")
output.write_to_file()
sys.exit(0)
