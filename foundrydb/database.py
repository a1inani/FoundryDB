import os
# An abstraction of a Database
class Database:
    def __init__(self, name):
        self._name = name
        nested_path = "foundries/"+name
        try:
            os.makedirs(nested_path, exist_ok=True) # exist_ok=True prevents error if folder already exists
            print(f"FoundryDB ready at {nested_path}")
        except Exception as e:
            print(f"An error occurred: {e}")