from color_recognization import image_colors_parser as icp
from costom_object import color 
from costom_object import image_labels as il
from costom_object import label as lb
from util import file_parser as f
class RunRecognition:
    '''
    執行整個流程
    '''
    @staticmethod
    def run(image_path, label_path):
        image_labels = RunRecognition.parse_label(label_path)
        image_labels.info()
        image_color = icp.ColorPasrser(image_path, image_labels)
        return image_color.clothes_color_map

    @staticmethod
    def parse_label(label_path):
        file_content = f.fileReader(label_path)  # 確認返回值為檔案內容字串
        lines = f.lineReader(file_content)      # 修改為處理字串的方法
        image_labels = il.ImageLabels(f.file_extension_remove(label_path))
        for line in lines:
            image_labels.addLabel(lb.Label(line))
        return image_labels
