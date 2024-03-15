import PIL
import cv2
import tempfile
import streamlit as st
from ultralytics import YOLO
import logging
from dotenv import load_dotenv
import os
import sys
from collections import Counter

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
model_path = os.getenv("MODEL_PATH")

if model_path is None:
    logging.error("MODEL_PATH not found in the environment variables.")
    st.error("MODEL_PATH not found in the environment variables.")
    sys.exit(1)

# Streamlit page configuration
st.set_page_config(
    page_title="Gun Detection - YOLO",
    page_icon="🐧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Main page title
st.title("Gun - Object Detection using YOLOv8")
st.caption('Upload a photo, video, or use your webcam')
st.caption('Then click the :blue[Detect Objects] button and check the result.')

# Sidebar for upload configuration
with st.sidebar:
    st.header("Upload Model Config")
    upload_type = st.radio("Choose the upload type:", ('Image', 'Video', 'Webcam'))
    
    source_file = None
    if upload_type == 'Image':
        source_file = st.file_uploader("Upload an image...", type=("jpg", "jpeg", "png", 'bmp', 'webp'))
    elif upload_type == 'Video':
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

def calculate_statistics(boxes):
    # Get the class labels of the detected objects
    labels = [int(box.cls) for box in boxes]
    # Count the occurrences of each label
    counter = Counter(labels)
    return dict(counter)

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

def process_webcam(model, confidence):
    stframe = st.empty()
    cap = cv2.VideoCapture(0)  # Webcam source

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Convert to the color scheme that YOLO expects
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res_plotted, _ = process_image(frame_rgb, model, confidence)
        frame = cv2.cvtColor(res_plotted, cv2.COLOR_RGB2BGR)
        stframe.image(frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()

# Displaying uploaded content and detection results
if source_file:
    if upload_type == 'Image':
        uploaded_image = PIL.Image.open(source_file)
        
        # Display uploaded image and detected image side by side
        col1, col2 = st.columns(2)
        
        # Display uploaded image in the first column
        with col1:
            st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        # Detect Objects button clicked
        if st.sidebar.button('Detect Objects'):
            logging.info("Detect Objects button clicked.")
            # Process and display the detected image
            detected_image, boxes = process_image(uploaded_image, model, confidence)
            
            # Calculate statistics
            stats = calculate_statistics(boxes)
            
            # Display statistics
            st.sidebar.header("Detection Statistics")
            for label, count in stats.items():
                st.sidebar.text(f"Class {label}: {count} instances")
            
            # Display detected image in the second column
            with col2:
                st.image(detected_image, caption="Detected Image", use_column_width=True)

                
                with st.expander("Detection Results"):
                    for box in boxes:
                        st.write(box.xywh)
    elif upload_type == 'Video':
        if st.sidebar.button('Detect Objects in Video'):
            logging.info("Detect Objects in Video button clicked.")
            process_video(source_file, model, confidence)

elif upload_type == 'Webcam':
    if st.sidebar.button('Start Webcam'):
        logging.info("Webcam started.")
        process_webcam(model, confidence)
else:
    logging.warning("No image, video or webcam selected.")
    st.write("Please upload an image, a video, or select webcam!")





