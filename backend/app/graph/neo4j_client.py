from contextlib import contextmanager
from typing import Any, Iterator

from neo4j import GraphDatabase, Driver

from app.config import settings

_driver: Driver | None = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


@contextmanager
def neo4j_session() -> Iterator[Any]:
    driver = get_driver()
    with driver.session() as session:
        yield session


def run_query(cypher: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    params = params or {}
    with neo4j_session() as session:
        result = session.run(cypher, params)
        return [dict(record) for record in result]


def close_driver() -> None:
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
