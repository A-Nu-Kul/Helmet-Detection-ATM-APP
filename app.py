"""
image, video, camera ---> frame ---> object detection send
show the detection result on the frame and in the streamlit app
"""
import cv2
import numpy as np
import streamlit as st
from src.detection_service import DetectionService
from src.audio_service import AudioService
from src.utils import get_video_stream


detection_service = DetectionService()
audio_service = AudioService()

st.title("Secure ATM- Helmet Detection ")
st.write("This apps detects whether a person is wearing a helmet or not using YOLOv8 model. ")

st.sidebar.title("Input settings")

input_type = st.sidebar.radio("Select input type", ("Image", "Video", "Camera"))

def process_image(image):
    frame, detections_classes = detection_service.detect(image)
    if "helmet" in detections_classes:
        audio_service.play_beep()
    return frame, detections_classes

def process_video(video_file_path):
    cap = cv2.VideoCapture(video_file_path)

    stframe = st.empty()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame, detections_classes = detection_service.detect(frame)
        if "helmet" in detections_classes:
            audio_service.play_beep()

        stframe.image(frame, channels="BGR", use_column_width=True)
    cap.release()

#streamlit app logic
if input_type == "image":
    uploaded_file = st.sidebar.file_uploader("Upload an image...", type=["jpg","jpeg", "png"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read() #b'string.....'
        np_array = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        process_image = process_image(image)
        st.image(process_image, channels="BGR", use_column_width=True)
