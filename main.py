from ontology_building.orka_alignments import OrkaFoundationalAlignments
from ontology_building.orka_core import OrkaCore
from ontology_building.orka_conceptualspaces import OrkaConceptualSpaces
from ontology_building.orka_full import OrkaFull

from ontology_building.orka_all import OrkaAll


from ontology_manager.manager import OrkaManager

# -----------------------------------------------------------------
# Ontology Builder
# -----------------------------------------------------------------
ontology_path = "owl/orka-all.owl"
builder = OrkaAll()
onto = builder.build()
builder.save(ontology_path)

# -----------------------------------------------------------------
# Observation Graph Builder
# -----------------------------------------------------------------

manager = OrkaManager()
manager.load_graph(ontology_path)
manager.build_robot_base_graph(sensors = ['camera', 'lidar'])
manager.reason_graph(save_path='owl/orka-reasoner.owl')
manager.save_graph("owl/orka-test.owl")
