import logging
from datetime import datetime
import colorlog
from LiveTradingConfig import LOG_LEVEL, log_to_file

def get_logger():
    l = logging.getLogger()
    if l.handlers: return l
    l.setLevel(LOG_LEVEL)
    ch = logging.StreamHandler()
    ch.setFormatter(colorlog.ColoredFormatter("%(log_color)s%(asctime)s %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S", log_colors={"DEBUG":"cyan","INFO":"bold_white","WARNING":"yellow","ERROR":"red","CRITICAL":"bold_red"}))
    l.addHandler(ch)
    if log_to_file:
        fh = logging.FileHandler(f"Live_Trading_{datetime.now():%d_%m_%Y_%H_%M_%S}.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%d-%m-%Y %H:%M:%S"))
        l.addHandler(fh)
    return l

log = get_logger()