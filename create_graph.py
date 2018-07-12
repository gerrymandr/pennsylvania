import geopandas
import logging

from graphmaker.graph import Graph
from clean_up import correct_islands
from main import plans

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

columns = ['rounded11', '2011', 'T16PRESR', 'T16PRESD',
           'T16SENR', 'T16SEND', 'population', 'GOV_4_1',
           'TS_4_1', 'Remedial']


def create_graph_from_shapefile(shapefile_path='./data/wes_with_districtings/wes_with_districtings.shp'):
    log.info(f"Creating the queen adjacency graph")
    pa_queen = Graph.from_shapefile(
        shapefile_path, adjacency_type='queen', data_columns=None, id_column='wes_id')
    log.info(f"Saving the queen adjacency graph")
    pa_queen.add_columns_from_shapefile(
        shapefile_path, columns, id_column='wes_id')

    # Fix nodes whose assignment is different from all their neighbors, and
    # whose neighbors all have the same assignment.
    # In practice, this affects one node's assignment in two plans. (Node '1')
    for plan in plans:
        correct_islands(pa_queen.graph, plan)

    pa_queen.save('./PA_queen.json')

    log.info(f"Creating the rook adjacency graph")
    pa_rook = Graph.from_shapefile(
        shapefile_path, adjacency_type='rook', data_columns=None, id_column='wes_id')
    pa_rook.add_columns_from_shapefile(
        shapefile_path, columns, id_column='wes_id')
    log.info(f"Saving the queen adjacency graph")

    for plan in plans:
        correct_islands(pa_rook.graph, plan)

    pa_rook.save('./PA_rook.json')


def main():
    create_graph_from_shapefile()


if __name__ == '__main__':
    main()
