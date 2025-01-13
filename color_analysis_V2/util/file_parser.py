import os
    
    
def fileReader(file_path):
    """
    @brief : Read the contents of a file
    @params : file_path (str) - Path to the file
    @returns : content (str) - Content of the file
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""


def lineReader(file_or_content):
    '''
    讀取內容並按行拆分
    @params : content (str) - 文件內容
    @returns : list[str] - 每行的內容
    '''
    if isinstance(file_or_content, str):
        return file_or_content.splitlines()
    return file_or_content.readlines()

def file_extension_remove(filename):
    '''
    去除檔案名稱的副檔名
    @params : filename (str) - 包含副檔名的檔案名稱
    @returns : str - 去除副檔名後的檔案名稱
    '''
    return os.path.splitext(filename)[0]