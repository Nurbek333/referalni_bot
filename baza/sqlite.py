import sqlite3

class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db
        self.create_table_users()
        self.create_table_referrals()

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users(
            full_name TEXT,
            telegram_id INTEGER UNIQUE,
            referral_link TEXT,
            points INTEGER DEFAULT 0
        );
        """
        self.execute(sql, commit=True)


    def create_table_referrals(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Referrals(
            referrer_id INTEGER,
            referred_id INTEGER
        );
        """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, telegram_id: int, full_name: str, referral_link: str = None):
        sql = """
        INSERT INTO Users (telegram_id, full_name, referral_link)
        VALUES (?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
        full_name=excluded.full_name,
        referral_link=excluded.referral_link;
        """
        self.execute(sql, parameters=(telegram_id, full_name, referral_link), commit=True)

    def add_referral(self, referrer_id: int, referred_id: int):
        sql = """
        INSERT INTO Referrals (referrer_id, referred_id)
        VALUES (?, ?);
        """
        self.execute(sql, parameters=(referrer_id, referred_id), commit=True)

    def add_points(self, telegram_id: int, points: int):
        sql = """
        UPDATE Users SET points = points + ?
        WHERE telegram_id = ?;
        """
        self.execute(sql, parameters=(points, telegram_id), commit=True)

    def add_points_column(self):
        sql = """
        ALTER TABLE Users ADD COLUMN points INTEGER DEFAULT 0;
        """
        self.execute(sql, commit=True)


    def get_user_points(self, telegram_id: int):
        sql = "SELECT points FROM Users WHERE telegram_id = ?;"
        result = self.execute(sql, parameters=(telegram_id,), fetchone=True)
        return result[0] if result else 0

    def get_username(self, telegram_id: int):
        sql = "SELECT full_name FROM Users WHERE telegram_id = ?;"
        result = self.execute(sql, parameters=(telegram_id,), fetchone=True)
        return result[0] if result else None

    def select_all_users(self):
        sql = "SELECT * FROM Users;"
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)[0]

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE;", commit=True)

    def all_users_id(self):
        return self.execute("SELECT telegram_id FROM Users;", fetchall=True)
    
    def user_exists(self, telegram_id):
        sql = "SELECT COUNT(*) FROM Users WHERE telegram_id = ?;"
        result = self.execute(sql, parameters=(telegram_id,), fetchone=True)
        return result[0] > 0

    def add_referral_link_column(self):
        sql = """
        ALTER TABLE Users ADD COLUMN referral_link TEXT;
        """
        self.execute(sql, commit=True)

    def recreate_table_users(self):
        self.execute("DROP TABLE IF EXISTS Users;", commit=True)
        self.create_table_users()


def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
