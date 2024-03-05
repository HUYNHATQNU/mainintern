import os
import io
import cv2
import yaml
import torch
import numpy as np
from PIL import Image
import streamlit as st
from typing import Union
from ultralytics import YOLO

# Define the device to be used for computation
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Initialize YOLO model
model = YOLO(r'C:\Users\rLap.com\OneDrive\Desktop\New folder\ultralytics\last.pt')


# Function for loading data from yaml file
def load_yaml(file_path: str) -> dict:
    """
    Load YAML file.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
        dict: Loaded YAML data.
    """
    with open(file_path, 'r') as file:
        try:
            data = yaml.safe_load(file)
            return data
        except yaml.YAMLError as exc:
            print(exc)


# Function for removing temporary files
'''def remove_temp(temp_file: str = 'temp') -> None:
    """
    Remove all files in the specified temporary directory.

    Args:
        temp_file (str, optional): Path to the temporary directory. Defaults to 'temp'.
    """
    for file in os.listdir(temp_file):
        os.remove(os.path.join(temp_file, file))'''




# Function for detecting objects in an image
def image_detect(image: str, confidence_threshold: float, max_detections: int, class_ids: list) -> None:
    """
    Detects objects in an image using YOLO model.

    Args:
        image (str): Path to the input image.
        confidence_threshold (float): Confidence threshold for object detection.
        max_detections (int): Maximum number of detections.
        class_ids (list): List of class IDs to consider for detection.
    """
    # Open the image
    image = Image.open(image)

    # Perform object detection
    results = model.predict(image, conf=confidence_threshold,
                            max_det=max_detections,classes=class_ids, device=DEVICE)

    # Plot the detected objects on the image
    plot = results[0].plot()

    # Convert color space from BGR to RGB
    processed_image = cv2.cvtColor(plot, cv2.COLOR_BGR2RGB)

    # Show the detected image
    st.image(processed_image, caption='Detected Image.', use_column_width='auto', output_format='auto', width=None)

    # Function for real-time object detection in a video stream
def video_detect(source: str, uploaded_video: Union[None, io.BytesIO], confidence_threshold: float,
                 max_detections: int, class_ids: list) -> None:
    """
    Performs real-time object detection in a video stream.

    Args:
        source (str): Video source
        uploaded_video (Union[None, io.BytesIO, str]): Uploaded video file.
        confidence_threshold (float): Confidence threshold for object detection.
        max_detections (int): Maximum number of detections.
        class_ids (list): List of class IDs to consider for detection.
    """
    # Display for video feed
    video_feed = st.empty()

    # Check if a video is uploaded or using webcam
    if source == "video":
        # Create a temporary file to save the uploaded video
        temp_video_path = f"temp/temp_{uploaded_video.name}"

        # Write uploaded video content to the temporary file
        with open(temp_video_path, "wb") as temp_video_file:
            temp_video_file.write(uploaded_video.getvalue())

        # Open the uploaded video file
        cap = cv2.VideoCapture(temp_video_path)
    