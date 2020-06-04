from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()


class GuildData(Base):
    __tablename__ = "guild_data"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, unique=True)


def add():
    engine = create_engine('sqlite:///users.db', echo=True)
    Base.metadata.create_all(bind=engine)
    maker = sessionmaker(bind=engine)
    session = maker()

    guild = GuildData()
    guild.id = 0
    guild.name = "Tidal Wave"

    session.add(guild)
    session.commit()

    session.close()

