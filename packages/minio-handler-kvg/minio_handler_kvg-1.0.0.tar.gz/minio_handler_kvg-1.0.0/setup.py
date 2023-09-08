from setuptools import setup

setup(
    name='minio_handler_kvg',
    version='1.0.0',
    description='A handler for MinIO storage',
    author='Vyacheslav Kosarev',
    author_email='vyach.kosarev@gmail.com',
    packages=['minio_handler'],
    install_requires=['minio'],
)

