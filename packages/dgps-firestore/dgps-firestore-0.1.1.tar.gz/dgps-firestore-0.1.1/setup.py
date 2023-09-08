import os
from setuptools import setup

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

# Get the subpackage to include from the environment variable
subpackage_to_include = os.environ.get('SUBPACKAGE_TO_INCLUDE', 'firestore')

# Construct the distribution name dynamically
distribution_name = f"dgps-{subpackage_to_include}"

# Read the requirements from the respective requirements.txt
with open(os.path.join(subpackage_to_include, 'requirements.txt')) as f:
    required_packages = f.read().splitlines()

setup(
    name=distribution_name,
    version=version,
    url="https://www.democracygps.org/team",
    author="Chris Krenn",
    author_email="crkrenn@gmail.com",
    description="Utility functions for DemocracyGPS",
    packages=[subpackage_to_include],  # Include the subpackage specified in the environment variable
    install_requires=required_packages,
)
