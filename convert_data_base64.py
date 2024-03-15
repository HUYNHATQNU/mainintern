import os
import base64
import sqlite3

directory = r'C:\Users\rLap.com\OneDrive\Desktop\New\train'
image_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

conn = sqlite3.connect('Violence_detection.db')
cursor = conn.cursor()

# Tạo bảng trong cơ sở dữ liệu nếu chưa tồn tại
cursor.execute('''CREATE TABLE IF NOT EXISTS Images
                  (id INTEGER PRIMARY KEY, filename TEXT, base64_data TEXT)''')

for image_file in image_files:
    with open(os.path.join(directory, image_file), 'rb') as file:
        image_data = file.read()
    # Mã hóa dữ liệu hình ảnh thành base64
    base64_encoded = base64.b64encode(image_data).decode('utf-8')
    # Thêm dữ liệu vào cơ sở dữ liệu
    cursor.execute('INSERT INTO Images (filename, base64_data) VALUES (?, ?)', (image_file, base64_encoded))

conn.commit()
conn.close()
