import subprocess
import sys
import socket
import threading

# Function to check and install required packages
def check_and_install(package_name):
    try:
        __import__(package_name)
    except ImportError:
        print(f"Package '{package_name}' is not installed.")
        try:
            print(f"Attempting to install '{package_name}' via pip...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"Successfully installed '{package_name}'.")
        except subprocess.CalledProcessError:
            print(f"Could not install '{package_name}'. Please check your internet connection or install it manually.")

check_and_install("opencv-python")  # for cv2
check_and_install("numpy")          # for numpy
check_and_install("Pillow")         # for ImageGrab

import numpy as np
import cv2
from PIL import ImageGrab

# Constants
MAX_PACKET_SIZE = 1024

class ScreenStreamer:
    def __init__(self, host, port=8080):
        #self.server_address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server_address = ('<broadcast>', port)

        self.running = True

    def start_streaming(self):
        print(f"Streaming to {self.server_address}")
        
        while self.running:
            # Capture the screen
            img = ImageGrab.grab()
            img_np = np.array(img)

            # Convert RGB to BGR
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            # Resize the image
            img_np = cv2.resize(img_np, (1280, 720))

            # Encode the image with JPEG quality
            _, img_encoded = cv2.imencode('.jpg', img_np, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            
            # Get the byte data of the image
            img_data = img_encoded.tobytes()

            # Split data into smaller packets
            total_packets = len(img_data) // MAX_PACKET_SIZE + 1
            for i in range(total_packets):
                start = i * MAX_PACKET_SIZE
                end = start + MAX_PACKET_SIZE
                packet = img_data[start:end]

                try:
                    # Send the current packet with a small sequence header (4 bytes)
                    header = f"{i}/{total_packets}".encode().ljust(8)  # 8-byte header
                    self.socket.sendto(header + packet, self.server_address)
                except OSError as e:
                    print(f"Error sending data: {e}")
            
            # Introduce a delay to control frame rate (30 FPS = 0.033 sec delay)
            threading.Event().wait(0.033)

    def stop_streaming(self):
        self.running = False
        self.socket.close()

def get_local_ip():
    # Get the local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

if __name__ == "__main__":
    local_ip = get_local_ip() 
    print(f"Local IP Address: {local_ip}")
    # Bind to all interfaces
    streamer = ScreenStreamer(host="0.0.0.0", port=8080)
    try:
        streamer.start_streaming()
    except KeyboardInterrupt:
        streamer.stop_streaming()
        print("Stopped streaming.")

