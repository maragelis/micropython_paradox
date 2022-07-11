import mqtt_params
import time
from mqtt import MQTTClient
import ubinascii
import machine
import micropython
import network
import esp
import config
esp.osdebug(None)
import gc
gc.collect()

cfg = config.configuration()
ssid = cfg.wifissid
password = cfg.wifipassword

#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'



station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())