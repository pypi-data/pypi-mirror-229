import json
import os
import subprocess
from minio import Minio

class minio_handler:
    #Разбор и обработка данных из файла клиента
    #На входе url, далее сохраняем при инициализации класса, парсим и работаем с тем, что есть
    def __init__(self, config):
        self.minio_host = config['MINIO_SERVER']
        self.minio_ac = config['MINIO_AC']
        self.minio_sc = config['MINIO_SC']
        self.client = Minio(self.minio_host, access_key=self.minio_ac, secret_key=self.minio_sc)

    def list_buckets(self):
        return self.client.list_buckets()

    def get_bucket_file_structure(self, bucket_name):
        names = []
        for item in self.client.list_objects(bucket_name, recursive=True):
            print(item.object_name)
            names.append(item.object_name)
        return names


    def upload_file(self, bucket_name, file_path, object_name=None):
        # if not object_name:
        #     object_name = os.path.basename(file_path)
        object_name = file_path
        self.client.fput_object(bucket_name, object_name, file_path)

    def download_file(self, bucket_name, object_name, file_path):
        self.client.fget_object(bucket_name, object_name, file_path)

    def download_bucket_content(self, bucket_name, start_path, local_path):
        for item in self.client.list_objects(bucket_name, prefix=start_path, recursive=True):
            try:
                if item.is_dir:
                    continue

                file_path = os.path.join(local_path, item.object_name)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                self.client.fget_object(bucket_name, item.object_name, file_path)
            except Exception as e:
                print(f"Error downloading object {item.object_name}: {str(e)}")