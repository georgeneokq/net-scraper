"""
For downloading images from a specified URL list.
"""

import json
from hashlib import md5
from time import sleep
from pathlib import Path
import requests
from parsers import file_path_parser


def download_images(
    urls: list[str], *, output_dir="data/images", delay=0.3, verbose=False
):
    """
    Download images from a list of URLs.

    Args:
        urls (list[str]): URL list
        output_dir (str, optional): Output directory
        delay (int): delay between downloads, in seconds
    """

    def print_if_verbose(string):
        if verbose:
            print(string)

    # Ensure directory is created
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print_if_verbose(f"Downloading from {len(urls)} URLs.")

    for url in urls:
        img_data = requests.get(url, timeout=10).content

        # Use md5 of image as file name
        file_name = f"{md5(img_data).hexdigest()}.png"
        file_path = Path(output_dir, file_name)
        with open(file_path, "wb") as f:
            f.write(img_data)

            if verbose:
                print_if_verbose(
                    f"Downloaded image from {url} to {str(file_path.absolute())}"
                )

        sleep(delay)


if __name__ == "__main__":
    args = file_path_parser()
    file_path = args["file_path"]

    with open(file_path, encoding="utf8") as f:
        urls = json.load(f)

    download_images(urls, verbose=True)
