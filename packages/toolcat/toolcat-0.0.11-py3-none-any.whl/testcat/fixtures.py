from pathlib import Path

import pytest

from toolcat.database import Database, Session


@pytest.fixture
def tmp_db_session(tmp_path):
    """
    Crates a database in the path define by tmpdir and loads all sql files
    from the migrations folder in the project root.
    """

    db = Database(tmp_path)
    for f in Path("migrations").glob("*.sql"):
        db.run_sql_file(f)

    with Session(db.engine) as session:
        yield session
