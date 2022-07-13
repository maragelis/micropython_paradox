import websrv
import paradoxEvents
import json
import threading
from machine import UART
from time import sleep

VERSION="0.01"

SEND_ALL_EVENTS = True



client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = cfg.root_topicIn
mqtt_server = cfg.mqttserver
print(f"mqtt_server:{cfg.mqttserver}, username:{cfg.mqttusername}, password:{cfg.mqttpassword}, topic:{cfg.root_topicIn}")

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
PANEL_LOGIN_IN_PROGRESS=False

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
    

def sub_cb(topic, msg):
    print((topic, msg))
    if topic == bytes(cfg.root_topicIn,"utf-8") :
        strmsg = msg.decode("utf-8")
        json_data = json.loads(strmsg)
        inmessage =inMessage()
        if "panel_password" in json_data:
            inmessage.panel_password=json_data["panel_password"]
        if "command" in json_data:
            inmessage.command = json_data["command"]
        if "subcommand" in json_data:
            inmessage.subcommand = json_data["subcommand"]
        else:
            inmessage.subcommand = "0"
            
        print(panel_control(inmessage))
            
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
  print('RESETTING ....')
  machine.reset()    

def serialRead():
    MESSAGE = bytearray(MESSAGE_LENGTH)
        
    if  paradoxserial.any() >= 37 :
        #reset_message()
        print(f"serialRead has data {paradoxserial.any()}")
        paradoxserial.readinto(MESSAGE)
        
        processMessage(MESSAGE)
        if SEND_ALL_EVENTS:
            get_event_data(MESSAGE)
        
        return True
    else:
        return False
    #sleep(0.5)
        
def serialReadWriteQuick(byteMessage):
    global MESSAGE
    
    paradoxserial.write(byteMessage)
    
    serial_message= bytearray(MESSAGE_LENGTH)
    loop = True
    while loop:
        if paradoxserial.any() >= 37 :
            print(f"serialReadWriteQuick has data {paradoxserial.any()}")
            paradoxserial.readinto(serial_message)
            if serial_message[0] & 0x10 == 0x10 :
                print("Returning 0x10 message")
                return serial_message
            if serial_message[0] & 0x00 == 0x00 and serial_message[4] != 0x00 :
                print(f"Returning 0x00 with serial_message[4] : {serial_message[4]}")
                return serial_message
            loop=False
        
        
        

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
            print(f"ARM_STATE update : triggered")
        elif sub_event==11:
            print("sub_event:11")
            hassioStatus[partition].stringArmStatus = "disarmed"
            hassioStatus[partition].intArmStatus = 3
            datachanged=True
            print(f"ARM_STATE update : disarmed")
        elif sub_event==12:
            print("sub_event:12")
            hassioStatus[partition].stringArmStatus = "armed_away"
            hassioStatus[partition].intArmStatus = 1
            datachanged=True
            print(f"ARM_STATE update : armed_away")
    elif (event == 6):
        print("event:6")
        if (sub_event == 3):
            print("sub_event:3")
            datachanged=True
            hassioStatus[partition].stringArmStatus = "armed_stay"
            hassioStatus[partition].intArmStatus = 0
            print(f"ARM_STATE update : armed_home")
        elif ( sub_event == 4):
            print("sub_event:4")
            datachanged=True
            hassioStatus[partition].stringArmStatus = "armed_sleep"
            hassioStatus[partition].intArmStatus = 2
            print(f"ARM_STATE update : armed_home")
    print(f"hassioStatus:{hassioStatus[partition]}")     
    
def get_event_data(serial_message):
    e0msg = E0_message()
    if serial_message[0] & 0xF0 == 0xE0:
        
        e0msg.Command=serial_message[0]
        e0msg.Century=serial_message[1]
        e0msg.Year=serial_message[2]
        e0msg.Month=serial_message[3]
        e0msg.Day=serial_message[4]
        e0msg.Hour=serial_message[5]
        e0msg.Minute=serial_message[6]
        e0msg.Event_Group_Number=serial_message[7]
        e0msg.Event_Supgroup_Number=serial_message[8]
        e0msg.Partition_Number=serial_message[9]
        e0msg.Data=paradoxEvents.getEvent(serial_message[7])
        client.publish(cfg.root_topicOut, e0msg.toJson())

