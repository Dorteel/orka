"""ORKA measurements ontology module.

This module extends the ORKA core ontology with legacy ORKA measurement
concepts and datatype-property hierarchy.
"""

from __future__ import annotations

from types import new_class

from owlready2 import DataProperty, Thing

from builder.orka_core import DEFAULT_BASE_IRI, define_core_module, get_orka_ontology


MEASUREMENT_CLASS_SPECS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("DataSet", ("Thing",)),
    ("DeepLearningModel", ("ComputerVisionAlgorithm",)),
    ("RadianPerSecond", ("MeasurementStandard",)),
)

# (property_name, parent_property_names)
MEASUREMENT_DATAPROPERTY_SPECS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("hasSensorCharacteristic", tuple()),
    ("hasAlgorithmCharacteristic", tuple()),
    ("hasExternalDescription", tuple()),
    ("hasDeepLearningModelCharacteristic", ("hasAlgorithmCharacteristic",)),
    ("hasAccuracy", ("hasSensorCharacteristic",)),
    ("hasAngularResolution", ("hasSensorCharacteristic",)),
    ("hasDetectionRange", ("hasSensorCharacteristic",)),
    ("hasEnergyConsumption", ("hasSensorCharacteristic",)),
    ("hasMaxRange", ("hasSensorCharacteristic",)),
    ("hasMeasurementRange", tuple()),
    ("hasMinRange", ("hasSensorCharacteristic",)),
    ("hasPowerRequirement", tuple()),
    ("hasScanningFrequency", ("hasSensorCharacteristic",)),
    ("hasDetectionThreshold", ("hasDeepLearningModelCharacteristic",)),
    ("hasFLOPsat640", ("hasDeepLearningModelCharacteristic",)),
    ("hasInferenceSpeed", ("hasDeepLearningModelCharacteristic",)),
    ("hasInferenceSpeedCPUb1", ("hasInferenceSpeed",)),
    ("hasInferenceSpeedV100b1", ("hasInferenceSpeed",)),
    ("hasInferenceSpeedV100b32", ("hasInferenceSpeed",)),
    ("hasInputSize", ("hasDeepLearningModelCharacteristic",)),
    ("hasNumberOfParameters", ("hasDeepLearningModelCharacteristic",)),
    ("hasmAPval50-95", ("hasDeepLearningModelCharacteristic",)),
    ("hasServiceName", tuple()),
    ("hasValue", tuple()),
    ("hasDBpediaURI", ("hasExternalDescription",)),
    ("hasWikiDataURI", ("hasExternalDescription",)),
    ("hasWordNetSynset", ("hasExternalDescription",)),
    ("inDataSet", tuple()),
    ("trainedOnDataSet", tuple()),
    ("hasProbability", tuple()),
    ("sparqlEndpoint", tuple()),
)


def _onto_get(onto, local_name: str):
    """Return ontology entity by local name, if present."""
    return onto[local_name]


def _ensure_class(onto, class_name: str, parent_names: tuple[str, ...]) -> type:
    """Create class if missing and ensure all expected parent links exist."""
    resolved_parents = []
    for parent_name in parent_names:
        if parent_name == "Thing":
            resolved_parents.append(Thing)
        else:
            parent = _onto_get(onto, parent_name)
            if parent is None:
                raise ValueError(
                    f"Missing parent class for {class_name}: {parent_name}"
                )
            resolved_parents.append(parent)

    parents = tuple(resolved_parents)
    cls = _onto_get(onto, class_name)
    if cls is None:
        cls = new_class(class_name, parents)
    else:
        for parent in parents:
            if parent not in cls.is_a:
                cls.is_a.append(parent)

    return cls


def _ensure_dataproperty(onto, prop_name: str, parent_names: tuple[str, ...]):
    """Create datatype property if missing and attach subproperty links."""
    prop = _onto_get(onto, prop_name)
    if prop is None:
        prop = new_class(prop_name, (DataProperty,))

    for parent_name in parent_names:
        parent_prop = _onto_get(onto, parent_name)
        if parent_prop is None:
            raise ValueError(
                f"Missing parent data property for {prop_name}: {parent_name}"
            )
        if parent_prop not in prop.is_a:
            prop.is_a.append(parent_prop)

    return prop


def define_measurement_module(onto) -> dict[str, type]:
    """Define legacy ORKA measurement classes and datatype properties."""
    sentinel = {
        "RadianPerSecond": onto.RadianPerSecond,
        "hasMeasurementRange": _onto_get(onto, "hasMeasurementRange"),
        "hasSensorCharacteristic": _onto_get(onto, "hasSensorCharacteristic"),
    }
    if all(sentinel.values()):
        return {
            "RadianPerSecond": onto.RadianPerSecond,
            "DeepLearningModel": onto.DeepLearningModel,
            "DataSet": onto.DataSet,
        }

    if onto.Measurement is None:
        define_core_module(onto)

    with onto:
        for class_name, parent_names in MEASUREMENT_CLASS_SPECS:
            _ensure_class(onto, class_name, parent_names)

        for prop_name, parent_names in MEASUREMENT_DATAPROPERTY_SPECS:
            _ensure_dataproperty(onto, prop_name, parent_names)

        # Domains/ranges from legacy ORKA where they are clear and localizable.
        _onto_get(onto, "hasDeepLearningModelCharacteristic").domain = [
            onto.DeepLearningModel
        ]
        _onto_get(onto, "hasMeasurementRange").domain = [onto.Sensor]
        _onto_get(onto, "hasMeasurementRange").range = [float]
        _onto_get(onto, "hasPowerRequirement").domain = [onto.Sensor]
        _onto_get(onto, "hasValue").domain = [onto.Characteristic]
        _onto_get(onto, "sparqlEndpoint").domain = [onto.Knowledge_Repository]
        _onto_get(onto, "sparqlEndpoint").range = [str]

    return {
        "RadianPerSecond": onto.RadianPerSecond,
        "DeepLearningModel": onto.DeepLearningModel,
        "DataSet": onto.DataSet,
    }


def build_measurement_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Convenience builder for core + measurements ontology."""
    onto = get_orka_ontology(base_iri=base_iri)
    define_core_module(onto)
    define_measurement_module(onto)
    return onto
