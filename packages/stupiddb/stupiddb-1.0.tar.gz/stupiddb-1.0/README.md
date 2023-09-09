# StupidDB

StupidDB is probably the stupidest database system ever made.

It's a simple KV Store, but every key is actually a directory, and inside this directory is a file containing the value of the key.

But it's still actually very easy to use!

## Here's the documentation :

You can install it using pip : `pip install stupiddb`

```python
import stupiddb

db = stupiddb.StupidDatabase("my_db")

db.set("cow", "mammal") # Set a KV pair

db.set_dict({"snake": "reptile", "mouse": "mammal", "crocodile": "reptile", "cat": "mammal"}) # Set multiple KV pairs using a dictionary syntax
 
print(f"The cow is a {db.get('cow')}") # Get a key's value

db.delete("cow") # Remove a key out of the database

database = db.get_as_dict() # Get the whole database as a dictionary

db.reset() # Remove all keys out of the database

```

And that's it!