from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData, Boolean

from util.data.table_helper import TableHelper


class GuildData:
    def __init__(self, guild_id):
        self.guild_id = guild_id

        engine = create_engine(f'sqlite:///data/guild_{self.guild_id}.db', echo=False)
        meta = MetaData()
        self.conn = engine.connect()

        self.booleans = self.Booleans(meta, self.conn)
        self.tags = self.Tags(meta, self.conn)

        meta.create_all(engine)

    class Booleans(TableHelper):
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

    class Tags(TableHelper):
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
