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

##########################################################
# here follows the scripts this strategy is using

class Route:
    def __init__(self):
        self.w_id = None
        self.w = None
        self.o_id = None
        self.o = None
        self.items = None
        self.weight = None

class RoutesChunk:
    def __init__(self):
        self.w = None
        self.routes = []
        self.weight = 0

def warehouses_closest_first(warehouses, o_pos):
    return sorted(warehouses, key = lambda w: distance(w.pos, o_pos))

def orders_most_items_first(orders):
    return sorted(orders, key = lambda o: len(o.items), reverse = True)

def weight_of_item(item, world):
    return world.pt_weights[item.pt_id]

def sorted_items_heaviest_first(items):
    return sorted(items, key = lambda i: i.weight, reverse = True)

def sorted_routes_heaviest_first(routes):
    return sorted(routes, key = lambda r: r.weight, reverse = True)

def grouped_routes_by_warehouse_id(routes):
    grouped = {}

    for r in routes:
        if r.w.id not in grouped:
            grouped[r.w.id] = []

        grouped[r.w.id].append(r)

    return grouped

def prepare_routes(world, state):
    routes = []
    temp_warehouses = copy.deepcopy(state.warehouses)

    # for each order find the nearest warehouses from which it can be fulfilled
    for o in orders_most_items_first(state.open_orders):
        temp_closest_warehouses = warehouses_closest_first(temp_warehouses, o.pos)
        items_not_found_yet = o.items[:]
        items_by_w = {}

        for item in o.items:
            item.weight = weight_of_item(item, world)

        for w in temp_closest_warehouses:
            for item in items_not_found_yet[:]:
                if w.stock[item.pt_id] > 0:
                    items_not_found_yet.remove(item)
                    w.stock[item.pt_id] -= 1

                    if w.id not in items_by_w:
                        items_by_w[w.id] = []
                    items_by_w[w.id].append(item)

            if len(items_not_found_yet) == 0:
                break

        for w_id, items in items_by_w.items():
            items_heaviest_first = sorted_items_heaviest_first(items)
            route = Route()
            route.w_id = w_id
            route.o = o
            route.o_id = o.id
            route.items = []
            route.weight = 0

            while True:
                for item in items_heaviest_first[:]:
                    if (route.weight + item.weight) > world.d_max_payload:
                        continue

                    items_heaviest_first.remove(item)
                    route.items.append(item)
                    route.weight += item.weight

                routes.append(route)

                route = Route()
                # we cannot set the actual warehouse here because
                # w is now the copied temp warehouse, not the actual one
                route.w_id = w_id
                route.o = o
                route.o_id = o.id
                route.items = []
                route.weight = 0

                if len(items_heaviest_first) == 0:
                    break

    # assign the real warehouse objects
    for route in routes:
        route.w = state.warehouses[route.w_id]

    # routes1 = sorted(routes, key = lambda r: r.weight, reverse = True)
    # for route in routes1:
    #     print(str(route.weight) + " " + str(len(route.items)))

    # print('all: ' + str(len(routes)))
    #
    # routes_one_item = list(filter(lambda r: len(r.items) == 1, routes))
    # print('1 item: ' + str(len(routes_one_item)))
    #
    # routes_2_items = list(filter(lambda r: len(r.items) == 2, routes))
    # print('2 items: ' + str(len(routes_2_items)))
    #
    # routes_3_items = list(filter(lambda r: len(r.items) == 3, routes))
    # print('3 items: ' + str(len(routes_3_items)))
    #
    # routes_4_items = list(filter(lambda r: len(r.items) == 4, routes))
    # print('4 items: ' + str(len(routes_4_items)))
    #
    # sys.exit(0)

    return routes

def is_route_efficient_to_chunk(route, chunk):
    distance_w2o = distance(route.w.pos, route.o.pos)
    for ch_route in chunk.routes:
        distance_o2o = distance(ch_route.o.pos, route.o.pos)

        if (distance_w2o < distance_o2o):
            return False

    return True

