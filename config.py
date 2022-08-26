import os
import json
import ubinascii
import machine
from cryptolib import aes


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
    homekit_user="0000"
    homekit_secure=False
    
    STAY_ARM = 0x01
    STAY_ARM2 = 0x02
    SLEEP_ARM = 0x03
    FULL_ARM = 0x04
    DISARM = 0x05
    BYPASS = 0x10
    PGMON = 0x32
    PGMOFF = 0x33
    SET_DATE =0x30
    ARM_STATE=0x91
    PANEL_STATUS=0x50
    CLOSE_CONNECTION=0x70


    MESSAGE_LENGTH=37
    
    SEND_ALL_EVENTS = True
    
    key = ubinascii.hexlify(machine.unique_id())
    
    zonedef={}
    
    def readconfig():
        
        if "config.json" in os.listdir():
            f = open("config.json")
            jsonstr = f.read()
            f.close()
            return json.loads(jsonstr)
        
    @classmethod
    def pad_string(cls,string):
        pad = 16 - len(string) % 16
        return string + "#"*pad
        
    @classmethod
    def decrypt(cls,password):
        vkey = configuration.pad_string(cls.key*2)
        g=aes(vkey,1)
        dpass = g.decrypt(password)
        return dpass.decode('utf-8').replace('#','')
    
    @classmethod
    def encrypt(cls,password):
        vkey = configuration.pad_string(cls.key*2)
        g=aes(vkey,1)
        dpass = g.encrypt(configuration.pad_string(password))
        return dpass
        
     
    @classmethod 
    def toJson(cls):
        config_dict = {
                "wifissid":cls.wifissid
                ,"wifipassword":cls.wifipassword
                ,"mqttserver":cls.mqttserver
                ,"mqttusername":cls.mqttusername
                ,"mqttpassword":cls.mqttpassword
                ,"root_topicOut":cls.root_topicOut
                ,"root_topicStatus":cls.root_topicStatus
                ,"root_topicIn":cls.root_topicIn
                ,"root_topicHassioArm":cls.root_topicHassioArm
                ,"root_topicHassio":cls.root_topicHassio
                ,"root_topicArmHomekit":cls.root_topicArmHomekit
                ,"ESP_UART":cls.ESP_UART
                ,"controller_name":cls.controller_name
                ,"timezone":cls.timezone
                ,"homekit":cls.homekit
                ,"homekit_secure":cls.homekit_secure
                ,"homekit_key":configuration.encrypt(cls.homekit_user)
                
            }
        return json.dumps(config_dict)
    
    @classmethod
    def load_zone_def(cls):
        if "zonedef.json" in os.listdir():
            print ("Loading zone def")
            with open('zonedef.json') as json_file:
                cls.zonedef = json.load(json_file)
        else:
            for i in range(32):
                if i not in cls.zonedef and i>0:
                    cls.zonedef[i] = {"enabled":true,"name":i,"type":"ContactSensor"}
                
    
    @classmethod
    def __init__(cls):
        if "config.json" in os.listdir():
            print("reading config file")
            f = open("config.json")
            jsonstr = f.read()
            jsonf = json.loads(jsonstr)
            f.close()
            cls.controller_name=jsonf["controller_name"]
            cls.wifissid = jsonf["wifissid"]
            cls.wifipassword = jsonf["wifipassword"]
            cls.mqttserver=jsonf["mqttserver"]
            cls.mqttusername=jsonf["mqttusername"]
            cls.mqttpassword=jsonf["mqttpassword"]
            cls.root_topicOut=cls.controller_name + jsonf["root_topicOut"]
            cls.root_topicStatus=cls.controller_name + jsonf["root_topicStatus"]
            cls.root_topicHassioArm=cls.controller_name + jsonf["root_topicHassioArm"]
            cls.root_topicHassio=cls.controller_name + jsonf["root_topicHassio"]
            cls.root_topicArmHomekit=cls.controller_name + jsonf["root_topicArmHomekit"]
            cls.root_topicIn=cls.controller_name + jsonf["root_topicIn"]
            cls.ESP_UART=jsonf["ESP_UART"]
            cls.timezone=jsonf["timezone"]
            cls.homekit=True if jsonf["homekit"]=="true" else False
            
            if 'homekit_key' in jsonf:
                cls.homekit_user=configuration.decrypt(jsonf["homekit_key"])
                
            if 'homekit_secure' in jsonf:
                cls.homekit_secure=True if jsonf["homekit_secure"]=="true" else False
        
                        
        configuration.load_zone_def()
                
    
    
        


        
