import scrapy
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import requests
import os
import time
import re
import util.logger as logger
import config.constant_config as cf


class FasBeeSpider(scrapy.Spider):
    """
    爬蟲類，用於抓取 fas-bee.com 網站的圖片資料。

    功能：
    - 支援多頁面爬取，並透過 URL 規律判斷下一頁
    - 使用 Selenium 配合 BeautifulSoup, 處理單頁式網站的 Lazy Loading
    - 過濾符合條件的圖片 URL
    - 支援圖片下載並以 image_{index}.jpg 命名
    """
    name = "fas_bee_spider"
    allowed_domains = ["fas-bee.com"]
    start_urls = ["https://fas-bee.com/zh-tw/collections"]
    page_number = 209
    max_pages = cf.MAX_PAGES_SPIDER_CRAWL

    def __init__(self):
        """
        init crawler, 配置 Selenium 驅動器與相關參數。
        """
        self.service = Service(executable_path="./chromedriver.exe")
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # 啟用無頭模式
        self.chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
        self.chrome_options.add_argument("--no-sandbox")  # 避免在某些環境中報錯
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.url_format = cf.START_URL

    def parse(self, response):
        """
        main crawler, 處理每個頁面的圖片提取與下載。
        """
        while self.page_number <= self.max_pages:  # 限制爬取頁數
            url = self.url_format.format(PAGE=self.page_number) # url 中的 {PAGE} 會被替換為 page_number
            logger.info(cf.PROCESS, f"Fetching page: {url}")
            self.driver.get(url)

            # 觸發 Lazy Loading
            self.lazy_loading_officer()

            # 提取圖片 URL
            imgs = self.imgs_url_save()

            for idx, img in enumerate(imgs):
                try:
                    img_url = self.img_filter(img)
                    if img_url:
                        logger.info(cf.IMAGE, f"{img_url}")
                        self.image_download_by_url(img_url, "images", image_index=idx + (self.page_number - 1) * len(imgs))
                except Exception as e:
                    logger.error(cf.PROCESS, f"Failed to process image {idx}: {e}")

            # 檢查是否有下一頁
            if not self.check_next_page_exist():
                logger.info(cf.PROCESS, f"No more content on page {self.page_number + 1}.")
                break
            self.page_number += 1  # 繼續爬取下一頁

        # 關閉 WebDriver
        self.driver.quit()

    def lazy_loading_officer(self):
        """
        使用 JavaScript 滾動頁面以觸發 Lazy Loading。
        """
        for _ in range(10):  # 根據需要調整滾動次數
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)  # 每次滾動後等待頁面加載
        time.sleep(3)  # 確保頁面完全加載

    def imgs_url_save(self):
        """
        使用 BeautifulSoup 解析頁面，返回所有圖片標籤。

        :return: 包含當前頁面所有 <img> 標籤的列表
        """
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        imgs = soup.find_all('img')
        logger.info(cf.PROCESS, f"Found {len(imgs)} images on page {self.page_number}.")
        return imgs

    def img_filter(self, img):
        """
        過濾出符合條件的圖片 URL。

        條件：
        - 目標 URL 的 `srcset` 屬性包含 `width=700`

        :param img: <img> 標籤
        :return: 符合條件的圖片 URL, 若無則返回 None
        """
        if 'srcset' not in img.attrs:
            return None

        srcset = img['srcset']
        for entry in srcset.split(','):
            parts = entry.strip().split(' ')
            if len(parts) == 2:  # 確保格式正確
                img_url = parts[0]
                try:
                    # 使用正則表達式檢查是否包含 `width=700`
                    if re.search(r'width=700', img_url):
                        if not img_url.startswith('http'):
                            img_url = 'https:' + img_url
                        return img_url
                except Exception as e:
                    logger.warning(cf.PROCESS, f"Error in filtering image URL: {e}")
        return None

    def check_next_page_exist(self):
        """
        檢查是否存在下一頁內容。

        :return: 如果下一頁存在圖片內容，返回 True, 否則返回 False
        """
        next_page_url = self.url_format + f"{self.page_number + 1}"
        self.driver.get(next_page_url)
        time.sleep(3)
        html_next_page = self.driver.page_source
        soup_next_page = BeautifulSoup(html_next_page, 'html.parser')
        return bool(soup_next_page.find_all('img'))

    def image_download_by_url(self, url, save_folder, image_index):
        """
        下載圖片到指定文件夾，並以 image_{index}.jpg 命名檔案。

        :param url: 圖片 URL
        :param save_folder: 保存圖片的文件夾
        :param image_index: 圖片的索引，用於命名
        """
        try:
            # 確保保存的文件夾存在
            os.makedirs(save_folder, exist_ok=True)

            # 發送請求下載圖片
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                # 根據索引生成檔案名稱
                file_name = f"image_{image_index}.jpg"
                save_path = os.path.join(save_folder, file_name)

                # 保存圖片
                with open(save_path, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)

                logger.info(cf.PROCESS, f"Image saved to: {save_path}")
            else:
                logger.error(cf.PROCESS, f"Failed to download image: {url}. HTTP status: {response.status_code}")

        except Exception as e:
            logger.error(cf.PROCESS, f"Error downloading image {url}: {e}")