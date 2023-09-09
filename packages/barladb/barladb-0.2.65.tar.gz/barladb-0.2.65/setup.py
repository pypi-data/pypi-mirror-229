from setuptools import setup

setup(
    name='barladb',
    version='0.2.65',
    description='Module for working with JSON file data',
    packages=['barladb'],
    author="barlin41k",
    zip_safe=False,
    long_description='''
# Изменения:
- English interface
- Minor changes to the interface and commands

# ToDo:
- None


# What is BarlaDB?
- `BarlaDB` is a library that is created for working with local databases in `.json` format. Has well-developed functions and logging! And most importantly, it has a very easy-to-learn interface, even for a beginner!

# Quickstart
```python
from barladb import db #Imports DB functions
from barladb import config #imports config
import socket
config.debug = True #Debug ON
config.log = True #Log ON

barladb = db.BarlaDB() #Creating an instance of a class
data = barladb.get("example.json") #We get the contents of the database and save it into the "data" variable
#Also, if your file is in a different directory:
#db.get("path/to/file/example")

print("Hello, User! Your computer name already in example.json.")
data["name"] = socket.gethostname()
barladb.save("example.json", data) #Saving the "data" variable to example.json
"""
My example.json looks like this:
    {
    "name": "barlin41k"
    }
In column "name", should be your hostname, but since mine is barlin41k, it comes out like this.
Let me remind you that this is just a short example of using the module.
"""
```
# How to install?
- `pip install barladb`

# Peculiarities BarlaDB:
- Has an easy and intuitive interface.
- Has no dependencies
- Everything is built in the popular `.json` data format.

# Links:
- [Documentation](https://sites.google.com/view/barladb/)
- [Github](https://github.com/barlin41k/barladb/)
- [PyPi](https://pypi.org/project/barladb/)
    ''',
    long_description_content_type="text/markdown",
    url="https://github.com/barlin41k/barladb",
    project_urls={
        "Documentation": "https://sites.google.com/view/barladb/",
        "GitHub": "https://github.com/barlin41k/barladb",
    })