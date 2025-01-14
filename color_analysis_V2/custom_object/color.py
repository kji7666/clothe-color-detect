from custom_object import color
from custom_object import image_labels
from custom_object import label


class Colors:
    '''
    儲存數種顏色與在範圍中佔比
    @param : color_map 儲存顏色與佔比
    @func : add_color 添加顏色與佔比
    @func : sort_color 可依照占比sort list中顏色
    '''
    def __init__(self):
        self.color_map = []

    def add_color(self, color, ratio):
        self.color_map.append((color, ratio))

    def sort_color(self):
        self.color_map.sort(key=lambda x: x[1], reverse=True)