def chunk_routes_1(world, routes):
    routes_by_w = grouped_routes_by_warehouse_id(routes)
    chunks = []

    for w_id, w_routes in routes_by_w.items():
        w_routes_heaviest_first = sorted_routes_heaviest_first(w_routes)
        w = w_routes_heaviest_first[0].w

        chunk = RoutesChunk()
        chunk.w = w
        chunk.routes = []
        chunk.weight = 0

        while True:
            for route in w_routes_heaviest_first[:]:
                if (chunk.weight + route.weight) > world.d_max_payload:
                    continue

                # TODO: chunk routes based on the distance
                # e.g. maybe chunk only those orders where distance between orders
                # is less than distance of any that from warehouse?
                # not sure
                if not is_route_efficient_to_chunk(route, chunk):
                    continue

                # TODO: also! if we will chunk together routes with same products,
                # it will in the end save turns on loading (might be interesting?)

                w_routes_heaviest_first.remove(route)
                chunk.routes.append(route)
                chunk.weight += route.weight

            chunks.append(chunk)

            chunk = RoutesChunk()
            chunk.w = w
            chunk.routes = []
            chunk.weight = 0

            if len(w_routes_heaviest_first) == 0:
                break

    for chunk in chunks:
        chunk.items_by_pt_id = {}

        for route in chunk.routes:
            for item in route.items:
                if item.pt_id not in chunk.items_by_pt_id:
                    chunk.items_by_pt_id[item.pt_id] = []

                chunk.items_by_pt_id[item.pt_id].append(item)


    # chunks1 = sorted(chunks, key = lambda ch: ch.weight, reverse = True)
    # for chunk in chunks1:
    #     print(str(chunk.weight) + " " + str(len(chunk.routes)))

    # print('all: ' + str(len(chunks)))
    #
    # chunks2 = list(filter(lambda ch: ch.weight == world.d_max_payload, chunks))
    # print('full weight: ' + str(len(chunks2)))
    #
    # chunks3 = list(filter(lambda ch: ch.weight > 190, chunks))
    # print('> 190: ' + str(len(chunks3)))
    #
    # chunks4 = list(filter(lambda ch: ch.weight > 180, chunks))
    # print('> 180: ' + str(len(chunks4)))
    #
    # sys.exit(0)

    return chunks

def chunk_routes_2(world, routes):
    routes_by_w = grouped_routes_by_warehouse_id(routes)
    chunks = []

    for w_id, w_routes in routes_by_w.items():
        w_routes_heaviest_first = sorted_routes_heaviest_first(w_routes)
        w = w_routes_heaviest_first[0].w

        chunk = RoutesChunk()
        chunk.w = w
        chunk.routes = []
        chunk.weight = 0

        while True:
            rel_route = w_routes_heaviest_first.pop(0)
            chunk.routes.append(rel_route)
            chunk.weight += rel_route.weight

            routes_with_closest_o = sorted(w_routes_heaviest_first, key = lambda r: distance(r.o.pos, rel_route.o.pos))

            for route in routes_with_closest_o:
                if (chunk.weight + route.weight) > world.d_max_payload:
                    continue

                if distance(route.o.pos, rel_route.o.pos) > distance(route.o.pos, route.w.pos):
                    continue

                # TODO: also! if we will chunk together routes with same products,
                # it will in the end save turns on loading (might be interesting?)

                # print("distance " + str(distance(route.o.pos, rel_route.o.pos)))

                w_routes_heaviest_first.remove(route)
                chunk.routes.append(route)
                chunk.weight += route.weight

            chunks.append(chunk)

            chunk = RoutesChunk()
            chunk.w = w
            chunk.routes = []
            chunk.weight = 0

            if len(w_routes_heaviest_first) == 0:
                break

    for chunk in chunks:
        chunk.items_by_o_id_and_pt_id = {}
        chunk.items_by_pt_id = {}

        for route in chunk.routes:

            if route.o.id not in chunk.items_by_o_id_and_pt_id:
                chunk.items_by_o_id_and_pt_id[route.o.id] = {}

            for item in route.items:
                if item.pt_id not in chunk.items_by_o_id_and_pt_id[route.o.id]:
                    chunk.items_by_o_id_and_pt_id[route.o.id][item.pt_id] = []

                if item.pt_id not in chunk.items_by_pt_id:
                    chunk.items_by_pt_id[item.pt_id] = []

                chunk.items_by_o_id_and_pt_id[route.o.id][item.pt_id].append(item)
                chunk.items_by_pt_id[item.pt_id].append(item)



    # chunks1 = sorted(chunks, key = lambda ch: ch.weight, reverse = True)
    # for chunk in chunks1:
    #     print(str(chunk.weight) + " " + str(len(chunk.routes)))

    # print('all: ' + str(len(chunks)))
    #
    # chunks2 = list(filter(lambda ch: ch.weight == world.d_max_payload, chunks))
    # print('full weight: ' + str(len(chunks2)))
    #
    # chunks3 = list(filter(lambda ch: ch.weight > 190, chunks))
    # print('> 190: ' + str(len(chunks3)))
    #
    # chunks4 = list(filter(lambda ch: ch.weight > 180, chunks))
    # print('> 180: ' + str(len(chunks4)))
    #
    # chunks5 = list(filter(lambda ch: ch.weight > 170, chunks))
    # print('> 170: ' + str(len(chunks5)))
    #
    # sys.exit(0)

    return chunks

