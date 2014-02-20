# -*- coding: utf-8 -*-


from ZODB import FileStorage, DB
import transaction


class Database(object):
    def __init__(self):
        self.storage = FileStorage.FileStorage('/home/luccox/KAMI/db/db.fs')
        self.db = DB(self.storage)

    def do_pack(self):
        self.db.pack()

    def close(self):
        self.db.close()
        print 'DB closed'
        self.storage.close()
        print 'DB storage closed'



class Connector(object):
    def __init__(self, database):
        self._connection = database.db.open()
        self.root = self._connection.root()

    def close(self):
        self.commit()
        self._connection.close()
        print 'DB connection closed'

    def commit(self):
        transaction.commit()

