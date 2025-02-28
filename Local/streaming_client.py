
import cv2
import numpy as np
import requests
import struct

def main():
    # Set the URL for the ESP32 Camera stream
    url = 'http://172.20.10.3/xiao/Hi-Xiao-Ling'  # Replace with your actual server URL

    # Initialize a session to handle the request
    with requests.Session() as session:
        # Send a GET request to the server
        response = session.get(url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            print("Connected to the camera stream.")

            # Read the response in chunks
            boundary = b'--kaki5'  # The boundary that separates the frames
            image_data = b''
            running = True 

            while running:
                for chunk in response.iter_content(chunk_size=1024):
                    image_data += chunk
                    # Check if we have enough data to find a full image
                    if boundary in image_data:
                        # Split the data into frames
                        frames = image_data.split(boundary)
                        for frame in frames[:-1]:  # Ignore the last chunk (incomplete frame)
                            if b'Content-Type: image/bmp' in frame:
                                # Extract the BMP image data
                                header_index = frame.index(b'\r\n\r\n') + 4  # Skip the header
                                bmp_data = frame[header_index:-4]  # Get the BMP data
                                classification_bytes = frame[-4:]  # Last 4 bytes for classification

                                # Decode classification
                                predicted_label = struct.unpack('i', classification_bytes)[0]
                                classes = ["Paper", "Rock", "Scissors"]
                                
                                if predicted_label in range(len(classes)):
                                    print(f"Prediction: {classes[predicted_label]}")
                                else:
                                    print("Invalid prediction received")

                                running = display_image(bmp_data)

                        # Keep only the last (incomplete) frame in the buffer
                        image_data = frames[-1]  # This might contain partial image data
                        
                    if not running:
                        break 
        else:
            print("Failed to connect to the camera stream.")

def display_image(bmp_data):
    # Convert the BMP data to a NumPy array
    nparr = np.frombuffer(bmp_data, np.uint8)

    # Read the image from the NumPy array
    image = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

    if image is not None:
        cv2.imshow('ESP32 Camera Stream', image)  # Display the image
        key = cv2.waitKey(1) 
        if key & 0xFF == ord('q'): 
            cv2.destroyAllWindows()
            return False  
    return True 

if __name__ == '__main__':
    main()
