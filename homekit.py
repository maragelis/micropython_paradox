import json



class homekit:
    
    def __init__(self, homebridge_prefix):
        
        self.to_add=f"{homebridge_prefix}/to/add"
        self.add_service=f"{homebridge_prefix}/to/add/service"
        self.to_remove=f"{homebridge_prefix}/to/remove"
        self.to_remove_service=f"{homebridge_prefix}/to/remove/service"
        self.to_get=f"{homebridge_prefix}/to/get"
        self.to_set=f"{homebridge_prefix}/to/set"
        self.to_set_reachability=f"{homebridge_prefix}/to/set/reachability"
        self.to_set_accessoryinformation=f"{homebridge_prefix}/to/set/accessoryinformation"
        self.from_get=f"{homebridge_prefix}/from/get"
        self.from_set=f"{homebridge_prefix}/from/set"
        self.from_response=f"{homebridge_prefix}/from/response"
        self.from_identify=f"{homebridge_prefix}/from/identify"
        self.accessory_name = ""
        
        
        self.STAY_ARM = 0
        self.AWAY_ARM = 1
        self.NIGHT_ARM = 2
        self.DISARMED = 3
        self.ALARM_TRIGGERED = 4
        self.MotionDetectorType="MotionSensor"
        self.ContactDetectorType="ContactSensor"
        self.MotionDetected_characteristic = "MotionDetected"
        self.ContactSensorState_characteristic="ContactSensorState"
        self.SecuritySystemCurrentState_characteristic="SecuritySystemCurrentState"
        self.SecuritySystemTargetState_characteristic="SecuritySystemTargetState"
        
    def main(self, **kwargs):
        self.accessory_name = kwargs.get('name')
        main_dic = {
            "name":  kwargs.get('name'),
            "service_name": kwargs.get('service_name'),
            "service": kwargs.get('service',"SecuritySystem")
            }
        return json.dumps(main_dic)
    
    def zone(self, **kwargs):
        #self.accessory_name = kwargs.get('name')
        zone_dic = {
            "name":  kwargs.get('name').replace('_',' '),
            "service_name": kwargs.get('service_name').replace('_',' '),
            "service": kwargs.get('service',"ContactSensor")
            }
        return json.dumps(zone_dic)
    
    
    def set_zone_value(self, zone, zone_type,state):
        characteristic = self.MotionDetected_characteristic
        valuestate = True if state=="ON" else False
        
        if zone_type =="ContactSensor":
            characteristic = self.ContactSensorState_characteristic
            valuestate = 1 if state=="ON" else 0
            
        set_dic = {"name": zone.replace('_',' '),
                   "service_name": zone.replace('_',' '),
                   "characteristic": characteristic,
                   "value": valuestate}
        return json.dumps(set_dic)
    
    def set_alarm_state(self, characteristic,intArmStatus):
                    
        set_dic = {"name": self.accessory_name,
                   "service_name": self.accessory_name,
                   "characteristic": characteristic,
                   "value": intArmStatus}
        return json.dumps(set_dic)
    
                        
