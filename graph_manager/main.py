import rdflib
from pathlib import Path
from rdflib.namespace import RDF
import json
import random
import uuid


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
    
    def add_sensor(self, sensor_name, sensor_type=None):
        sensor_uri = self.obs_graph_base[sensor_name]
        if sensor_type is None:
            sensor_type = self.ORKA.Sensor
        self.graph.add((sensor_uri, RDF.type, sensor_type))
        return sensor_uri
    
    def add_procedure(self, procedure_name):
        procedure_uri = self.obs_graph_base[procedure_name]
        self.graph.add((procedure_uri, RDF.type, self.ORKA.Procedure))
        return procedure_uri
    
    def add_observation(self, observation_name):
        observation_uri = self.obs_graph_base[observation_name]
        self.graph.add((observation_uri, RDF.type, self.ORKA.Observation))
        return observation_uri
    
    def add_Measurement(self, measurement_name):
        measurement_uri = self.obs_graph_base[measurement_name]
        self.graph.add((measurement_uri, RDF.type, self.ORKA.Measurement))
        return measurement_uri
    
    def add_entity(self, entity_name):
        entity_uri = self.obs_graph_base[entity_name]
        self.graph.add((entity_uri, RDF.type, self.ORKA.Entity))
        return entity_uri
    
    def add_characteristic(self, characteristic_name):
        characteristic_uri = self.obs_graph_base[characteristic_name]
        self.graph.add((characteristic_uri, RDF.type, self.ORKA.Characteristic))
        return characteristic_uri
    
    def add_result(self, result_name):
        result_uri = self.obs_graph_base[result_name]
        self.graph.add((result_uri, RDF.type, self.ORKA.Result))
        return result_uri
    
    def save_graph(self, file_path, format="turtle"):
        self.graph.serialize(destination=file_path, format=format)

    def build_static_graph(self, robot_name, sensors, procedures):
        self.add_robot(robot_name)

        for sensor in sensors:
            sensor_name = sensor["name"]
            sensor_type = self.ORKA[sensor["type"]]
            self.add_sensor(sensor_name, sensor_type)

        for procedure in procedures:
            self.add_procedure(procedure)


    def update_graph_with_observation(self, observation_name, measurement_name, sensor, result, procedure_name=None, entity_name=None, characteristic_name=None):
        observation = self.add_observation(observation_name)
        measurement = self.add_Measurement(measurement_name)
        result_uri = self.add_result(result)
        self.graph.add((observation, self.ORKA.hasMeasurement, measurement))
        self.graph.add((measurement, self.ORKA.hasResult, result_uri))
        self.graph.add((measurement, self.ORKA.madeBySensor, sensor))
        if procedure_name:
            procedure = self.add_procedure(procedure_name)
            self.graph.add((measurement, self.ORKA.usedProcedure, procedure))
        if entity_name:
            entity = self.add_entity(entity_name)
            self.graph.add((observation, self.ORKA.ofEntity, entity))
        if characteristic_name:
            characteristic = self.add_characteristic(characteristic_name)
            self.graph.add((entity, self.ORKA.hasCharacteristic, characteristic))
        return self.graph


    def load_robot_config(self, path: str) -> dict:
        """Load robot configuration derived from URDF."""
        with open(path, "r") as f:
            return json.load(f)


def generate_test_sensor_data(gm: GraphManager, sensor_name: str):
    """Generate synthetic observation data for testing."""
    obs_id = f"obs_{uuid.uuid4().hex[:6]}"
    meas_id = f"meas_{uuid.uuid4().hex[:6]}"
    res_id = f"res_{uuid.uuid4().hex[:6]}"

    fake_distance = round(random.uniform(0.5, 5.0), 2)

    gm.update_graph_with_observation(
        observation_name=obs_id,
        measurement_name=meas_id,
        sensor=gm.obs_graph_base[sensor_name],
        result=res_id,
        procedure_name="synthetic_procedure",
        entity_name="synthetic_entity",
        characteristic_name="distance"
    )

    return {
        "observation": obs_id,
        "value": fake_distance
    }

def test_full_pipeline():
    gm = GraphManager()
    config = gm.load_robot_config("graph_manager/test_robot_config.json")

    gm.build_static_graph(config["robot"]["name"], config["sensors"], [])
    data = generate_test_sensor_data(gm, "lidar_1")

    # sanity checks
    obs_uri = gm.obs_graph_base[data["observation"]]
    assert (obs_uri, RDF.type, gm.ORKA.Observation) in gm.graph

    print("✅ Static + dynamic graph test passed")
    print("Triples:", len(gm.graph))

    gm.save_graph("test_output_graph.ttl")

if __name__ == "__main__":
    test_full_pipeline()