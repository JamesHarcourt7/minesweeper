import sqlite3


class Database:

    def __init__(self):
        self.db = sqlite3.connect('minesweeper_db.db')
        self.cursor = self.db.cursor()
        self.db_check()

    def db_check(self):
        self.cursor.execute('select name from sqlite_master where name=?', ('SkidMarksDatabase.db',))
        result = self.cursor.fetchall()
        if len(result) != 1:
            self.create()

    def create(self):
        table_names = {
            'Scores15': '''Score_ID integer, User text, Time double, Date text, primary key(Score_ID)''',
            'Scores20': '''Score_ID integer, User text, Time double, Date text, primary key(Score_ID)''',
            'Scores30': '''Score_ID integer, User text, Time double, Date text, primary key(Score_ID)'''
                        }

        for k, v in table_names.items():
            sql = 'create table if not exists ' + k + '(' + v + ')'
            self.cursor.execute(sql)
            self.db.commit()

    def return_scores(self, table):
        self.cursor.execute('select User, Time, Date from Scores' + str(table))
        return self.cursor.fetchall()

    def add_score(self, user, time, date, table):
        self.cursor.execute('select * from Scores' + str(table))
        s_id = len(self.cursor.fetchall()) + 1

        sql = 'insert into Scores' + str(table) + ' (Score_ID, User, Time, Date) values (?, ?, ?, ?)'
        self.cursor.execute(sql, (s_id, user, time, date,))

        self.db.commit()
