from settings import s3_settings as s3_s


invalid_content_type_text = "Content type must be .png, .jpg, .jpeg or .webp"
failed_upload_file_text = "Failed uploading file. Try again"
max_file_size_exceeded = (
    f"Max file size exceeded. "
    f"Max size is {s3_s.MAX_IMAGE_SIZE / 1024}mb"
)
