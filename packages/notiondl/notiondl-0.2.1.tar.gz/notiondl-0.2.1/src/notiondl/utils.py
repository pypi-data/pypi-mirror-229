"""Utilities for notiondl."""

import os
import shutil
import requests
import logging

session = requests.Session()
logger = logging.getLogger(__name__)


def unzip_all(path: str) -> None:
    """Unzips all the packed files in a directory."""
    logger.info(f"Unzipping all files in {path}")
    for file in os.listdir(path):
        if file.endswith(".zip"):
            full_file_path = os.path.join(path, file)
            shutil.unpack_archive(full_file_path, path, "zip")
            os.remove(full_file_path)
    logger.info(f"Unzipped all files in {path}")


def shorten_file_name(path: str, n: int = 255) -> str:
    """Shortens a file name to `n` characters. Defaults to 255."""
    # pick the first part if there is '?' in the path
    path = path.split("?")[0]
    if len(path.split("/")[-1]) < n + 1:
        return path
    part = path.split("/")[-1]
    # pick the last 255 characters if still too long
    cut = part[len(part) - n :]
    if len(part) > n:
        path = "/".join(path.split("/")[:-1]) + "/" + cut
    return path


def download_url(url: str, path: str, **kwargs) -> None:
    """Downloads a file from a url to a path."""
    logger.info(f"Downloading {url} to {path}")
    p = shorten_file_name(path)
    response = session.get(url, stream=True, **kwargs)
    response.raise_for_status()
    with open(p, "wb") as f:
        shutil.copyfileobj(response.raw, f)


def rename_extracted_pages(path: str, pages: dict, format: str) -> None:
    """Renames the extracted pages to their original names."""
    for file in os.listdir(path):
        if file.endswith(format):
            fname = file.split(".")[0]
            for k, v in pages.items():
                if fname.split()[-1] == v:
                    new = k if k.endswith(format) else k + "." + format
                    os.rename(f"{path}/{file}", f"{path}/{new}")


def pages_from_str(page_id: str) -> dict:
    """Constructs the pages dict from a comma separated string.
    <NAME>:<ID> format is supported."""
    pages = {}
    for page_id in page_id.split(","):
        if ":" in page_id:
            if len(page_id.split(":")) != 2:
                raise ValueError(
                    f"Invalid page ID format: {page_id}. Use <NAME>:<ID> format."
                )
            name, id = page_id.split(":")
            pages[name] = id
        else:
            pages[page_id] = page_id
    return pages


def to_uuid_format(s: str, error_msg: str = None) -> str:
    """Converts a string to the uuid format."""
    if len(s) != 32:
        raise ValueError(f"{error_msg}A UUID must be 32 characters long. given length: {len(s)}")
    if "-" == s[8] and "-" == s[13] and "-" == s[18] and "-" == s[23]:
        return s
    return f"{s[:8]}-{s[8:12]}-{s[12:16]}-{s[16:20]}-{s[20:]}"
