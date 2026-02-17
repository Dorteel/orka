"""ORKA sensors ontology module.

This module extends the ORKA core ontology with the legacy ORKA sensor
hierarchy while keeping ORKA-native classes as the source vocabulary.
"""

from __future__ import annotations

from types import new_class

from owlready2 import ObjectProperty

from builder.orka_core import DEFAULT_BASE_IRI, define_core_module, get_orka_ontology


# Legacy ORKA sensor hierarchy. Parent names must be defined earlier in this list
# or in the ORKA core module.
SENSOR_CLASS_SPECS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Active_Sensor", ("Sensor",)),
    ("Passive_Sensor", ("Sensor",)),
    ("Exteroceptor_Sensor", ("Sensor",)),
    ("IdentificationSensor", ("Sensor",)),
    ("Distance_Sensor", ("Sensor", "Exteroceptor_Sensor")),
    ("Light_Sensor", ("Sensor", "Exteroceptor_Sensor")),
    ("Touch_Sensor", ("Sensor", "Exteroceptor_Sensor")),
    ("Motor_Sensor", ("Sensor", "ProprioceptorSensor")),
    ("Speed_Sensor", ("Sensor",)),
    ("Altitude_Sensor", ("Sensor", "ProprioceptorSensor")),
    ("Accelerometer", ("Exteroceptor_Sensor", "Passive_Sensor", "Speed_Sensor")),
    ("Active_Optical", ("Active_Sensor", "Exteroceptor_Sensor", "Position_Sensor")),
    ("Barometric_Altimeter", ("Altitude_Sensor",)),
    ("Brush_Encoder", ("Motor_Sensor", "Passive_Sensor")),
    ("Bumper", ("Exteroceptor_Sensor", "Passive_Sensor", "Touch_Sensor")),
    (
        "Camera",
        (
            "Distance_Sensor",
            "Exteroceptor_Sensor",
            "IdentificationSensor",
            "Passive_Sensor",
            "Speed_Sensor",
        ),
    ),
    ("Capacitive_Sensor", ("Distance_Sensor", "Exteroceptor_Sensor", "Passive_Sensor")),
    ("Capacity_Encoder", ("Active_Sensor", "Motor_Sensor")),
    ("Compass", ("Heading_Sensor", "Passive_Sensor")),
    ("Contact_Array", ("Exteroceptor_Sensor", "Passive_Sensor", "Touch_Sensor")),
    ("DepthCamera", ("Active_Sensor", "Exteroceptor_Sensor", "IdentificationSensor", "Position_Sensor")),
    ("Doppler_Radar", ("Active_Sensor", "Exteroceptor_Sensor", "Speed_Sensor")),
    ("Doppler_Sound", ("Active_Sensor", "Exteroceptor_Sensor", "Speed_Sensor")),
    ("Force_Sensor", ("Exteroceptor_Sensor", "Passive_Sensor", "Touch_Sensor")),
    ("GPS", ("Active_Sensor", "Position_Sensor", "ProprioceptorSensor")),
    ("GPS_Altimeter", ("Altitude_Sensor",)),
    ("Gyroscope", ("Heading_Sensor", "Passive_Sensor")),
    ("Inclinometer", ("Heading_Sensor", "Passive_Sensor")),
    ("Inductive_Encoder", ("Active_Sensor", "Motor_Sensor")),
    ("Inertial_Unit", ("Heading_Sensor", "Speed_Sensor")),
    ("Lidar", ("Active_Sensor", "Exteroceptor_Sensor", "IdentificationSensor")),
    ("Magnetic_Encoder", ("Active_Sensor", "Motor_Sensor")),
    ("Magnetic_Sensor", ("Distance_Sensor", "Exteroceptor_Sensor")),
    ("Optical_Barrier", ("Active_Sensor", "Exteroceptor_Sensor", "Touch_Sensor")),
    ("Optical_Encoder", ("Active_Sensor", "Motor_Sensor")),
    ("Photodiode", ("Light_Sensor",)),
    ("Phototransistor", ("Light_Sensor",)),
    ("Potentiometer", ("Motor_Sensor", "Passive_Sensor")),
    ("Proximity_Sensor", ("Exteroceptor_Sensor", "Passive_Sensor", "Touch_Sensor")),
    ("RF_Beacon", ("Active_Sensor", "Exteroceptor_Sensor", "Position_Sensor")),
    ("Radar", ("Active_Sensor", "Distance_Sensor", "Exteroceptor_Sensor", "IdentificationSensor")),
    ("Radar_Altimeter", ("Altitude_Sensor",)),
    (
        "Radio_Frequency_Identification",
        ("Active_Sensor", "Exteroceptor_Sensor", "IdentificationSensor"),
    ),
    ("Reflective_Beacon", ("Active_Sensor", "Exteroceptor_Sensor", "Position_Sensor")),
    ("Resistive_Sensor", ("Exteroceptor_Sensor", "Passive_Sensor", "Touch_Sensor")),
    ("Resolver", ("Active_Sensor", "Motor_Sensor")),
    ("Sonar", ("Active_Sensor", "Distance_Sensor", "Exteroceptor_Sensor")),
    ("Sound", ("Exteroceptor_Sensor", "IdentificationSensor", "Passive_Sensor")),
    ("Structures_Light", ("Distance_Sensor",)),
    ("Switch", ("Exteroceptor_Sensor", "Passive_Sensor", "Touch_Sensor")),
    ("Torque_Sensor", ("Motor_Sensor", "Passive_Sensor")),
    ("Ultrasound", ("Active_Sensor", "Distance_Sensor", "Exteroceptor_Sensor", "IdentificationSensor")),
    ("Ultrasound_Beacon", ("Active_Sensor", "Exteroceptor_Sensor", "Position_Sensor")),
    ("WheelDropSensor", ("Touch_Sensor",)),
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


