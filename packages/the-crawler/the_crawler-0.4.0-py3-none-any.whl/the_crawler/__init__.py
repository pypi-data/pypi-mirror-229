import argparse
import concurrent.futures
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import List, Tuple
from urllib.parse import unquote, urljoin, urlparse
import os

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

# Log info and up to console, everything to file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
file_handler = TimedRotatingFileHandler(
    os.path.join(os.getcwd(), f"{__name__}.log"), when="midnight", backupCount=7
)
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s]: %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def validate_url(url: str) -> str:
    _ = urlparse(url)
    return url


def validate_output_directory(output_directory: str) -> str:
    if os.path.isdir(output_directory):
        return output_directory
    raise argparse.ArgumentTypeError(
        f"Supplied output directory '{output_directory}' does not exist, aborting!"
    )


def get_parser():
    parser = argparse.ArgumentParser(
        description="Crawls given url for content",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("base_url", type=validate_url)
    parser.add_argument("--recurse", "-r", action="store_true")
    parser.add_argument(
        "--output-directory", "-o", type=validate_output_directory, default=os.getcwd()
    )
    parser.add_argument(
        "--extensions", "-e", nargs="+", type=str, default=[".cbr", ".pdf", ".epub", ".cbz", ".cb7"]
    )
    parser.add_argument("--max-workers", type=int, default=1)
    return parser


def download_file_idempotent(url, save_path):
    if os.path.isfile(save_path):
        return
    response = requests.get(url)
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=10**7):  # 10MiB
            file.write(chunk)


def download_files(downloadable_links: List[str], max_workers: int) -> Tuple[int, int]:
    succeeded = failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_file_idempotent, url, save_path): save_path
            for url, save_path in downloadable_links
        }
        total = len(futures)
        for future in tqdm(
            concurrent.futures.as_completed(futures), total=total, dynamic_ncols=True, position=0
        ):
            save_path = futures[future]
            file_name = os.path.basename(save_path)
            try:
                future.result()
            except Exception:
                logger.warning("Failed to download %s", file_name, exc_info=True)
                failed += 1
            else:
                logger.debug("Downloaded %s", file_name)
                succeeded += 1
    return succeeded, failed


def make_sub_output_directory(base: str, url: str) -> str:
    parts = urlparse(url)
    output_directory = os.path.join(base, unquote(parts.path.strip("/")))
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    return output_directory


def collect_links(
    base_url: str, extensions: List[str], recurse: bool, output_directory: str
) -> List[str]:
    visited_urls = set()
    to_visit = [base_url]
    to_download = set()

    pbar = tqdm(dynamic_ncols=True, desc="Collecting links to download", position=0)
    while to_visit:
        pbar.update(n=1)
        url = to_visit.pop()
        logger.debug("Crawling %s", unquote(url))
        visited_urls.add(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract links to other pages and files
        if recurse:
            for link in soup.find_all("a"):
                href = link.get("href")
                if (
                    href
                    and not href.startswith(".")
                    and href not in visited_urls
                    and not any(href.endswith(ext) for ext in extensions)
                ):
                    to_visit.append(urljoin(url, href))
                    logger.debug("Will visit %s", unquote(to_visit[-1]))

        # Collect downloadable links
        downloadable_links = [
            link
            for link in soup.find_all("a", href=True)
            if any(link["href"].endswith(ext) for ext in extensions)
        ]
        if downloadable_links:
            sub_output_directory = make_sub_output_directory(output_directory, url)
            for link in downloadable_links:
                href = link["href"]
                if any(href.endswith(ext) for ext in extensions):
                    file_url = urljoin(url, href)
                    file_name = os.path.join(sub_output_directory, unquote(os.path.basename(href)))
                    to_download.add((file_url, file_name))
                    logger.debug("Will download %s", unquote(file_url))
    return list(to_download)


def main():
    parser = get_parser()
    args = parser.parse_args()
    args_dict = vars(args)
    max_workers = args_dict.pop("max_workers")
    links_to_download = collect_links(**args_dict)
    logger.info("Collected %d links, downloading now...", len(links_to_download))
    succeeded, failed = download_files(links_to_download, max_workers)
    logger.info(
        "Download complete, %d successes and %d failures of %d files",
        succeeded,
        failed,
        len(links_to_download),
    )
