import os
import json

class configuration:
    wifissid=""
    wifipassword=""
    mqttserver=""
    mqttusername=""
    mqttpassword=""
    root_topicOut=""
    root_topicStatus=""
    root_topicIn=""
    root_topicHassioArm=""
    root_topicHassio=""
    root_topicArmHomekit=""
    
    def readconfig():
        
        if "config.json" in os.listdir():
            f = open("config.json")
            jsonstr = f.read()
            f.close()
            return json.loads(jsonstr)
    
    def __init__(self):
        if "config.json" in os.listdir():
            f = open("config.json")
            jsonstr = f.read()
            jsonf = json.loads(jsonstr)
            f.close()
            self.wifissid = jsonf["wifissid"]
            self.wifipassword = jsonf["wifipassword"]
            self.mqttserver=jsonf["mqttserver"]
            self.mqttusername=jsonf["mqttusername"]
            self.mqttpassword=jsonf["mqttpassword"]
            self.root_topicOut=jsonf["root_topicOut"]
            self.root_topicStatus=jsonf["root_topicStatus"]
            self.root_topicHassioArm=jsonf["root_topicHassioArm"]
            self.root_topicHassio=jsonf["root_topicHassio"]
            self.root_topicArmHomekit=jsonf["root_topicArmHomekit"]
            self.root_topicIn=jsonf["root_topicIn"]
    
    
    
        


        
