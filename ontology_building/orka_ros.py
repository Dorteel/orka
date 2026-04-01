from __future__ import annotations

import sys
from pathlib import Path

from owlready2 import DataProperty, FunctionalProperty, ObjectProperty, Thing, Imp

from ontology_building.orka_core import OrkaCore

DEFAULT_OUTPUT = Path(__file__).resolve().with_name("orka-ros.owl")


class OrkaROS(OrkaCore):
    """Extends ORKA core with minimal ROS vocabulary."""

    def extend(self):
        onto = self.onto

        with onto:
            # -----------------------------------------------------------------
            # Core ROS classes
            # -----------------------------------------------------------------

            class ROSInterface(Thing):
                """A generic ROS communication interface."""

            class ROSTopic(ROSInterface):
                """A ROS topic used for publish/subscribe communication."""

            class ROSService(ROSInterface):
                """A ROS service used for request/response communication."""

            class ROSMessageType(Thing):
                """A ROS message or service type."""

            # -----------------------------------------------------------------
            # Object properties
            # -----------------------------------------------------------------

            class usesInterface(ObjectProperty):
                domain = [onto.System]
                range = [ROSInterface]

            class hasMessageType(ObjectProperty):
                domain = [ROSInterface]
                range = [ROSMessageType]

            # optional but handy from the start
            class publishesTo(ObjectProperty):
                domain = [onto.Procedure]
                range = [ROSTopic]

            class subscribesTo(ObjectProperty):
                domain = [onto.Procedure]
                range = [ROSTopic]

            class hasBaseROSTopic(ObjectProperty):
                domain = [onto.Sensor]
                range = [ROSTopic]

            class callsService(ObjectProperty):
                domain = [onto.System]
                range = [ROSService]

            class providesService(ObjectProperty):
                domain = [onto.Procedure]
                range = [ROSService]

            # -----------------------------------------------------------------
            # Data properties
            # -----------------------------------------------------------------

            class hasROSName(DataProperty, FunctionalProperty):
                domain = [ROSInterface]
                range = [str]

            class hasROSPackage(DataProperty, FunctionalProperty):
                domain = [ROSMessageType]
                range = [str]

            class hasROSTypeName(DataProperty, FunctionalProperty):
                domain = [ROSMessageType]
                range = [str]

            # -----------------------------------------------------------------
            # Sensory ROS message types (instances)
            # -----------------------------------------------------------------

            sensor_msgs = {
                "PointCloud": "Legacy point cloud representation using geometry_msgs/Point32.",
                "PointCloud2": "Standard structured point cloud message used by most depth sensors.",
                "Imu": "Inertial measurement unit data including orientation, angular velocity, and acceleration.",
                "CompressedImage": "Compressed image transport format used for efficient image streaming.",
                "TimeReference": "Time reference from an external source such as GPS.",
                "Range": "Single range reading from distance sensors such as sonar or IR.",
                "Illuminance": "Ambient light intensity measurement.",
                "PointField": "Definition of a field within a PointCloud2 message.",
                "MagneticField": "Magnetometer measurement of magnetic field strength.",
                "CameraInfo": "Camera calibration parameters and intrinsic matrix.",
                "JoyFeedbackArray": "Array of feedback commands for joystick devices.",
                "JoyFeedback": "Single feedback command for a joystick device.",
                "NavSatFix": "Global navigation satellite system fix including latitude, longitude, and altitude.",
                "ChannelFloat32": "Channel of float32 values used in older point cloud messages.",
                "Temperature": "Temperature measurement from a sensor.",
                "Joy": "Joystick input including axes and button states.",
                "MultiDOFJointState": "State of joints with multiple degrees of freedom.",
                "LaserEcho": "Echo measurements from a laser scanner.",
                "RelativeHumidity": "Relative humidity measurement.",
                "NavSatStatus": "Status information for GNSS navigation messages.",
                "FluidPressure": "Fluid pressure measurement such as barometric pressure.",
                "BatteryState": "Battery status including voltage, current, and charge.",
                "RegionOfInterest": "Subregion definition within an image.",
                "JointState": "Joint position, velocity, and effort states.",
                "LaserScan": "2D laser range scan from a lidar sensor.",
                "Image": "Raw uncompressed image message.",
                "MultiEchoLaserScan": "Laser scan containing multiple echoes per beam.",
            }

            for msg, description in sensor_msgs.items():
                instance_name = f"sensor_msgs_msg_{msg}"

                m = ROSMessageType(instance_name)
                m.hasROSName = f"sensor_msgs/msg/{msg}"
                m.hasROSPackage = "sensor_msgs"
                m.hasROSTypeName = msg

                # Owlready comment annotation
                m.comment.append(description)

            # -----------------------------------------------------------------
            # SWRL rules:
            # Sensor(?s) ^ hasBaseROSTopic(?s, ?t) ^ hasMessageType(?t, ?m) ^
            # hasROSName(?m, "...") -> Camera(?s)
            # -----------------------------------------------------------------

            rules = [
                ("infer_camera_from_image",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/Image") -> Camera(?s)'),

                ("infer_camera_from_compressed_image",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/CompressedImage") -> Camera(?s)'),

                ("infer_camera_from_camera_info",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/CameraInfo") -> Camera(?s)'),

                ("infer_pointcloud_sensor_from_pointcloud",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/PointCloud") -> PointCloudSensor(?s)'),

                ("infer_pointcloud_sensor_from_pointcloud2",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/PointCloud2") -> PointCloudSensor(?s)'),

                ("infer_imu_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/Imu") -> IMUSensor(?s)'),

                ("infer_time_reference_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/TimeReference") -> TimeReferenceSensor(?s)'),

                ("infer_range_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/Range") -> Distance_Sensor(?s)'),

                ("infer_illuminance_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/Illuminance") -> IlluminanceSensor(?s)'),

                ("infer_magnetic_field_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/MagneticField") -> MagneticFieldSensor(?s)'),

                ("infer_joy_device_from_feedback_array",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/JoyFeedbackArray") -> JoyInputDevice(?s)'),

                ("infer_joy_device_from_feedback",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/JoyFeedback") -> JoyInputDevice(?s)'),

                ("infer_gnss_sensor_from_fix",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/NavSatFix") -> GNSSSensor(?s)'),

                ("infer_gnss_sensor_from_status",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/NavSatStatus") -> GNSSSensor(?s)'),

                ("infer_pointcloud_sensor_from_channelfloat32",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/ChannelFloat32") -> PointCloudSensor(?s)'),

                ("infer_temperature_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/Temperature") -> TemperatureSensor(?s)'),

                ("infer_joy_device_from_joy",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/Joy") -> JoyInputDevice(?s)'),

                ("infer_joint_encoder_from_multidofjointstate",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/MultiDOFJointState") -> JointEncoder(?s)'),

                ("infer_lidar_from_laserecho",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/LaserEcho") -> Lidar(?s)'),

                ("infer_humidity_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/RelativeHumidity") -> HumiditySensor(?s)'),

                ("infer_pressure_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/FluidPressure") -> PressureSensor(?s)'),

                ("infer_battery_sensor",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/BatteryState") -> BatterySensor(?s)'),

                ("infer_camera_from_roi",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/RegionOfInterest") -> Camera(?s)'),

                ("infer_joint_encoder_from_jointstate",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/JointState") -> JointEncoder(?s)'),

                ("infer_lidar_from_laserscan",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/LaserScan") -> Lidar(?s)'),

                ("infer_lidar_from_multiecholaserscan",
                 'Sensor(?s), hasBaseROSTopic(?s, ?t), hasMessageType(?t, ?m), hasROSName(?m, "sensor_msgs/msg/MultiEchoLaserScan") -> Lidar(?s)'),
            ]

            for rule_name, rule_body in rules:
                rule = Imp(rule_name)
                rule.set_as_rule(rule_body)


def main():
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    builder = OrkaROS()
    saved_path = builder.save(output_path)
    print(f"Saved ORKA ROS ontology to: {saved_path}")


if __name__ == "__main__":
    main()