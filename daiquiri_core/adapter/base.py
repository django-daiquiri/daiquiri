class BaseAdapter(object):

    def execute(self, sql):
        return self.cursor.execute(sql)

    def fetchone(self, sql, args=None):
        if args:
            self.cursor.execute(sql, args)
        else:
            self.cursor.execute(sql)

        return self.cursor.fetchone()

    def fetchall(self, sql, args=None):
        if args:
            self.cursor.execute(sql, args)
        else:
            self.cursor.execute(sql)

        return self.cursor.fetchall()
