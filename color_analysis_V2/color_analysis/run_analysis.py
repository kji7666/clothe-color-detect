from custom_object import color 
from custom_object import image_labels as il
from custom_object import label as lb
import colorsys
from ast import literal_eval
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import math
import os
import csv
from constant import path_config as path

class RunAnalysis:
    @staticmethod
    def run_and_save_to_csv(label_to_color_map, csv_path):
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
            row = ["NULL"] * 3
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
        b, g, r = rgb
        return f"({r}, {g}, {b})"

    @staticmethod
    def is_similar_color(color1, color2):
        """
        @brief 判斷 color1, color2 是否為同色系顏色
        @param color1 (tuple): 第一個 RGB 顏色 (r1, g1, b1)
        @param color2 (tuple): 第二個 RGB 顏色 (r2, g2, b2)
        @return (bool): 若兩顏色的差異總和小於等於 60, 且 RGB 值各自不相差超過 30, 返回 True, 否則返回 False
        """
        try:
            r1, g1, b1 = color1
            r2, g2, b2 = color2
        except ValueError as e:
            raise ValueError(f"Invalid color format: {color1}, {color2}") from e

        diff = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
        return diff <= 60 and abs(r1 - r2) <= 30 and abs(g1 - g2) <= 30 and abs(b1 - b2) <= 30
    
    @staticmethod
    def analysis_csv(csv_path = path.RESULT_CSV_PATH):
        '''
        @brief 分析統計存入 csv 檔的顏色組合, 並視覺化數據
        建立 top_bottom_coat_list (key : (label_0_color, label_1_color, label_2_color), value : 此顏色組合的數量)
        與 top_bottom_list (key : (label_0_color, label_1_color), value : 此顏色組合的數量)
        逐行讀入 .cvs
        格式 : NULL,NULL,"(54, 54, 103)" -> label_0_color, label_1_color, label_2_color
        if (假如此行只有一個有效(非NULL)value) : continue
        if (假如此行有兩個有效value 且為label0, label2)  : 存入top_bottom_list
        if (假如此行有三個有效value) : 存入 top_bottom_coat_dict
        '''

        top_bottom_coat_dict = {}
        top_bottom_dict = {}

        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                try:
                    # 過濾 NULL 並記錄非空值索引
                    valid_values = [(i, literal_eval(val)) for i, val in enumerate(row) if val != "NULL"]
                    # 若只有一個有效值，跳過
                    if len(valid_values) < 2:
                        continue
                    # 若為兩個有效值
                    if len(valid_values) == 2:
                        keys = tuple(val[1] for val in valid_values)
                        top_bottom_dict[keys] = top_bottom_dict.get(keys, 0) + 1
                    # 若為三個有效值
                    if len(valid_values) == 3:
                        keys = tuple(val[1] for val in valid_values)
                        top_bottom_coat_dict[keys] = top_bottom_coat_dict.get(keys, 0) + 1
                except ValueError as e:
                    print(f"Error processing row: {row}, error: {e}")
        RunAnalysis.visualize_result(top_bottom_coat_dict, top_bottom_dict)

    @staticmethod
    def visualize_result(top_bottom_coat_dict, top_bottom_dict, csv_path = path.RESULT_CSV_PATH):
        RunAnalysis.plot_top_combinations_with_coat(RunAnalysis.statistics_top_bottom_coat_combination(top_bottom_coat_dict), top_n=3)
        RunAnalysis.plot_top_combinations(RunAnalysis.statistics_top_bottom_combination(top_bottom_dict), top_n=3)
        #return top_bottom_coat_dict, top_bottom_dict
    
    @staticmethod
    def statistics_top_bottom_coat_combination(top_bottom_coat_dict):
        """
        因為顏色即使 RGB 值有些許差異，也算是同個色系。
        對 top_bottom_coat_dict 進行合併統計相似顏色的組合。
        @param top_bottom_coat_dict (dict): 包含顏色組合及其次數的字典。
        @return (list): 合併相似顏色後，按數量排序的列表。
        """
        # 取出所有鍵並轉換為列表以進行遍歷
        keys = list(top_bottom_coat_dict.keys())

        # 使用集合儲存已合併的鍵
        merged_keys = set()

        # 遍歷所有組合進行比較
        for i in range(len(keys)):
            if keys[i] in merged_keys:
                continue

            # 確保顏色為有效格式
            try:
                a_rgb1, a_rgb2, a_rgb3 = keys[i]
            except ValueError:
                raise ValueError(f"Invalid key format in top_bottom_coat_dict: {keys[i]}")

            for j in range(i + 1, len(keys)):
                if keys[j] in merged_keys:
                    continue

                try:
                    b_rgb1, b_rgb2, b_rgb3 = keys[j]
                except ValueError:
                    raise ValueError(f"Invalid key format in top_bottom_coat_dict: {keys[j]}")

                b_rgb1, b_rgb2, b_rgb3 = keys[j]

                # 檢查三個 RGB 值是否屬於同一色系
                if (RunAnalysis.is_similar_color(a_rgb1, b_rgb1) and
                    RunAnalysis.is_similar_color(a_rgb2, b_rgb2) and
                    RunAnalysis.is_similar_color(a_rgb3, b_rgb3)):

                    # 合併數量
                    top_bottom_coat_dict[keys[i]] += top_bottom_coat_dict[keys[j]]

                    # 將相似組合標記為已合併
                    merged_keys.add(keys[j])

        # 刪除已合併的鍵
        for key in merged_keys:
            del top_bottom_coat_dict[key]

        # 將字典轉換為列表並排序
        sorted_list = sorted(top_bottom_coat_dict.items(), key=lambda x: x[1], reverse=True)

        return sorted_list

    @staticmethod
    def plot_top_combinations_with_coat(color_combinations, top_n=3):
        """
        使用 matplotlib 印出前 N 名顏色組合的配色，並以由上到下的三個圓形表示顏色。
        自動調整圖表佈局以適應視窗大小。
        @param color_combinations (list): 包含顏色組合和數量的排序列表 [(key, value)]。
        @param top_n (int): 要顯示的前 N 名組合，預設為 3。
        """
        # 確保不超出列表長度
        top_n = min(top_n, len(color_combinations))

        # 動態計算行列數：每行最多 3 個組合
        max_columns = 3
        rows = math.ceil(top_n / max_columns)
        cols = min(max_columns, top_n)

        # 設定圖表大小，根據行數和列數調整
        plt.figure(figsize=(cols * 3, rows * 3))

        # 遍歷前 N 名組合
        for idx, (colors, count) in enumerate(color_combinations[:top_n]):
            ax = plt.subplot(rows, cols, idx + 1)

            # 確保每組有三個顏色
            if len(colors) != 3:
                raise ValueError(f"Expected 3 colors in combination, but got {len(colors)}: {colors}")

            # 設置圓形的中心點與半徑
            centers = [(0.5, 0.8), (0.5, 0.5), (0.5, 0.2)]  # 三個圓的位置
            radius = 0.1

            # 繪製三個圓形
            for center, color in zip(centers, colors):
                rgb_color = tuple(int(c) for c in color)  # 確保 RGB 值為整數
                circle = Circle(center, radius, color=[c / 255.0 for c in rgb_color])
                ax.add_patch(circle)

            # 設定標題與軸
            ax.set_title(f"Rank {idx + 1}\nCount: {count}", fontsize=10)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')  # 確保軸的比例為 1:1
            ax.axis("off")

        # 自動調整子圖間距
        plt.tight_layout()
        plt.subplots_adjust(bottom=0)  # 去除底部工具欄
        plt.show()

    @staticmethod
    def statistics_top_bottom_combination(top_bottom_dict):
        """
        因為顏色即使 RGB 值有些許差異，也算是同個色系。
        對 top_bottom_coat_dict 進行合併統計相似顏色的組合。
        @param top_bottom_coat_dict (dict): 包含顏色組合及其次數的字典。
        @return (list): 合併相似顏色後，按數量排序的列表。
        """
        # 取出所有鍵並轉換為列表以進行遍歷
        keys = list(top_bottom_dict.keys())

        # 使用集合儲存已合併的鍵
        merged_keys = set()

        # 遍歷所有組合進行比較
        for i in range(len(keys)):
            if keys[i] in merged_keys:
                continue

            # 確保顏色為有效格式
            try:
                a_rgb1, a_rgb2 = keys[i]
            except ValueError:
                raise ValueError(f"Invalid key format in top_bottom_coat_dict: {keys[i]}")

            for j in range(i + 1, len(keys)):
                if keys[j] in merged_keys:
                    continue

                try:
                    b_rgb1, b_rgb2 = keys[j]
                except ValueError:
                    raise ValueError(f"Invalid key format in top_bottom_coat_dict: {keys[j]}")

                b_rgb1, b_rgb2 = keys[j]

                # 檢查三個 RGB 值是否屬於同一色系
                if (RunAnalysis.is_similar_color(a_rgb1, b_rgb1) and
                    RunAnalysis.is_similar_color(a_rgb2, b_rgb2)):

                    # 合併數量
                    top_bottom_dict[keys[i]] += top_bottom_dict[keys[j]]

                    # 將相似組合標記為已合併
                    merged_keys.add(keys[j])

        # 刪除已合併的鍵
        for key in merged_keys:
            del top_bottom_dict[key]

        # 將字典轉換為列表並排序
        sorted_list = sorted(top_bottom_dict.items(), key=lambda x: x[1], reverse=True)

        return sorted_list

    @staticmethod
    def plot_top_combinations(color_combinations, top_n=3):
        """
        使用 matplotlib 印出前 N 名顏色組合的配色，並以由上到下的三個圓形表示顏色。
        自動調整圖表佈局以適應視窗大小。
        @param color_combinations (list): 包含顏色組合和數量的排序列表 [(key, value)]。
        @param top_n (int): 要顯示的前 N 名組合，預設為 3。
        """
        # 確保不超出列表長度
        top_n = min(top_n, len(color_combinations))

        # 動態計算行列數：每行最多 3 個組合
        max_columns = 3
        rows = math.ceil(top_n / max_columns)
        cols = min(max_columns, top_n)

        # 設定圖表大小，根據行數和列數調整
        plt.figure(figsize=(cols * 3, rows * 3))

        # 遍歷前 N 名組合
        for idx, (colors, count) in enumerate(color_combinations[:top_n]):
            ax = plt.subplot(rows, cols, idx + 1)

            # 確保每組有兩個顏色
            if len(colors) != 2:
                raise ValueError(f"Expected 3 colors in combination, but got {len(colors)}: {colors}")

            # 設置圓形的中心點與半徑
            centers = [(0.5, 0.8), (0.5, 0.5)]  # 兩個圓的位置
            radius = 0.1

            for center, color in zip(centers, colors):
                rgb_color = tuple(int(c) for c in color)  # 確保 RGB 值為整數
                circle = Circle(center, radius, color=[c / 255.0 for c in rgb_color])
                ax.add_patch(circle)

            # 設定標題與軸
            ax.set_title(f"Rank {idx + 1}\nCount: {count}", fontsize=10)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal')  # 確保軸的比例為 1:1
            ax.axis("off")

        # 自動調整子圖間距
        plt.tight_layout()
        plt.subplots_adjust(bottom=0)  # 去除底部工具欄
        plt.show()