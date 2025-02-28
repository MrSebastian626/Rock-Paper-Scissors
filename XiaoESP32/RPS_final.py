from camera import FrameSize, PixelFormat, Camera
import emlearn_cnn_fp32 as emlearn_cnn
from image_preprocessing import strip_bmp_header, resize_96x96_to_32x32
import array
import esp
import gc
import socket
from Wifi import Sta
import socket as soc
import struct


hdr = {
  # live stream -
  # URL: /live
  'stream': """HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace; boundary=kaki5
Connection: keep-alive
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Expires: Thu, Jan 01 1970 00:00:00 GMT
Pragma: no-cache""",
  # live stream -
  # URL:
  'frame': """--kaki5
Content-Type: image/bmp"""}

UID = const('xiao')          # authentication user
PWD = const('Hi-Xiao-Ling')  # authentication password

MODEL = 'model.tmdl'

CAMERA_PARAMETERS = {
    "data_pins": [15,17,18,16,14,12,11,48],
    "vsync_pin": 38,
    "href_pin": 47,
    "sda_pin": 40,
    "scl_pin": 39,
    "pclk_pin": 13,
    "xclk_pin": 10,
    "xclk_freq": 20000000,
    "powerdown_pin": -1,
    "reset_pin": -1,
    "frame_size": FrameSize.R96X96,
    "pixel_format": PixelFormat.GRAYSCALE
}

cam = Camera(**CAMERA_PARAMETERS)
cam.init()
cam.set_bmp_out(True)

print("camera initialized")

# load model
model = None
with open(MODEL, 'rb') as f:
    model_data = array.array('B', f.read())
    gc.collect()
    model = emlearn_cnn.new(model_data)
    
out_length = model.output_dimensions()[0]
probabilities = array.array('f', (-1 for _ in range(out_length)))


sta = Sta()              # Station mode (i.e. need WiFi router)
sta.wlan.disconnect()    # disconnect from previous connection
AP = "Sebastian\u2019s_iPhone"  # change to your SSID
PW = "Password"  # change to your password
sta.connect(AP, PW) # connect to dlink
sta.wait()

con = ()
for i in range(5):
    if sta.wlan.isconnected():con=sta.status();break
    else: print("WIFI not ready. Wait...");sleep(2)
else:
    print("WIFI not ready")
if con and cam: # WiFi and camera are ready
   if cam:
     # set preffered camera setting
     cam.set_frame_size(0)     # frame size 96x96
     cam.set_contrast(2)       # increase contrast
     cam.set_special_effect(2)
     print("hi")
   if con:
     # TCP server
     port = 80
     addr = soc.getaddrinfo('0.0.0.0', port)[0][-1]
     s = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
     s.setsockopt(soc.SOL_SOCKET, soc.SO_REUSEADDR, 1)
     s.bind(addr)
     s.listen(1)
     # s.settimeout(5.0)
     while True:
        cs, ca = s.accept()   # wait for client connect
        print('Request from:', ca)
        w = cs.recv(200) # blocking
        (_, uid, pwd) = w.decode().split('\r\n')[0].split()[1].split('/')
        # print(_, uid, pwd)
        if not (uid==UID and pwd==PWD):
           print('Not authenticated')
           cs.close()
           continue
        # We are authenticated, so continue serving
        cs.write(b'%s\r\n\r\n' % hdr['stream'])
        pic=cam.capture()
        put=cs.write
        hr=hdr['frame']
        while True:
           # once connected and authenticated just send the bmp data
           # client use HTTP protocol (not RTSP)
           try:
            img = cam.capture()
            #Resize the image so that we can feed it into the model
            img_resize = resize_96x96_to_32x32(img)
            img_strip = strip_bmp_header(array.array('B', img_resize))
            try:
                model.run(img_strip, probabilities)
            except Exception as e:
                print("Error during model execution:", e)
            predicted_class = -1
            max_prob = -1
            for i in range(len(probabilities)):
                if probabilities[i] > max_prob:
                    max_prob = probabilities[i]
                    predicted_class = i
            put(b'%s\r\n\r\n' % hr)
            put(img)
            put(b'\r\n')  # send and flush the send buffer
            
            put(struct.pack('i', predicted_class)) #Send the prediction made on the image
           except Exception as e:
              print('TCP send error', e)
              cs.close()
              break
else:
   if not con:
      print("WiFi not connected.")
   if not cam:
      print("Camera not ready.")
   print("System not ready. Please restart")
   
cam.deinit()
