from graphmaker.graph import Graph
from rundmcmc.defaults import BasicChain, default_constraints
from rundmcmc.partition import Partition
from rundmcmc.updaters import (votes_updaters, Tally, perimeters, exterior_boundaries,
                               interior_boundaries, boundary_nodes, cut_edges, polsby_popper,
                               cut_edges_by_part)
from rundmcmc.scores import mean_median, mean_thirdian, efficiency_gap
from rundmcmc.run import pipe_to_table
from rundmcmc.output import p_value_report
from rundmcmc.chain import MarkovChain
from rundmcmc.validity import Validator, within_percent_of_ideal_population, L1_reciprocal_polsby_popper, UpperBound
from rundmcmc.accept import always_accept
from rundmcmc.proposals import propose_random_flip

import functools
import pprint

plans = ['CD_CR', 'CD_remedia', 'GOV_4_1', 'TS_4_1']


def run_pa(plan='CD_CR'):
    graph = Graph.load('./wes_graph.json').graph

    assignment = {node: graph.nodes[node][plan] for node in graph.nodes}

    updaters = {
        **votes_updaters(['VoteA', 'VoteB']),
        'population': Tally('POP100', alias='population'),
        'perimeters': perimeters,
        'exterior_boundaries': exterior_boundaries,
        'interior_boundaries': interior_boundaries,
        'boundary_nodes': boundary_nodes,
        'cut_edges': cut_edges,
        'areas': Tally('utm_area', alias='areas'),
        'polsby_popper': polsby_popper,
        'cut_edges_by_part': cut_edges_by_part
    }

    partition = Partition(graph, assignment, updaters)

    scores = {
        'Mean-Median': functools.partial(mean_median, proportion_column_name='VoteA%'),
        'Mean-Thirdian': functools.partial(mean_thirdian, proportion_column_name='VoteA%'),
        'Efficiency Gap': functools.partial(efficiency_gap, col1='VoteA', col2='VoteB'),
    }

    initial_scores = {key: score(partition)
                      for key, score in scores.items()}

    population_constraint = within_percent_of_ideal_population(partition, 0.01)

    compactness_limit = L1_reciprocal_polsby_popper(partition) * 1.01
    compactness_constraint = UpperBound(
        L1_reciprocal_polsby_popper, compactness_limit)

    is_valid = Validator(default_constraints +
                         [population_constraint, compactness_constraint])

    chain = MarkovChain(propose_random_flip, is_valid,
                        always_accept, partition, total_steps=1000000)

    # chain = BasicChain(partition, total_steps=1000000)

    table = pipe_to_table(chain, scores)

    return {key: p_value_report(key, table[key], initial_scores[key]) for key in scores}


if __name__ == '__main__':
    pprint.pprint(run_pa())
