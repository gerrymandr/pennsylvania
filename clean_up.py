import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import geopandas
import pandas
import logging

from graphmaker.geospatial import reprojected
from graphmaker.graph import Graph
from main import plans

log = logging.getLogger(__name__)
handler = logging.FileHandler(filename='./logs/clean_up_islands.log', mode='w')
log.addHandler(handler)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)


def corrections_for_islands(graph, column):
    new_assignments = dict()
    for node in graph.nodes:
        value_of_one = graph.nodes[list(graph.neighbors(node))[0]][column]
        all_neighbors_agree = all(
            graph.nodes[neighbor][column] == value_of_one for neighbor in graph[node])
        if (graph.nodes[node][column] != value_of_one) and all_neighbors_agree:
            new_assignments[node] = value_of_one
            log.info(f"{node} : {value_of_one}")
    return new_assignments


def correct_islands(graph, column):
    corrections = corrections_for_islands(graph, column)
    log.info(f"Found {len(corrections)} islands to correct")
    for node, new_assignment in corrections.items():
        graph.nodes[node][column] = new_assignment


def main(shapefile_path='./wes_unitsPA/wes_units_PA.shp', graph_path='wes_graph.json'):
    pa = Graph.load(graph_path)

    shape = geopandas.read_file(shapefile_path)
    shape = shape.set_index('wes_id')

    for plan in plans:
        log.info(f"Plan: {plan}")
        try:
            plot_plan(shape, plan, f"./plots/{plan}_before.svg")
        except Exception:
            log.error("There was an error while trying to plot", exc_info=1)

        correct_islands(pa.graph, plan)
        assignment = {node: pa.graph.nodes[node][plan]
                      for node in pa.graph.nodes}

        try:
        plot_plan(shape, assignment, f"./plots/{plan}_after.svg")
        except Exception:
            log.error("There was an error while trying to plot", exc_info=1)

    pa.save()


def plot_plan(df, plan, filepath):
    if isinstance(plan, dict):
        df['assignment'] = pandas.Series(plan).astype('category')
    elif isinstance(plan, str):
        df['assignment'] = df[plan].astype('category')
    else:
        raise ValueError('Plan should be an assignment or a column name.')

    clean_df = df.dropna(subset=['assignment'])

    clean_df = reprojected(clean_df)

    _, ax = plt.subplots(1)
    clean_df.plot(ax=ax, linewidth=0.5, edgecolor='0.5',
                  column='assignment', categorical=True)
    ax.set_axis_off()

    plt.axis('equal')
    plt.savefig(filepath)


if __name__ == '__main__':
    main()
