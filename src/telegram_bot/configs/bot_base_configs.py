import json
from dataclasses import dataclass


@dataclass
class KafkaConsumerCfg:
    kafka_topic: str
    bootstrap_servers: list
    group_id: str
    client_id: str
    check_crcs: bool
    # consumer_timeout_ms: int
    session_timeout_ms: int
    request_timeout_ms: int
    max_partition_fetch_bytes: int
    max_poll_records: int
    auto_offset_reset: str
    enable_auto_commit: bool
    max_poll_interval_ms: int
    value_deserializer: object
    key_deserializer: object
    pool_cache_limit: int
    stop_processing: bool
    processes: int


@dataclass
class S3ClientConfig:
    aws_access_key_id: str
    aws_secret_access_key: str


@dataclass
class TgBotConfig:
    token: str
    image_dir: str
    kafka_server: list
    s3_client_config: S3ClientConfig
    mongoDB_url: str
    max_sending_cats: int
    max_load_photos: int
