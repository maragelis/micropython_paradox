import time
from umqtt.simple import MQTTClient
import ubinascii
import machine
import micropython
import network
import json
import threading
from machine import UART ,WDT
import ntptime
import esp
import config
esp.osdebug(None)
import gc
import sys
gc.collect()

cfg = config.configuration()
ssid = cfg.wifissid
password = cfg.wifipassword

#EXAMPLE IP ADDRESS
#mqtt_server = '192.168.1.144'
led = machine.Pin(2, machine.Pin.OUT)
repl_button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)


            
station = network.WLAN(network.STA_IF)
#station.config(dhcp_hostname="Paradox32CTL")


station.active(True)
led.value(station.isconnected())
station.connect(ssid, password)

ti = time.time()
while (time.time()-ti < 10) and (station.isconnected() == False):
  pass

if station.isconnected() == False:
    print('Starting AP mode')
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="paradox32CTL", password="configparadox",authmode=network.AUTH_WPA_WPA2_PSK)
    print('AP Connection successful')
    print(ap.ifconfig())
else:
    station.config(dhcp_hostname=cfg.controller_name)
    print(station.config('dhcp_hostname'))
    led.value(station.isconnected())
    print('Connection successful')
    print(station.ifconfig())

    import webrepl
#webrepl.start()
