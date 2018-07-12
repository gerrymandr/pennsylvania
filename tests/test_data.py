from graphmaker.graph import Graph
from rundmcmc.partition import Partition
from rundmcmc.updaters import (Tally, perimeters, exterior_boundaries,
                               interior_boundaries, boundary_nodes, cut_edges, polsby_popper,
                               cut_edges_by_part)
from rundmcmc.validity import single_flip_contiguous
from main import plans


def set_up_plan(plan):
    graph = Graph.load('./PA_queen.json').graph

    assignment = {node: graph.nodes[node][plan] for node in graph.nodes}

    updaters = {
        'perimeters': perimeters,
        'exterior_boundaries': exterior_boundaries,
        'interior_boundaries': interior_boundaries,
        'boundary_nodes': boundary_nodes,
        'cut_edges': cut_edges,
        'areas': Tally('area', alias='areas'),
        'polsby_popper': polsby_popper,
        'cut_edges_by_part': cut_edges_by_part
    }

    return Partition(graph, assignment, updaters)


def test_polsby_popper_between_zero_and_one():
    for plan in plans:
        partition = set_up_plan(plan)
        assert all(
            [0 < value < 1 for value in partition['polsby_popper'].values()])


def test_connected_districts():
    for plan in plans:
        partition = set_up_plan(plan)
        assert single_flip_contiguous(partition)
