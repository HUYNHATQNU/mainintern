import os
import shutil
import random

def split_data(source, train_dir, test_dir, split_ratio):
    """
    Chia dữ liệu từ thư mục nguồn thành thư mục train và test với tỷ lệ cho trước.
    
    Parameters:
    - source: Đường dẫn đến thư mục chứa dữ liệu nguồn.
    - train_dir: Đường dẫn đến thư mục train.
    - test_dir: Đường dẫn đến thư mục test.
    - split_ratio: Tỷ lệ dữ liệu sẽ được chia vào thư mục train (vd: 0.8 là 80% train, 20% test).
    """
    # Tạo thư mục train và test nếu chưa tồn tại
    if not os.path.exists(train_dir):
        os.makedirs(train_dir)
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # Lấy danh sách tệp từ thư mục nguồn
    files = os.listdir(source)
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
source_dir = "C:\\Users\\rLap.com\\OneDrive\\Desktop\\New folder\\images"
# Đường dẫn đến thư mục train và test
train_dir = "C:\\Users\\rLap.com\\OneDrive\\Desktop\\Thực Tập TMA\\train"
test_dir = "C:\\Users\\rLap.com\\OneDrive\\Desktop\\Thực Tập TMA\\test"
# Tỷ lệ dữ liệu sẽ được chia vào thư mục train
split_ratio = 0.7

# Chia dữ liệu
split_data(source_dir, train_dir, test_dir, split_ratio)
