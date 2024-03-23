import os
import time
from spot_controller import SpotController
import cv2
import apriltag
import uuid
import mimetypes
import requests

ROBOT_IP = "10.0.0.3"
SPOT_USERNAME = "admin"
SPOT_PASSWORD = "2zqa8dgw7lor"

def capture_image():
    camera_capture = cv2.VideoCapture(0)
    rv, image = camera_capture.read()
    camera_capture.release()
    if rv:
        print(f"Image Dimensions: {image.shape}")
        filename = f"{uuid.uuid4().hex}.jpg"  # Generate a random file name
        cv2.imwrite(filename, image)
        return filename, image
    else:
        print("Failed to capture image")
        return None, None

def upload_image_to_api(image_file, auth_token):
    url = 'https://mb-spot.storage.api2.merklebot.com/contents/'
    mime_type, _ = mimetypes.guess_type(image_file)

    headers = {
        'accept': 'application/json',
        'Authorization': auth_token
    }
    files = {
        'file_in': (image_file, open(image_file, 'rb'), mime_type)
    }

    response = requests.post(url, headers=headers, files=files)
    return response

def detect_apriltag(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Initialize the AprilTag detector
    detector = apriltag.Detector()
    
    # Detect AprilTags in the grayscale image
    detections = detector.detect(gray)
    
    # Check if any AprilTag is detected
    return len(detections) > 0

def main():
    auth_token = os.getenv('AUTH_TOKEN')
    
    with SpotController(username=SPOT_USERNAME, password=SPOT_PASSWORD, robot_ip=ROBOT_IP) as spot:
        time.sleep(2)
        for _ in range(3):  # Example loop, adjust as necessary
            image_file, image = capture_image()
            
            upload_image_to_api(image_file, auth_token)
            
            if detect_apriltag(image):
                print("AprilTag detected! Playing sound...")
                os.system(f"ffplay -nodisp -autoexit -loglevel quiet 'the-price-is-right-theme-song-lq.mp3'")
                break

            # Example movements (adjust as needed)
            spot.move_head_in_points(yaws=[0.2, 0], pitches=[0.3, 0], rolls=[0.4, 0], sleep_after_point_reached=1)
            spot.move_to_goal(goal_x=0.5, goal_y=0)
            spot.move_by_velocity_control(v_x=-0.3, v_y=0, v_rot=0, cmd_duration=2)
            time.sleep(3)

        print("Finished checking for AprilTag.")

if __name__ == '__main__':
    main()
