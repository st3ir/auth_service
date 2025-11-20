from uuid import uuid4

from fastapi import UploadFile

from settings import s3_settings as s3_s
from lib.s3.handlers import put_object_to_s3, remove_object_from_s3
from service.exceptions.api.files import (
    FailedUploadImageException,
    InvalidContentTypeException,
    MaxImageSizeExceededException,
)


async def process_image(
    img: UploadFile,
    oldest_image_if_exist: str | None = None
) -> str:

    if img.content_type not in s3_s.ALLOWED_IMAGE_TYPES:
        raise InvalidContentTypeException()

    try:
        img_name = await upload_user_image(img)
    except Exception:
        raise FailedUploadImageException()

    if oldest_image_if_exist \
            and 'default.png' not in oldest_image_if_exist:
        remove_object_from_s3(oldest_image_if_exist)

    return img_name


async def upload_user_image(file: UploadFile):

    gen_name = f'{uuid4().hex.upper()}.png'

    try:
        content = await file.read()
        if len(content) > s3_s.MAX_IMAGE_SIZE:
            raise MaxImageSizeExceededException()

        await file.seek(0)
        url = f'{s3_s.S3_IMAGES_PATH}/{gen_name}'
        put_object_to_s3(gen_name, file.file, url)
    finally:
        await file.close()

    return s3_s.USER_STATIC_IMG_URL + gen_name
