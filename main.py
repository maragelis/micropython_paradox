import websrv
import paradoxEvents
import utils
import ParadoxSubEvent
gc.collect()

print("hold 0 'boot button' for 5sec or ctrl-c to enter repl")
led.value(False)

replloopcnt=0
while replloopcnt <= 5:
    if repl_button.value() == 0:
        utils.trace("Dropping to REPL")
        sys.exit()
    else:
        print(f"waiting for repl {5-replloopcnt} {'.' * replloopcnt} ")
        replloopcnt +=1
        time.sleep(1)
        
    
            
VERSION="1.6.202208120955"

SEND_ALL_EVENTS = True
tim1 = machine.Timer(0)

#wdt = WDT(timeout=10000)


client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = cfg.root_topicIn
mqtt_server = cfg.mqttserver
utils.trace(f"mqtt_server:{cfg.mqttserver}, username:{cfg.mqttusername}, password:{cfg.mqttpassword}, topic:{cfg.root_topicIn}")

paradoxserial = UART(cfg.ESP_UART,baudrate=9600)
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
CLOSE_CONNECTION=0x70


MESSAGE_LENGTH=37

PANEL_IS_LOGGED_IN=False
COMUNTICATION_INIT=False
PANEL_LOGIN_IN_PROGRESS=False

LIFO=[]

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
    intArmStatus=0
    stringArmStatus=""
    HomeKit=""
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
    

    

