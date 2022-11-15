from dataclasses import dataclass

from telegram_bot.configs.bot_base_configs import S3ClientConfig


@dataclass
class ServiceConfig:
    mongoDB_url: str
    bot_token: str
    s3_client_config: S3ClientConfig


default_service_config = ServiceConfig(
    mongoDB_url="mongodb://localhost:27017/",
    bot_token="",
    s3_client_config=S3ClientConfig(
                    aws_access_key_id="",
                    aws_secret_access_key=""
                )
)