from custom_object import color
from custom_object import image_labels
from custom_object import label

class ImageLabels:
    '''
    儲存圖像名稱及其標籤
    @param imageName : 圖像名稱
    @param label_list : 儲存標籤的list
    @func : addLabel 添加標籤
    @func : info 返回圖像名稱及標籤數量
    '''
    def __init__(self, imageName):
        self.imageName = imageName
        self.label_list = []

    def addLabel(self, label):
        self.label_list.append(label)

    def info(self):
        return f"Image: {self.imageName}, Labels Count: {len(self.label_list)}"

