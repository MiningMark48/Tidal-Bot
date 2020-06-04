from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData, Boolean
from sqlalchemy.sql import select


class CstmTable:
    def __init__(self, table: Table, conn):
        self.table = table
        self.conn = conn

    def insert_(self, items: list):
        self.conn.execute(self.table.insert(), items)

    def fetch_by_name(self, name: str):
        sel = self.table.select().where(self.table.columns.name == name)
        return list(self.conn.execute(sel))

    def toggle_boolean(self, name: str):
        val = self.fetch_by_name(name)
        print(val)
        if val:
            rep = self.table.update().where(self.table.columns.name == name).values(value=not val[0][2])
            self.conn.execute(rep)
        else:
            self.insert_([{'name': name, 'value': True}])
        print(val)


class GuildData:
    def __init__(self, guild_id):
        self.guild_id = guild_id

        engine = create_engine(f'sqlite:///data/guild_{self.guild_id}.db', echo=True)
        meta = MetaData()
        self.conn = engine.connect()

        self.booleans = self.Booleans(meta, self.conn)
        self.tags = self.Tags(meta, self.conn)

        meta.create_all(engine)

    class Booleans(CstmTable):
        def __init__(self, meta, conn):
            self.conn = conn

            self.booleans = Table(
                'booleans', meta,
                Column('id', Integer, primary_key=True),
                Column('name', String, unique=True),
                Column('value', Boolean)
            )

            super().__init__(self.booleans, self.conn)

        def insert(self, name: str, value: bool):
            self.insert_([{'name': name, 'value': value}])

    class Tags(CstmTable):
        def __init__(self, meta, conn):
            self.conn = conn

            self.tags = Table(
                'tags', meta,
                Column('id', Integer, primary_key=True),
                Column('name', String, unique=True),
                Column('value', String)
            )

            super().__init__(self.tags, self.conn)

        def insert(self, name: str, value: str):
            self.insert_([{'name': name, 'value': value}])
