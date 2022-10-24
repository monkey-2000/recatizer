from dataclasses import dataclass


@dataclass
class DBConfig:
    mongoDB_url: str

default_db_config = DBConfig("mongodb://localhost:27017/")