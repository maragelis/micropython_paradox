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
    ESP_UART=0
    controller_name="Paradox32CTL"
    timezone = 2
    homekit = False
    
    
    def readconfig():
        
        if "config.json" in os.listdir():
            f = open("config.json")
            jsonstr = f.read()
            f.close()
            return json.loads(jsonstr)
        
    def toJson(self):
        return json.dumps(self.__dict__)
    
    def __init__(self):
        if "config.json" in os.listdir():
            f = open("config.json")
            jsonstr = f.read()
            jsonf = json.loads(jsonstr)
            f.close()
            self.controller_name=jsonf["controller_name"]
            self.wifissid = jsonf["wifissid"]
            self.wifipassword = jsonf["wifipassword"]
            self.mqttserver=jsonf["mqttserver"]
            self.mqttusername=jsonf["mqttusername"]
            self.mqttpassword=jsonf["mqttpassword"]
            self.root_topicOut=self.controller_name + jsonf["root_topicOut"]
            self.root_topicStatus=self.controller_name + jsonf["root_topicStatus"]
            self.root_topicHassioArm=self.controller_name + jsonf["root_topicHassioArm"]
            self.root_topicHassio=self.controller_name + jsonf["root_topicHassio"]
            self.root_topicArmHomekit=self.controller_name + jsonf["root_topicArmHomekit"]
            self.root_topicIn=self.controller_name + jsonf["root_topicIn"]
            self.ESP_UART=jsonf["ESP_UART"]
            self.timezone=jsonf["timezone"]
            self.homeit=jsonf["homekit"]
            self.homekit_user=jsonf["homekit_user"]
                
    

        


        
