import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from io import BytesIO
from PIL import Image, ImageDraw
from ultralytics import YOLO
import io
import logging
from PIL import ImageFont

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
    logging.info("Serving index_api.html")
    return FileResponse("index_api.html")


@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    logging.info("Received a file for object detection.")
    contents = await file.read()
    image = Image.open(BytesIO(contents))

    confidence = 0.4  # Set your confidence level here

    try:
        detected_boxes = []  # Initialize the list of bounding boxes
        num_guns_detected = 0
        num_fake_guns_detected = 0

        # Predict objects in the image
        results = model.predict(image, conf=confidence)
        logging.info("Object detection performed.")

        # Iterate through each prediction result
        for result in results:
            # Check if the result has bounding boxes
            if result.boxes is not None:
                # Iterate through each bounding box in the prediction result
                for box in result.boxes:
                    # Convert xyxy tensor to list and format coordinates
                    xyxy_list = box.xyxy.tolist()

                    # Add bounding box info to the list with confidence
                    detected_boxes.append({
                        "class": int(box.cls),       # Class of the object
                        "confidence": float(box.conf), # Confidence
                        "xyxy": xyxy_list
                    })

                    # Increment the corresponding count based on the detected class
                    if box.cls == 0:
                        num_guns_detected += 1
                    elif box.cls == 1:
                        num_fake_guns_detected += 1

        logging.info(f"Detected {len(detected_boxes)} objects.")

        # Return the list of bounding boxes as JSON
        detection_message = f"{num_guns_detected} Gun{'s' if num_guns_detected != 1 else ''} detected and {num_fake_guns_detected} Fake Gun{'s' if num_fake_guns_detected != 1 else ''} detected."
        return JSONResponse(content={"detected_objects": detected_boxes, "detection_message": detection_message})
    except Exception as ex:
        logging.error("Error during object detection.", exc_info=True)
        return JSONResponse(content={"error": f"Error during object detection: {ex}"})


@app.post("/detect_and_return_image")
async def detect_objects_and_return_image(file: UploadFile = File(...)):
    logging.info("Received a file for object detection and returning image with boxes.")
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    confidence = 0.4

    class_names = {0: "Gun", 1: "Fake Gun"}

    try:
        detected_boxes = []
        num_guns_detected = 0
        num_fake_guns_detected = 0

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

                    # Increment the corresponding count based on the detected class
                    if cls == 0:
                        num_guns_detected += 1
                    elif cls == 1:
                        num_fake_guns_detected += 1

        logging.info(f"Detected {len(detected_boxes)} objects with image return.")

        # Create a new image with larger size
        new_image = Image.new('RGB', (image.width, image.height + 50), color = (255, 255, 255))
        new_image.paste(image, (0, 0))

        # Draw bounding boxes on the image
        draw = ImageDraw.Draw(new_image)
        for box in detected_boxes:
            draw.rectangle(box["xyxy"], outline="red", width=3)
            # Display class name and confidence next to each bounding box
            draw.text((box["xyxy"][0], box["xyxy"][1] - 10), f"{box['class_name']} Conf: {box['confidence']:.2f}", fill="red")

        # Generate the detection message
        detection_message = f"{num_guns_detected} Gun{'s' if num_guns_detected != 1 else ''} detected and {num_fake_guns_detected} Fake Gun{'s' if num_fake_guns_detected != 1 else ''} detected."
        
        text_size = 12

        # Draw detection message below the image
        draw.text((10, image.height + 10), detection_message, fill="red", font=ImageFont.truetype("arial.ttf", text_size))

        logging.info("Completed drawing bounding boxes and messages on the image.")

        logging.info(f"Detected {num_guns_detected} Gun{'s' if num_guns_detected != 1 else ''} and {num_fake_guns_detected} Fake Gun{'s' if num_fake_guns_detected != 1 else ''}.")
        
        # Convert the new image to binary data
        image_bytes = BytesIO()
        new_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        logging.info("Returning the image with detected objects as a streaming response.")
        # Return the predicted image as a streaming response
        return StreamingResponse(io.BytesIO(image_bytes.read()), media_type="image/png")

    except Exception as ex:
        logging.error("Error during object detection and returning image.", exc_info=True)
        return JSONResponse(content={"error": f"Error during object detection: {ex}"})
