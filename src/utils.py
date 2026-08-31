import cv2

def get_video_stream(camera_source):
    """
    Get video stream from the specified camera source.
    :param camera_source: Camera source index (default is 0 for the first camera)
    :return: VideoCapture object
    """
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        raise ValueError(f"Unable to open camera source {camera_source}")
    return cap
