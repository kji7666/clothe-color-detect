import os

def file_path_getter(img_folder_path, label_folder_path):
    """
    @brief: 創建一個 list 儲存 img_path 和 label_path 的 pair, img_path 和 label_path 的檔名必須一致(不包括副檔名)
    @params: img_folder_path, label_folder_path
    @returns: list
    """
    # 確認兩個路徑是否存在
    if not os.path.exists(img_folder_path):
        raise FileNotFoundError(f"Image folder path '{img_folder_path}' not found.")
    if not os.path.exists(label_folder_path):
        raise FileNotFoundError(f"Label folder path '{label_folder_path}' not found.")
    
    # 取得 img_folder_path 與 label_folder_path 中所有檔名
    img_files = [os.path.splitext(f)[0] for f in os.listdir(img_folder_path) if os.path.isfile(os.path.join(img_folder_path, f))]
    label_files = [os.path.splitext(f)[0] for f in os.listdir(label_folder_path) if os.path.isfile(os.path.join(label_folder_path, f))]
    
    # 確認檔名是否一致
    common_files = set(img_files) & set(label_files)
    
    if not common_files:
        raise FileNotFoundError("No matching files found between image and label folders.")
    
    file_pairs = []
    for file_name in common_files:
        img_path = os.path.normpath(os.path.join(img_folder_path, f"{file_name}.jpg"))
        label_path = os.path.normpath(os.path.join(label_folder_path, f"{file_name}.txt"))
        file_pairs.append((img_path, label_path))
    
    return file_pairs


