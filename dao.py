import psycopg2 as pc2
import secrets

class Dao:
    def save(self, id, group):
        pass

    def get(self, id):
        pass

    def delete(self, id):
        pass


class DatabaseDao(Dao):
    def __init__(self):
        self.connection = pc2.connect(
            user=secrets.user,
            password=secrets.password,
            host=secrets.host,
            database=secrets.database,
            port=secrets.port
        )

    def save(self, id, group):
        cursor = self.connection.cursor()
        cursor.execute(f"INSERT INTO groups VALUES ({id}, '{group}')")
        self.connection.commit()
        cursor.close()

    def get(self, id):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT group_name FROM groups WHERE chat_id={id}")
        response = cursor.fetchone()
        if response is None:
            return None
        response = response[0]
        cursor.close()
        return response

    def delete(self, id):
        cursor = self.connection.cursor()
        cursor.execute(f"DELETE FROM groups WHERE chat_id={id}")
        self.connection.commit()
        cursor.close()


class InMemoryDao(Dao):
    def __init__(self):
        self.memory = {}

    def save(self, id, group):
        self.memory[id] = group

    def get(self, id):
        return self.memory[id]

    def delete(self, id):
        self.memory.pop(id)


if __name__ == '__main__':
    a = DatabaseDao()
    a.delete(228228)
    print((a.get(228228)))
