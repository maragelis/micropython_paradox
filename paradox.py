from machine import UART
import json
import config
from time import sleep

cfg = config.configuration()

paradoxserial = UART(2,baudrate=9600)
paradoxserial.init()

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


MESSAGE_LENGTH=37

PANEL_IS_LOGGED_IN=False
COMUNTICATION_INIT=False

MESSAGE = bytearray(MESSAGE_LENGTH)
MESSAGEOUT = bytearray(MESSAGE_LENGTH)

class paradoxArm:
    intArmStatus=0
    stringArmStatus=""
    Partition=0
    sent=0
    
    def toJson(self):
        return json.dumps(self.__dict__)
    
    def __str__(self):
        return f"paradoxArm intArmStatus:{str(self.intArmStatus)} ,stringArmStatus:{self.stringArmStatus},Partition:{str(self.Partition)},sent:{str(self.sent)}"

hassioStatus1 = paradoxArm()
hassioStatus2 = paradoxArm()
hassioStatus = (hassioStatus1,hassioStatus2)


class E0_message:
    Command=""
    Century=""
    Year=""
    Month=""
    Day=""
    Hour=""
    Minute=""
    Event_Group_Number=""
    Event_Supgroup_Number=""
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
    state=False
    Partition_Number=0
    topic=""
    
    def toJson(self):
        return json.dumps(self.__dict__)
    

class inMessage:
   
    panel_password=""
    command= ""
    subcommand="0"
        
    def __str__(self):
        return f"panel_password:{self.panel_password}, command:{self.command}, subcommand:{self.subcommand}"


class paradox_arm_status:
    intArmStatus=0
    stringArmStatus=""
    partition=0
    sent=0
    

def serialRead():
    global MESSAGE
    reset_message()
    if paradoxserial.any() >= 37 :
        print("Serial has data")
        paradoxserial.readinto(MESSAGE)
        return True
    else:
        return False
    
def serialWrite():
    buffer_count = paradoxserial.write(MESSAGEOUT)
    if buffer_count==MESSAGE_LENGTH:
        return True
    else:
        return False
    
    
def updateArmStatus(event, sub_event, partition):
    print(f"updateArmStatus event:{event}, sub_event:{sub_event},partition:{partition} ")
    global hassioStatus
    datachanged = False
    hassioStatus[partition].Partition  = partition
    if (event == 2):
        print("event:2")
        if sub_event==4:
            print("sub_event:4")
            
            hassioStatus[partition].stringArmStatus = "triggered"
            hassioStatus[partition].intArmStatus=4
            datachanged=True
        elif sub_event==11:
            print("sub_event:11")
            hassioStatus[partition].stringArmStatus = "disarmed"
            hassioStatus[partition].intArmStatus = 3
            datachanged=True
        elif sub_event==12:
            print("sub_event:12")
            hassioStatus[partition].stringArmStatus = "armed_away"
            hassioStatus[partition].intArmStatus = 1
            datachanged=True
    elif (event == 6):
        print("event:6")
        if (sub_event == 3):
            print("sub_event:3")
            datachanged=True
            hassioStatus[partition].stringArmStatus = "armed_home"
            hassioStatus[partition].intArmStatus = 0
        elif ( sub_event == 4):
            print("sub_event:4")
            datachanged=True
            hassioStatus[partition].stringArmStatus = "armed_home"
            hassioStatus[partition].intArmStatus = 2
    print(f"hassioStatus:{hassioStatus[partition]}")     
    
def get_event_data():
    e0msg = E0_message()
    e0msg.Command=MESSAGE[0]
    e0msg.Century=MESSAGE[1]
    e0msg.Year=MESSAGE[2]
    e0msg.Month=MESSAGE[3]
    e0msg.Day=MESSAGE[4]
    e0msg.Hour=MESSAGE[5]
    e0msg.Minute=MESSAGE[6]
    e0msg.Event_Group_Number=MESSAGE[7]
    e0msg.Event_Supgroup_Number=MESSAGE[8]
    e0msg.Partition_Number=MESSAGE[9]
    e0msg.Data=MESSAGE[15:30].decode().strip()
    return e0msg.toJson()

def processMessage():
    print("processMessage")
    global hassioStatus
    print(MESSAGE)
    
    if MESSAGE[0] == 0x01 or MESSAGE[0] == 0x00:
        COMUNTICATION_INIT=True
    
    if MESSAGE[0] == 0xE0:
        event=MESSAGE[7]
        sub_event=MESSAGE[8]
        partition=MESSAGE[9]
        
        if MESSAGE[7] == 0 or MESSAGE[7]==1:
            print("E0 Zone Message receivied")
            e = zone_message()
            e.zone=MESSAGE[8]
            e.state=True if MESSAGE[7] == 1 else False 
            e.Partition_Number=MESSAGE[9]
            e.zone_name=MESSAGE[15:30].decode().strip()
            e.topic = cfg.root_topicHassio.decode() + "/zone" + str(MESSAGE[8])
            print(f"returning zoneJson  {e.toJson()}")
            return e.toJson()
        elif (MESSAGE[7] == 48 and MESSAGE[8] == 3):
            PANEL_IS_LOGGED_IN = False
            print(f"Panel Login status:{PANEL_IS_LOGGED_IN}")
        elif (MESSAGE[7] == 48 and MESSAGE[8] == 2 ):
            PANEL_IS_LOGGED_IN = true
            print(f"Panel Login status:{PANEL_IS_LOGGED_IN}")
        elif event == 2 or event == 6:
            print(f"event:{event} updateArmStatus")
            updateArmStatus(event,sub_event, partition)
            print(f"returned from updateArmStatus")
            return 
        elif (event != 2 and sub_event != 12) :
            print(f"event:{event},sub_event:{sub_event} sendArmStatus")
            if (hassioStatus[partition].sent != hassioStatus[partition].intArmStatus):
                hassioStatus[partition].sent = hassioStatus[partition].intArmStatus
                return sendArmStatus(hassioStatus[partition])
                
    print(f"Ended processMessage")
      
            

