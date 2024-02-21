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
    'a':'https://www.google.com/search?q=boxing&tbm=isch&ved=2ahUKEwjJ1ZvFp7uEAxX20DQHHUoUAfcQ2-cCegQIABAA&oq=box&gs_lp=EgNpbWciA2JveCoCCAAyCBAAGIAEGLEDMggQABiABBixAzIIEAAYgAQYsQMyCBAAGIAEGLEDMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAESNUsUJMVWKoscAJ4AJABAJgBWKABqQOqAQE1uAEByAEA-AEBigILZ3dzLXdpei1pbWeoAgrCAgoQABiABBiKBRhDwgIGEAAYBxgewgIEECMYJ8ICDhAAGIAEGIoFGLEDGIMBwgIGEAAYBRgewgIHECMY6gIYJ4gGAQ&sclient=img&ei=jVXVZYlb9qHT6Q_KqIS4Dw&bih=569&biw=1280&rlz=1C1ONGR_enVN959VN959&hl=vi'
    ,'b':'https://www.google.com/search?q=danh+nhau&tbm=isch&ved=2ahUKEwjsn5neqbuEAxUY1jQHHaZbCcQQ2-cCegQIABAA&oq=danh+nhau&gs_lp=EgNpbWciCWRhbmggbmhhdTIEECMYJzIFEAAYgAQyBRAAGIAEMgUQABiABDIFEAAYgAQyBRAAGIAEMgUQABiABDIGEAAYBRgeMgYQABgFGB4yBhAAGAUYHkjCE1DGBljkEHAAeACQAQCYAdUBoAGoCKoBBTcuMi4xuAEDyAEA-AEBigILZ3dzLXdpei1pbWfCAg0QABiABBiKBRhDGLEDwgIKEAAYgAQYigUYQ8ICCBAAGIAEGLEDwgIOEAAYgAQYigUYsQMYgwHCAgsQABiABBixAxiDAYgGAQ&sclient=img&ei=2lfVZezKEJis0-kPpreloAw&bih=569&biw=1280&rlz=1C1ONGR_enVN959VN959&hl=vi'
    ,'c':'https://www.google.com/search?q=%C3%B4m+nhau+tr%C3%AAn+%C4%91%C6%B0%E1%BB%9Dng&tbm=isch&ved=2ahUKEwjqrZ_vsruEAxUcxjQHHR1FB94Q2-cCegQIABAA&oq=%C3%B4m+nhau+tr%C3%AAn+%C4%91%C6%B0%E1%BB%9Dng&gs_lp=EgNpbWciGMO0bSBuaGF1IHRyw6puIMSRxrDhu51uZ0jBPFCvBlilOHAFeACQAQGYAdYDoAHkFaoBCjE1LjUuMC4xLjG4AQPIAQD4AQGKAgtnd3Mtd2l6LWltZ8ICBBAjGCfCAgUQABiABMICChAAGIAEGIoFGEPCAgYQABgFGB7CAgYQABgIGB6IBgE&sclient=img&ei=bWHVZarDOZyM0-kPnYqd8A0&bih=569&biw=1280&rlz=1C1ONGR_enVN959VN959'
}

# Lặp qua danh sách các URL và thực hiện quy trình tải ảnh
for url_key in urls_to_scrape:
    scrape_images_from_google(url_key,urls_to_scrape[url_key])
    print(urls_to_scrape[url])