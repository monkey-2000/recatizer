import os

from dotenv import load_dotenv

from dataclasses import dataclass

from src.services.configs.services_base_configs import S3ClientConfig, RedisClientConfig

load_dotenv()

@dataclass
class ServiceConfig:
    mongoDB_url: str
    bot_token: str
    s3_client_config: S3ClientConfig
    redis_client_config: RedisClientConfig
    models_path: str
    local_models_path: str
    embedding_size: int
    answer_time_delay: int  ## dely time for bot loader (one cat  in 5 sec)
    ans_check_frequency: int  ## how often do we check for answers in main _nference_loop
    cats_in_answer: int


default_service_config = ServiceConfig(
    mongoDB_url="mongodb://localhost:27017/",
    bot_token=os.environ.get('BOT_TOKEN'),
    s3_client_config=S3ClientConfig(
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    local_path=os.environ.get('LOCAL_PATH'),
                ),
    redis_client_config=RedisClientConfig(host=os.environ.get("REDIS_URL"),
                                          port=6379,
                                          db=0
    ),
    models_path=os.environ.get('MODEL_PATH'),
    local_models_path=os.environ.get('LOCAL_MODEL_PATH'),
    embedding_size=512,
    answer_time_delay=30,  ## dely time for bot loader (one cat  in 5 sec)
    ans_check_frequency=60,  ## how often do we check for answers in main _nference_loop
    cats_in_answer=5
)

