from custom_object import color 
from custom_object import image_labels as il
from custom_object import label as lb
import colorsys

import os
import csv
from constant import path_config as path

class RunAnalysis:
    @staticmethod
    def run(label_to_color_map, csv_path):
        """
        @brief: 將所有標籤與顏色資料保存到指定的 CSV 檔案
        @param:
            label_to_color_map (dict): {label_name: Colors}, 包含標籤名稱及對應顏色的字典。
            csv_path (str): 儲存的 CSV 檔案路徑。
        """
        RunAnalysis.save_to_csv(label_to_color_map, csv_path)


    @staticmethod
    def save_to_csv(label_to_color_map, csv_path):
        """
        @brief: 將單一標籤的顏色資料保存到指定的 CSV 檔案
        @param:
            label_name (int): 標籤名稱
            colors (Colors): 包含顏色與佔比的物件
            csv_path (str): CSV 文件存儲路徑
        """
        # 確保目錄存在
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # 開啟 CSV 並寫入
        with open(csv_path, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # 寫入標籤及顏色資料
            row = ["NULL"] * 3 # 如果is_same_row=True, 就寫入前一行
            for label_name, colors in label_to_color_map.items():
                row[label_name] = f'{RunAnalysis.rgb_to_color_name(colors.color_map[0][0])}'
            writer.writerow(row)

    @staticmethod
    def rgb_to_color_name(rgb):
        """
        將 RGB 顏色轉換為 紅橙黃綠藍紫黑白 顏色類型
        @param:
            rgb (tuple): RGB 顏色 (R, G, B)，範圍 0-255
        @return:
            str: 顏色類型（如 "紅色", "藍色", "白色"）
        """
        
        # 將 RGB 值分開
        r, g, b = rgb
        
        # 將 RGB 值轉為 [0, 1] 範圍
        b, g, r = r / 255.0, g / 255.0, b / 255.0

        # RGB 轉 HSV
        h, s, v = colorsys.rgb_to_hsv(r, g, b)

        # 將 Hue 從 0~1 轉為角度 (0~360)
        h = h * 360

        # 判斷黑色或白色
        if s < 0.3:
            if v < 0.3:
                return "黑色"
            elif v >= 0.8:
                return "白色"

        # 判斷色系
        if 330 <= h < 360 or 0 <= h < 30:
            color = "紅色"
        elif 30 <= h < 60:
            color = "橙色"
        elif 60 <= h < 90:
            color = "黃色"
        elif 90 <= h < 150:
            color = "綠色"
        elif 150 <= h < 210:
            color = "青色"
        elif 210 <= h < 270:
            color = "藍色"
        elif 270 <= h < 330:
            color = "紫色"

        # 判斷深淺
        if v > 0.7 and s < 0.4:
            tone = "淺"
        elif v < 0.4:
            tone = "深"
        else:
            tone = ""

        return f"{tone}{color}"

    @staticmethod
    def is_similar_color(color1, color2) :
        '''
        @brief 判斷color1, color2是否為同色系顏色
        @param color1(str)
        @param color2(str)
        '''
    @staticmethod
    def visualize_result(csv_path = path.RESULT_CSV_PATH):
        '''
        建立 top_bottom_coat_dict (key : (label_0_color, label_1_color, label_2_color), value : 此顏色組合的數量)
        與 top_bottom_dict (key : (label_0_color, label_1_color), value : 此顏色組合的數量)
        逐行讀入 cvs, 格式 : NULL,NULL,"(54, 54, 103)" -> label_0_color, label_1_color, label_2_color
        假如此行只有一個有效(非NULL)value則捨去
        假如此行有兩個有效value則
        '''