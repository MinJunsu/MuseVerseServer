import logging
from datetime import datetime

from fastapi import UploadFile

from azure.storage.blob import BlobServiceClient

"""
def create_directory(client: BlobServiceClient, dir_name: str) -> None:
    try:
        container_client = client.create_container('media')

    except Exception as e:
        print("ResourceExistsError", e)
        logging.info("ResourceExistsError:", e)
"""


class BlobAlreadyExists:
    pass


async def upload_local_file(connection_string: str, credential: str, file: UploadFile) -> str:
    try:
        file_format = file.filename.split('.')[-1]
        file_name = f"{str(int(datetime.now().timestamp()))}.{file_format}"
        data = await file.read()
        client = BlobServiceClient.from_connection_string(conn_str=connection_string, credential=credential)

        blob_client = client.get_blob_client(container='media', blob=file_name)
        blob_client.upload_blob(data)

    except Exception as e:
        print("upload_error", e)
        logging.info("ResourceExistsError:", e)

    return 'media/' + file_name
