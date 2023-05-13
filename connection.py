
from sqlalchemy import create_engine

from models.users import users


def connection_engine():
    print("Try to create connection")
    try:
        engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
        """
         Maybe I should done it with migrations, but nah :).
        """
        users.create(engine)

        return engine
    except Exception as e:
        print(e)
