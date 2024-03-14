from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import io
from PIL import Image, ImageDraw
from ultralytics import YOLO
import os
from io import BytesIO
import logging
from dotenv import load_dotenv

app = FastAPI()

# Load YOLO model
# Load environment variables from .env file
load_dotenv()

# Get the model path
model_path = os.getenv('MODEL_PATH')
model = YOLO(model_path)
try:
    model = YOLO(model_path)
except Exception as ex:
    raise RuntimeError(f"Unable to load model. Check the specified path: {model_path}") from ex

confidence = 0.4 
class_boxs = {'0':'Vilolence','1':'Not_Violence'}

@app.get("/")
async def get_index():
    return FileResponse("index.html")

# Configuring logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s-%(levelname)s-%(message)s', level=logging.INFO)
logger = logging.getLogger('uvicorn.error')

@app.post("/detect")
async def detect_objects(file: UploadFile = File(...), confidence: float = 0.4):
    contents = await file.read()
    image = Image.open(BytesIO(contents))
    try:
        logging.info('Straring object detection...')
        detected_boxes = []  
        # Predicting objects
        logger.info('Predicting objects...')
        results = model.predict(image, conf=confidence)

        # Iterating through each prediction result
        for result in results:
            # Checking if the result has bounding boxes
            if result.boxes is not None:
                # Iterating through each bounding box in the prediction result
                for box in result.boxes:
                    # Converting tensor xyxy to list to avoid serialization error
                    xyxy_list = box.xyxy.tolist()

                    # Adding bounding box information to the list
                    if box.cls == '0':
                        box_cls = class_boxs['0']
                    else:
                        box_cls = class_boxs['1']
                    detected_boxes.append({
                        "class": box_cls,       
                        "confidence": float(box.conf), 
                        "xyxy": xyxy_list
                    })
        logger.info("Object detection completed.")
        # Returning the list of bounding boxes as JSON
        return JSONResponse(content={"detected_objects": detected_boxes})
    except Exception as ex:
        logger.error(f"Error during object detection: {ex}")
        return JSONResponse(content={"error": f"Error during object detection: {ex}"})

@app.post("/detect_and_return_image")
async def detect_objects_and_return_image(file: UploadFile = File(...), confidence: float = 0.4):
    logging.info("Received a file for object detection and returning image with boxes.")
    
    try:
        # Reading the image file from the request
        image = Image.open(io.BytesIO(await file.read()))

        detected_boxes = []  
        # Predicting objects in the image
        results = model.predict(image, conf=confidence)
        logging.info("Object detection performed for image return.")
        
        # Iterating through each prediction result
        for result in results:
            # Checking if the result has bounding boxes
            if result.boxes is not None:
                # Iterating through each bounding box in the prediction result
                for box in result.boxes:
                    xyxy_list = box.xyxy.tolist()
                    box_cls = class_boxs.get(str(box.cls), "Unknown")
                    detected_boxes.append({
                        "class": box_cls,       
                        "confidence": float(box.conf), 
                        "xyxy": xyxy_list
                    })
        logging.info(f"Detected {len(detected_boxes)} objects with image return.")

        # Drawing bounding boxes on the image
        image_with_boxes = image.copy()
        draw = ImageDraw.Draw(image_with_boxes)
        for box in detected_boxes:
            draw.rectangle(box["xyxy"], outline="red", width=3)
            draw.text((box["xyxy"][0], box["xyxy"][1] - 10),f"{box['class']} Conf: {box['confidence']:.2f}", fill="red")
        logging.info("Completed drawing bounding boxes.")
        
        # Converting the image to binary data
        image_bytes = io.BytesIO()
        image_with_boxes.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        logging.info("Returning the image with detected objects as a streaming response.")
        
        # Returning the predicted image as a streaming response
        return StreamingResponse(image_bytes, media_type="image/png")

    except Exception as ex:
        logging.error("Error during object detection and returning image.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during object detection: {ex}")
