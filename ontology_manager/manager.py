from pathlib import Path
import uuid

from owlready2 import (
    get_ontology,
    sync_reasoner,
    sync_reasoner_pellet,
    OwlReadyInconsistentOntologyError,
    default_world,
)


class GraphManager:
    def __init__(self, graph_path: str | Path | None = None):
        self.graph_path = Path(graph_path) if graph_path else None
        self.ontology = None

    def load_graph(self, path: str | Path | None = None):
        # Load the ontology from disk.
        load_path = Path(path) if path else self.graph_path
        if load_path is None:
            raise ValueError("No ontology path provided.")

        load_path = load_path.resolve()
        self.ontology = get_ontology(load_path.as_uri()).load()
        return self.ontology

    def save_graph(self, path: str | Path, fmt: str = "rdfxml"):
        # Save the ontology to disk.
        if self.ontology is None:
            raise ValueError("No ontology loaded.")

        path = Path(path).resolve()
        self.ontology.save(file=str(path), format=fmt)
        return path

    def query_graph(self, query: str):
        # Run a SPARQL query on the ontology world.
        if self.ontology is None:
            raise ValueError("No ontology loaded.")

        return list(default_world.sparql(query))

    def reason_graph(
        self,
        reasoner: str = "hermit",
        *,
        infer_property_values: bool = True,
        infer_data_property_values: bool = True,
        debug: int = 0,
        save_path: str | Path | None = None,
        fmt: str = "rdfxml",
    ) -> dict[str, object]:
        # Run reasoning and optionally save the inferred ontology.
        if self.ontology is None:
            raise ValueError("No ontology loaded.")

        normalized_reasoner = reasoner.strip().lower()
        if normalized_reasoner not in {"hermit", "pellet"}:
            raise ValueError("Unsupported reasoner. Use 'hermit' or 'pellet'.")

        try:
            with self.ontology:
                if normalized_reasoner == "pellet":
                    sync_reasoner_pellet(
                        infer_property_values=infer_property_values,
                        infer_data_property_values=infer_data_property_values,
                        debug=debug,
                    )
                else:
                    sync_reasoner(
                        infer_property_values=infer_property_values,
                        debug=debug,
                    )
        except OwlReadyInconsistentOntologyError:
            return {
                "consistent": False,
                "reasoner": normalized_reasoner,
                "saved_to": None,
            }

        saved_to = None
        if save_path is not None:
            saved_to = self.save_graph(path=save_path, fmt=fmt)

        return {
            "consistent": True,
            "reasoner": normalized_reasoner,
            "saved_to": saved_to,
        }

    def print_graph(self):
        print(self.ontology.world.as_rdflib_graph().serialize(format="turtle"))

    def uid(self, prefix: str):
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

class OrkaManager(GraphManager):
    def __init__(self, ontology_path: str | Path | None = None, **kwargs):
        super().__init__(**kwargs)
        self.ontology_path = Path(ontology_path) if ontology_path else None
        self.ontology = None


    def build_robot_base_graph(self,
                               robot_name = 'default_robot',
                               system_name = 'system',
                               sensors = [],
                               ):
        
        onto = self.ontology
        
        with onto:
            robot = onto.Robot(robot_name)

            system = onto.System(f"{robot_name}_{system_name}")
            system.hostedBy.append(robot)
            
            for s in sensors:
                sensor = onto.Sensor(f"{robot_name}_{s}")
                sensor.implementedBy.append(system)

                standardprocedure = onto.Procedure(f"{s}_software")
                standardprocedure.implementedOn.append(robot)



        return {
            "robot": robot,
            "system": system,
        }
    

    def update_observation_graph(self):
        pass

    def add_observation(self,
                        sensor = None,
                        procedure = None,
                        data = None,):
        pass



class OrkaROSManager(OrkaManager):
    pass