def get_chunk_for_drone(state, chunked_routes, d):
    # TODO: here could be smart choosing of the chunk based on how
    # many orders will be closed by that flight

    # print("chunks: " + str(len(chunked_routes)))
    # for chunk in chunked_routes:
    #     print(str(len(chunk.routes)))

    for w in find_closest_nonempty_warehouses(state, d):
        chunks_of_w = list(filter(lambda ch: ch.w == w, chunked_routes))

        if len(chunks_of_w) > 0:
            chunk = chunks_of_w[0]
            chunked_routes.remove(chunk)
            return chunk

    return None


##########################################################
# here follows the actual simulation

state = copy.deepcopy(initial_state)
routes = prepare_routes(world, state)
chunked_routes = chunk_routes_2(world, routes)
output = Output(sys.argv[2])

for turn in range(world.turns):
    print("-- starting turn " + str(turn))

    idle_drones = [d for d in state.drones if d.turns_to_pos == 0]

    for d in idle_drones:
        # find action to do
        chunk = get_chunk_for_drone(state, chunked_routes, d)

        if chunk == None:
            continue

        w = chunk.w

        turns_till_idle_again = 0

        # drone has to get to the warehouse first
        turns_till_idle_again += distance(d.pos, w.pos)
        print("  * sending drone " + str(d.id) + " to warehouse " + str(w.id) +  " at " + str(w.pos[0]) + "-" + str(w.pos[1]) + " (distance: " + str(distance(d.pos, w.pos)) + ")")

        # load stuff from warehouse
        for pt_id, items in chunk.items_by_pt_id.items():
            qty = len(items)

            output.load(d.id, w.id, pt_id, qty)
            print("  * loading drone " + str(d.id) + " with product " + str(pt_id) + " of qty " + str(qty))

            print("  $ stock of " + str(pt_id) + " at warehouse " + str(w.id) + " was " + str(w.stock[pt_id]) + ", is now " + str(w.stock[pt_id] - qty))
            w.stock[pt_id] -= qty

            # every load command takes one turn
            turns_till_idle_again += 1

        from_pos = w.pos

        for o_id, items_by_pt_id in chunk.items_by_o_id_and_pt_id.items():
            o = state.open_orders[o_id]

            # drone has to get to order
            turns_till_idle_again += distance(from_pos, o.pos)
            print("  * sending drone " + str(d.id) + " to order " + str(o.id) + " pos " + str(o.pos[0]) + "-" + str(o.pos[1]) + " (distance: " + str(distance(from_pos, o.pos)) + ")")

            # drone has to unload
            for pt_id, items in items_by_pt_id.items():
                qty = len(items)

                output.deliver(d.id, o.id, pt_id, qty)
                print("  * unloading drone " + str(d.id) + " with product " + str(pt_id) + " of qty " + str(qty))

                # every deliver command takes one turn
                turns_till_idle_again += 1

                for item in items:
                    item.delivered = True

            from_pos = o.pos

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
