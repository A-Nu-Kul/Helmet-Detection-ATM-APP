"""
image, video, camera --> frame --> object detection send
show the detection result on the frame and in the streamlit app
"""
 
import os
import sys
import importlib.util
from pathlib import Path
from tempfile import NamedTemporaryFile

import cv2
import numpy as np
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent


def load_local_module(module_name, relative_path):
    module_path = (BASE_DIR / relative_path).resolve()
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module '{module_name}' from '{module_path}'")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


detection_module = load_local_module("detection_service", "src/detection_service.py")
audio_module = load_local_module("audio_service", "src/audio_service.py")
utils_module = load_local_module("utils", "src/utils.py")

DetectionService = detection_module.DetectionService
AudioService = audio_module.AudioService
get_video_stream = utils_module.get_video_stream


detection_service = DetectionService()
audio_service = AudioService()
 
st.title("Secure ATM - Helmet Detection App")
st.write("This app detects whether a person is wearing a helmet or not while entering the ATM premises. If a person is detected with a helmet, an alert sound will be played.")
 
st.sidebar.title("Input settings")
 
input_type = st.sidebar.radio("Select input type", ("Image", "Video", "Camera"))
 
 
def process_image(image):
    frame, detections_classes = detection_service.detect(image)
   # Display status
    if "nohelmet" in detections_classes:
        st.success(" NO HELMET DETECTED")

    elif "helmet" in detections_classes:
        st.error(" HELMET DETECTED")

        # Beep ONLY for helmet
        audio_service.play_beep()

    else:
        st.success("No helmet/head detected")

    return frame
 
def process_video(video_file_path):
    cap = cv2.VideoCapture(video_file_path)
 
    stframe = st.empty()
    status_placeholder = st.empty()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
  # YOLO Detection
        frame, detections_classes = detection_service.detect(frame)
  # Display 
        with status_placeholder.container():
            if "nohelmet" in detections_classes:
                st.success("No Helmet Detected")

            elif "helmet" in detections_classes:
                st.error("Helmet Detected")
            # Sound only for Helmet
                audio_service.play_beep()

            else:
                st.success("No Helmet! Head or Cap detected")    
            
        #Display video frame
        stframe.image(frame, channels="BGR", width="stretch")
    cap.release()
 
 
def process_camera(camera_source):
    cap = get_video_stream(camera_source)
 
    stframe = st.empty()
    status_placeholder = st.empty()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Unable to read from the camera.")
            break
 
        frame, detections_classes = detection_service.detect(frame)
        with status_placeholder.container():
            # If there is no helmet
            if "nohelmet" in detections_classes:
                st.success("No Helmet Detected")      
            # If there is a helmet
            elif "helmet" in detections_classes:  
                st.error("Helmet Detected")   
                audio_service.play_beep() #Only beeps for Helmet
            #If nothing is detected
            else:
                st.success("No helmet/Head detected")      
        stframe.image(frame, channels="BGR", width="stretch")
    cap.release()
 
 
# streamlit app logic
if input_type == "Image":
    uploaded_file = st.sidebar.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        np_array = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
 
        processed_image = process_image(image)
        st.image(processed_image, channels="BGR", width="stretch")
 
 
if input_type == "Video":
    uploaded_file = st.sidebar.file_uploader("Upload a video...", type=["mp4", "avi", "mov"])
    if uploaded_file is not None:
        with NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_file_path = tmp_file.name
        process_video(video_file_path)
        os.remove(video_file_path)
 
 
if input_type == "Camera":
    camera_source = st.sidebar.number_input("Camera source (default is 0)", min_value=0, value=0, step=1)
    process_camera(camera_source)
