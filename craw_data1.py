#!/usr/bin/env python
# coding: utf-8

# In[14]:


import os
import time
import requests
import base64
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def download_image(img_data, save_path):
    try:
        with open(save_path, 'wb') as f:
            f.write(img_data)
        print(f"Đã tải xuống hình ảnh thành công và lưu vào '{save_path}'")
    except Exception as e:
        print(f"Lỗi khi tải xuống hình ảnh: {e}")

def scrape_images_from_google(url_key,url, max_images=500):
    # Khởi tạo trình duyệt
    driver = webdriver.Chrome()

    # Mở trang web
    driver.get(url)

    # Lặp để cuộn trang và tải thêm ảnh
    for i in range(5):  # Cuộn trang 5 lần,
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Đợi để trang cuộn và ảnh tải thêm

    # Trích xuất HTML từ trang web sau khi cuộn
    html = driver.page_source

    # Sử dụng BeautifulSoup để phân tích HTML
    soup = BeautifulSoup(html, "html.parser")

    # Tìm tất cả các thẻ <img> trong HTML
    images = soup.find_all("img", class_="rg_i")

    # Tạo thư mục để lưu trữ ảnh (nếu chưa tồn tại)
    os.makedirs("images", exist_ok=True)

    # Số lượng ảnh tải về tối đa
    downloaded_images = 0

    # Lặp qua danh sách các hình ảnh và tải chúng về
    for img in images:
        img_url = img.get("src")
        if img_url:
            try:
                if "base64," in img_url:
                    img_data = base64.b64decode(img_url.split("base64,")[1])
                else:
                    response = requests.get(img_url)
                    response.raise_for_status()  # Xác nhận không có lỗi khi yêu cầu
                    img_data = response.content
                img_filename = os.path.join("images", f"image_{downloaded_images}_{url_key}.jpg")
                download_image(img_data, img_filename)
                downloaded_images += 1
                if downloaded_images >= max_images:
                    break
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {img_url}: {str(e)}")

    # Đóng trình duyệt
    driver.quit()

# Danh sách các URL của trang web
urls_to_scrape = {
    'a':'https://www.google.com/search?sca_esv=b9615c6636962dbd&sxsrf=ACQVn08XCnWRi4kYPhDM3p7HXmCwHVBbYg:1708456506946&q=%E1%BA%A3nh+x%E1%BA%A3+s%C3%BAng&tbm=isch&source=lnms&sa=X&ved=2ahUKEwivtte50LqEAxXV4TgGHeQ0DxoQ0pQJegQIDBAB&biw=1536&bih=730&dpr=1.25'
    ,'b':'https://www.google.com/search?sca_esv=b9615c6636962dbd&sxsrf=ACQVn0-8cWSckfTI3XBcpy52ETDBMAwmuw:1708459535597&q=%E1%BA%A3nh+x%E1%BA%A3+s%C3%BAng+kh%E1%BB%A7ng+b%E1%BB%91&tbm=isch&source=lnms&sa=X&ved=2ahUKEwiZ1O3d27qEAxXcqWMGHfEBA4gQ0pQJegQIDhAB&biw=1536&bih=730&dpr=1.25'
    ,'c':'https://www.google.com/search?sca_esv=37890abde774ea9a&sxsrf=ACQVn0_RxmIVXfGCeFsZxvKtRf9Nr_zvvw:1708480318246&q=ng%C6%B0%E1%BB%9Di+c%E1%BA%A7m+s%C3%BAng&tbm=isch&source=lnms&sa=X&ved=2ahUKEwjw7eWTqbuEAxVMUvUHHSbzAqoQ0pQJegQICxAB&biw=1536&bih=730&dpr=1.25'
}

# Lặp qua danh sách các URL và thực hiện quy trình tải ảnh
for url_key in urls_to_scrape:
    scrape_images_from_google(url_key,urls_to_scrape[url_key])
    print(urls_to_scrape[url])


# In[ ]:




