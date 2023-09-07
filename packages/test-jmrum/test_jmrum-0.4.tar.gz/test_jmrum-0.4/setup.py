
from setuptools import setup, find_packages

# Setting up
setup(
      
        name="test_jmrum", 
        version=0.4,
        author="Jessica Rumbelow",
        author_email="<jessica@leap-labs.com>",
        description="DESCRIPTION",
        long_description="LONG_DESCRIPTION",
        packages=find_packages(),
        install_requires=['torch', 'test'],
        
        keywords=["python", "leap"]
)
