from neo4j import GraphDatabase
from .config import COGNODB_URI, COGNODB_USER, COGNODB_PASSWORD


def create_driver():
    if not COGNODB_URI or not COGNODB_PASSWORD:
        return None
    return GraphDatabase.driver(
        COGNODB_URI,
        auth=(COGNODB_USER, COGNODB_PASSWORD),
        max_connection_pool_size=20,
    )


driver = create_driver()


def close_driver():
    if driver:
        driver.close()
