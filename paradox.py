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
    
    if paradoxserial.any() >= 37 :
        reset_message()
        print("Serial has data")
        paradoxserial.readinto(MESSAGE)
        if MESSAGE[0]==0x72:
            while paradoxserial.any()>0:
                paradoxserial.read()
                return False
        
        return True
    else:
        return False
    
def serialWrite(byteMessage):
    buffer_count = paradoxserial.write(byteMessage)
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
    if MESSAGE[0] == 0xE0:
        
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
    print(f"MESSAGE is {hex(MESSAGE[0])} - {MESSAGE[0]}c ")
    
       
    if MESSAGE[0] == 0x01 or MESSAGE[0] == 0x00:
        COMUNTICATION_INIT=True
        print(f"Message is {hex(MESSAGE[0])}")
    
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
            e.topic = cfg.root_topicHassio + "/zone" + str(MESSAGE[8])
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
    global PANEL_IS_LOGGED_IN
    print("Starting panel_control")
    init = initialize_comunitcation()
    print(f"initialize_comunitcation {init}")
    if serialWrite(init):
        while not serialRead():
            pass
            
    initmessage = MESSAGE    
    for x in range(MESSAGE_LENGTH):
        print(f"[initmessage{x}]={hex(initmessage[x])}")
    
    print(f"Message : {MESSAGE[0]}")    
    login = panel_login(inCommand.panel_password,initmessage)
    print(f"panel_login {login[14]} {login[15]}")
    for x in range(MESSAGE_LENGTH):
        print(f"[login{x}]={hex(login[x])}") 
        
    if serialWrite(login):
        print("Login written to serial")
        while not (serialRead()):
            pass
        
    for x in range(MESSAGE_LENGTH):
        print(f"[MESSAGE{x}]={hex(MESSAGE[x])}")    
    
    print(f"Message : {MESSAGE[0]}")
    if MESSAGE[0]==0x10:
        PANEL_IS_LOGGED_IN=True
        
    
    print(f"PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
    
    panel_command = get_panel_command(inCommand.command)
    panel_subcommand = int(inCommand.subcommand) & 0xff
    armdata = bytearray(MESSAGE_LENGTH)
    armdata[0] = 0x40
    armdata[2] = panel_command
    armdata[3] = panel_subcommand
    armdata[33] = 0x05
    armdata[34] = 0x00
    armdata[35] = 0x00
    armdata = checksum_calculate(armdata)
    
    if serialWrite(armdata):
        print("armdata written to serial")
        while not (serialRead()):
            pass
    return True

def reset_message():
    global MESSAGE
    MESSAGE = bytearray(MESSAGE_LENGTH)
    MESSAGE[0]=255
    return MESSAGE

def checksum_calculate(data):
    checksum = 0
    for x in range(MESSAGE_LENGTH-1):  
        checksum += data[x]
    
    print(f"calculate checksum for {checksum}")
    while (checksum > 255) :
        intch =int(checksum / 256)
        checksum = checksum - intch * 256
    print(f"checksum = {checksum}")
    #checksum = checksum #& 0xFF
    #print(type(checksum))
    data[36] =  checksum
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

def panel_login(panel_password, initMessage):
    pass1 = "0x" + str(panel_password)[0:2]
    pass2 = "0x" + str(panel_password)[2:4]
    
    data1=bytearray(MESSAGE_LENGTH)
    
    data1[0] = 0x00;
    data1[4] = initMessage[4]& 0xff
    data1[5] = initMessage[5]& 0xff
    data1[6] = initMessage[6]& 0xff
    data1[7] = initMessage[7]& 0xff
    data1[7] = initMessage[8]& 0xff
    data1[9] = initMessage[9]& 0xff
    data1[10] = 0x00;
    data1[11] = 0x00;
    data1[13] = 0x55;
    data1[14] = int(pass1, 16)
    data1[15] = int(pass2, 16)
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