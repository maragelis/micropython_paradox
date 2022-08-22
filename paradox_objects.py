import json

class status_0:
    def __init__(self):
        self.Timer_Loss = ""
        self.PowerTrouble  = ""
        self.ACFailureTroubleIndicator = ""
        self.NoLowBatteryTroubleIndicator = ""
        self.TelephoneLineTroubleIndicator = ""
        self.ACInputDCVoltageLevel = ""
        self.PowerSupplyDCVoltageLevel =""
        self.BatteryDCVoltageLevel=""
        
    def toJson(self):
        return json.dumps(self.__dict__)
    
class status_1:
    def __init__(self):
        self.Fire=False
        self.Audible=False
        self.Silent=False
        self.AlarmFlg=False
        self.StayFlg=False
        self.SleepFlg=False
        self.ArmFlg=False
        
    def toJson(self):
        return json.dumps(self.__dict__)
        
class paradoxArm:
    intArmStatus=99
    stringArmStatus=""
    HomeKit=""
    Partition=0
    sent=0
    
    def toJson(self):
        return json.dumps(self.__dict__)
    
    def __str__(self):
        return f"paradoxArm intArmStatus:{str(self.intArmStatus)} ,stringArmStatus:{self.stringArmStatus},Partition:{str(self.Partition)},sent:{str(self.sent)}"


class E0_message:
    Command=""
    Century=""
    Year=""
    Month=""
    Day=""
    Hour=""
    Minute=""
    Event_Group_Number=""
    Event_Subgroup_Number=""
    Event_Group_Desc=""
    Event_Subgroup_Desc=""
    Partition_Number=""
    Data=""
    
    def toJson(self):
        return json.dumps(self.__dict__)

class arm_message:
    Armstatus=""
    ArmStatusD=""
    topic=""
    
    def toJson(self):
        return json.dumps(self.__dict__)

class zone_message:
    zone=0
    zone_name=""
    state=""
    Partition_Number=0
    topic=""
    zone_def=""
    zone_type=""
    
    def toJson(self):
        return json.dumps(self.__dict__)
    

class inMessage:
   
    panel_password=""
    command= ""
    subcommand="0"
    
    def toJson(self):
        return json.dumps(self.__dict__)
        
    def __str__(self):
        return f"panel_password:{self.panel_password}, command:{self.command}, subcommand:{self.subcommand}"


class paradox_arm_status:
    intArmStatus=0
    stringArmStatus=""
    partition=0
    sent=0
    
