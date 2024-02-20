#!/usr/bin/env python

import sys
import os

for line in sys.stdin:
    # Lấy tên file từ biến môi trường
    file_name = os.environ["map_input_file"]
    
    # Tách từ trong dòng
    words = line.strip().split()
    
    # Đếm số lần xuất hiện của các từ quan trọng
    count_mapreduce = words.count("MapReduce")
    count_map = words.count("Map")
    count_reduce = words.count("Reduce")
    
    # Gửi kết quả ra output
    print(f"{file_name}\tMapReduce\t{count_mapreduce}")
    print(f"{file_name}\tMap\t{count_map}")
    print(f"{file_name}\tReduce\t{count_reduce}")
