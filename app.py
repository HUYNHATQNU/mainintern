import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from io import BytesIO
from PIL import Image, ImageDraw
from ultralytics import YOLO
import io
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
model_path = os.getenv("MODEL_PATH")
logging.info(f"Model path from env: {model_path}")

try:
    model = YOLO(model_path)
    logging.info("Model loaded successfully.")
except Exception as ex:
    logging.error("Unable to load model. Check the specified path.", exc_info=True)
    raise RuntimeError(f"Unable to load model. Check the specified path: {model_path}") from ex


@app.get("/")
async def get_index():
    logging.info("Serving index.html")
    return FileResponse("index.html")


@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    logging.info("Received a file for object detection.")
    contents = await file.read()
    image = Image.open(BytesIO(contents))

    confidence = 0.4  # Set your confidence level here

    try:
        detected_boxes = []  # Initialize the list of bounding boxes

        # Dự đoán các đối tượng trong hình ảnh
        results = model.predict(image, conf=confidence)
        logging.info("Object detection performed.")

        for result in results:
            # Kiểm tra xem kết quả có hộp giới hạn không
            if result.boxes is not None:
                # Lặp qua từng hộp giới hạn của kết quả dự đoán
                for box in result.boxes:
                    # Chuyển đổi tensor xyxy thành danh sách và sửa định dạng tọa độ
                    xyxy_list = box.xyxy.tolist()

                    # Thêm thông tin của hộp giới hạn vào danh sách với độ tin cậy
                    detected_boxes.append({
                        "class": int(box.cls),       # Class of the object
                        "confidence": float(box.conf), # Confidence
                        "xyxy": xyxy_list
                    })
        logging.info(f"Detected {len(detected_boxes)} objects.")

        # Trả về danh sách các hộp giới hạn dưới dạng JSON
        return JSONResponse(content={"detected_objects": detected_boxes})
    except Exception as ex:
        logging.error("Error during object detection.", exc_info=True)
        return JSONResponse(content={"error": f"Error during object detection: {ex}"})


from fastapi.responses import JSONResponse
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw
from io import BytesIO
import io

@app.post("/detect_and_return_image")
async def detect_objects_and_return_image(file: UploadFile = File(...)):
    logging.info("Received a file for object detection and returning image with boxes.")
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    confidence = 0.4

    class_names = {0: "Gun", 1: "Fake Gun"}

    try:
        detected_boxes = []
        gun_message = None

        # Predict objects in the image
        results = model.predict(image, conf=confidence)
        logging.info("Object detection performed for image return.")

        # Iterate through each prediction result
        for result in results:
            if result.boxes is not None:
                # Iterate through each bounding box in the prediction result
                for box in result.boxes:
                    cls = int(box.cls)  # Get the class ID of the object
                    class_name = class_names.get(cls, "Unknown")  # Get the class name from the map or use "Unknown" if not found
                    
                    xyxy_list = [float(coord) for coord in box.xyxy.flatten()]
                    detected_boxes.append({
                        "class": cls,
                        "class_name": class_name,
                        "confidence": float(box.conf),
                        "xyxy": xyxy_list
                    })

                    # Check if it is a gun or a fake gun and assign the corresponding message
                    if cls == 0:
                        gun_message = "Gun detected!"
                    elif cls == 1:
                        gun_message = "Fake gun detected!"

        logging.info(f"Detected {len(detected_boxes)} objects with image return.")

        # Draw bounding boxes on the image
        image_with_boxes = image.copy()
        draw = ImageDraw.Draw(image_with_boxes)
        for box in detected_boxes:
            draw.rectangle(box["xyxy"], outline="red", width=3)
            # Display class name and confidence next to each bounding box
            draw.text((box["xyxy"][0], box["xyxy"][1] - 10), f"{box['class_name']} Conf: {box['confidence']:.2f}", fill="red")

        # Display the gun message if present
        if gun_message:
            draw.text((10, 10), gun_message, fill="red")

        logging.info("Completed drawing bounding boxes and messages on the image.")

        # Convert the image to binary data
        image_bytes = BytesIO()
        image_with_boxes.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        logging.info("Returning the image with detected objects as a streaming response.")
        # Return the predicted image as a streaming response
        return StreamingResponse(io.BytesIO(image_bytes.read()), media_type="image/png")

    except Exception as ex:
        logging.error("Error during object detection and returning image.", exc_info=True)
        return JSONResponse(content={"error": f"Error during object detection: {ex}"})


