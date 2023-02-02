import os
import shutil


import cv2


class LocalStorage():

    def __init__(self, path='tmp_local_storage'):
        if not os.path.exists(path):
            os.mkdir(path)
        self.path = os.path.abspath(path)


    def save_image(self, image_path: str):
        s3_path = os.path.join(self.path, os.path.basename(image_path))
        return shutil.copy(image_path, s3_path)

    def load_image(self, image_path: str):
        image  = cv2.imread(image_path, cv2.IMREAD_COLOR)
        return image