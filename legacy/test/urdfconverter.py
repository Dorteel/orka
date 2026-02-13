import xml.etree.ElementTree as ET
from rdflib import Graph, Literal, RDF, URIRef, Namespace, XSD
from rdflib.namespace import SOSA, RDFS, OWL
from io import StringIO


class robot_graph():
    def __init__(self, model_path) -> None:
        # URDF model related variables
        self.model_path = model_path
        self.model = ET.parse(model_path)
        self.model_root = self.model.getroot()
        assert self.model_root.tag == 'robot', "Root is not robot! Check URDF file!"

        self.namespaces = self.get_namespaces()
        # Graph
        self.name = self.model_root.attrib['name']

        self.KnowRob = Namespace("http://knowrob.org/kb/knowrob.owl#")
        self.URDF = Namespace("http://knowrob.org/kb/urdf.owl#")
        self.SOMA = Namespace("http://www.ease-crc.org/ont/SOMA.owl#")
        self.robotNS = Namespace("http://example.org/" + self.name + '/')
        self.sensNS = Namespace(self.robotNS + 'sensors/')
        self.linksNS = Namespace(self.robotNS + 'links/')
        self.jointNS = Namespace(self.robotNS + 'joints/')
        self.actuatorNS = Namespace(self.robotNS + 'actuators/')
        self.sensPropNS = Namespace(self.robotNS + 'sensorProperties/')


        
        self.robotName = URIRef("http://example.org/" + self.name)
        self.robotKG = Graph().add((self.robotName, RDF.type, self.URDF.Robot))

        self.robotKG.bind('urdf', self.URDF)
        self.robotKG.bind('knowrob', self.KnowRob)
        self.robotKG.bind('self', self.robotNS)
        self.robotKG.bind('soma', self.SOMA)
        self.robotKG.bind('joints', self.jointNS)
        self.robotKG.bind('sensorProperty', self.sensPropNS)
        self.robotKG.bind('links', self.linksNS)

        self.robotKG.add((self.robotName, RDF.type, SOSA.Platform))
        self.robotKG.add((self.robotName, self.URDF.hasURDFName, Literal(self.name)))
        # Adding some ontology alignment statement
        self.robotKG.add((self.KnowRob.SensorDevice, OWL.sameAs, SOSA.Sensor))
        self.robotKG.add((self.URDF.Robot, RDFS.subClassOf, SOSA.Platform))
        # First find all the links and create them in the knowledgeBase
        self.find_links()
        self.find_joints()
        self.find_sensors()
        # Save the knowledgeGraph in the output folder
        self.robotKG.serialize(destination='output/' + self.name + ".ttl", format='ttl')


    def get_namespaces(self):
        '''
        Returns the namespaces defined in the URDF file
        '''
        f = open(self.model_path, "r")
        xml_data = f.read() 
        my_namespaces = dict([node for _, node in ET.iterparse(StringIO(xml_data), events=['start-ns'])])
        return my_namespaces

    
    def find_links(self):
        '''
        Looks through all the links and add them to the KG
         - name
         - mass
         - geometry (box, cylinder, sphere or mesh)
         http://wiki.ros.org/urdf/XML/link
        '''
        for link in self.model_root.findall("./link"):
            # Add the link with it's name to the Knowledge Graph
            linkNode = self.linksNS[link.attrib['name']]
            self.robotKG.add((linkNode, RDF.type, self.URDF.Link))
            self.robotKG.add((self.robotName, self.URDF.hasLink, linkNode))
            self.robotKG.add((linkNode, self.URDF.hasURDFName, Literal(link.attrib['name'])))
            
            # Check if the mass of the link is described
            if link.find('inertial'):
                massValue = link.find('inertial').find('mass').get('value')
                self.robotKG.add((linkNode, self.SOMA.hasMassValue, Literal(massValue, datatype=XSD.double)))
            
            # Add the shape of the objects and it's properties
            if link.find('.//collision/geometry'):
                shape = list(link.find('collision').find('geometry'))
                assert len(shape) == 1, 'Multiple shapes described for single link {}'.format(link.attrib['name'])
                shapeType = shape[0].tag.capitalize() + 'Shape'
                self.robotKG.add((linkNode, self.SOMA.hasCollisionShape, self.SOMA[shapeType]))
                if shapeType == 'BoxShape':
                    size = [float(x) for x in shape[0].attrib['size'].split(' ')]
                    self.robotKG.add((linkNode, self.SOMA.hasLength, Literal(size[0], datatype=XSD.float)))
                    self.robotKG.add((linkNode, self.SOMA.hasWidth, Literal(size[1], datatype=XSD.float)))
                    self.robotKG.add((linkNode, self.SOMA.hasDepth, Literal(size[2], datatype=XSD.float)))
                elif shapeType == 'CylinderShape':
                    self.robotKG.add((linkNode, self.SOMA.hasRadius, Literal(float(shape[0].attrib['radius']), datatype=XSD.double)))
                    self.robotKG.add((linkNode, self.SOMA.hasLength, Literal(float(shape[0].attrib['length']), datatype=XSD.double)))
                elif shapeType == 'SphereShape':
                    self.robotKG.add((linkNode, self.SOMA.hasRadius, Literal(float(shape[0].attrib['radius']), datatype=XSD.double)))
                else:
                    self.robotKG.add((linkNode, self.SOMA.hasFilePath, Literal(shape[0].attrib['filename'])))


    def find_joints(self):
        '''
        Looks through all the joints and add them to the KG
        So far it only looks at the name of the joint and the mass value if specified
        '''

        # Transmission joints are treated separately
        for actuator in self.model_root.findall("./transmission/actuator"):
            actNode = self.actuatorNS[actuator.attrib['name']] # Create a node
            self.robotKG.add((actNode, RDF.type, SOSA.Actuator))    # Add as actuator
            self.robotKG.add((self.robotName, SOSA.hosts, actNode)) # Add as part of the robot

        for joint in self.model_root.findall("./joint"):
            # Add the joint with it's name to the Knowledge Graph
            jointNode = self.jointNS[joint.attrib['name']]
            self.robotKG.add((self.robotName, self.URDF.hasJoint, jointNode))
            self.robotKG.add((jointNode, RDF.type, self.URDF[joint.attrib['type'].capitalize() + 'Joint']))
            self.robotKG.add((jointNode, self.URDF.hasURDFName, Literal(joint.attrib['name'])))
            if joint.attrib['type'] in ['revolute', 'prismatic']:
                axis = joint.find('axis').attrib['xyz']
                self.robotKG.add((jointNode, self.URDF.hasAxisVector, Literal(axis)))
                vel = Literal(joint.find('limit').attrib['velocity'], datatype=XSD.float)
                self.robotKG.add((jointNode, self.URDF.hasMaxJointVelocity, vel))
                lowLimit = Literal(joint.find('limit').attrib['lower'], datatype=XSD.float)
                upLimit =  Literal(joint.find('limit').attrib['upper'], datatype=XSD.float)
                self.robotKG.add((jointNode, self.URDF.hasLowerLimit, lowLimit))
                self.robotKG.add((jointNode, self.URDF.hasUpperLimit, upLimit))
            parent = self.robotNS[joint.find('parent').attrib['link']]
            child = self.robotNS[joint.find('child').attrib['link']]
            self.robotKG.add((jointNode, self.URDF.hasParentLink, parent))
            self.robotKG.add((jointNode, self.URDF.hasChildLink, child))


    def find_sensors(self):
        '''
        Adds the sensors and their properties to the graph
        http://sdformat.org/spec?ver=1.5&elem=sensor
        Considered sensors: http://wiki.ros.org/urdf/XML/sensor/proposals
        Uses sosa:Sensor
        '''
        sensorList = ["ray", "camera", "imu", "depth", "contact"]
        for sensorName in sensorList:
            sensorType = Literal(sensorName + "Sensor")
            self.robotKG.add((self.robotNS[sensorType], RDF.type, SOSA.Sensor))
            self.robotKG.add((self.robotNS[sensorType], RDF.type, self.KnowRob.SensorDevice))
        for sensor in self.model_root.findall(".//sensor"):
            sensNode = self.sensNS[sensor.attrib['name']] # Create a node
            self.robotKG.add((sensNode, RDF.type, SOSA.Sensor))    # Add as sensor
            self.robotKG.add((self.robotName, SOSA.hosts, sensNode)) # Add as part of the robot
            self.robotKG.add((sensNode, RDF.type, self.KnowRob.SensorDevice)) 
            # Add the properties of the sensor
            sensortype = sensor.find(sensor.attrib['type'])
            if sensor.attrib['type'] == 'depth': sensortype = sensor.find('camera')
            if not sensortype: continue
            self.robotKG.add((sensNode, RDF.type, self.sensNS[sensor.attrib['type']]))
            if sensortype.tag == 'ray':
                # Relevant fields are: samples, minRange, maxRange, resolution
                rangeElem = sensortype.find('range')
                if rangeElem:
                    minRange = Literal(rangeElem.find("min").text)
                    maxRange = Literal(rangeElem.find("max").text)
                    self.robotKG.add((sensNode,self.KnowRob.hasSensorRange, minRange))
                    self.robotKG.add((sensNode,self.KnowRob.hasSensorRange, maxRange)) 

            elif sensortype.tag in ['camera', 'depth']:
                
                fov = Literal(sensortype.find('horizontal_fov').text, datatype=XSD.float)
                imgWidth = Literal(sensortype.find('image/width').text, datatype=XSD.integer)
                imgHeight = Literal(sensortype.find('image/height').text, datatype=XSD.integer)
                self.robotKG.add((sensNode, self.sensPropNS.hasFieldOfView, fov))
                self.robotKG.add((sensNode, self.sensPropNS.hasImageWidth, imgWidth))
                self.robotKG.add((sensNode, self.sensPropNS.hasImageHeight, imgHeight))

if __name__ == "__main__":
    robots = ['test/pr2.urdf', 'test/turtlebot3_burger.urdf', 'test/locobot_wx250s.urdf']
    for robot in robots:
        # print('\n{}\n{}\n{}\n'.format('*'*len(robot), robot, '*'*len(robot)))
        robot_graph(robot)