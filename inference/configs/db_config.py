from dataclasses import dataclass


@dataclass
class DBConfig:
    mongoDB_url: str