import subprocess
import sys
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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

# Check and install required packages
check_and_install("opencv-python")  # for cv2
check_and_install("numpy")          # for numpy
check_and_install("mss")            # for mss
import cv2
import numpy as np
import mss
import time

class ScreenHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/screen':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

            with mss.mss() as sct:
                # Get screen dimensions
                monitor = sct.monitors[1]  # Monitor 1 (Primary)

                while True:
                    # Capture screen
                    screen = sct.grab(monitor)
                    img_np = np.array(screen)

                    # Convert BGRA to BGR (remove alpha channel)
                    img_np = img_np[:, :, :3]

                    # Encode the image in another thread
                    _, img_encoded = cv2.imencode('.jpg', img_np, [int(cv2.IMWRITE_JPEG_QUALITY), 90])

                    # Write the JPEG image to the response
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(b'Content-Length: %d\r\n' % len(img_encoded))
                    self.wfile.write(b'\r\n')
                    self.wfile.write(img_encoded.tobytes())
                    self.wfile.write(b'\r\n')

                    # Introduce delay to maintain ~30 FPS
                    time.sleep(1 / 30)
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=ScreenHandler):
    server_address = ('', 8080)  # Listen on all interfaces on port 8080
    httpd = server_class(server_address, handler_class)
    print(f"Server started at http://{get_local_ip()}:8080/screen")
    httpd.serve_forever()

def get_local_ip():
    # Get the local IP address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('8.8.8.8', 80))  # Connect to an external address to get local IP
    ip = s.getsockname()[0]
    s.close()
    return ip

if __name__ == "__main__":
    # Run the server in a separate thread
    server_thread = threading.Thread(target=run)
    server_thread.start()

