import os
from util import folderTraversal as ft
from color_recognization import run_recognization as run
from constant import path_config as path

def process_files(img_folder_path, label_folder_path):
    """
    @brief: 遍歷檔案對並調用 ColorParser 方法處理
    @params: img_folder_path, label_folder_path
    """
    file_pairs = ft.file_path_getter(img_folder_path, label_folder_path)
    for img_path, label_path in file_pairs:
        print(f"Processing: {img_path}, {label_path}")
        if not os.path.exists(img_path):
            print(f"Error: File not found at {img_path}")
            continue
        if not os.path.exists(label_path):
            print(f"Error: File not found at {label_path}")
            continue
        try:
            # 調用 ColorParser 類處理圖片
            run.RunRecognition.color_parse(img_path, label_path).draw_boxes_and_save()
        except Exception as e:
            print(f"Error processing {img_path} and {label_path}: {e}")

def run():
    process_files(path.IMAGE_FOLDER_PATH, path.LABEL_FOLDER_PATH)

run()
