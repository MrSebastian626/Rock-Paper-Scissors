from time import sleep
import network

class Sta:
   AP = "Sebastian\u2019s_iPhone"  # Please put in wifi name
   PWD = "Password" #Please input password

   def __init__(my, ap='', pwd=''):
      network.WLAN(network.AP_IF).active(False)  # Disable AP mode
      my.wlan = network.WLAN(network.STA_IF)
      my.wlan.active(True)

      my.ap = ap or Sta.AP
      my.pwd = pwd or Sta.PWD

   def connect(my, ap='', pwd=''):
      if ap:
          my.ap = ap
          my.pwd = pwd

      print(f"Trying to connect to: {my.ap} with password: {my.pwd}")

      # Scan for networks if having trouble
      #print("Scanning for WiFi networks...")
      #available_networks = [net[0].decode() for net in my.wlan.scan()]
      #print("Available networks:", available_networks)

      if my.ap not in available_networks:
          print(f"ERROR: '{my.ap}' not found. Check if the hotspot is ON.")
          return

      if not my.wlan.isconnected():
          print(f"Connecting to {my.ap}...")
          my.wlan.connect(my.ap, my.pwd)

          for _ in range(10):  # Try for 10 seconds
              if my.wlan.isconnected():
                  print("Connected successfully!")
                  print("IP Address:", my.wlan.ifconfig()[0])
                  return
              else:
                  print("Retrying...")
                  sleep(1)
          print("Failed to connect.")

   def status(my):
      if my.wlan.isconnected():
          return my.wlan.ifconfig()
      else:
          return ()

   def wait(my):
      cnt = 30
      while cnt > 0:
         print("Waiting..." )
         if my.wlan.isconnected():
           print(f"Connected to {my.ap}")
           print('Network config:', my.wlan.ifconfig())
           return
         else:
           sleep(5)
           cnt -= 5
      print("Failed to connect after waiting.")

   def scan(my):
      return my.wlan.scan()  # Scan for available networks

# Run the connection
sta = Sta()
sta.connect()
