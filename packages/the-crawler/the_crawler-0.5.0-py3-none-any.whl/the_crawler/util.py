import concurrent.futures
import hashlib
import logging
import os
from typing import List, Set, Tuple
from urllib.parse import unquote, urljoin, urlparse

from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

logger = logging.getLogger(__name__)


def _download_file_idempotent(url, output_directory):
    sub_output_directory = make_tree_from_url(output_directory, url)
    save_path = os.path.join(sub_output_directory, unquote(os.path.basename(url)))
    if os.path.isfile(save_path):
        return
    response = requests.get(url, stream=True)
    with open(save_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=10**7):  # 10MiB
            file.write(chunk)


def download_files(
    output_directory: str, downloadable_links: List[str], max_workers: int
) -> Tuple[int, int]:
    succeeded = failed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_download_file_idempotent, url, output_directory): url
            for url in downloadable_links
        }
        total = len(futures)
        for future in tqdm(
            concurrent.futures.as_completed(futures), total=total, dynamic_ncols=True, position=0
        ):
            url = futures[future]
            file_name = os.path.basename(url)
            try:
                future.result()
            except Exception:
                logger.warning("Failed to download %s", file_name, exc_info=True)
                failed += 1
            else:
                logger.info("Downloaded %s", file_name)
                succeeded += 1
    return succeeded, failed


def make_tree_from_url(base: str, url: str) -> str:
    parts = urlparse(url)
    output_directory = os.path.join(base, unquote(parts.path.strip("/")))
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    return output_directory


def cache_filename_from_url(url: str, recurse: bool) -> str:
    hash_obj = hashlib.sha256(unquote(url).encode("utf-8"))
    return f"{hash_obj.hexdigest()}{'_r' if recurse else ''}"


def categorize_link(full_link, extensions, recurse):
    response = requests.head(full_link)
    if response.headers.get("Content-Type", "") == "text/html":
        if recurse:
            return "visit"
    elif not extensions or any(full_link.lower().endswith(ext) for ext in extensions):
        return "download"
    return "ignore"


def collect_links(
    base_url: str,
    extensions: List[str],
    recurse: bool,
    output_directory: str,
    force_collection: bool,
    max_workers: int,
) -> List[str]:
    norm_extensions = [ext.strip().lower() for ext in extensions]
    cache_filename = cache_filename_from_url(base_url, recurse)
    cache_path = os.path.join(output_directory, cache_filename)
    if os.path.isfile(cache_path):
        if force_collection:
            logger.info("Force collection requested, ignoring cached results")
        else:
            logger.info("Loading cached urls from %s", cache_path)
            # Load saved file
            with open(cache_path) as fp:
                return [url.strip() for url in fp.readlines()]

    visited_urls: Set[str] = set()
    to_visit: List[str] = [unquote(base_url)]
    to_download: Set[str] = set()

    pbar = tqdm(dynamic_ncols=True, desc="Collecting links to download", position=0)
    while to_visit:
        pbar.update(n=1)
        url = to_visit.pop()
        logger.info("Crawling %s", url)
        visited_urls.add(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    categorize_link,
                    urljoin(url + "/", unquote(link["href"])),
                    norm_extensions,
                    recurse,
                ): urljoin(url + "/", unquote(link["href"]))
                for link in soup.find_all("a")
                if link.get("href", None) and not link["href"].startswith(".")
            }
            for future in concurrent.futures.as_completed(futures):
                full_link = futures[future]
                try:
                    action = future.result()
                except Exception:
                    pass
                else:
                    logger.info("Will %s %s", action, full_link)
                    match action:
                        case "visit":
                            to_visit.append(full_link)
                        case "download":
                            to_download.add(full_link)
                        case _:
                            pass

    with open(cache_path, "w") as fp:
        for url in to_download:
            fp.write(url + "\n")
    return list(to_download)
