import socket
import cv2
import numpy as np
import time

MAX_PACKET_SIZE = 1024  # Keep this in sync with the sender
UDP_IP = ""  # Your server's IP address
UDP_PORT = 8080
TIMEOUT = 5  # Seconds to wait for packets before resetting buffer

class StreamReceiver:
    def __init__(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))
        self.socket.settimeout(1.0)  # Set socket timeout to 1 second
        self.buffer = {}
        self.total_packets = None
        self.last_packet_time = time.time()
        self.current_frame = 0

    def reset_buffer(self):
        self.buffer.clear()
        self.total_packets = None
        self.current_frame = 0

    def receive_stream(self):
        print("Client started. Waiting for data...")
        while True:
            try:
                # Check if buffer needs to be reset due to timeout
                if time.time() - self.last_packet_time > TIMEOUT:
                    print("Buffer timeout - resetting")
                    self.reset_buffer()

                # Receive packet from socket
                try:
                    data, addr = self.socket.recvfrom(MAX_PACKET_SIZE + 20)
                    self.last_packet_time = time.time()
                except socket.timeout:
                    continue
                except socket.error as e:
                    print(f"Socket error: {e}")
                    continue

                # Validate packet size
                if len(data) < 8:
                    print("Received invalid packet (too small)")
                    continue

                try:
                    # Extract header information
                    packet_info = data[:8].decode('utf-8').strip()
                    packet_num, total_packets = map(int, packet_info.split('/'))

                    # Validate packet numbers
                    if packet_num < 0 or total_packets <= 0 or packet_num >= total_packets:
                        print(f"Invalid packet numbers: {packet_num}/{total_packets}")
                        continue

                    # Store packet data
                    packet_data = data[8:]
                    self.buffer[packet_num] = packet_data

                    # Check if we have all packets
                    if len(self.buffer) == total_packets:
                        # Verify we have all packet numbers
                        if all(i in self.buffer for i in range(total_packets)):
                            # Reassemble the image
                            img_data = b''.join([self.buffer[i] for i in range(total_packets)])
                            
                            try:
                                # Convert to numpy array and decode
                                img_np = np.frombuffer(img_data, dtype=np.uint8)
                                img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

                                if img is not None:
                                    # Display the image
                                    cv2.imshow("UDP Stream", img)
                                    if cv2.waitKey(1) & 0xFF == ord('q'):
                                        print("User requested exit")
                                        break
                                else:
                                    print("Failed to decode image")
                            except Exception as e:
                                print(f"Error processing image: {e}")

                            # Clear buffer for next frame
                            self.reset_buffer()
                        else:
                            print("Missing packets in sequence")
                            self.reset_buffer()

                except ValueError as e:
                    print(f"Error parsing packet header: {e}")
                    continue
                except Exception as e:
                    print(f"Unexpected error processing packet: {e}")
                    continue

            except Exception as e:
                print(f"Main loop error: {e}")
                continue

        # Cleanup
        print("Closing client...")
        self.socket.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        receiver = StreamReceiver(UDP_IP, UDP_PORT)
        receiver.receive_stream()
    except KeyboardInterrupt:
        print("\nExiting due to user interrupt")
    except Exception as e:
        print(f"Fatal error: {e}")
