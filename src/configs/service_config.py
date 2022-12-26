import os

from dotenv import load_dotenv

from dataclasses import dataclass
from src.telegram_bot.configs.bot_base_configs import S3ClientConfig


load_dotenv()


@dataclass
class ServiceConfig:
    mongoDB_url: str
    bot_token: str
    kafka_broker_ip: list
    s3_client_config: S3ClientConfig
    models_path: str
    local_models_path: str
    answer_time_delay: int
    ans_check_frequency: int
    cats_in_answer: int


default_service_config = ServiceConfig(
    mongoDB_url=os.environ.get("MONGO_URL"),
    # mongoDB_url="mongodb://localhost:27017/"
    bot_token=os.environ.get("BOT_TOKEN"),
    kafka_broker_ip=["localhost:9092"],
    s3_client_config=S3ClientConfig(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    ),
    models_path=os.environ.get("MODEL_PATH"),
    local_models_path=os.environ.get("LOCAL_MODEL_PATH"),
    answer_time_delay=30,  ## dely time for bot loader (one cat  in 5 sec)
    ans_check_frequency=60,  ## how often do we check for answers in main _nference_loop
    cats_in_answer=5,
)
