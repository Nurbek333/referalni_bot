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
        if parameters is None:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        try:
            cursor.execute(sql, parameters)
            if commit:
                connection.commit()
            if fetchall:
                data = cursor.fetchall()
            if fetchone:
                data = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            points INTEGER DEFAULT 0,
            referrer_id INTEGER,
            level_1_points INTEGER DEFAULT 0,
            level_2_points INTEGER DEFAULT 0,
            level_3_points INTEGER DEFAULT 0
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

    def add_user(self, user_id, username, referrer_id=None):
        sql = "INSERT INTO users (user_id, username, referrer_id) VALUES (?, ?, ?)"
        self.execute(sql, parameters=(user_id, username, referrer_id), commit=True)

        # Referal tizimini yangilash
        if referrer_id:
            # 1-daraja uchun ball qo'shish
            self.add_points(referrer_id, 1, level=1)
            
            # 2-daraja uchun ball qo'shish
            referrer_level_2 = self.get_referrer(referrer_id)
            if referrer_level_2:
                self.add_points(referrer_level_2, 0.5, level=2)
                
                # 3-daraja uchun ball qo'shish
                referrer_level_3 = self.get_referrer(referrer_level_2)
                if referrer_level_3:
                    self.add_points(referrer_level_3, 0.25, level=3)

    def add_referral(self, referrer_id: int, referred_id: int):
        sql = """
        INSERT INTO Referrals (referrer_id, referred_id)
        VALUES (?, ?);
        """
        self.execute(sql, parameters=(referrer_id, referred_id), commit=True)

        # Update referral count and points
        self.increment_referral_count(referrer_id)
        self.add_points(referrer_id, 1)
        self.add_points_for_referrer_chain(referrer_id, 0.5)

    def increment_referral_count(self, referrer_id: int):
        sql = """
        UPDATE users SET referral_count = referral_count + 1
        WHERE user_id = ?;
        """
        self.execute(sql, parameters=(referrer_id,), commit=True)

    def add_points(self, user_id, points, level=1):
        if level == 1:
            sql = "UPDATE users SET points = points + ?, level_1_points = level_1_points + ? WHERE user_id = ?"
        elif level == 2:
            sql = "UPDATE users SET points = points + ?, level_2_points = level_2_points + ? WHERE user_id = ?"
        elif level == 3:
            sql = "UPDATE users SET points = points + ?, level_3_points = level_3_points + ? WHERE user_id = ?"
        self.execute(sql, parameters=(points, points, user_id), commit=True)

    def get_user_points(self, user_id: int):
        sql = "SELECT points FROM users WHERE user_id = ?;"
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] if result else 0

    def get_username(self, user_id: int):
        sql = "SELECT username FROM users WHERE user_id = ?;"
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] if result else None

    def select_all_users(self):
        sql = "SELECT * FROM users;"
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM users;", fetchone=True)[0]

    def delete_users(self):
        self.execute("DELETE FROM users WHERE TRUE;", commit=True)

    def all_users_id(self):
        return self.execute("SELECT user_id FROM users;", fetchall=True)

    def user_exists(self, user_id: int):
        sql = "SELECT COUNT(*) FROM users WHERE user_id = ?;"
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] > 0

    def add_referral_link_column(self):
        sql = """
        ALTER TABLE users ADD COLUMN referral_link TEXT;
        """
        self.execute(sql, commit=True)

    def recreate_table_users(self):
        self.execute("DROP TABLE IF EXISTS users;", commit=True)
        self.create_table_users()

    def add_referrer_id_column(self):
        sql = """
        ALTER TABLE users ADD COLUMN referrer_id INTEGER;
        """
        try:
            self.execute(sql, commit=True)
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e):
                print("Referrer ID column already exists.")

    def get_user_friends_recursive(self, user_id: int, level=0, max_level=3):
        if level > max_level:
            return []

        sql = """
        WITH RECURSIVE friends(id, username, level) AS (
            SELECT user_id, username, 0
            FROM users
            WHERE user_id = ?
            UNION ALL
            SELECT u.user_id, u.username, f.level + 1
            FROM users u
            INNER JOIN friends f ON u.referrer_id = f.id
        )
        SELECT id, username FROM friends;
        """
        friends = self.execute(sql, parameters=(user_id,), fetchall=True)
        return friends

    def add_points_for_referrer_chain(self, user_id: int, points: float):
        current_level = 1
        while current_level <= 3:
            referrer_id = self.get_user_referrer(user_id)
            if referrer_id:
                self.add_points(referrer_id, points, level=current_level)
                user_id = referrer_id
                points *= 0.5  # Reduce points for each level
                current_level += 1
            else:
                break

    def get_user_referrer(self, user_id: int):
        sql = "SELECT referrer_id FROM users WHERE user_id = ?;"
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] if result else None

    def get_referrer(self, user_id):
        sql = "SELECT referrer_id FROM users WHERE user_id = ?;"
        result = self.execute(sql, parameters=(user_id,), fetchone=True)
        return result[0] if result else None


    def get_top_users_by_points(self, top_n=10):
        sql = """
        SELECT user_id, username, SUM(points) AS total_points
        FROM users
        GROUP BY user_id, username
        ORDER BY total_points DESC
        LIMIT ?;
        """
        return self.execute(sql, parameters=(top_n,), fetchall=True)
    

    
    
def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
