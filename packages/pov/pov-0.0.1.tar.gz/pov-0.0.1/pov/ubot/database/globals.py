from . import cli
from typing import Dict, List, Union

collection = cli["pov"]["globals"]

class Globals:
    def __init__(self, variable, value):
        self.variable = str(variable)
        self.value = value

    def to_dict(self):
        return {"variable": self.variable, "value": self.value}

    @staticmethod
    def from_dict(dict):
        return Globals(dict["variable"], dict["value"])

async def gvarstatus(variable):
    result = await collection.find_one({"variable": str(variable)})
    if result is not None:
        return result["value"]
    else:
        return None

async def addgvar(variable, value):
    await collection.replace_one({"variable": str(variable)}, Globals(str(variable), value).to_dict(), upsert=True)

async def delgvar(variable):
    await collection.delete_one({"variable": str(variable)})
