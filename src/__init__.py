from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT/'src'
RESOURCES = ROOT/'resources'
ANALYSIS_SOLUTION = ROOT/'analysis_solution'
ENTITIES_DURING_SIMULATION_DATA = ANALYSIS_SOLUTION / 'entities_during_simulation_data'
GRAPH_PRODUCTION_MATERIAL = ANALYSIS_SOLUTION / 'graph_production_material'
print(ROOT)