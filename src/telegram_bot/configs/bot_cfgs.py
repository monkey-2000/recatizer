import json
import os

from dotenv import load_dotenv

from src.telegram_bot.configs.bot_base_configs import (
    TgBotConfig,
    S3ClientConfig,
    KafkaConsumerCfg, RedisClientConfig,
)

load_dotenv()

consumer_msg_cfd = KafkaConsumerCfg(
    kafka_topic="my-topic",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    bootstrap_servers=["localhost:9092"],
    group_id="my-group",
    client_id="client1",
    check_crcs=True,  # defult value True
    # consumer_timeout_ms=[float('inf')],  # defult value [float('inf')]
    session_timeout_ms=10000,  # defult value 1000 ms
    request_timeout_ms=305000,  # defult value  305000 ms
    max_poll_interval_ms=300000 * 10,  # defult value  300000 ms
    max_partition_fetch_bytes=1048576,  # defult value  1048576 bytes
    max_poll_records=1000,  # defult value 500
    value_deserializer=lambda v: json.loads(v.decode("ascii")),
    key_deserializer=lambda v: json.loads(v.decode("ascii")),
    #### for main_loop method witch don't working properly
    pool_cache_limit=1,
    stop_processing=False,
    processes=2,
)


bot_config = TgBotConfig(
    token=os.environ.get("BOT_TOKEN"),
    image_dir=os.environ.get("PROJECT_DIR") + "/tmp",
    kafka_server=["localhost:9092"],
    s3_client_config=S3ClientConfig(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        local_path=os.environ.get('LOCAL_PATH'),
    ),
    redis_client_config = RedisClientConfig(host="localhost",
                                            port=6379,
                                            db=0),
    mongoDB_url=os.environ.get("MONGO_URL"),
    max_sending_cats=5,
    max_load_photos=5)

