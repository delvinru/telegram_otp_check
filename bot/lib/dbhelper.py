from loguru import logger
import sqlite3


class DBHelper:
    def __init__(self, dbname="db/students.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.cursor = self.conn.cursor()
    
    def setup(self):
        """Setup database"""

        logger.info('Initialize database')

        query = """CREATE TABLE IF NOT EXISTS profiles (
            `id` INTEGER PRIMARY KEY,
            `username` TEXT NOT NULL,
            `name` TEXT NOT NULL,
            `group` TEXT NOT NULL,
            `id_card` TEXT NOT NULL
        )"""

        self.cursor.execute(query)

        query = """CREATE TABLE IF NOT EXISTS visits (
            id INTEGER  PRIMARY KEY AUTOINCREMENT, 
            user INTEGER, 
            timestamp DATETIME DEFAULT (datetime('now','localtime'))
        )"""

        self.cursor.execute(query)
        self.conn.commit()
    
    def init_user(self, uid=None, username=None, name=None, group=None, id_card=None):
        """Register user in database"""

        self.cursor.execute(
            'INSERT INTO `profiles` (`id`, `username`, `name`, `group`, `id_card`) VALUES (?, ?, ?, ?, ?)', 
            (uid, username, name, group, id_card,)
        )

        logger.info(f'{uid} {username} {name} registered')
        self.conn.commit()
    
    def search_user(self, uid=None):
        """Search user in database"""

        self.cursor.execute('SELECT `id`,`name` from `profiles` WHERE `id`=?', (uid,))
        return self.cursor.fetchone()
    
    def mark_user(self, uid=None):
        """Mark a user in the database if they want to register for a class"""

        self.cursor.execute('INSERT INTO visits (user) VALUES(?)', (str(uid),))
        self.conn.commit()