def define_sensor_module(onto) -> dict[str, type]:
    """Define the legacy ORKA sensor hierarchy on the given ontology."""
    sentinel = {
        "Active_Sensor": onto.Active_Sensor,
        "Distance_Sensor": onto.Distance_Sensor,
        "Lidar": onto.Lidar,
        "Camera": onto.Camera,
        "WheelDropSensor": onto.WheelDropSensor,
    }
    if all(sentinel.values()):
        return {"Lidar": onto.Lidar, "Camera": onto.Camera, "IMU": onto.IMU}

    if onto.Sensor is None:
        define_core_module(onto)

    with onto:
        # Legacy Heading_Sensor also specializes passive and proprioceptor sensors.
        if onto.Passive_Sensor is None:
            _ensure_class(onto, "Passive_Sensor", ("Sensor",))
        if onto.Passive_Sensor not in onto.Heading_Sensor.is_a:
            onto.Heading_Sensor.is_a.append(onto.Passive_Sensor)
        if onto.ProprioceptorSensor not in onto.Heading_Sensor.is_a:
            onto.Heading_Sensor.is_a.append(onto.ProprioceptorSensor)

        for class_name, parent_names in SENSOR_CLASS_SPECS:
            _ensure_class(onto, class_name, parent_names)

        # Backward-compatible alias retained for code that expects IMU.
        _ensure_class(onto, "IMU", ("Inertial_Unit",))

        if onto.mountedOn is None:
            class mountedOn(ObjectProperty):
                domain = [onto.Sensor]
                range = [onto.Robot]

    return {
        "Lidar": onto.Lidar,
        "Camera": onto.Camera,
        "IMU": onto.IMU,
    }


def build_sensor_ontology(base_iri: str = DEFAULT_BASE_IRI):
    """Convenience builder for core + sensors ontology."""
    onto = get_orka_ontology(base_iri=base_iri)
    define_core_module(onto)
    define_sensor_module(onto)
    return onto
