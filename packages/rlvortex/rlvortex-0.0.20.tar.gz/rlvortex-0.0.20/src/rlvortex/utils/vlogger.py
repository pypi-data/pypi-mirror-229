from optparse import Option
import os
import enum
import logging
import json
from datetime import datetime, timezone
from torch.utils.tensorboard import SummaryWriter
from typing import Optional, Union


class LogType(enum.Enum):
    Vanish = 1
    Screen = 2
    File = 3


class VLogger:
    def __init__(
        self,
        log_type: LogType,
        log_path: Optional[os.PathLike],
    ) -> None:
        self.start_time_str = (
            datetime.now(timezone.utc).astimezone().strftime("%H:%M:%S-%d_%m_%y")
        )
        self.log_type = log_type
        self.log_path = log_path
        self.__setup_logger_config()

    def __setup_logger_config(self):
        self.logger = logging.getLogger()
        handler = (
            logging.StreamHandler()
            if self.log_type == LogType.Screen
            else logging.FileHandler(str(self.log_path))
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s-%(levelname)s \n%(message)s")
        )
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def info_dict(self, dict_info: dict):
        if self.log_type == LogType.Vanish:
            return
        self.logger.info(json.dumps(dict_info, sort_keys=False, indent=4))

    def info(self, msg: str):
        if self.log_type == LogType.Vanish:
            return
        logging.info(msg)

    def debug(self, msg: str):
        if self.log_type == LogType.Vanish:
            return
        logging.debug(msg)
