from django.conf import settings
from minio import Minio


def get_minio_client():
    return Minio(
        settings.MINIO_STORAGE_ENDPOINT,
        access_key=settings.MINIO_STORAGE_ACCESS_KEY,
        secret_key=settings.MINIO_STORAGE_SECRET_KEY,
        secure=False
    )


def put_file_into_minio(filename, filepath):
    """
    :param filename: str
    :param filepath: str
    :return path to file: str
    """
    path_to_file = settings.MINIO_DATASETS_BUCKET_URL + '/' + filename
    minio_client = get_minio_client()
    minio_client.fput_object(
        settings.MINIO_STORAGE_DATASETS_BUCKET_NAME, filename,
        file_path=filepath,
        content_type='application/csv'
    )
    return path_to_file


def get_file_from_minio(
    filename, bucket=settings.MINIO_STORAGE_MEDIA_BUCKET_NAME
):
    minio_client = get_minio_client()
    # file_object = minio_client.get_object(
    #     settings.MINIO_STORAGE_DATASETS_BUCKET_NAME, filename
    # )
    file_object = minio_client.get_object(
        bucket, filename
    )
    return file_object


def get_image_from_minio(field_file):
    minio_client = get_minio_client()
    image_object = minio_client.get_object(
        settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, field_file.name
    )
    return image_object


def delete_from_minio(image_name):
    minio_client = get_minio_client()
    minio_client.remove_object(
        settings.MINIO_STORAGE_MEDIA_BUCKET_NAME, image_name
    )
