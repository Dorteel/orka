from pathlib import Path
import re
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

    def safe_name(self, value: str, prefix: str = "orka"):
        name = re.sub(r"[^0-9A-Za-z_]+", "_", value.strip("/"))
        name = re.sub(r"_+", "_", name).strip("_")
        return name or self.uid(prefix)

    def add_property_value(self, subject, property_name: str, value):
        current = getattr(subject, property_name)
        if hasattr(current, "append"):
            current.append(value)
        else:
            setattr(subject, property_name, value)

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
                        interface_name,
                        interface_kind = "topic",
                        interface_type = None,
                        sensor = None,
                        procedure = None,
                        data = None,
                        max_recognitions = 50,
                        store_raw_data = False,):
        if self.ontology is None:
            raise ValueError("No ontology loaded.")

        interface_kind = interface_kind.strip().lower()
        if interface_kind not in {"topic", "service"}:
            raise ValueError("interface_kind must be 'topic' or 'service'.")

        onto = self.ontology
        suffix = self.safe_name(interface_name, prefix=interface_kind)

        with onto:
            observation = onto.Observation(self.uid(f"observation_{suffix}"))
            measurement = onto.Measurement(self.uid(f"measurement_{suffix}"))
            result = onto.Result(self.uid(f"result_{suffix}"))
            procedure = procedure or onto.Procedure(self.uid(f"observe_{suffix}"))

            self.add_property_value(observation, "hasMeasurement", measurement)
            self.add_property_value(measurement, "usedProcedure", procedure)
            self.add_property_value(measurement, "hasResult", result)

            if sensor is not None:
                self.add_property_value(measurement, "madeBySensor", sensor)

            recognition_items = self._recognition_items(data)
            if max_recognitions and max_recognitions > 0:
                mapped_items = recognition_items[:max_recognitions]
            else:
                mapped_items = recognition_items

            if data is not None and store_raw_data:
                result.comment.append(str(data))
            elif data is not None:
                result.comment.append(f"Observed {len(recognition_items)} recognition item(s).")

            if len(mapped_items) < len(recognition_items):
                result.comment.append(f"Mapped first {len(mapped_items)} recognition item(s).")

            if interface_kind == "service":
                interface = onto.ROSService(f"service_{suffix}")
                self.add_property_value(procedure, "providesService", interface)
            else:
                interface = onto.ROSTopic(f"topic_{suffix}")
                self.add_property_value(procedure, "subscribesTo", interface)

            interface.hasROSName = interface_name

            if interface_type:
                message_type = onto.search_one(hasROSName=interface_type)
                if message_type is None:
                    type_suffix = self.safe_name(interface_type, prefix="message_type")
                    message_type = onto.ROSMessageType(f"ros_type_{type_suffix}")
                    message_type.hasROSName = interface_type

                    package, _, type_name = interface_type.partition("/")
                    message_type.hasROSPackage = package
                    message_type.hasROSTypeName = type_name or interface_type

                self.add_property_value(interface, "hasMessageType", message_type)

            for item in mapped_items:
                entity = onto.DetectableEntity(self.uid("detected_entity"))
                self.add_property_value(observation, "ofEntity", entity)

                for class_name, value in self._recognition_characteristics(item):
                    characteristic = getattr(onto, class_name)(self.uid(class_name.lower()))
                    characteristic.comment.append(str(value))
                    self.add_property_value(entity, "hasCharacteristic", characteristic)

        return {
            "observation": observation,
            "measurement": measurement,
            "result": result,
            "interface": interface,
        }

    def _recognition_items(self, data):
        if data is None:
            return []

        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]

        if isinstance(data, dict):
            if self._looks_like_recognition(data):
                return [data]

            items = []
            for value in data.values():
                items.extend(self._recognition_items(value))
            return items

        return []

    def _looks_like_recognition(self, value):
        return any(key in value for key in ("id", "name", "shape", "position", "size", "orientation", "colors"))

    def _recognition_characteristics(self, item):
        mapping = [
            ("id", "ID"),
            ("name", "Name"),
            ("shape", "Shape"),
            ("position", "Position"),
            ("orientation", "Orientation"),
            ("colors", "Color"),
        ]

        characteristics = [
            (class_name, item[key])
            for key, class_name in mapping
            if key in item
        ]

        size = item.get("size")
        if isinstance(size, (list, tuple)):
            size_mapping = [("Length", 0), ("Width", 1), ("Height", 2)]
            characteristics.extend(
                (class_name, size[index])
                for class_name, index in size_mapping
                if len(size) > index
            )

        return characteristics



class OrkaROSManager(OrkaManager):
    pass
