import config.path_config as path
import config.constant_config as constant
from datetime import datetime
import os
import inspect

def ensure_path_exists(log_path):
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)  # 如果目錄不存在，自動建立

def format_message(message):
    # 獲取調用 info 函數的來源函數名稱
    # [0] == format_message, [1] == _record, [2] == info, [3] == 呼叫info的function
    caller_function_name = inspect.stack()[3].function
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"[{timestamp}] Called from: {caller_function_name} - {message}\n"

def AUC_record(message):
    ensure_path_exists(path.AUC_LOG_PATH)
    with open(path.AUC_LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(format_message(message))

def PROCESS_record(message):
    ensure_path_exists(path.PROCESS_LOG_PATH)
    with open(path.PROCESS_LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(format_message(message))

def IMAGE_record(message):
    ensure_path_exists(path.IMAGE_LOG_PATH)
    with open(path.IMAGE_LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(f"{message}\n")

def info(type, message):
    # if (type == constant.AUC):
    #     AUC_record(message)
    # el
    if (type == constant.PROCESS):
        PROCESS_record(message)
    elif (type == constant.IMAGE):
        IMAGE_record(message)
