import PIL
import cv2
import tempfile
import streamlit as st
from ultralytics import YOLO
import logging
from dotenv import load_dotenv
import os
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
model_path = os.getenv("MODEL_PATH")

if model_path is None:
    logging.error("MODEL_PATH not found in the environment variables.")
    st.error("MODEL_PATH not found in the environment variables.")
    sys.exit(1)

# Setting page layout
st.set_page_config(
    page_title="Gun Detection - YOLO",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Creating main page heading
st.title("Gun - Object Detection using YOLOv8",)
st.caption('Upload a photo or video')
st.caption('Then click the :blue[Detect Objects] button and check the result.')

# Creating sidebar for image and video configuration
with st.sidebar:
    st.header("Upload Config")
    upload_type = st.radio("Choose the upload type:", ('Image', 'Video'))
    
    if upload_type == 'Image':
        source_file = st.file_uploader("Upload an image...", type=("jpg", "jpeg", "png", 'bmp', 'webp'))
    else:
        source_file = st.file_uploader("Upload a video...", type=("mp4", "avi", "mov", 'mkv'))

    # Model Options
    confidence = st.slider("Select Model Confidence", 25, 100, 40) / 100

# Load the YOLO model
try:
    logging.info(f"Loading YOLO model from path: {model_path}")
    model = YOLO(model_path)
    logging.info("Model loaded successfully.")
except Exception as ex:
    logging.error(f"Unable to load model. Check the specified path: {model_path}", exc_info=True)
    st.error(f"Unable to load model. Check the specified path: {model_path}")
    sys.exit(1)

def process_image(image, model, confidence):
    logging.info("Processing image for object detection.")
    res = model.predict(image, conf=confidence)
    res_plotted = res[0].plot()[:, :, ::-1]
    return res_plotted, res[0].boxes

def process_video(video_file, model, confidence):
    logging.info("Processing video for object detection.")
    tfile = tempfile.NamedTemporaryFile(delete=False) 
    tfile.write(video_file.read())
    vf = cv2.VideoCapture(tfile.name)

    stframe = st.empty()
    while vf.isOpened():
        ret, frame = vf.read()
        if not ret:
            break
        res_plotted, _ = process_image(frame, model, confidence)
        frame = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
        stframe.image(frame)

# Creating main section for displaying images and results
columns = st.columns(2)
col1, col2 = columns[0], columns[1]

# Displaying uploaded content and detection results
if source_file:
    if upload_type == 'Image':
        uploaded_image = PIL.Image.open(source_file)
        
        # Display uploaded image in the first column
        col1.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

        # Detect Objects button clicked
        if st.sidebar.button('Detect Objects'):
            logging.info("Detect Objects button clicked.")
            # Process and display the detected image in the second column
            detected_image, boxes = process_image(uploaded_image, model, confidence)
            col2.image(detected_image, caption="Detected Image", use_column_width=True)
            
            with col2.expander("Detection Results"):
                for box in boxes:
                    col2.write(box.xywh)
    else:
        if st.sidebar.button('Detect Objects in Video'):
            logging.info("Detect Objects in Video button clicked.")
            process_video(source_file, model, confidence)
else:
    logging.warning("No image or video uploaded.")
    st.write("Please upload an image or video!")
