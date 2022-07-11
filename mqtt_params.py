import time
from mqtt import MQTTClient
import ubinascii
import machine
import json
import paradox
import config

cfg = config.configuration()

client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = cfg.root_topicIn
mqtt_server = cfg.mqttserver
print(f"mqtt_server:{cfg.mqttserver}, username:{cfg.mqttusername}, password:{cfg.mqttpassword}, topic:{cfg.root_topicIn}")

def sub_cb(topic, msg):
    print((topic, msg))
    if topic == bytes(cfg.root_topicIn,"utf-8") :
        strmsg = msg.decode("utf-8")
        json_data = json.loads(strmsg)
        inmessage =paradox.inMessage()
        if "panel_password" in json_data:
            inmessage.panel_password=json_data["panel_password"]
        if "command" in json_data:
            inmessage.command = json_data["command"]
        if "subcommand" in json_data:
            inmessage.subcommand = json_data["subcommand"]
        else:
            inmessage.subcommand = "0"
            
        print(paradox.panel_control(inmessage))
            
        print(f"ESP received message : {inmessage}")

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, user=cfg.mqttusername , password=cfg.mqttpassword)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()
  