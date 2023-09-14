class Dao:
    def save(self, id, group):
        pass

    def get(self, id):
        pass


class InMemoryDao(Dao):
    def __init__(self):
        self.memory = {}

    def save(self, id, group):
        self.memory[id] = group

    def get(self, id):
        return self.memory[id]
