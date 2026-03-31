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
                pass

            class Exteroceptor_Sensor(onto.Sensor):
                pass

            class Passive_Sensor(onto.Sensor):
                pass

            class IdentificationSensor(onto.Sensor):
                pass

            class Light_Sensor(onto.Sensor, Exteroceptor_Sensor):
                pass

            class Distance_Sensor(onto.Sensor, Exteroceptor_Sensor):
                pass

            class Touch_Sensor(onto.Sensor, Exteroceptor_Sensor):
                pass

            class Proximity_Sensor(Touch_Sensor, Passive_Sensor):
                pass

            class Resistive_Sensor(Touch_Sensor, Passive_Sensor):
                pass

            class Force_Sensor(Touch_Sensor, Exteroceptor_Sensor, Passive_Sensor):
                pass

            class Capacitive_Sensor(Distance_Sensor, Exteroceptor_Sensor, Passive_Sensor):
                pass

            class Magnetic_Sensor(Distance_Sensor, Exteroceptor_Sensor):
                pass

            class Position_Sensor(onto.PositionSensor):
                pass

            class Heading_Sensor(onto.HeadingSensor, Passive_Sensor):
                pass

            class Motor_Sensor(onto.ProprioceptorSensor):
                pass

            class Altitude_Sensor(onto.ProprioceptorSensor):
                pass

            class Speed_Sensor(onto.Sensor):
                pass

            class Torque_Sensor(Motor_Sensor, Passive_Sensor):
                pass

            class WheelDropSensor(Touch_Sensor):
                pass

            # -----------------------------------------------------------------
            # Characteristics
            # -----------------------------------------------------------------

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