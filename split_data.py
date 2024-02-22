#!/usr/bin/env python
# coding: utf-8

# In[40]:


import os
import shutil
import random

def split_data(source, train_dir, test_dir, split_ratio):
    # Tạo thư mục train và test nếu chưa tồn tại
    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Lấy danh sách tệp từ thư mục nguồn
    files = [f for f in os.listdir(source) if f != '.ipynb_checkpoints']
    # Số lượng tệp cần di chuyển vào thư mục train
    num_train = int(len(files) * split_ratio)
    # Ngẫu nhiên chọn các tệp cho train
    train_files = random.sample(files, num_train)
    
    # Di chuyển tệp vào thư mục train hoặc test
    for file in files:
        source_file = os.path.join(source, file)
        if file in train_files:
            shutil.copy(source_file, train_dir)
        else:
            shutil.copy(source_file, test_dir)

# Đường dẫn đến thư mục chứa dữ liệu nguồn
source_dir = "C:\\Users\\ASUS\\Documents\\THỰC TẬP TỐT NGHIỆP\\images"
# Đường dẫn đến thư mục train và test
train_dir = "C:\\Users\\ASUS\\Documents\\THỰC TẬP TỐT NGHIỆP\\train"
test_dir = "C:\\Users\\ASUS\\Documents\\THỰC TẬP TỐT NGHIỆP\\test"
# Tỷ lệ dữ liệu sẽ được chia vào thư mục train
split_ratio = 0.7

# Chia dữ liệu
split_data(source_dir, train_dir, test_dir, split_ratio)


# In[ ]:




