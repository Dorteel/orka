"""Utilities for loading robot and sensor definitions from Xacro/URDF XML."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class SensorSpec:
    name: str
    sensor_type: str
    reference_link: str | None = None


@dataclass(frozen=True)
class RobotSpec:
    name: str
    sensors: tuple[SensorSpec, ...]


_XML_SUFFIXES = (
    ".urdf.xacro",
    ".xacro",
    ".urdf",
)

_SENSOR_NAME_HINTS = (
    "sensor",
    "camera",
    "imu",
    "lidar",
    "laser",
    "radar",
    "sonar",
    "depth",
)

_XACRO_SENSOR_MACRO_TYPES = {
    "xtion_pro_live": "camera",
    "orbbec_astra": "camera",
    "realsense": "camera",
    "stereo_camera": "camera",
    "lidar": "lidar",
    "laser": "laser",
    "imu": "imu",
}


def load_xacro(path: str | Path) -> ET.ElementTree:
    """Load a xacro/URDF file as XML."""
    source = Path(path)
    return ET.parse(source)


def parse_robot_spec(path: str | Path) -> RobotSpec:
    """Parse robot and sensor definitions from a xacro/URDF file or directory."""
    source = Path(path)
    files = _collect_sources(source)
    if not files:
        raise FileNotFoundError(f"No xacro/URDF files found at: {source}")

    robot_name: str | None = None
    sensors_by_name: dict[str, SensorSpec] = {}

    for file in files:
        try:
            root = load_xacro(file).getroot()
        except ET.ParseError:
            # Some robotics files may be templated and not directly parseable XML.
            continue

        root_name = root.attrib.get("name")
        if root_name and robot_name is None:
            robot_name = root_name

        for spec in _extract_sensor_specs(root):
            key = sanitize_iri_fragment(spec.name)
            sensors_by_name.setdefault(key, spec)

    if robot_name is None:
        robot_name = _default_robot_name(source)

    return RobotSpec(name=robot_name, sensors=tuple(sensors_by_name.values()))


def sanitize_iri_fragment(value: str) -> str:
    """Sanitize text so it can safely be used as an OWL individual name."""
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    if not cleaned:
        return "instance"
    if cleaned[0].isdigit():
        return f"n_{cleaned}"
    return cleaned


def _closest_gazebo_reference(
    element: ET.Element, parent_map: dict[ET.Element, ET.Element]
) -> str | None:
    """Find the surrounding gazebo reference for a sensor, if present."""
    parent = parent_map.get(element)
    while parent is not None:
        if parent.tag.endswith("gazebo"):
            return parent.attrib.get("reference")
        parent = parent_map.get(parent)
    return None


def _collect_sources(source: Path) -> list[Path]:
    if source.is_file():
        return [source]
    if not source.exists():
        return []
    files = [
        path
        for path in source.rglob("*")
        if path.is_file() and path.name.endswith(_XML_SUFFIXES)
    ]
    return sorted(files)


def _extract_sensor_specs(root: ET.Element) -> list[SensorSpec]:
    parent_map = {child: parent for parent in root.iter() for child in parent}
    specs: list[SensorSpec] = []

    for element in root.iter():
        local = _local_name(element.tag).lower()

        if local == "sensor":
            specs.append(
                SensorSpec(
                    name=element.attrib.get("name", "sensor"),
                    sensor_type=element.attrib.get("type", "unknown"),
                    reference_link=_closest_gazebo_reference(element, parent_map),
                )
            )
            continue

        if _is_xacro_tag(element.tag) and local in _XACRO_SENSOR_MACRO_TYPES:
            specs.append(
                SensorSpec(
                    name=element.attrib.get("name", local),
                    sensor_type=_XACRO_SENSOR_MACRO_TYPES[local],
                    reference_link=element.attrib.get("parent"),
                )
            )
            continue

        if local == "link":
            link_name = element.attrib.get("name", "")
            if _looks_like_sensor_name(link_name):
                specs.append(
                    SensorSpec(
                        name=link_name,
                        sensor_type=_infer_sensor_type(link_name),
                        reference_link=None,
                    )
                )

    return specs


def _local_name(tag: str) -> str:
    return tag.split("}", 1)[-1]


def _is_xacro_tag(tag: str) -> bool:
    return tag.startswith("{http://ros.org/wiki/xacro}")


def _looks_like_sensor_name(name: str) -> bool:
    normalized = name.strip().lower()
    if normalized.endswith("_link"):
        return False
    return any(hint in normalized for hint in _SENSOR_NAME_HINTS)


def _infer_sensor_type(name: str) -> str:
    normalized = name.strip().lower()
    if "camera" in normalized:
        return "camera"
    if "imu" in normalized:
        return "imu"
    if "lidar" in normalized or "laser" in normalized or "scan" in normalized:
        return "lidar"
    if "radar" in normalized:
        return "radar"
    if "sonar" in normalized:
        return "sonar"
    if "depth" in normalized:
        return "depth"
    return "unknown"


def _default_robot_name(source: Path) -> str:
    if source.is_dir():
        return source.name
    name = source.name
    for suffix in _XML_SUFFIXES:
        if name.endswith(suffix):
            return name[: -len(suffix)] or source.stem
    return source.stem
