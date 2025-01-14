from custom_object import color
from custom_object import image_labels
from custom_object import label

class Label:
    '''
    @brief 一張 image 對應的其中一個 label
    @input line Label在初始化時會以空白切割字串, 並填入attribute中
    @param name : label 的名稱
    @param x : label 的 x 座標
    @param y : label 的 y 座標
    @param w : label 的寬度
    @param h : label 的高度
    '''
    def __init__(self, line):
        '''
        解析並初始化 Label 的屬性
        @params : line (str) - 文件中其中一行的字串
        '''
        self.name, self.x, self.y, self.w, self.h = Label.labelParser(line)

    def __str__(self):
        '''
        格式化輸出 Label 的資訊
        '''
        return f"Label(name={self.name}, x={self.x:.4f}, y={self.y:.4f}, w={self.w:.4f}, h={self.h:.4f})"

    @staticmethod
    def labelParser(line):
        '''
        解析一行 YOLOv5 格式的標籤數據
        '''
        parts = line.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid label line: {line}")
        name = int(parts[0])
        x, y, w, h = map(float, parts[1:])
        return name, x, y, w, h

