from setuptools import find_packages, setup

package_name = "memory_manager"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
    ],
    install_requires=["setuptools", "PyYAML"],
    zip_safe=True,
    maintainer="kai",
    maintainer_email="kai@example.com",
    description="ORKA ROS2 memory manager services.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "memory_manager_node = memory_manager.memory_manager_node:main",
        ],
    },
)
