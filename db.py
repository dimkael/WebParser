from sqlalchemy import (
    MetaData, Table, Column, Integer, String, DateTime, create_engine
)


meta = MetaData()
connection = {
    'user': 'postgres',
    'database': 'storage',
    'host': '127.0.0.1',
    'password': ' '
}
dsn = f'postgresql://{connection["user"]}:{connection["password"]}@{connection["host"]}/{connection["database"]}'


Links = Table(
    'links', meta,
    Column('id', Integer, primary_key=True),
    Column('domain', String),
    Column('url', String),
    Column('topic', String),
    Column('link', String),
    Column('datetime', DateTime),
    Column('response', Integer)
)


if __name__ == '__main__':
    engine = create_engine(dsn)
    meta.drop_all(engine)
    meta.create_all(engine)