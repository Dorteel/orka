"""ORKA characteristics ontology module.

This module extends the ORKA core ontology with the legacy ORKA
characteristics hierarchy.
"""

from __future__ import annotations

from types import new_class

from builder.orka_core import DEFAULT_BASE_IRI, define_core_module, get_orka_ontology


# Legacy ORKA characteristic hierarchy. Parent names must exist in core or
# earlier entries in this list.
CHARACTERISTIC_CLASS_SPECS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ObjectProperty", ("Characteristic",)),
    ("EnvironmentProperty", ("Characteristic",)),
    ("ActivityType", ("Characteristic",)),
    ("ObjectType", ("Characteristic",)),
    ("VisualCharactersitic", ("ObjectProperty",)),
    ("MaterialProperty", ("ObjectProperty",)),
    ("SpatialProperty", ("ObjectProperty",)),
    ("TemporalProperty", ("ObjectProperty",)),
    ("ThermalProperty", ("ObjectProperty",)),
    ("AngularForce", ("ObjectProperty",)),
    ("LinearForce", ("ObjectProperty",)),
    ("Location", ("SpatialProperty",)),
    ("Orientation", ("SpatialProperty",)),
    ("Position", ("Location",)),
    ("Angular_position", ("Location",)),
    ("Altitude", ("Position",)),
    ("Latitude", ("Position",)),
    ("Angle", ("Orientation",)),
    ("Inclination", ("Angle",)),
    ("Pitch", ("Angle",)),
    ("Roll", ("Angle",)),
    ("Yaw", ("Angle",)),
    ("GeometricProperty", ("VisualCharactersitic",)),
    ("SizeProperty", ("GeometricProperty",)),
    ("Structure", ("GeometricProperty",)),
    ("Shape", ("GeometricProperty",)),
    ("Depth", ("SizeProperty",)),
    ("Height", ("SizeProperty",)),
    ("Length", ("SizeProperty",)),
    ("SurfaceArea", ("SizeProperty",)),
    ("Volume", ("SizeProperty",)),
    ("Width", ("SizeProperty",)),
    ("ComplexStructure", ("Structure",)),
    ("SimpleStructure", ("Structure",)),
    ("Color", ("VisualCharactersitic",)),
    ("Pattern", ("VisualCharactersitic",)),
    ("MaterialName", ("MaterialProperty",)),
    ("Density", ("MaterialProperty",)),
    ("Flexibility", ("MaterialProperty",)),
    ("Weight", ("MaterialProperty",)),
    ("Temperature", ("EnvironmentProperty", "ThermalProperty")),
    ("Brightness", ("EnvironmentProperty",)),
    ("Humidity", ("EnvironmentProperty",)),
    ("Age", ("TemporalProperty",)),
    ("CreationDate", ("TemporalProperty",)),
    ("DestructionDate", ("TemporalProperty",)),
    ("ExpirationDate", ("TemporalProperty",)),
)


def _ensure_class(onto, class_name: str, parent_names: tuple[str, ...]) -> type:
    """Create class if missing and ensure all expected parent links exist."""
    parents = tuple(getattr(onto, parent_name) for parent_name in parent_names)
    if any(parent is None for parent in parents):
        missing = [name for name in parent_names if getattr(onto, name) is None]
        missing_str = ", ".join(missing)
        raise ValueError(f"Missing parent classes for {class_name}: {missing_str}")

    cls = getattr(onto, class_name)
    if cls is None:
        cls = new_class(class_name, parents)
    else:
        for parent in parents:
            if parent not in cls.is_a:
                cls.is_a.append(parent)

    return cls


def define_characteristic_module(onto) -> dict[str, type]:
    """Define the legacy ORKA characteristics hierarchy on the ontology."""
    sentinel = {
        "ObjectProperty": onto.ObjectProperty,
        "EnvironmentProperty": onto.EnvironmentProperty,
        "Color": onto.Color,
        "Temperature": onto.Temperature,
        "Age": onto.Age,
    }
    if all(sentinel.values()):
        return {
            "ObjectProperty": onto.ObjectProperty,
            "EnvironmentProperty": onto.EnvironmentProperty,
            "Color": onto.Color,
        }

    if onto.Characteristic is None:
        define_core_module(onto)

    with onto:
        for class_name, parent_names in CHARACTERISTIC_CLASS_SPECS:
            _ensure_class(onto, class_name, parent_names)

    return {
        "ObjectProperty": onto.ObjectProperty,
        "EnvironmentProperty": onto.EnvironmentProperty,
        "Color": onto.Color,
    }


def build_characteristics_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Convenience builder for core + characteristics ontology."""
    onto = get_orka_ontology(base_iri=base_iri)
    define_core_module(onto)
    define_characteristic_module(onto)
    return onto
