import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from skimage.color import rgb2lab, lab2rgb
import os
import cv2
from costom_object import color as co
from costom_object import image_labels
from costom_object import label
from constant import path_config as path
class ColorPasrser:
    '''
    @brief 執行整個顏色偵測流程, 並存為 map : label -> color
    @param image_path : 圖片路徑
    @param label_path : 標籤路徑
    @param clothes_color_map : 儲存每個標籤偵測的主要顏色
    '''
    def __init__(self, image_path, img_label):
        self.image_path = image_path
        self.img_label = img_label
        self.clothes_color_map = {}

        img = self.__img_reader()
        self.__handle_img_by_labels(img, img_label)

    def __img_reader(self):
        '''
        @brief 讀取圖片並返回圖片物件
        '''
        import cv2
        return cv2.imread(self.image_path)

    def __handle_img_by_labels(self, image, image_labels):
        '''
        @brief 處理圖片中的每個標籤, 對於每個標籤, 裁剪圖片並偵測主要顏色, 存入 clothes_color_map
        '''
        for label in image_labels.label_list:
            cropped_img = self.__img_cropping(image, label)
            color_obj = self.__color_recognition(cropped_img)
            if label.name in self.clothes_color_map:
                print(f"Warning: Duplicate label {label.name} found!")
            self.clothes_color_map[label.name] = color_obj

    def __img_cropping(self, image, label, scale=0.7):
        '''
        @brief 使用標籤資訊裁剪圖片，並自動縮小範圍以保障物體居中
        因為避免抓到背景部分，所以將框的範圍縮小為 70%
        '''
        height, width, _ = image.shape
        x_center = int(label.x * width)
        y_center = int(label.y * height)
        box_width = int(label.w * width)
        box_height = int(label.h * height)

        # 計算裁剪範圍
        x1 = max(0, x_center - int((box_width * scale) // 2))
        y1 = max(0, y_center - int((box_height * scale) // 2))
        x2 = min(width, x_center + int((box_width * scale) // 2))
        y2 = min(height, y_center + int((box_height * scale) // 2))
        
        return image[y1:y2, x1:x2]


    def __color_recognition(self, cropped_img, n_colors=5, tolerance=0.05):
        '''
        @brief: 偵測圖片中的主要顏色，對顏色變化有容忍度，並顯示數種顏色的比例
        @params:
            cropped_img: np.array - 裁剪的圖片
            n_colors: int - 聚類的顏色數量
            tolerance: float - 顏色比例的最低顯示閾值
        @return:
            color_obj: Color - 包含顏色與比例的物件
        '''
        reshaped_img = cropped_img.reshape(-1, 3)
        # rgb2lab() 用來將 RGB 轉換為 LAB
        # input 要求為 0-1 的浮點數, reshape 為 3 維後, 除以rgb最大值, scale 為 0-1, 再reshape回原本的形狀
        lab_img = rgb2lab(reshaped_img.reshape(-1, 1, 3) / 255.0).reshape(-1, 3)

        # 使用 KMeans 聚類顏色
        kmeans = KMeans(n_clusters=n_colors, random_state=42)
        labels = kmeans.fit_predict(lab_img)
        cluster_centers = kmeans.cluster_centers_

        # 計算每個聚類的比例
        unique, counts = np.unique(labels, return_counts=True)
        total_pixels = np.sum(counts)
        color_ratios = [(tuple(lab2rgb([cluster_centers[label]])[0] * 255), count / total_pixels)
                        for label, count in zip(unique, counts)]
        
        # 過濾比例低於容忍度的顏色
        color_ratios = [cr for cr in color_ratios if cr[1] > tolerance]

        # 按比例排序
        color_ratios.sort(key=lambda x: x[1], reverse=True)

        # 建立 Color 物件
        color_obj = co.Colors()
        for color, ratio in color_ratios:
            color_obj.add_color(tuple(map(int, color)), ratio)  # 將浮點 RGB 轉為整數

        return color_obj

    def show_color(self):
        '''
        @brief: 使用 matplotlib 顯示每個標籤的主要顏色與比例，並逐行印出顏色資訊, 主要用來確認顏色偵測結果
        '''
        for label_name, color_obj in self.clothes_color_map.items():
            print(f"Label {label_name}:")

            # 提取顏色與比例
            colors = [np.array(color) / 255.0 for color, _ in color_obj.color_map]  # 顏色正規化為 0-1
            ratios = [ratio for _, ratio in color_obj.color_map]

            # 逐行列印顏色資訊
            for i, (color, ratio) in enumerate(color_obj.color_map, 1):
                print(f"  Color {i}: RGB {color}, Proportion: {ratio:.2%}")

            # 繪製顏色比例條
            fig, ax = plt.subplots(figsize=(8, 2))
            y_pos = np.arange(len(colors))

            ax.barh(y_pos, ratios, color=colors, edgecolor='black')
            ax.set_yticks(y_pos)
            ax.set_yticklabels([f"Color {i+1}" for i in range(len(colors))])
            ax.set_xlim(0, 1)
            ax.set_xlabel("Proportion")
            ax.set_title(f"Label {label_name} Color Proportions")

            plt.tight_layout()
            plt.show()

    def draw_boxes_and_save(self, output_folder=path.RESULT_FOLDER_PATH):
        '''
        @brief: 在圖片上繪製標籤框，並以偵測到的顏色作為框的顏色，儲存修改後的圖片至指定資料夾, 主要為了確認框的位置與辨識的顏色是否正確
        '''

        # 確保資料夾存在
        os.makedirs(output_folder, exist_ok=True)

        # 讀取原始圖片
        image = self.__img_reader()

        # 繪製每個標籤的框
        for label in self.img_label.label_list:
            # 計算框的頂點座標
            height, width, _ = image.shape
            x_center = int(label.x * width)
            y_center = int(label.y * height)
            box_width = int(label.w * width)
            box_height = int(label.h * height)
            x1 = max(0, x_center - box_width // 2)
            y1 = max(0, y_center - box_height // 2)
            x2 = min(width, x_center + box_width // 2)
            y2 = min(height, y_center + box_height // 2)

            # 從顏色物件中提取主要顏色
            if label.name in self.clothes_color_map:
                # 偵測到的主要顏色
                primary_color = self.clothes_color_map[label.name].color_map[0][0]
                # OpenCV 的顏色格式需要整數值
                color = tuple(map(int, primary_color))
            else:
                # 若沒有偵測到顏色，使用預設顏色
                color = (255, 255, 255)  # 白色

            # 繪製框
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

            # 添加標籤文字
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = f"Label {label.name}"
            cv2.putText(image, text, (x1, y1 - 10), font, 0.5, color, 1, cv2.LINE_AA)

        # 建立輸出檔案路徑
        output_path = os.path.join(output_folder, os.path.basename(self.image_path))

        # 儲存繪製後的圖片
        cv2.imwrite(output_path, image)
        print(f"Image saved with bounding boxes to: {output_path}")
