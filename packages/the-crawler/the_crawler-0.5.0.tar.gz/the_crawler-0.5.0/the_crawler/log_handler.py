from io import TextIOBase
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

default_log_format = "[%(asctime)s - %(levelname)s - %(name)s]: %(message)s"


class LogHandler(TextIOBase):
    log_filename = os.path.join(os.getcwd(), f"{__name__.split('.')[0]}.log")

    def __init__(
        self, file_log_level: int, console_log_level: int, log_format: str = default_log_format
    ):
        super().__init__()
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        self._console_handler = logging.StreamHandler()
        self._console_handler.setLevel(console_log_level)
        self._file_handler = TimedRotatingFileHandler(
            self.log_filename, when="midnight", interval=1, backupCount=7
        )
        self._file_handler.setLevel(file_log_level)
        formatter = logging.Formatter(log_format)
        self._console_handler.setFormatter(formatter)
        self._file_handler.setFormatter(formatter)
        root_logger.addHandler(self._console_handler)
        root_logger.addHandler(self._file_handler)
        self._stdout = sys.stdout
        self._stderr = sys.stderr

    def write(self, *args, **kwargs):
        self._console_handler.stream.write(*args, **kwargs)
        self._file_handler.stream.write(*args, **kwargs)

    def __enter__(self):
        sys.stdout = self
        sys.stderr = self

    def __exit__(self, *_):
        sys.stdout = self._stdout
        sys.stderr = self._stderr
