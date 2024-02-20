import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

def download_image(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"Đã tải xuống hình ảnh thành công và lưu vào '{save_path}'")
        else:
            print(f"Lỗi khi tải xuống hình ảnh từ URL: {url}")
    except Exception as e:
        print(f"Lỗi khi tải xuống hình ảnh: {e}")

# Khởi tạo trình duyệt
driver = webdriver.Chrome()

# Mở trang web
driver.get("https://www.google.com/search?sca_esv=0f23f44a810f0132&sxsrf=ACQVn09ttMuVhIn4QphdbAF2UHbvCD7_LQ:1708440076795&q=danh+nhau&tbm=isch&source=lnms&sa=X&ved=2ahUKEwi6wpafk7qEAxUZ2DQHHYWhDQUQ0pQJegQICxAB&biw=1280&bih=569&dpr=1.5")

# Trích xuất HTML từ trang web
html = driver.page_source

# Sử dụng BeautifulSoup để phân tích HTML
soup = BeautifulSoup(html, "html.parser")

# Tìm tất cả các thẻ <img> trong HTML
images = soup.find_all("img", class_="rg_i")

# Tạo thư mục để lưu trữ ảnh (nếu chưa tồn tại)
os.makedirs("images", exist_ok=True)

# Số lượng ảnh tải về tối đa
max_images = 10
downloaded_images = 10

# Lặp qua danh sách các hình ảnh và tải chúng về
for img in images:
    img_url = img.get("src")
    if img_url:
        try:
            response = requests.get(img_url)
            response.raise_for_status()  # Xác nhận không có lỗi khi yêu cầu
            img_filename = os.path.join("images", f"image_{downloaded_images}.jpg")
            with open(img_filename, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {img_filename}")
            downloaded_images += 1
            if downloaded_images >= max_images:
                break
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {img_url}: {str(e)}")

# Đóng trình duyệt
driver.quit()
