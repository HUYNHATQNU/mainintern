# -*- coding: utf-8 -*-
"""yolov8.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ukf8pohoEMKyc-6JxmgK_ynpoSAwcLF5
"""

from google.colab import drive
drive.mount('/content/drive/', force_remount=True)

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive/

!pip install ultralytics

!git clone https://github.com/ultralytics/ultralytics

!wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/MyDrive

!yolo task=detect mode=train model=yolov8n.pt data=/content/drive/MyDrive/intern/train_demo.yaml epochs=200 imgsz=640 batch =20 optimizer='AdamW' lr0=0.001

!yolo export model='/content/drive/MyDrive/runs/detect/200epoch_20batch/weights/last.pt' format=tflite imgsz=640
