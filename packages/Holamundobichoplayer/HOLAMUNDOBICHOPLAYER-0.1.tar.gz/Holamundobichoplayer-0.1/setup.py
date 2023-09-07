import setuptools
from pathlib import Path
longi= Path("README.md").read_text() 
setuptools.setup(
    name="Holamundobichoplayer",
    version= "0.01",
    long_description=longi,
    packages=setuptools.find_packages(
        exclude=["mocks","tests"]
    )
    


)