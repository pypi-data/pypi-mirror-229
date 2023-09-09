import argparse
import logging
from urllib.parse import unquote, urlparse
import os

from the_crawler.log_handler import LogHandler
from the_crawler.util import cache_filename_from_url, collect_links, download_files


def valid_url(url: str) -> str:
    try:
        urlparse(url)
    except Exception:
        raise argparse.ArgumentTypeError(f"Supplied url '{url}' is not a valid url!")
    return url


def extant_directory(output_directory: str) -> str:
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
    parser.add_argument("base_url", type=valid_url)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Changes the console log level from INFO to WARNING; defers to --verbose",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Changes the console log level from INFO to DEBUG; takes precedence over --quiet",
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help=(
            "Stops after collecting links to be downloaded; useful for checking the cache before "
            "continuing"
        ),
    )
    parser.add_argument(
        "--force-collection",
        action="store_true",
        help="Forces recollection of links, even if the cache file is present",
    )

    parser.add_argument(
        "--recurse",
        "-r",
        action="store_true",
        help="If specified, will follow links to child pages and search them for content",
    )
    parser.add_argument(
        "--output-directory",
        "-o",
        type=extant_directory,
        default=os.getcwd(),
        help="The location to store the downloaded content; must already exist",
    )
    parser.add_argument(
        "--extensions",
        "-e",
        nargs="?",
        type=str,
        default=[],
        help=(
            "If specified, will restrict the types of files downloaded to those matching the "
            "extensions provided; case-insensitive"
        ),
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=os.cpu_count(),
        help=f"The maximum number of parallel downloads to support; defaults to {os.cpu_count()}",
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    args_dict = vars(args)
    collect_only = args_dict.pop("collect_only")

    # Always log everything to file, set console log level based on `--quiet` and `--verbose` flags
    console_log_level = logging.INFO
    if args_dict.pop("quiet"):
        console_log_level = logging.WARNING
    if args_dict.pop("verbose"):
        console_log_level = logging.DEBUG

    with LogHandler(file_log_level=logging.DEBUG, console_log_level=console_log_level):
        logger = logging.getLogger(__name__)
        logger.info("Collecting links beneath %s", unquote(args.base_url))
        links_to_download = collect_links(**args_dict)
        if collect_only:
            cache_filename = cache_filename_from_url(args_dict["base_url"], args_dict["recurse"])
            cache_path = os.path.join(args_dict["output_directory"], cache_filename)
            logger.info(
                "Collected %d links, review %s before proceeding",
                len(links_to_download),
                cache_path,
            )
        else:
            logger.info("Collected %d links, downloading now...", len(links_to_download))
            succeeded, failed = download_files(
                args_dict["output_directory"], links_to_download, args_dict["max_workers"]
            )
            logger.info(
                "Download complete, %d successes and %d failures of %d files",
                succeeded,
                failed,
                len(links_to_download),
            )
