import sqlalchemy as sa
import sqlalchemy.orm as orm
from rich import print

from db.modelbase import SqlAlchemyBase

__factory = None


def global_init(db_file: str):
    global __factory

    if not db_file or not db_file.strip():
        raise Exception("You must specify a db file.")

    conn_str = "sqlite:///" + db_file.strip()
    print(f"[bold]Connecting to DB with {conn_str}[/]")

    engine = sa.create_engine(
        conn_str, echo=False, connect_args={"check_same_thread": False}
    )

    __factory = orm.sessionmaker(bind=engine)

    import db.__all_models

    SqlAlchemyBase.metadata.create_all(engine)
    return engine


def create_session():
    global __factory
    return __factory()
