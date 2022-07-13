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
led = machine.Pin(2, machine.Pin.OUT)


station = network.WLAN(network.STA_IF)
#station.config(dhcp_hostname="Paradox32CTL")


station.active(True)
led.value(station.isconnected())
station.connect(ssid, password)


while station.isconnected() == False:
  pass

station.config(dhcp_hostname=cfg.controller_name)
print(station.config('dhcp_hostname'))
led.value(station.isconnected())
print('Connection successful')
print(station.ifconfig())