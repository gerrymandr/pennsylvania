from clean_up import corrections_for_islands
import networkx


def test_clean_up():
    graph = networkx.Graph([(0, 1), (1, 2), (2, 3), (3, 1)])
    graph.nodes[0]['color'] = graph.nodes[1]['color'] = graph.nodes[2]['color'] = 'a'
    graph.nodes[3]['color'] = 'b'

    assert corrections_for_islands(graph, 'color') == {3: 'a'}
