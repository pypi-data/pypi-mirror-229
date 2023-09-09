import os
import json

# TODO:
#     repo
#     delete

class StupidDatabase:


    def __init__(self, name):
        """
        name: the name of the database

        Create/Load the database
        """
        self.name = name
        if self.name not in os.listdir():
            os.mkdir(self.name)


    def set(self, key: str, value):
        """
        key: the key, has to be str
        value: the value, can be any type

        Set a key to a value in the database
        """
        try:
            os.mkdir(self.name + "/" + key)
        except FileExistsError:
            pass

        if type(value) == str:
            open(self.name + "/" + key + "/type", "w").write("str")
        elif type(value) == int:
            open(self.name + "/" + key + "/type", "w").write("int")
        elif type(value) == float:
            open(self.name + "/" + key + "/type", "w").write("float")
        elif type(value) == bool:
            open(self.name + "/" + key + "/type", "w").write("bool")
        elif type(value) in [list, dict, tuple]:
            open(self.name + "/" + key + "/type", "w").write("json")
        
        open(self.name + "/" + key + "/value", "w").write(str(value)) if type(value) not in [list, dict, tuple, set] else json.dump(value, open(self.name + "/" + key + "/value", "w"))
    
    def set_dict(self, dictionary: dict):
        """
        dictionary: the dictionary

        Convert a dictionary into a bunch of key value pairs
        """

        for key in dictionary:
            self.set(key, dictionary[key])

    def get(self, key: str):
        """
        Get a key's value
        """

        try:
            value_type = open(self.name + "/" + key + "/type", "r").read()
            value = open(self.name + "/" + key + "/value", "r").read()
        except FileNotFoundError:
            raise KeyError(f"Key '{key}' does not exist")
        
        if value_type == "str":
            return value
        elif value_type == "int":
            return int(value)
        elif value_type == "float":
            return float(value)
        elif value_type == "bool":
            return True if value == "True" or value == "true" else False
        elif value_type == "json":
            return json.loads(value)
    
    def delete(self, key: str):
        """
        Delete a key
        """
        try:
            for file in os.listdir(self.name + "/" + key):
                os.remove(self.name + "/" + key + "/" + file)
            os.rmdir(self.name + "/" + key)
        except FileNotFoundError:
            raise KeyError(f"Key '{key}' does not exist")
    
    def get_as_dict(self):
        """
        Get the whole database as a dictionary
        """

        db = {}

        for dir in os.listdir(self.name):
            db[dir] = self.get(dir)
        
        return db

    def reset(self):
        """
        Reset the whole database to zero!
        """
        for key in os.listdir(self.name):
            if key != ".DS_STORE": self.delete(key) 