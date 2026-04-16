from __future__ import annotations

import sys
from pathlib import Path

from owlready2 import Thing, get_ontology

from ontology_building.orka_core import OrkaCore

DEFAULT_OUTPUT = Path(__file__).resolve().with_name("orka-full.owl")

ORKA_SOURCE = Path(__file__).resolve().parent.parent / "orka.owl"
OBOE_STANDARDS_SOURCE = Path(__file__).resolve().parent.parent / "oboe-standards.owl"


class OrkaFull(OrkaCore):
    """Extends ORKA core with selected sensor types, characteristics, and standards."""

    def extend(self):

        onto = self.onto
        with onto:
            # -----------------------------------------------------------------
            # Sensor Types
            # -----------------------------------------------------------------

            class Active_Sensor(onto.Sensor):
                comment = ["A sensor that actively emits energy or signals to measure the environment."]

            class Passive_Sensor(onto.Sensor):
                comment = ["A sensor that observes naturally occurring signals without emitting energy."]

            class IdentificationSensor(onto.Sensor):
                comment = ["A sensor used for identifying entities, tags, or markers."]

            class Exteroceptor_Sensor(onto.Sensor):
                comment = ["A sensor that measures properties of the external environment."]

            class Distance_Sensor(onto.Sensor, Exteroceptor_Sensor):
                comment = ["A sensor that measures distance or range to external objects."]

            class Light_Sensor(onto.Sensor, Exteroceptor_Sensor):
                comment = ["A sensor that measures light or optical signals."]

            class Speed_Sensor(onto.Sensor):
                comment = ["A sensor that measures speed or velocity-related quantities."]

            class Position_Sensor(onto.Sensor):
                comment = ["A sensor that determines spatial position."]

            class Heading_Sensor(onto.Sensor, Passive_Sensor, onto.ProprioceptorSensor):
                comment = ["A sensor that measures heading or orientation."]

            class Touch_Sensor(onto.Sensor, Exteroceptor_Sensor):
                comment = ["A sensor that detects touch, contact, or impact."]

            class Altitude_Sensor(onto.Sensor, onto.ProprioceptorSensor):
                comment = ["A sensor that measures altitude relative to a reference level."]

            class Motor_Sensor(onto.Sensor, onto.ProprioceptorSensor):
                comment = ["A sensor that monitors motor or actuator state."]

            class Temperature_Sensor(onto.Sensor, onto.ProprioceptorSensor):
                comment = ["A sensor measuring the temperature."]

            class Pressure_Sensor(onto.Sensor, onto.Exteroceptor_Sensor):
                comment = ["A sensor measuring the temperature."]

            class Humidity_Sensor(onto.Sensor, onto.Exteroceptor_Sensor):
                comment = ["A sensor measuring the temperature."]

            # -----------------------------------------------------------------
            # Vision, ranging, and identification
            # -----------------------------------------------------------------

            class Camera(Distance_Sensor, Exteroceptor_Sensor, IdentificationSensor, Passive_Sensor, Speed_Sensor):
                comment = ["A passive visual sensor capturing image-based information."]

            class DepthCamera(Active_Sensor, Exteroceptor_Sensor, IdentificationSensor, Position_Sensor):
                comment = ["A camera-like sensor that actively acquires depth information."]

            class LiDAR(Active_Sensor, Exteroceptor_Sensor, IdentificationSensor):
                comment = ["A laser-based active sensor used for ranging and scene measurement."]

            class RPLIDAR_A2(LiDAR):
                comment = ["A specific LiDAR model represented as a subclass of LiDAR."]

            class Radar(Active_Sensor, Distance_Sensor, Exteroceptor_Sensor, IdentificationSensor):
                comment = ["A radio-based active sensor used for ranging and detection."]

            class Sonar(Active_Sensor, Distance_Sensor, Exteroceptor_Sensor):
                comment = ["A sound-based active sensor used for distance measurement."]

            class Ultrasound(Active_Sensor, Distance_Sensor, Exteroceptor_Sensor, IdentificationSensor):
                comment = ["An ultrasonic active sensor used for range or detection tasks."]

            class Structures_Light(Distance_Sensor):
                comment = ["A structured-light sensing device used for distance measurement."]

            class Active_Optical(Active_Sensor, Exteroceptor_Sensor, Position_Sensor):
                comment = ["An active optical positioning sensor."]

            class RF_Beacon(Active_Sensor, Exteroceptor_Sensor, Position_Sensor):
                comment = ["A radio-frequency beacon used for positioning or localization."]

            class Reflective_Beacon(Active_Sensor, Exteroceptor_Sensor, Position_Sensor):
                comment = ["A reflective beacon used for localization."]

            class Ultrasound_Beacon(Active_Sensor, Exteroceptor_Sensor, Position_Sensor):
                comment = ["An ultrasonic beacon used for localization."]

            class Radio_Frequency_Identification(Active_Sensor, Exteroceptor_Sensor, IdentificationSensor):
                comment = ["An RFID-based identification sensor."]

            class Optical_Barrier(Active_Sensor, Exteroceptor_Sensor, Touch_Sensor):
                comment = ["A sensor that detects interruption of a light beam."]

            # -----------------------------------------------------------------
            # Magnetic and light subtypes
            # -----------------------------------------------------------------

            class Magnetic_Sensor(Distance_Sensor, Exteroceptor_Sensor):
                comment = ["A sensor that measures magnetic field or magnetic proximity."]

            class Photodiode(Light_Sensor):
                comment = ["A semiconductor light sensor converting light into electrical current."]

            class Phototransistor(Light_Sensor):
                comment = ["A transistor-based light sensor responding to incident light."]

            # -----------------------------------------------------------------
            # Touch-related subtypes
            # -----------------------------------------------------------------

            class Bumper(Exteroceptor_Sensor, Passive_Sensor, Touch_Sensor):
                comment = ["A contact sensor that detects collisions or impacts."]

            class Contact_Array(Exteroceptor_Sensor, Passive_Sensor, Touch_Sensor):
                comment = ["An array of contact sensors detecting multiple touch points."]

            class Proximity_Sensor(Exteroceptor_Sensor, Passive_Sensor, Touch_Sensor):
                comment = ["A sensor detecting nearby objects without direct contact."]

            class Resistive_Sensor(Exteroceptor_Sensor, Passive_Sensor, Touch_Sensor):
                comment = ["A touch-related sensor based on resistive measurement."]

            class Force_Sensor(Exteroceptor_Sensor, Passive_Sensor, Touch_Sensor):
                comment = ["A sensor that measures force applied through contact."]

            class Switch(Exteroceptor_Sensor, Passive_Sensor, Touch_Sensor):
                comment = ["A binary touch or contact sensor."]

            class WheelDropSensor(Touch_Sensor):
                comment = ["A sensor that detects when a wheel is no longer supported by the ground."]

            # -----------------------------------------------------------------
            # Motion and inertial sensing
            # -----------------------------------------------------------------

            class Accelerometer(Exteroceptor_Sensor, Passive_Sensor, Speed_Sensor):
                comment = ["A sensor that measures linear acceleration."]

            class Doppler_Radar(Active_Sensor, Exteroceptor_Sensor, Speed_Sensor):
                comment = ["A radar sensor measuring motion via Doppler shift."]

            class Doppler_Sound(Active_Sensor, Exteroceptor_Sensor, Speed_Sensor):
                comment = ["A sound-based Doppler sensor measuring motion or speed."]

            class Inertial_Unit(Heading_Sensor, Speed_Sensor):
                comment = ["A sensor unit combining inertial measurements such as orientation and motion."]

            class Battery_Sensor(onto.ProprioceptorSensor):
                comment = ["A sensor unit combining inertial measurements such as orientation and motion."]

            # -----------------------------------------------------------------
            # Position and altitude sensing
            # -----------------------------------------------------------------

            class GPS(Active_Sensor, Position_Sensor, onto.ProprioceptorSensor):
                comment = ["A satellite-based positioning sensor."]

            class Barometric_Altimeter(Altitude_Sensor):
                comment = ["An altimeter estimating altitude from air pressure."]

            class GPS_Altimeter(Altitude_Sensor):
                comment = ["An altimeter estimating altitude from GPS signals."]

            class Radar_Altimeter(Altitude_Sensor):
                comment = ["An altimeter measuring altitude using radar reflection."]

            # -----------------------------------------------------------------
            # Heading sensing
            # -----------------------------------------------------------------

            class Compass(Heading_Sensor, Passive_Sensor):
                comment = ["A heading sensor based on magnetic north."]

            class Gyroscope(Heading_Sensor, Passive_Sensor):
                comment = ["A sensor measuring angular velocity or rotation."]

            class Inclinometer(Heading_Sensor, Passive_Sensor):
                comment = ["A sensor measuring tilt relative to gravity."]

            # -----------------------------------------------------------------
            # Motor sensing
            # -----------------------------------------------------------------

            class Capacity_Encoder(Active_Sensor, Motor_Sensor):
                comment = ["A motor encoder based on capacitive sensing principles."]

            class Inductive_Encoder(Active_Sensor, Motor_Sensor):
                comment = ["A motor encoder based on inductive sensing principles."]

            class Magnetic_Encoder(Active_Sensor, Motor_Sensor):
                comment = ["A motor encoder based on magnetic sensing principles."]

            class Optical_Encoder(Active_Sensor, Motor_Sensor):
                comment = ["A motor encoder based on optical sensing principles."]

            class Resolver(Active_Sensor, Motor_Sensor):
                comment = ["A rotary position sensor used for measuring motor shaft angle."]

            class Brush_Encoder(Motor_Sensor, Passive_Sensor):
                comment = ["A passive motor encoder using brush contact."]

            class Potentiometer(Motor_Sensor, Passive_Sensor):
                comment = ["A passive position sensor using variable resistance."]

            class Torque_Sensor(Motor_Sensor, Passive_Sensor):
                comment = ["A sensor measuring torque at a motor or actuator."]

            # -----------------------------------------------------------------
            # Thermal sensing
            # -----------------------------------------------------------------
            class Thermometer(Temperature_Sensor, Passive_Sensor):
                comment = ["A sensor measuring the temperature of the environment."]

            class Thermocamera(Temperature_Sensor, Passive_Sensor):
                comment = ["A camera providing temperature estimates of the field of view."]
            # -----------------------------------------------------------------
            # Acoustic sensing
            # -----------------------------------------------------------------

            class Sound(Exteroceptor_Sensor, IdentificationSensor, Passive_Sensor):
                comment = ["A passive sensor class for sound-based perception."]

            class Microphone(Sound):
                comment = ["A sensor that captures sound waves as audio signals."]

            # -----------------------------------------------------------------
            # Distance subtype
            # -----------------------------------------------------------------

            class Capacitive_Sensor(Distance_Sensor, Exteroceptor_Sensor, Passive_Sensor):
                comment = ["A passive capacitive sensor used for distance or proximity sensing."]

            # -----------------------------------------------------------------
            # Characteristics
            # -----------------------------------------------------------------

            class IdentificationCharacteristic(onto.Characteristic):
                pass

            class Name(IdentificationCharacteristic):
                pass

            class ID(IdentificationCharacteristic):
                pass

            class VisualCharactersitic(onto.Characteristic):
                pass

            class Color(VisualCharactersitic):
                pass

            class Pattern(VisualCharactersitic):
                pass

            class GeometricProperty(VisualCharactersitic):
                pass

            class Shape(GeometricProperty):
                pass

            class Structure(GeometricProperty):
                pass

            class SimpleStructure(Structure):
                pass

            class ComplexStructure(Structure):
                pass

            class SizeProperty(GeometricProperty):
                pass

            class Length(SizeProperty):
                pass

            class Width(SizeProperty):
                pass

            class Height(SizeProperty):
                pass

            class Depth(SizeProperty):
                pass

            class SurfaceArea(SizeProperty):
                pass

            class Volume(SizeProperty):
                pass

            class ActivityType(onto.Characteristic):
                pass

            class ObjectType(onto.Characteristic):
                pass

            class Position(onto.Characteristic):
                pass

            class Orientation(onto.Characteristic):
                pass

            # -----------------------------------------------------------------
            # Measurement Standards
            # -----------------------------------------------------------------
        
            onto.Standard("Acre")
            onto.Standard("AcreToMeterSquared")
            onto.Standard("AcreToSquareMeter")
            onto.Standard("Ampere")
            onto.Standard("Angstrom")
            onto.Standard("AngstromToMeter")
            onto.Standard("Are")
            onto.Standard("Bar")
            onto.Standard("BarToKilopascal")
            onto.Standard("Becquerel")
            onto.Standard("Bushel")
            onto.Standard("BushelToLiter")
            onto.Standard("Candela")
            onto.Standard("Celsius")
            onto.Standard("CelsiusToKelvin")
            onto.Standard("Centigram")
            onto.Standard("CentigramToKilogram")
            onto.Standard("Centimeter")
            onto.Standard("CentimeterCubed")
            onto.Standard("CentimeterPerSecond")
            onto.Standard("CentimeterSquared")
            onto.Standard("CentimeterToMeter")
            onto.Standard("Centisecond")
            onto.Standard("CentisecondToSecond")
            onto.Standard("Day")
            onto.Standard("Decibar")
            onto.Standard("DecibarToBar")
            onto.Standard("Decigram")
            onto.Standard("DecigramToKilogram")
            onto.Standard("Decimeter")
            onto.Standard("DecimeterToMeter")
            onto.Standard("Decisecond")
            onto.Standard("DecisecondToSecond")
            onto.Standard("DegreToRadian")
            onto.Standard("Degree")
            onto.Standard("Dekagram")
            onto.Standard("DekagramToKilogram")
            onto.Standard("Dekameter")
            onto.Standard("DekameterToMeter")
            onto.Standard("Dekasecond")
            onto.Standard("DekasecondToSecond")
            onto.Standard("FahrenheitDegree")
            onto.Standard("FahrenheitDegreeToKelvin")
            onto.Standard("Fathom")
            onto.Standard("FathomToMeter")
            onto.Standard("Foot")
            onto.Standard("FootGoldCoast")
            onto.Standard("FootGoldCoastToMeter")
            onto.Standard("FootSquared")
            onto.Standard("FootToMeter")
            onto.Standard("Gallon")
            onto.Standard("GallonToLiter")
            onto.Standard("Grad")
            onto.Standard("GradToRadian")
            onto.Standard("Gram")
            onto.Standard("GramPerGram")
            onto.Standard("GramPerLiter")
            onto.Standard("GramPerMeterCubed")
            onto.Standard("GramToKilogram")
            onto.Standard("Hectare")
            onto.Standard("Hectogram")
            onto.Standard("HectogramToKilogram")
            onto.Standard("Hectometer")
            onto.Standard("HectometerToMeter")
            onto.Standard("Hectopascal")
            onto.Standard("HectopascalToPascal")
            onto.Standard("Hectosecond")
            onto.Standard("HectosecondToSecond")
            onto.Standard("Hertz")
            onto.Standard("Hour")
            onto.Standard("HourToSecond")
            onto.Standard("Inch")
            onto.Standard("InchCubed")
            onto.Standard("InchToMeter")
            onto.Standard("Kelvin")
            onto.Standard("Kilogram")
            onto.Standard("KilogramPerLiter")
            onto.Standard("KilogramPerMeterCubed")
            onto.Standard("KilogramPerMeterSquared")
            onto.Standard("KilogramPerMeterSquaredPerDay")
            onto.Standard("Kilohertz")
            onto.Standard("Kiloliter")
            onto.Standard("Kilometer")
            onto.Standard("KilometerSquared")
            onto.Standard("KilometerToMeter")
            onto.Standard("Kilopascal")
            onto.Standard("Kilosecond")
            onto.Standard("KilosecondToSecond")
            onto.Standard("Knot")
            onto.Standard("LinkClarke")
            onto.Standard("LinkClarkeToMeter")
            onto.Standard("Liter")
            onto.Standard("LiterPerSecond")
            onto.Standard("LiterToMeterCubed")
            onto.Standard("Lumen")
            onto.Standard("Megagram")
            onto.Standard("MegagramToKilogram")
            onto.Standard("Megahertz")
            onto.Standard("Megameter")
            onto.Standard("MegameterToMeter")
            onto.Standard("Megasecond")
            onto.Standard("MegasecondToSecond")
            onto.Standard("Meter")
            onto.Standard("MeterCubed")
            onto.Standard("MeterPerSecond")
            onto.Standard("MeterSquared")
            onto.Standard("MicroeinsteinsPerMeterSquaredPerSecond")
            onto.Standard("Microgram")
            onto.Standard("MicrogramPerGram")
            onto.Standard("MicrogramPerLiter")
            onto.Standard("MicrogramPerMeterCubed")
            onto.Standard("MicrogramToKilogram")
            onto.Standard("Microliter")
            onto.Standard("Micrometer")
            onto.Standard("MicrometerSquared")
            onto.Standard("MicrometerToMeter")
            onto.Standard("MicromolePerKilogram")
            onto.Standard("MicromolePerLiter")
            onto.Standard("MicromolePerMeterCubed")
            onto.Standard("Micron")
            onto.Standard("MicronToMeter")
            onto.Standard("Microsecond")
            onto.Standard("MicrosecondToSecond")
            onto.Standard("MicrosiemensPerMeter")
            onto.Standard("Mile")
            onto.Standard("MileSquared")
            onto.Standard("MileToMeter")
            onto.Standard("Millibar")
            onto.Standard("MillibarToBar")
            onto.Standard("Milligram")
            onto.Standard("MilligramPerLiter")
            onto.Standard("MilligramPerMeterCubed")
            onto.Standard("MilligramPerMeterCubedPerDay")
            onto.Standard("MilligramPerMeterSquaredPerDay")
            onto.Standard("MilligramToKilogram")
            onto.Standard("Millihertz")
            onto.Standard("Milliliter")
            onto.Standard("MilliliterPerLIter")
            onto.Standard("Millimeter")
            onto.Standard("MillimeterSquared")
            onto.Standard("MillimeterToMeter")
            onto.Standard("MillimolePerLiter")
            onto.Standard("MillimolePerMeterCubed")
            onto.Standard("Millisecond")
            onto.Standard("MillisecondToSecond")
            onto.Standard("MillisiemensPerMeter")
            onto.Standard("Minute")
            onto.Standard("MinuteToSecond")
            onto.Standard("Mole")
            onto.Standard("MolePerLiter")
            onto.Standard("MolePerMeterCubed")
            onto.Standard("Nanogram")
            onto.Standard("NanogramPerLiter")
            onto.Standard("NanogramToKilogram")
            onto.Standard("Nanometer")
            onto.Standard("NanometerToMeter")
            onto.Standard("NanomolePerLiter")
            onto.Standard("Nanosecond")
            onto.Standard("NanosecondToSecond")
            onto.Standard("NauticalMile")
            onto.Standard("NauticalMileToMeter")
            onto.Standard("Newton")
            onto.Standard("NominalDay")
            onto.Standard("NominalDayToSecond")
            onto.Standard("NominalHour")
            onto.Standard("NominalHourToSecond")
            onto.Standard("NominalLeapYear")
            onto.Standard("NominalLeapYearToSecond")
            onto.Standard("NominalMinute")
            onto.Standard("NominalMinuteToSecond")
            onto.Standard("NominalWeek")
            onto.Standard("NominalWeekToSecond")
            onto.Standard("NominalYear")
            onto.Standard("NominalYearToSecond")
            onto.Standard("Number")
            onto.Standard("NumberPerMeterSquared")
            onto.Standard("PartPerThousand")
            onto.Standard("Pascal")
            onto.Standard("Percent")
            onto.Standard("Pint")
            onto.Standard("PintToLiter")
            onto.Standard("Pound")
            onto.Standard("PoundToKilogram")
            onto.Standard("PracticalSalinityUnit")
            onto.Standard("Quart")
            onto.Standard("QuartToLiter")
            onto.Standard("Radian")
            onto.Standard("ReciprocalMeter")
            onto.Standard("Second")
            onto.Standard("Siemens")
            onto.Standard("SiemensPerMeter")
            onto.Standard("Ton")
            onto.Standard("TonToKilogram")
            onto.Standard("Tonne")
            onto.Standard("TonneToKilogram")
            onto.Standard("Volt")
            onto.Standard("WattPerMeterSquared")
            onto.Standard("WattPerMeterSquaredPerSteradian")
            onto.Standard("Yard")
            onto.Standard("YardIndian")
            onto.Standard("YardIndianToMeter")
            onto.Standard("YardSquared")
            onto.Standard("YardToMeter")




    def save(self, output_path: str | Path = DEFAULT_OUTPUT):
        output_path = Path(output_path).resolve()
        self.build()
        self.onto.save(file=str(output_path), format="rdfxml")
        return output_path


def main():
    output_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    builder = OrkaFull()
    saved_path = builder.save(output_path)
    print(f"Saved ORKA full ontology to: {saved_path}")


if __name__ == "__main__":
    main()