from dataclasses import dataclass


@dataclass
class ServiceConfig:
    mongoDB_url: str
    bot_token: str

default_service_config = ServiceConfig("mongodb://localhost:27017/", "5725782396:AAHCjlA4YKa0YlPudMBRNsWI1nEtEOClI5w")