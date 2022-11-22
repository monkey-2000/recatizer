import os

from dotenv import load_dotenv

from dataclasses import dataclass
from telegram_bot.configs.bot_base_configs import S3ClientConfig


load_dotenv()

@dataclass
class ServiceConfig:
    mongoDB_url: str
    bot_token: str
    s3_client_config: S3ClientConfig
    models_path: str


default_service_config = ServiceConfig(
    mongoDB_url="mongodb://localhost:27017/",
    bot_token=os.environ.get('BOT_TOKEN'),
    s3_client_config=S3ClientConfig(
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
                ),
    models_path=os.environ.get('MODEL_PATH')
)

