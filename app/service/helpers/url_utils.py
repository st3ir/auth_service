import re


def extract_base_url(url: str) -> str:
    # Define the regular expression pattern to extract the base URL
    if not isinstance(url, str):
        return ''
    pattern = r'^(?:http:\/\/|https:\/\/)?(?:www\.)?([^\/\n]+)'
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return ''
