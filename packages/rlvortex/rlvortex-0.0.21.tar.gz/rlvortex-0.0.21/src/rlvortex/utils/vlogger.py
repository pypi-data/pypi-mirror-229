import os
import enum
import json
from datetime import datetime, timezone
from typing import Optional
from loguru import logger as loggeru


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
        if self.log_type == LogType.File:
            assert (
                self.log_path is not None
            ), "log_path must be provided when log_type is File"
            loggeru.add(self.log_path)

    def info_dict(self, dict_info: dict):
        if self.log_type == LogType.Vanish:
            return
        loggeru.info(json.dumps(dict_info, sort_keys=False, indent=4))

    def info(self, msg: str):
        if self.log_type == LogType.Vanish:
            return
        loggeru.info(msg)

    def debug(self, msg: str):
        if self.log_type == LogType.Vanish:
            return
        loggeru.debug(msg)
