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
    def get_connection(self):
        return pc2.connect(
            user=secrets.user,
            password=secrets.password,
            host=secrets.host,
            database=secrets.database,
            port=secrets.port
        )

    def save(self, id, group):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO groups VALUES ({id}, '{group}')")
        connection.commit()
        cursor.close()
        connection.close()

    def get(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT group_name FROM groups WHERE chat_id={id}")
        response = cursor.fetchone()
        if response is None:
            return None
        response = response[0]
        cursor.close()
        connection.close()
        return response

    def delete(self, id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM groups WHERE chat_id={id}")
        connection.commit()
        cursor.close()
        connection.close()


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
