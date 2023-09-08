# Load the urdf_parser_py manifest, you use your own package
# name on the condition but in this case, you need to depend on
# urdf_parser_py.
import roslib; roslib.load_manifest('urdfdom_py')
import rospy

# Import the module

from urdf_parser_py.urdf import URDF

# 1. Parse a string containing the robot description in URDF.
# Pro: no need to have a roscore running.
# Cons: n/a
# Note: it is rare to receive the robot model as a string.
robot = URDF.from_xml_string("<robot name='myrobot'></robot>")

# - OR -

# 2. Load the module from a file.
# Pro: no need to have a roscore running.
# Cons: using hardcoded file location is not portable.
robot = URDF.from_xml_file()

# - OR -

# 3. Load the module from the parameter server.
# Pro: automatic, no arguments are needed, consistent
#      with other ROS nodes.
# Cons: need roscore to be running and the parameter to
#      to be set beforehand (through a roslaunch file for
#      instance).
robot = URDF.from_parameter_server()

# Print the robot
print(robot)