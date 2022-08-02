import time
from mqtt import MQTTClient
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


while station.isconnected() == False:
  pass

station.config(dhcp_hostname=cfg.controller_name)
print(station.config('dhcp_hostname'))
led.value(station.isconnected())
print('Connection successful')
print(station.ifconfig())

#import webrepl
#webrepl.start()