def processMessage(serial_message):
    #print("processMessage")
    global hassioStatus,PANEL_IS_LOGGED_IN
    print(f"processMessage serial_message is {hex(serial_message[0])} - {serial_message[0]}c ")
    #for x in range(MESSAGE_LENGTH):
    #    print(f"[serial_message{x}]={hex(serial_message[x])}")
       
    print(f"FIXED serial_message[0] {hex(serial_message[0] & 0xF0)} - {serial_message[0] & 0xF0}c ")    
    if serial_message[0] & 0xF0 == 0xE0 :
        print(f"Entired 0xE")
        event=serial_message[7]
        sub_event=serial_message[8]
        partition=serial_message[9]
        
        if serial_message[7] == 0 or serial_message[7]==1:
            print("E0 Zone Message receivied")
            e = zone_message()
            e.zone=serial_message[8]
            e.state=True if serial_message[7] == 1 else False 
            e.Partition_Number=serial_message[9]
            e.zone_name=serial_message[15:30].decode().strip()
            e.topic = cfg.root_topicHassio + "/zone" + str(serial_message[8])
            print(f"returning zoneJson  {e.toJson()}")
            client.publish(e.topic, e.toJson())
            
        
            
        elif (serial_message[7] == 48 and serial_message[8] == 3):
            PANEL_IS_LOGGED_IN = False
            print(f"Panel Login from E0 message PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
            
        elif (serial_message[7] == 48 and serial_message[8] == 2 ):
            PANEL_IS_LOGGED_IN = True
            print(f"Panel Login from E0 message PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
           
                   
        elif event == 2 or event == 6:
            print(f"event:{event} updateArmStatus")
            updateArmStatus(event,sub_event, partition)
            print(f"returned from updateArmStatus")
            
            if (event == 2 and sub_event == 11):
                sendArmStatus(hassioStatus[partition])
            
            if (event == 6 and sub_event == 27) or (event == 6  and sub_event>=3 and sub_event <= 6):
                sendArmStatus(hassioStatus[partition])
                
        elif (event != 2 and sub_event != 12) :
            print(f"process message event:{event},sub_event:{sub_event} sendArmStatus")
            if (hassioStatus[partition].sent != hassioStatus[partition].intArmStatus):
                hassioStatus[partition].sent = hassioStatus[partition].intArmStatus
                sendArmStatus(hassioStatus[partition])  
        
        
    print(f"Ended processMessage")
      
            

def program_init(version):
    print(version)
    return f"Program started ver:{version}".encode()
    


def panel_control(inCommand=inMessage()):
    
    global PANEL_IS_LOGGED_IN
    if not PANEL_IS_LOGGED_IN:
        print(f"panel_control PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
        panel_login(inCommand.panel_password)
        print(f"panel_control PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
    
    panel_command = get_panel_command(inCommand.command)
    panel_subcommand = int(inCommand.subcommand) 
    armdata = bytearray(MESSAGE_LENGTH)
    armdata[0] = 0x40
    armdata[2] = panel_command
    armdata[3] = panel_subcommand
    armdata[33] = 0x05
    armdata[34] = 0x00
    armdata[35] = 0x00
    armdata = checksum_calculate(armdata)
    #for x in range(MESSAGE_LENGTH):
    #    print(f"[armdata{x}]={hex(armdata[x])}")
        
    if serialWrite(armdata):
        print("armdata written to serial")
        
    return True


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

def panel_login(panel_password):
    global PANEL_LOGIN_IN_PROGRESS,PANEL_IS_LOGGED_IN
    
    PANEL_LOGIN_IN_PROGRESS=True
    sleep(1)
    initMessage = initialize_comunitcation()
    
    print("Sent initialize_comunitcation")
    rinitMessage = serialReadWriteQuick(initMessage)
    print("returned initialize_comunitcation")
    print(rinitMessage)
    
    pass1 = "0x" + str(panel_password)[0:2]
    pass2 = "0x" + str(panel_password)[2:4]
    
    data1=bytearray(MESSAGE_LENGTH)
    
    data1[0] = 0x00;
    data1[4] = rinitMessage[4]& 0xff
    data1[5] = rinitMessage[5]& 0xff
    data1[6] = rinitMessage[6]& 0xff
    data1[7] = rinitMessage[7]& 0xff
    data1[7] = rinitMessage[8]& 0xff
    data1[9] = rinitMessage[9]& 0xff
    data1[10] = 0x00;
    data1[11] = 0x00;
    data1[13] = 0x55;
    data1[14] = int(pass1, 16)
    data1[15] = int(pass2, 16)
    data1[33] = 0x05;
    data1=checksum_calculate(data1)
    initMessage = serialReadWriteQuick(data1)  
    if (initMessage[0] == 0x10):
        PANEL_IS_LOGGED_IN=True
    
    PANEL_LOGIN_IN_PROGRESS=False




def get_panel_command(arm_request):
    arm_request=arm_request.lower()
    retval = 0
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
    print(f"SENDING ARM STATUS {hass}")
    arm_mesg=arm_message()
    arm_mesg.topic = cfg.root_topicHassioArm + str(hass.Partition)
    arm_mesg.Armstatus =  hass.intArmStatus
    arm_mesg.ArmStatusD = hass.stringArmStatus
    client.publish(arm_mesg.topic,arm_mesg.toJson() )
    return arm_mesg.toJson() 
  
try:
  client = connect_and_subscribe()
  client.publish(cfg.root_topicStatus, program_init(VERSION))
except OSError as e:
  restart_and_reconnect()


Serial_loop_msg=False
def serialloop():
    global Serial_loop_msg,PANEL_LOGIN_IN_PROGRESS
    while True:
        try:
            client.check_msg()
            if PANEL_LOGIN_IN_PROGRESS != Serial_loop_msg:
                  print(f"PANEL_LOGIN_IN_PROGRESS Status changed to {PANEL_LOGIN_IN_PROGRESS}")
                  Serial_loop_msg=PANEL_LOGIN_IN_PROGRESS
            if not PANEL_LOGIN_IN_PROGRESS:
              serialRead()            

        except OSError as e:
            restart_and_reconnect()

#serialloop()
t1= threading.Thread(target=serialloop)

if __name__ == '__main__':
    try:
        t1.start()
        #serialloop()
        print("Starting Webserver")
        websrv.runsrv()
    except:
        restart_and_reconnect()
    