import json
import os
import config

class homekit:
    default_topic="homebridge"
    to_add=f"{default_topic}/to/add"
    add_service=f"{default_topic}/to/add/service"
    to_remove=f"{default_topic}/to/remove"
    to_remove_service=f"{default_topic}/to/remove/service"
    to_get=f"{default_topic}/to/get"
    to_set=f"{default_topic}/to/set"
    to_set_reachability=f"{default_topic}/to/set/reachability"
    to_set_accessoryinformation=f"{default_topic}/to/set/accessoryinformation"
    from_get=f"{default_topic}/from/get"
    from_set=f"{default_topic}/from/set"
    from_response=f"{default_topic}/from/response"
    from_identify=f"{default_topic}/from/identify"
    controller_name="paradox32CTL"
    mqttclient =""
    
    STAY_ARM = 0
    AWAY_ARM = 1
    NIGHT_ARM = 2
    DISARMED = 3
    ALARM_TRIGGERED = 4
    MotionDetectorType="MotionSensor"
    ContactDetectorType="ContactSensor"
    MotionDetected_characteristic = "MotionDetected"
    ContactSensorState_characteristic="ContactSensorState"
    SecuritySystemCurrentState_characteristic="SecuritySystemCurrentState"
    SecuritySystemTargetState_characteristic="SecuritySystemTargetState"
    
    @classmethod
    def __init__(cls, homebridge_prefix,controller_name, mqttclient):
        cls.to_add=f"{homebridge_prefix}/to/add"
        cls.add_service=f"{homebridge_prefix}/to/add/service"
        cls.to_remove=f"{homebridge_prefix}/to/remove"
        cls.to_remove_service=f"{homebridge_prefix}/to/remove/service"
        cls.to_get=f"{homebridge_prefix}/to/get"
        cls.to_set=f"{homebridge_prefix}/to/set"
        cls.to_set_reachability=f"{homebridge_prefix}/to/set/reachability"
        cls.to_set_accessoryinformation=f"{homebridge_prefix}/to/set/accessoryinformation"
        cls.from_get=f"{homebridge_prefix}/from/get"
        cls.from_set=f"{homebridge_prefix}/from/set"
        cls.from_response=f"{homebridge_prefix}/from/response"
        cls.from_identify=f"{homebridge_prefix}/from/identify"
        cls.controller_name = controller_name
        cls.mqttclient =mqttclient

        homekit.add_homekit_accessories()
    
    @classmethod
    def add_homekit_accessories(cls):
        try:
            homekit.main()
            homekit.zone()   
        except OSError as e:
                print(e)
            
        
    
    @classmethod    
    def main(cls):
        main_dic = {
            "name":  cls.controller_name,
            "service_name": cls.controller_name,
            "service":"SecuritySystem"}
        cls.mqttclient.publish(cls.to_add,json.dumps(main_dic))
    
    @classmethod
    def zone(cls):
        #self.accessory_name = kwargs.get('name')
        
        if "homekitconfig.json" in os.listdir():
         with open('homekitconfig.json') as json_file:
             z_dic = json.load(json_file)
        else:
            z_dic=[]
        
        cfgx=config.configuration()
                
        for i in cfgx.zonedef :
                if cfgx.zonedef[i]["enabled"]:
                    obj_name = f"{i}_{cfgx.zonedef[i]['name']}"
                    if obj_name not in z_dic:
                        z_dic.append(obj_name)
                        #print(f"obj_name:{obj_name} service={zonedef[i]['type']}")
                        #json_obj = zone(name=obj_name,service_name=obj_name,service=cfg.zonedef[i]["type"])
                        fobj_name = obj_name.replace('_',' ')
                        zone_dic = {"name":fobj_name,"service_name": fobj_name,"service":cfgx.zonedef[i]["type"]}
                        
                        cls.mqttclient.publish(cls.to_add,json.dumps(zone_dic))
                        time.sleep(1)
        
        f = open('homekitconfig.json','w')
        f.write(json.dumps(z_dic))
        f.close()      
               
        
        return True
    
    @classmethod
    def set_zone_value(cls, zone, zone_type,state):
        characteristic = cls.MotionDetected_characteristic
        valuestate = True if state=="ON" else False
        
        if zone_type =="ContactSensor":
            characteristic = cls.ContactSensorState_characteristic
            valuestate = 1 if state=="ON" else 0
            
        set_dic = {"name": zone.replace('_',' '),
                   "service_name": zone.replace('_',' '),
                   "characteristic": characteristic,
                   "value": valuestate}
        
        cls.mqttclient.publish(homekit.to_set,json.dumps(set_dic))
        return True
    
    @classmethod
    def set_alarm_state(cls, characteristic,intArmStatus):
                    
        set_dic = {"name": cls.controller_name,
                   "service_name": cls.controller_name,
                   "characteristic": characteristic,
                   "value": intArmStatus}
        cls.mqttclient.publish(homekit.to_set,json.dumps(set_dic))
        return True
    
                        
