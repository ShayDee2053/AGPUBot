import psycopg2 as pc2
import secrets

class Dao:
    def save(self, id, group, user_name, first_name):
        pass

    def get(self, id):
        pass

    def get_username_by_id(self, chat_id):
        pass

    def get_ids_by_group(self, group_name):
        pass

    def delete(self, id):
        pass


class DatabaseDao(Dao):
    def get_connection(self):
        try:
            pc2.connect(user=secrets.user, password=secrets.password, host=secrets.host, database=secrets.database, port=secrets.port)
        except:
            return "db_error"
        return pc2.connect(
            user=secrets.user,
            password=secrets.password,
            host=secrets.host,
            database=secrets.database,
            port=secrets.port
        )

    def save(self, id, group, user_name, first_name):
        connection = self.get_connection()
        if connection == "db_error":
            return "db_error"
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO groups VALUES ({id}, '{group}')")
        cursor.execute(f"INSERT INTO usernames VALUES ({id}, '{user_name}')")
        cursor.execute(f"INSERT INTO first_names VALUES ({id}, '{first_name}')")
        connection.commit()
        cursor.close()
        connection.close()

    def get_ids_by_group(self, group_name):
        connection = self.get_connection()
        if connection == "db_error":
            return "db_error"
        cursor = connection.cursor()
        cursor.execute(f"select chat_id from groups where group_name='2{group_name}'")
        ids = []
        response = cursor.fetchall()
        for row in response:
            ids.append(row[0])
        cursor.close()
        connection.close()
        return ids

    def get_username_by_id(self, chat_id):
        connection = self.get_connection()
        if connection == "db_error":
            return "db_error"
        cursor = connection.cursor()
        cursor.execute(f"select user_name from usernames where chat_id={chat_id}")
        response = cursor.fetchone()
        if response is None:
            return None
        response = response[0]
        cursor.close()
        connection.close()
        return response

    def get(self, id):
        connection = self.get_connection()
        if connection == "db_error":
            return "db_error"
        cursor = connection.cursor()
        cursor.execute(f"SELECT group_name FROM groups WHERE chat_id={id}")
        response = cursor.fetchone()
        if response is None:
            return None
        response = response[0]
        cursor.close()
        connection.close()
        return response

    def is_available(self):
        if self.get_connection() == "db_error":
            return False
        return True

    def delete(self, id):
        connection = self.get_connection()
        if connection == "db_error":
            return "db_error"
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM groups WHERE chat_id={id}")
        cursor.execute(f"DELETE FROM usernames WHERE chat_id={id}")
        cursor.execute(f"DELETE FROM first_names WHERE chat_id={id}")
        connection.commit()
        cursor.close()
        connection.close()


class InMemoryDao(Dao):
    def __init__(self):
        self.memory = {}

    def save(self, id, group, user_name, first_name):
        self.memory[id] = group

    def get(self, id):
        return self.memory[id]

    def delete(self, id):
        self.memory.pop(id)


if __name__ == '__main__':
    a = DatabaseDao()
    print(a.get_ids_by_group("ВМ-ИВТ-2-1"))
