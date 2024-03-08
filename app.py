from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from io import BytesIO
from PIL import Image, ImageDraw
from ultralytics import YOLO
import io

app = FastAPI()

# Load YOLO model
model_path = r'C:\Users\ASUS\Desktop\gun\best.pt'
try:
    model = YOLO(model_path)
except Exception as ex:
    raise RuntimeError(f"Unable to load model. Check the specified path: {model_path}") from ex


@app.get("/")
async def get_index():
    return FileResponse("index.html")


@app.post("/detect")
async def detect_objects(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents))

    confidence = 0.4  # Set your confidence level here

    try:
        detected_boxes = []  # Initialize the list of bounding boxes

        # Predict objects in the image
        results = model.predict(image, conf=confidence)

        # Iterate through each prediction result
        for result in results:
            # Check if the result has bounding boxes
            if result.boxes is not None:
                # Iterate through each bounding box of the prediction result
                for box in result.boxes:
                    # Convert xyxy tensor to list to avoid serialization errors
                    xyxy_list = box.xyxy.tolist()

                    # Add bounding box information to the list
                    detected_boxes.append({
                        "class": int(box.cls),       # Class of the object
                        "confidence": float(box.conf), # Confidence
                        "xyxy": xyxy_list
                    })

        # Return the list of bounding boxes as JSON
        return JSONResponse(content={"detected_objects": detected_boxes})
    except Exception as ex:
        return JSONResponse(content={"error": f"Error during object detection: {ex}"})


@app.post("/detect_and_return_image")
async def detect_objects_and_return_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents))

    confidence = 0.4  # Đặt mức độ tin cậy của bạn ở đây

    try:
        detected_boxes = []  # Khởi tạo danh sách hộp giới hạn

        # Dự đoán các đối tượng trong hình ảnh
        results = model.predict(image, conf=confidence)

        # Lặp qua từng kết quả dự đoán
        for result in results:
            # Kiểm tra xem kết quả có hộp giới hạn không
            if result.boxes is not None:
                # Lặp qua từng hộp giới hạn của kết quả dự đoán
                for box in result.boxes:
                    # Chuyển đổi tensor xyxy thành danh sách và sửa định dạng tọa độ
                    xyxy_list = [float(coord) for coord in box.xyxy.flatten()]

                    # Thêm thông tin của hộp giới hạn vào danh sách với độ tin cậy
                    detected_boxes.append({
                        "class": int(box.cls),       # Lớp của đối tượng
                        "confidence": float(box.conf), # Độ tin cậy
                        "xyxy": xyxy_list
                    })

        # Vẽ hộp giới hạn lên ảnh
        image_with_boxes = image.copy()
        for box in detected_boxes:
            ImageDraw.Draw(image_with_boxes).rectangle(box["xyxy"], outline="red", width=3)
            ImageDraw.Draw(image_with_boxes).text((box["xyxy"][0], box["xyxy"][1]), f"Conf: {box['confidence']:.2f}", fill="red")

        # Chuyển đổi ảnh thành dữ liệu nhị phân
        image_bytes = BytesIO()
        image_with_boxes.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        # Trả về ảnh đã được dự đoán dưới dạng streaming response
        return StreamingResponse(io.BytesIO(image_bytes.read()), media_type="image/png")

    except Exception as ex:
        return JSONResponse(content={"error": f"Lỗi trong quá trình phát hiện đối tượng: {ex}"})