def sub_cb(topic, msg):
    utils.trace((topic, msg))
    if topic == bytes(cfg.root_topicIn,"utf-8") :
        strmsg = msg.decode("utf-8")
        try:
            json_data = json.loads(strmsg.lower())
        except ValueError as e:
            client.publish(cfg.root_topicStatus, "malformatted json message try {'command':'arm','password':'1234'}" )
            return
            
        if "esp_command" in json_data:
                pass
        
        elif "panel_command" in json_data:
            if (str(json_data['panel_command']) == "setdate"):
                set_panel_date(str(json_data['password']))
                
            elif (str(json_data['panel_command']) == "status_0"):
                panel_status_0(str(json_data['password']))
                
            elif (str(json_data['panel_command']) == "status_1"):
                panel_status_1(str(json_data['password']))
                
            else:
                client.publish(cfg.root_topicStatus, "unknown panel_command" )
                
                
        elif ("command" in json_data):
            inmessage =inMessage()
            inmessage.command = json_data["command"]
            inmessage.panel_password=""
            fixed_password = ""
            
            if "panel_password" in json_data:
                fixed_password=str(json_data["panel_password"])
                
            elif "password" in json_data:
                fixed_password=str(json_data["password"])
            
            if len(fixed_password)>=4:
                for i in fixed_password:
                    inmessage.panel_password += i if i != '0' else 'A'
            else:
                inmessage.panel_password = "0000"
            
        
            if "subcommand" in json_data:
                inmessage.subcommand = json_data["subcommand"]
            else:
                inmessage.subcommand = "0"
            
            utils.trace(panel_control(inmessage))
        else:
            client.publish(cfg.root_topicStatus, "malformatted json message" )
        
        gc.collect()        
        utils.trace(f"ESP received message : {msg}")

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, user=cfg.mqttusername , password=cfg.mqttpassword,keepalive=30)
  client.set_callback(sub_cb)
  client.set_last_will(f"{cfg.controller_name}/reachable","false",retain=True)
  client.connect()
  client.subscribe(topic_sub)
  client.publish(f"{cfg.controller_name}/reachable","true",retain=True)
  utils.trace('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  utils.trace('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  utils.trace('RESETTING ....')
  machine.reset()    

def serialRead():
    try:
        
    
        MESSAGE = bytearray(MESSAGE_LENGTH)
            
        if  paradoxserial.any() >= 37 :
            #reset_message()
            utils.trace(f"serialRead has data {paradoxserial.any()}")
            paradoxserial.readinto(MESSAGE)
            
            if (MESSAGE[7] == 3 and MESSAGE[8] <=1):
                return True
            
            processMessage(MESSAGE)
            if SEND_ALL_EVENTS:
                get_event_data(MESSAGE)
            
            return True
        else:
            return False
    except OSError as e:
        print(e)
        restart_and_reconnect()
    #sleep(0.5)
        
def serialReadWriteQuick(byteMessage):
    global MESSAGE
    time_start = time.time()
    paradoxserial.write(byteMessage)
    
    serial_message= bytearray(MESSAGE_LENGTH)
    loop = True
    while loop :
        if paradoxserial.any() >= 37 :
            utils.trace(f"serialReadWriteQuick has data {paradoxserial.any()}")
            paradoxserial.readinto(serial_message)
            if serial_message[0] & 0x10 == 0x10 :
                utils.trace("Returning 0x10 message")
                return serial_message
            if serial_message[0] & 0x00 == 0x00 and serial_message[4] != 0x00 :
                utils.trace(f"Returning 0x00 with serial_message[4] : {serial_message[4]}")
                return serial_message
            loop=False
        
        
        

def serialWrite(byteMessage):
    wcnt =0 ;
    while paradoxserial.write(byteMessage) != MESSAGE_LENGTH:
        wcnt = wcnt +1
        time.sleep(1)
        if wcnt > 5:
            return False
        else:
            return True
    
    
    '''
    buffer_count = paradoxserial.write(byteMessage)
    if buffer_count==MESSAGE_LENGTH:
        return True
    else:
        buffer_count = paradoxserial.write(byteMessage)
        if buffer_count==MESSAGE_LENGTH:
            return True
        else:
            return False
    '''
    
    
def updateArmStatus(event, sub_event, partition):
    utils.trace(f"updateArmStatus event:{event}, sub_event:{sub_event},partition:{partition} ")
    global hassioStatus
    datachanged = False
    hassioStatus[partition].Partition  = partition
    if (event == 2):
        utils.trace("event:2")
        if sub_event>=2 and sub_event <=6 :
            utils.trace("sub_event:4")
            
            hassioStatus[partition].stringArmStatus = "triggered"
            hassioStatus[partition].intArmStatus=4
            hassioStatus[partition].HomeKit="T"
            datachanged=True
            utils.trace(f"ARM_STATE update : triggered")
        elif sub_event==11:
            utils.trace("sub_event:11")
            hassioStatus[partition].stringArmStatus = "disarmed"
            hassioStatus[partition].HomeKit="D"
            hassioStatus[partition].intArmStatus = 3
            datachanged=True
            utils.trace(f"ARM_STATE update : disarmed")
        elif sub_event==12:
            utils.trace("sub_event:12")
            hassioStatus[partition].stringArmStatus = "armed_away"
            hassioStatus[partition].HomeKit="AA"
            hassioStatus[partition].intArmStatus = 1
            datachanged=True
            utils.trace(f"ARM_STATE update : armed_away")
    elif (event == 6):
        utils.trace("event:6")
        if (sub_event == 3):
            utils.trace("sub_event:3")
            datachanged=True
            hassioStatus[partition].stringArmStatus = "armed_home"
            hassioStatus[partition].HomeKit="SA"
            hassioStatus[partition].intArmStatus = 0
            utils.trace(f"ARM_STATE update : armed_home")
        elif ( sub_event == 4):
            utils.trace("sub_event:4")
            datachanged=True
            hassioStatus[partition].stringArmStatus = "armed_home"
            hassioStatus[partition].HomeKit="NA"
            hassioStatus[partition].intArmStatus = 2
            utils.trace(f"ARM_STATE update : armed_home")
    utils.trace(f"hassioStatus:{hassioStatus[partition]}")     
    
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
        e0msg.Event_Subgroup_Desc=ParadoxSubEvent.getsubEvent(serial_message[7],serial_message[8])
        e0msg.Event_Subgroup_Number=serial_message[8]
        e0msg.Partition_Number=serial_message[9]
        e0msg.Event_Group_Desc=paradoxEvents.getEvent(serial_message[7])
        client.publish(cfg.root_topicOut, e0msg.toJson())

def processMessage(serial_message):
    #utils.trace("processMessage")
    global hassioStatus,PANEL_IS_LOGGED_IN
    utils.trace(f"processMessage serial_message is {hex(serial_message[0])} - {serial_message[0]}c ")
    #for x in range(MESSAGE_LENGTH):
    #    utils.trace(f"[serial_message{x}]={hex(serial_message[x])}")
     
    utils.trace(f"FIXED serial_message[0] {hex(serial_message[0] & 0xF0)} - {serial_message[0] & 0xF0}c ")
    if serial_message[0] & 0xF0 == 0x50 and serial_message[3] == 0x00:
        process_status_0_message(serial_message)
        process_status_0_zones(serial_message)
        
    elif serial_message[0] & 0xF0 == 0x50 and serial_message[3] == 0x01:
        process_status_1_message(serial_message)
        
    elif serial_message[0] & 0xF0 == 0xE0 :
        utils.trace(f"Entired 0xE")
        event=serial_message[7]
        sub_event=serial_message[8]
        partition=serial_message[9]
        
        
        if serial_message[7] == 0 or serial_message[7]==1:
            
            
            utils.trace("E0 Zone Message receivied")
            e = zone_message()
            e.zone=serial_message[8]
            e.state="ON" if serial_message[7] == 1 else "OFF" 
            e.Partition_Number=serial_message[9]
            e.zone_name=serial_message[15:30].decode().strip()
            e.topic = f"{cfg.controller_name}/zones/zone{str(serial_message[8])}"
            utils.trace(f"returning zoneJson  {e.toJson()}")
            client.publish(e.topic, str(e.state), True, 1 )
            
            #e.topic = cfg.root_topicArmHomekit + "/zone" + str(serial_message[8])
            #client.publish(e.topic, str(e.state), True, 1 )
            e.topic = cfg.root_topicStatus
            client.publish(cfg.root_topicStatus, e.toJson())    
        
            
        elif (serial_message[7] == 48 and serial_message[8] == 3):
            PANEL_IS_LOGGED_IN = False
            utils.trace(f"Panel Login from E0 message PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
            
        elif (serial_message[7] == 48 and serial_message[8] == 2 ):
            PANEL_IS_LOGGED_IN = True
            utils.trace(f"Panel Login from E0 message PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
           
        elif event == 29 or event == 31:
            send = paradoxArm()
            send.stringArmStatus="pending"
            send.intArmStatus=99
            send.Partition = partition
            sendArmStatusMQtt(send)
            
            
        
        elif event == 2 or event == 6:
            utils.trace(f"event:{event} updateArmStatus")
            updateArmStatus(event,sub_event, partition)
            utils.trace(f"returned from updateArmStatus")
            
            if (event == 2 and sub_event == 11):
                sendArmStatus(hassioStatus[partition])
            
            elif (event == 6 and sub_event == 27) or (event == 6  and sub_event>=3 and sub_event <= 6):
                sendArmStatus(hassioStatus[partition])
                
            elif event==2 and sub_event==12:
                sendArmStatus(hassioStatus[partition])
                
            if hassioStatus[partition].intArmStatus==4:
                sendArmStatusMQtt(hassioStatus[partition])
                
                
        #elif (event != 2 and sub_event != 12) :
        #    utils.trace(f"process message event:{event},sub_event:{sub_event} sendArmStatus")
        #    if (hassioStatus[partition].sent != hassioStatus[partition].intArmStatus):
        #        hassioStatus[partition].sent = hassioStatus[partition].intArmStatus
        #        sendArmStatus(hassioStatus[partition])  
        
        
    utils.trace(f"Ended processMessage")
      
def panel_status_0(panel_password):
    
    if PANEL_IS_LOGGED_IN ==False:
        panel_login(panel_password)
        
    statusdata = bytearray(MESSAGE_LENGTH)
    statusdata[0] = 0x50
    statusdata[1] = 0x00
    statusdata[2] = 0x80
    statusdata[3] = 0x00
    statusdata[33] = 0x05
    statusdata = checksum_calculate(statusdata)
    if serialWrite(statusdata):
        utils.trace("armdata written to serial")
        
    return True


def panel_status_1(panel_password):
    if PANEL_IS_LOGGED_IN ==False:
        panel_login(panel_password)
        
    statusdata = bytearray(MESSAGE_LENGTH)


    statusdata[0] = 0x50;
    statusdata[1] = 0x00;
    statusdata[2] = 0x80;
    statusdata[3] = 0x01;
    statusdata[33] = 0x05;
    statusdata = checksum_calculate(statusdata)
    if serialWrite(statusdata):
        utils.trace("armdata written to serial")
        
    return True


        

def process_status_1_message(inData):
    
    statusmsg = status_1()
    statusmsg.Fire= (inData[17]>>7)&1
    statusmsg.Audible=(inData[17]>>6)&1
    statusmsg.Silent=(inData[17]>>5)&1
    statusmsg.AlarmFlg=(inData[17]>>4)&1
    statusmsg.StayFlg=(inData[17]>>2)&1
    statusmsg.SleepFlg=(inData[17]>>1)&1
    statusmsg.ArmFlg=(inData[17]>>0)&1
 
    client.publish(f"{cfg.controller_name}/status_message_1",statusmsg.toJson())     


def process_status_0_message(inData):
  
    statusmsg = status_0()
    statusmsg.Timer_Loss = str((inData[4]>> 7) & 1)
    statusmsg.PowerTrouble  = str((inData[4]>>1) &1)
    statusmsg.ACFailureTroubleIndicator = str((inData[6]>>1) &1)
    statusmsg.NoLowBatteryTroubleIndicator = str((inData[6]>>0)&1)
    statusmsg.TelephoneLineTroubleIndicator = str((inData[8]>>0)&1)
    statusmsg.ACInputDCVoltageLevel = str(inData[15])
    statusmsg.PowerSupplyDCVoltageLevel =str(inData[16])
    statusmsg.BatteryDCVoltageLevel=str(inData[17])
    
    client.publish(f"{cfg.controller_name}/status_message_0",statusmsg.toJson())
    
    
def process_status_0_zones(inData):
    Zonename ="";
    zcnt = 0;
    zonemq = {}
    for i in range(19, 22):
        for j in range( 0 , 8):
            zcnt = zcnt+1
            Zonename = "zone" + str(zcnt)
            zonemq[Zonename] =  (inData[i]>>j)&1
    
    for k in zonemq:
        msg = "ON" if zonemq[k] == 1 else "OFF" 
        client.publish(f"{cfg.controller_name}/zones/{k}",msg,True,1)
        #time.sleep(0.2)
        #client.publish(f"{cfg.root_topicArmHomekit}/{k}",msg,True,1)
        
        
    mqmsg = json.dumps(zonemq)   
    client.publish(f"{cfg.controller_name}/status_message_0_zone",mqmsg)

   
        

def program_init(version):
    utils.trace(version)
    return f"Program started ver:{version}".encode()
    


def panel_control(inCommand=inMessage()):
    
    #panel_login(inCommand.panel_password)
    
    if PANEL_IS_LOGGED_IN ==False:
        panel_login(inCommand.panel_password)
    
    
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
    #    utils.trace(f"[armdata{x}]={hex(armdata[x])}")
        
    if serialWrite(armdata):
        utils.trace("armdata written to serial")
        
    return True


def set_panel_date(password):
    print('set_panel_date')
    panel_login(password)
    ntptime.settime()
    UTC_OFFSET = int(cfg.timezone) * 60 * 60
    actual_time = time.localtime(time.time() + UTC_OFFSET)
    datemsg = bytearray(MESSAGE_LENGTH)
    datemsg[0] = 0x30
    datemsg[4] = 0x21
    datemsg[5] = actual_time[0]-2000
    datemsg[6] = actual_time[1]
    datemsg[7] = actual_time[2]
    datemsg[8] = actual_time[3]
    datemsg[9] = actual_time[4]
    datemsg[33] = 0x05
    
    datemsg = checksum_calculate(datemsg)
    #for x in range(MESSAGE_LENGTH):
    #    utils.trace(f"[armdata{x}]={hex(armdata[x])}")
        
    if serialWrite(datemsg):
        utils.trace(f"datemsg written to serial date:{str(time.localtime(time.time() + UTC_OFFSET))}")
        
    return True


def checksum_calculate(data):
    checksum = 0
    for x in range(MESSAGE_LENGTH-1):  
        checksum += data[x]
    
    utils.trace(f"calculate checksum for {checksum}")
    while (checksum > 255) :
        intch =int(checksum / 256)
        checksum = checksum - intch * 256
    utils.trace(f"checksum = {checksum}")
    #checksum = checksum #& 0xFF
    #utils.trace(type(checksum))
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
    global COMUNTICATION_INIT,PANEL_LOGIN_IN_PROGRESS,PANEL_IS_LOGGED_IN
    
    PANEL_LOGIN_IN_PROGRESS=True
    #sleep(1)
    initMessage = initialize_comunitcation()
    
    
    utils.trace("Sent initialize_comunitcation")
    rinitMessage = serialReadWriteQuick(initMessage)
    COMUNTICATION_INIT=True
    websrv.set_panel_isconnected(COMUNTICATION_INIT)
    utils.trace("returned initialize_comunitcation")
    #utils.trace(rinitMessage)
    
    pass1 = "0x" + str(panel_password)[0:2]
    pass2 = "0x" + str(panel_password)[2:4]
    
    data1=bytearray(MESSAGE_LENGTH)
    
    data1[0] = 0x00;
    data1[4] = rinitMessage[4]
    data1[5] = rinitMessage[5]
    data1[6] = rinitMessage[6]
    data1[7] = rinitMessage[7]
    data1[7] = rinitMessage[8]
    data1[9] = rinitMessage[9]
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
    time.sleep(1)



def get_panel_command(arm_request):
    arm_request=arm_request.lower()
    retval = 0
    if (arm_request == "stay" or arm_request=="0"):
        retval= STAY_ARM
    elif (arm_request == "close" or arm_request=="1"):
        retval= CLOSE_CONNECTION
    elif (arm_request == "arm" or arm_request=="1"):
        retval= FULL_ARM
    elif (arm_request == "sleep" or arm_request=="2"):
        retval= SLEEP_ARM
    elif (arm_request == "disarm" or arm_request == "off" or arm_request == "3"):
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
    

def sendArmStatusMQtt(hass):
    print(f"SENDING ARM STATUS {hass}")
    
        
    arm_mesg=arm_message()
    arm_mesg.topic = cfg.root_topicHassioArm + str(hass.Partition)
    arm_mesg.Armstatus =  hass.intArmStatus
    arm_mesg.ArmStatusD = hass.stringArmStatus
    client.publish(arm_mesg.topic,hass.stringArmStatus, True, 1 )
    
    if hass.intArmStatus != 99:
        arm_mesg.topic = f"{cfg.root_topicArmHomekit}/Arm{str(hass.Partition)}"
        client.publish(arm_mesg.topic, hass.HomeKit, True, 1 )
    
    time.sleep(1)
    client.publish(cfg.root_topicStatus, hass.toJson())    
    return arm_mesg.toJson() 
  
def sendArmStatus(hass):
    utils.trace(f"SENDING ARM STATUS {hass}")
    
    LIFO.append(hass)
    print(f"Added to LIFO {hass.HomeKit}")
    #return arm_mesg.toJson() 
  
def timer_tick(timer):
    #print('timer ticked')
    client.ping()
    led.value(True)
    time.sleep(0.5)
    led.value(False)
    
    

Serial_loop_msg=False
def serialloop():
    global LIFO,Serial_loop_msg,PANEL_LOGIN_IN_PROGRESS,KILL_THREAD
    serial_last_read = time.time()
    wdt = WDT(timeout=10000)
    while True:
        wdt.feed()
        
        try:
            
            client.check_msg()
            #if PANEL_LOGIN_IN_PROGRESS != Serial_loop_msg:
            #      print(f"PANEL_LOGIN_IN_PROGRESS Status changed to {PANEL_LOGIN_IN_PROGRESS}")
            #      Serial_loop_msg=PANEL_LOGIN_IN_PROGRESS
            #if not PANEL_LOGIN_IN_PROGRESS:
            if serialRead():
                serial_last_read = time.time()
                  #print(f"LIFO len:{len(LIFO)}")
            
            
            if len(LIFO)>0 and (time.time() - serial_last_read > 5):
                LIFO = list(set(LIFO))
                print(f"LIFO is {LIFO}")
                for i in LIFO:
                        if not isinstance(i, str):
                            sendArmStatusMQtt(i)
                            
                            
               
                print("cleared LIFO")
                LIFO.clear()   
                
                
            gc.collect()
            
            
        except OSError as e:
            print(e)
            restart_and_reconnect()
            

if __name__ == '__main__':
    try:
        
        if station.isconnected() == True:
            
            t1= threading.Thread(target=serialloop)
            t2= threading.Thread(target=webrepl.start)
            websrv.set_webpage_vars(station.ifconfig(),COMUNTICATION_INIT)
            print('Starting MQTT')
            client = connect_and_subscribe()
            client.publish(cfg.root_topicStatus, f"PROGRAM {program_init(VERSION).decode()} IFconfig:{station.ifconfig()}")
            print('Starting Timer')
            
            tim1.init(period=5000, mode=machine.Timer.PERIODIC, callback=timer_tick)
            print('Starting serial loop')
            t1.start()
            
        print('Starting webrepl thread')
        t2.start()
        print("Starting Webserver")
        websrv.runsrv()
    except:
        restart_and_reconnect()
    