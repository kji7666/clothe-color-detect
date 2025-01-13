import os
import sys

def compile_and_run_all_py_files(directory):
    """
    編譯並執行指定目錄下所有 .py 檔案
    :param directory: 目錄路徑
    """
    # 確認目錄是否存在
    if not os.path.isdir(directory):
        print(f"指定的目錄 {directory} 不存在")
        return
    
    # 遍歷目錄中的所有檔案
    for filename in os.listdir(directory):
        # 只處理 .py 檔案
        if filename.endswith('.py'):
            file_path = os.path.join(directory, filename)
            try:
                print(f"正在執行 {file_path}...")
                # 打開並執行檔案
                with open(file_path, 'r') as file:
                    code = file.read()
                    exec(code, globals())  # 執行檔案內容
                print(f"{file_path} 執行完成")
            except Exception as e:
                print(f"執行 {file_path} 時發生錯誤: {e}")

# 使用範例
directory = 'your_directory_path'  # 這裡替換為你的目錄路徑
compile_and_run_all_py_files(directory)