def program_init(version):
    return f"Program started ver:{version}".encode()
    


def panel_control(inCommand=inMessage()):
    global MESSAGEOUT
    print("Starting panel_control")
    MESSAGEOUT = initialize_comunitcation()
    print(f"initialize_comunitcation {MESSAGEOUT}")
    serialWrite()
    cnt=0
    while not COMUNTICATION_INIT:
        sleep(1)
        cnt +=1
        if cnt>=5:
            print("COMUNTICATION_INIT problem")
            return
    
    
    MESSAGEOUT = panel_login(inCommand.panel_password)
    print(f"panel_login {MESSAGEOUT}")
    serialWrite()        
    cnt=0
    while not PANEL_IS_LOGGED_IN:
        sleep(1)
        cnt +=1
        if cnt>=5:
            print("panel login problem")
            return
    
    
    panel_command = get_panel_command(inCommand.command)
    panel_subcommand = int(inCommand.subcommand) & 0xff
    armdata = bytearray(MESSAGE_LENGTH)
    armdata[0] = 0x40
    armdata[2] = panel_command
    armdata[3] = panel_subcommand
    armdata[33] = 0x05
    armdata[34] = 0x00
    armdata[35] = 0x00
    MESSAGEOUT = checksum_calculate(armdata)
    serialWrite()

def reset_message():
    global MESSAGE
    MESSAGE = bytearray(MESSAGE_LENGTH)
    return MESSAGE

def checksum_calculate(data):
    checksum = 0
    for x in range(MESSAGE_LENGTH-1):  
        checksum += data[x]
    
    print(f"calculate checksum for {checksum}")
    while (checksum > 255) :
        checksum = checksum - (checksum / 256) * 256
    print(f"checksum = {checksum}")
    #checksum = checksum #& 0xFF
    #print(type(checksum))
    data[36] =  checksum & 0xFF
    return data

def initialize_comunitcation():
    data = bytearray(MESSAGE_LENGTH)
    data[0] = 0x5f
    data[1] = 0x20
    data[33] = 0x05
    data[34] = 0x00
    data[35] = 0x00
    data = checksum_calculate(data)
    return data

def panel_login(panel_password):
    data1=bytearray(MESSAGE_LENGTH)
    data1[0] = 0x00;
    data1[4] = MESSAGE[4]
    data1[5] = MESSAGE[5]
    data1[6] = MESSAGE[6]
    data1[7] = MESSAGE[7]
    data1[7] = MESSAGE[8]
    data1[9] = MESSAGE[9]
    data1[10] = 0x00;
    data1[11] = 0x00;
    data1[13] = 0x55;
    data1[14] = int((str(panel_password)[0:2])) # //panel pc password digit 1 & 2
    data1[15] = int((str(panel_password)[2:4])) # //panel pc password digit 3 & 4
    data1[33] = 0x05;
    data1=checksum_calculate(data1)
    return data1




def get_panel_command(arm_request):
    arm_request=arm_request.lower()
    retval = 0x00
    if (arm_request == "stay" or arm_request=="0"):
        retval= STAY_ARM
    elif (arm_request == "arm" or arm_request=="1"):
        retval= FULL_ARM
    elif (arm_request == "sleep" or arm_request=="2"):
        retval= SLEEP_ARM
    elif (arm_request == "disarm" or arm_request == "3"):
        return DISARM
    elif (arm_request == "bypass" or arm_request == "10"):
        retval= BYPASS
    elif (arm_request == "pgm_on" or arm_request == "pgmon"):
        retval= PGMON
    elif (arm_request == "pgm_off" or arm_request == "pgmoff"):
        retval= PGMOFF
    elif (arm_request == "panelstatus" ):
        retval= PANEL_STATUS
    elif (arm_request == "setdate"):
        retval= SET_DATE
    elif (arm_request == "armstate"):
        retval= ARM_STATE
    return retval
    


  
def sendArmStatus(hass):
    print("Sending ArmStatus")
    arm_mesg=arm_message()
    arm_mesg.topic = cfg.root_topicHassioArm.decode() + str(hass.Partition)
    arm_mesg.Armstatus =  hass.intArmStatus
    arm_mesg.ArmStatusD = hass.stringArmStatus
    
    return arm_mesg.toJson() 