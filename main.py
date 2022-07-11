import websrv
import paradox
import paradoxEvents
import mqtt_params
import json
import threading


VERSION="0.01_init"

SEND_ALL_EVENTS = True
  
print(paradox.program_init(VERSION))

  
try:
  client = mqtt_params.connect_and_subscribe()
  client.publish(cfg.root_topicStatus, paradox.program_init(VERSION))
except OSError as e:
  mqtt_params.restart_and_reconnect()



def serialloop():
    while True:
      try:
        if (paradox.serialRead()):
            jsonstr = paradox.processMessage()
            if (jsonstr is not None):
                jsondata = json.loads(jsonstr)
                client.publish(jsondata["topic"], jsonstr)
            if SEND_ALL_EVENTS:
                allevent = paradox.get_event_data()
                client.publish(mqtt_topics.root_topicOut, allevent)
        client.check_msg()
      except OSError as e:
        mqtt_params.restart_and_reconnect()

t1= threading.Thread(target=serialloop)

if __name__ == '__main__':
    try:
        t1.start()
        #startloop()
        print("Starting Webserver")
        websrv.runsrv()
    except:
        mqtt_params.restart_and_reconnect()
    