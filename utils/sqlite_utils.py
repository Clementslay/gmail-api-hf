import sqlite3


class SqliteUtils:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None

    def connect(self):
        print(f"Establing connection to DB: `{self.db_name}`..")
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        print("Connection established successfully")

    def execute_query(self, query):
        print(f"Executing query: {query}")
        self.cursor.execute(query)
        self.conn.commit()
        print("Query executed successfully")

        return self.query_results_as_dict(rows=self.cursor.fetchall())

    def execute_many(self, query, data):
        print(f"Executing execute many query: {query}")
        self.cursor.executemany(query, self.convert_to_tuple_list(data))
        self.conn.commit()
        print("Execute many query executed successfully")
        return self.cursor.fetchall()

    def convert_to_tuple_list(self, dict_list):
        return list(map(lambda d: (d['id'], d['from'], d['to'], d['subject'], d['date_received']), dict_list))

    def query_results_as_dict(self, rows):
        if not self.cursor.description:
            return rows

        column_names = [description[0] for description in self.cursor.description]
        return [dict(zip(column_names, row)) for row in rows]

    def __del__(self):
        print("Closing connection..")
        self.conn.close()
        print("Connection closed.")
