import sqlite3


class DBHelper:
    def __init__(self, dbname="../bot/db/students.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    def search_users(self, from_time: str, to_time: str):
        """Search user in database"""

        self.cursor.execute(
            "SELECT profiles.name, profiles.`group`, visits.timestamp from profiles "
            "JOIN visits on profiles.id = visits.user where "
            "visits.timestamp >= ? and visits.timestamp <= ?",
            (from_time, to_time,)
        )
        return self.cursor.fetchall()