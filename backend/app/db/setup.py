from pathlib import Path
from sqlalchemy import text

from app.db.db import engine


def run_create_tables_script():
    sql_path = Path("database/01_create_tables.sql")

    if not sql_path.exists():
        raise FileNotFoundError("Ficheiro SQL não encontrado.")

    sql = sql_path.read_text(encoding="utf-8")

    with engine.begin() as connection:
        connection.execute(text(sql))

    return True