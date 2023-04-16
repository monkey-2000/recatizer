import json
import os

from dotenv import load_dotenv

from src.services.configs.services_base_configs import S3ClientConfig, RedisClientConfig
from src.telegram_bot.configs.bot_base_configs import TgBotConfig


load_dotenv()


bot_config = TgBotConfig(
    token=os.environ.get("BOT_TOKEN"),
    image_dir=os.environ.get("PROJECT_DIR") + "/tmp",
    kafka_server=["localhost:9092"],
    s3_client_config=S3ClientConfig(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        local_path=os.environ.get('LOCAL_PATH'),
    ),
    redis_client_config = RedisClientConfig(host=os.environ.get("REDIS_URL"),
                                            port=6379,
                                            db=0),
    mongoDB_url=os.environ.get("MONGO_URL"),
    max_sending_cats=5,
    max_load_photos=5)

