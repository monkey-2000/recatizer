import os.path
import cv2
import boto3
import numpy as np

from src.utils.local_storage import LocalStorage


class YandexS3Client:
    def __init__(self, access_key: str, secret_key: str, bucket_name: str = "recatizer-bucket"):
        self.session = boto3.session.Session()
        self.s3 = self.session.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket_name = bucket_name


    def save_image(self, image_path: str):
        s3_path = os.path.join("users_data", os.path.basename(image_path))
        self.s3.upload_file(image_path, self.bucket_name, s3_path)
        return s3_path

    def load_image(self, image_path: str):
        get_object_response = self.s3.get_object(Bucket=self.bucket_name, Key=image_path)
        bin_image = get_object_response['Body'].read()
        image_data = np.frombuffer(bin_image, dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_UNCHANGED)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image



    def download_file(self, file_path: str, result_path: str):
            self.s3.download_file(
                self.bucket_name,
                file_path,
                result_path
            )
