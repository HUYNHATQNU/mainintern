from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import io
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO
import os
from io import BytesIO
import logging
from dotenv import load_dotenv
import time
from minio import Minio
from database import *
import base64
from sqlalchemy.exc import SQLAlchemyError
app = FastAPI()

# Configuring logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s-%(levelname)s-%(message)s', level=logging.INFO)
logger = logging.getLogger('uvicorn.error')
message=f""

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

'''@app.post("/webhook")
async def handle_webhook(request: Request):
    # Đọc nội dung của webhook từ request
    webhook_data = await request.json()

    # Xử lý thông báo từ MinIO
    # Ở đây, bạn có thể thực hiện các thao tác như lưu thông tin về tệp hình ảnh vào cơ sở dữ liệu hoặc thực hiện xử lý khác
    # Ví dụ:
    image_name = webhook_data['Records'][0]['s3']['object']['key']
    bucket_name = webhook_data['Records'][0]['s3']['bucket']['name']
    # Tiếp tục xử lý thông báo dựa trên thông tin nhận được từ webhook

    # Trả về phản hồi
    return {"message": "Webhook received successfully"}'''

@app.post("/detect")
#async def detect_objects(file: UploadFile = File(...), confidence: float = 0.4):
async def detect_objects(file: UploadFile = File(...), confidence: float = 0.4):
    contents = await file.read()
    start_time=time.time()
    try:
         # save data MinIO
        save_to_minio(file.filename, contents)
        logging.info("Image uploaded to MinIO successfully.")
        logging.info('Straring object detection...')
        #send_notification(file.filename)
        detected_boxes = [] 
        image = Image.open(BytesIO(contents))
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
                    if box.cls == 0:
                        box_cls = class_boxs['0']
                    elif box.cls ==1:
                        box_cls = class_boxs['1']
                    detected_boxes.append({
                        "class": box_cls,       
                        "confidence": float(box.conf), 
                        "xyxy": xyxy_list,
                    })
                    # Check if any object is detected
        if detected_boxes:
            # Convert the image to base64 format
            image_base64 = base64.b64encode(contents).decode("utf-8")

            # Save pred to database
            with Session() as session:
                detected_image = DetectedImage(image_name=file.filename, image_data=image_base64)
                session.add(detected_image)
                session.commit()
                logging.info("Detected image saved to the database.")

        end_time=time.time()
        processing_time = end_time - start_time  # Calculate execution time
        logging.info(f"Processing time: {processing_time}")
        logger.info("Object detection completed.")
        # Returning the list of bounding boxes as JSON
        return JSONResponse(content={"detected_objects": detected_boxes, "message" : message})
    except SQLAlchemyError as ex:
        logging.error("Error saving detected image to the database.", exc_info=True)
        return JSONResponse(content={"error": f"Error saving detected image: {ex}"})

@app.post("/detect_and_return_image")
async def detect_objects_and_return_image(file: UploadFile = File(...), confidence: float = 0.4):
    contents = await file.read()
    start_time=time.time()
    violence=0
    try:
         # save data MinIO
        save_to_minio(file.filename, contents)
        logging.info("Image uploaded to MinIO successfully.")
        logging.info('Straring object detection...')
        detected_boxes = [] 
        image = Image.open(BytesIO(contents))
        # Predicting objects
        logger.info('Predicting objects...')
        results = model.predict(image, conf=confidence)
        # Iterating through each prediction result
        for result in results:
            # Checking if the result has bounding boxes
            if result.boxes is not None:
                # Iterating through each bounding box in the prediction result
                for box in result.boxes:
                    xyxy_list = box.xyxy.tolist()
                    if box.cls == 0:
                        box_cls = class_boxs['0']
                        violence +=1
                    elif box.cls == 1:
                        box_cls = class_boxs['1']
                    detected_boxes.append({
                        "class": int(box.cls),
                        "class_name": box_cls,  
                        "confidence": float(box.conf), 
                        "xyxy": xyxy_list
                    })
        logging.info(f"Detected {len(detected_boxes)} objects with image return.")
        if detected_boxes:
            image_base64 = base64.b64encode(contents).decode("utf-8")

            # Save to database
            with Session() as session:
                detected_image = DetectedImage(image_name=file.filename, image_data=image_base64)
                session.add(detected_image)
                session.commit()
                logging.info("Detected image saved to the database.")

            save_to_minio(file.filename, contents)
            logging.info("Image uploaded to MinIO successfully.")
        # Drawing bounding boxes on the image
        image_with_boxes = image.copy()
        draw = ImageDraw.Draw(image_with_boxes)
        for box in detected_boxes:
            xyxy_float = [float(coord) for coord in box["xyxy"][0]]
            if box['class'] == 0:
                draw.rectangle(xyxy_float, outline="red", width=3)
                draw.text((xyxy_float[0], xyxy_float[1] - 10), f"{box['class_name']}:{box['confidence']:.2f}", fill="red")
            elif box['class'] == 1:
                draw.rectangle(xyxy_float, outline="green", width=3)
                draw.text((xyxy_float[0], xyxy_float[1] - 10), f"{box['class_name']}:{box['confidence']:.2f}", fill="green")
        logging.info("Completed drawing bounding boxes.")
        if violence != 0:
            message='Warring: Violence'
            text_size = 20
            font = ImageFont.truetype("arial.ttf", text_size)
            draw.text((10, 10), f"{message}", fill="red",font=font)

        # Converting the image to binary data
        image_bytes = io.BytesIO()
        image_with_boxes.save(image_bytes, format="PNG")
        image_bytes.seek(0)
        end_time = time.time()  # Record the processing end time
        processing_time = end_time - start_time  # Calculate execution time

        logging.info("Returning the image with detected objects as a streaming response.")
        
        # Record execution time in the log file
        logging.info(f"Processing time: {processing_time}")
        # Returning the predicted image as a streaming response
        return StreamingResponse(image_bytes, media_type="image/png")

    except Exception as ex:
        logging.error("Error during object detection and returning image.", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error during object detection: {ex}")