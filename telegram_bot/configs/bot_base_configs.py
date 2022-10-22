import json
from dataclasses import dataclass

@dataclass
class KafkaConsumerCfg:
    kafka_topic: str
    bootstrap_servers: list
    group_id: str
    client_id: str
    check_crcs: bool
    consumer_timeout_ms: int
    session_timeout_ms: int
    request_timeout_ms: int
    max_partition_fetch_bytes: int
    max_poll_records: int