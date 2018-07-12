import json
import logging

from graphmaker.graph import Graph
from graphmaker.resources import BlockPopulationShapefile
from graphmaker.match import map_units_to_parts_via_blocks
from graphmaker.reports.splitting import splitting_report
import pandas
import geopandas

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)


def match_wes_units_to_remedial_plan():
    pa = Graph.load('./wes_graph.json')

    blocks = pandas.read_csv('./data/block_to_wesid.csv', dtype=str)
    plan = pandas.read_csv(
        './data/remedial/blocks_to_remedial.csv', names=['GEOID10', 'remedial'], dtype=str)

    blocks = blocks.set_index('GEOID10')
    plan = plan.set_index('GEOID10')

    blocks['remedial'] = plan['remedial']

    log.info('Mapping units to parts')
    mapping = map_units_to_parts_via_blocks(
        blocks, pa.graph, unit='wes_id', part='remedial')

    for node in mapping:
        if node != '0':
            pa.graph.nodes[node]['remedial'] = mapping[node]

    pa.save('./wes_graph2.json')

    log.info('Getting block populations')

    block_pops = geopandas.read_file(
        '../graphmaker/graphmaker/blocks/42/tabblock2010_42_pophu.shp')
    block_pops['GEOID10'] = block_pops['BLOCKID10'].astype('object')
    block_pops = block_pops.set_index('GEOID10')

    blocks['population'] = block_pops['POP10'].astype(int)

    log.info('Creating report')
    report = splitting_report(blocks, 'wes_id', 'remedial')

    with open('./reports/splitting_energy_remedial_plan.json', 'w') as f:
        json.dump(report, f)

    return report


def main():
    match_wes_units_to_remedial_plan()


if __name__ == '__main__':
    main()
