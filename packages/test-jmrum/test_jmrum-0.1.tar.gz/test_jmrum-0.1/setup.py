
from setuptools import setup, find_packages

VERSION = "0.0.1" 
DESCRIPTION = "My first Python package"
LONG_DESCRIPTION = "My first Python package with a slightly longer description"

# Setting up
setup(
      
        name="test_jmrum", 
        version=0.1,
        author="Jessica Rumbelow",
        author_email="<jessica@leap-labs.com>",
        description="DESCRIPTION",
        long_description="LONG_DESCRIPTION",
        packages=find_packages(),
        install_requires=['pytorch'],
        
        keywords=["python", "leap"]
)
