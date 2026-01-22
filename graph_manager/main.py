import rdflib
from pathlib import Path


class GraphManager:
    def __init__(self, base_uri = "http://example.org/orka/observation_graph/"):
        self.ORKA = rdflib.Namespace("https://w3id.org/def/orka#")
        owl_path = Path(__file__).resolve().parent.parent / "orka.owl"
        self.graph = rdflib.Graph()
        self.graph.parse(str(owl_path))
        self.graph.bind("orka", self.ORKA)
        self.obs_graph_base = rdflib.Namespace(base_uri)

    def add_robot(self, robot_name):
        robot_uri = self.obs_graph_base[robot_name]
        self.graph.add((robot_uri, rdflib.RDF.type, self.ORKA.Robot))
        return robot_uri
    
    def add_sensor(self, sensor_name, sensor_type=self.ORKA.Sensor):
        robot_uri = self.obs_graph_base[sensor_name]
        self.graph.add((robot_uri, rdflib.RDF.type, sensor_type))
        return robot_uri

def test_graph_manager():
    gm = GraphManager()
    robot = gm.add_robot("robot_1")

    print("Robot URI:", robot)
    print("Triples in graph:", len(gm.graph))

if __name__ == "__main__":
    test_graph_manager()