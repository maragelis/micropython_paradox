import websrv
import paradoxEvents
import utils
import ParadoxSubEvent
from homekit import homekit
import paradox_objects as pobj

gc.collect()

VERSION="1.6.202208121926"



hk = ""
client=""
paradoxserial=""
LIFO=[]
hassioStatus1 = pobj.paradoxArm()
hassioStatus2 = pobj.paradoxArm()
hassioStatus = (hassioStatus1,hassioStatus2)
PANEL_IS_LOGGED_IN=False
COMUNTICATION_INIT=False
PANEL_LOGIN_IN_PROGRESS=False


def main():
    global hk,client,paradoxserial
    print("hold 0 'boot button' for 5sec or ctrl-c to enter repl")
    led.value(False)
    
    
    websrv.cfg = cfg
    websrv.set_webpage_vars(station.ifconfig(),COMUNTICATION_INIT)

    replloopcnt=0
    while replloopcnt <= 5:
        if repl_button.value() == 0:
            utils.trace("Dropping to REPL")
            sys.exit()
        else:
            print(f"waiting for repl {5-replloopcnt} {'.' * replloopcnt} ")
            replloopcnt +=1
            time.sleep(1)
       
    
    paradoxserial = UART(cfg.ESP_UART,baudrate=9600)
    paradoxserial.init()

    try:
        t1= threading.Thread(target=serialloop)
        t2= threading.Thread(target=webrepl.start)
        if station.isconnected() == True:
            
            
            
            print('Starting MQTT')
            client = connect_and_subscribe()
            client.publish(cfg.root_topicStatus, f"PROGRAM {program_init(VERSION).decode()} IFconfig:{station.ifconfig()}")
            print('Starting Timer')
            tim1 = machine.Timer(0)
            tim1.init(period=5000, mode=machine.Timer.PERIODIC, callback=timer_tick)
            
            if cfg.homekit==True :
                print ("Loading homekit accessories")
                hk=homekit(homebridge_prefix=f"{cfg.root_topicIn}/homebridge",controller_name=cfg.controller_name ,mqttclient=client)
                
                        
            print('Starting serial loop')
            t1.start()
            
        print('Starting webrepl thread')
        t2.start()
        print("Starting Webserver")
        websrv.runsrv()
    except:
        restart_and_reconnect()
    

def sub_cb(topic, msg):
    #print((topic, msg))
        
    if topic == bytes(f"{homekit.from_set}/{cfg.controller_name}","utf-8") and cfg.homekit==True:
        print("in homekit command")
        strmsg = msg.decode("utf-8")
        try:
            json_data = json.loads(strmsg.lower())
            cmd = pobj.inMessage()
            cmd.panel_password = cfg.homekit_user
            cmd.command = str(json_data['value'])
            
            
            if panel_control(cmd):
                hk.set_alarm_state(homekit.SecuritySystemTargetState_characteristic,json_data['value'])
            
        except ValueError as e:
            client.publish(cfg.root_topicStatus, "malformatted json message try {'command':'arm','password':'1234'}" )
            return
            
        #print(strmsg)
        return



    if topic == bytes(cfg.root_topicIn,"utf-8"):
        strmsg = msg.decode("utf-8")
        try:
            json_data = json.loads(strmsg.lower())
            
            if "password" in json_data:
                password = str(json_data['password'])
            elif cfg.homekit_user != "0000":
                password = cfg.homekit_user
            else:
                password = "0000"
            
        except ValueError as e:
            client.publish(cfg.root_topicStatus, "malformatted json message try {'command':'arm','password':'1234'}" )
            return
            
        if "esp_command" in json_data:
                pass
        
        elif "panel_command" in json_data:
            if (str(json_data['panel_command']) == "setdate"):
                set_panel_date(password)
                
            elif (str(json_data['panel_command']) == "status_0"):
                panel_status_0(password)
                
            elif (str(json_data['panel_command']) == "status_1"):
                panel_status_1(password)
            
            elif (str(json_data['panel_command']) == "arm_state"):
                sendArmStatusMQtt(hassioStatus1)
                if hassioStatus2.intArmStatus!=99:
                    sendArmStatusMQtt(hassioStatus2)
                
            
            else:
                client.publish(cfg.root_topicStatus, "unknown panel_command" )
                
                
        elif ("command" in json_data) and cfg.homekit_secure == False:
            inmessage =pobj.inMessage()
            inmessage.command = json_data["command"]
            inmessage.panel_password=""
            fixed_password = ""
            
            if "panel_password" in json_data:
                fixed_password=password
                
            elif "password" in json_data:
                fixed_password=password
            
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
    global client
    
    client_id = cfg.mqttclientid#ubinascii.hexlify(machine.unique_id())
    topic_sub = f"{cfg.root_topicIn}/#"
    mqtt_server = cfg.mqttserver
    utils.trace(f"mqtt_server:{cfg.mqttserver}, username:{cfg.mqttusername}, password:{cfg.mqttpassword}, topic:{cfg.root_topicIn}")

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
        
    
        MESSAGE = bytearray(cfg.MESSAGE_LENGTH)
            
        if  paradoxserial.any() >= 37 :
            #reset_message()
            #print(f"serialRead has data {paradoxserial.any()}")
            paradoxserial.readinto(MESSAGE)
            
            if (MESSAGE[7] == 3 and MESSAGE[8] <=1):
                #print("return for bell")
                return True
            
            
                
            processMessage(MESSAGE)
            if cfg.SEND_ALL_EVENTS:
                get_event_data(MESSAGE)
            
            return True
        else:
            return False
    except OSError as e:
        print(e)
        restart_and_reconnect()
    #sleep(0.5)
    
def serialReadWriteQuick(byteMessage):
    time_start = time.time()
    paradoxserial.write(byteMessage)
    
    serial_message= bytearray(cfg.MESSAGE_LENGTH)
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
    while paradoxserial.write(byteMessage) != cfg.MESSAGE_LENGTH:
        wcnt = wcnt +1
        time.sleep(1)
        if wcnt > 5:
            return False
        else:
            return True
    




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
    e0msg = pobj.E0_message()
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
    
def process_zone_message(serial_message):
    
    #zone message
    utils.trace("E0 Zone Message receivied")
    e = pobj.zone_message()
    e.zone=serial_message[8]
    e.state="ON" if serial_message[7] == 1 else "OFF" 
    e.Partition_Number=serial_message[9]
    e.zone_name=serial_message[15:30].decode().strip()
    e.topic = f"{cfg.controller_name}/zones/zone{str(serial_message[8])}"
    e.zone_def = f"zone{str(serial_message[8])}"
    e.zone_type=homekit.ContactDetectorType
    zonename=f"zone{str(serial_message[8])}"
    
    if zonename in cfg.zonedef:
        e.zone_def=f"zone{str(serial_message[8])}_{cfg.zonedef[zonename]['name']}"
        e.topic = f"{cfg.controller_name}/zones/{e.zone_def}"
        e.zone_type=cfg.zonedef[zonename]['type']
    
    if cfg.homekit_secure == False:
        utils.trace(f"returning zoneJson  {e.toJson()}")
        client.publish(e.topic, str(e.state), True, 1 )
        
        e.topic = cfg.root_topicStatus
        client.publish(cfg.root_topicStatus, e.toJson())  
    
    if cfg.homekit==True  and isinstance(hk, homekit):
        hk.set_zone_value(zone=e.zone_def,zone_type=e.zone_type,state=e.state)
    
            
     

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
            process_zone_message(serial_message)
            
             
        
        elif (serial_message[7] == 44 and serial_message[8] == 1):
            client.publish(f"{cfg.controller_name}/AC_failure","true",retain=True)
        
        elif (serial_message[7] == 45 and serial_message[8] == 1):
            client.publish(f"{cfg.controller_name}/AC_failure","false",retain=True)
                
        elif (serial_message[7] == 44 and serial_message[8] == 2):
            client.publish(f"{cfg.controller_name}/Battery_failure","true",retain=True)
        
        elif (serial_message[7] == 45 and serial_message[8] == 2):
                client.publish(f"{cfg.controller_name}/Battery_failure","false",retain=True)
            
        elif (serial_message[7] == 48 and serial_message[8] == 3):
            PANEL_IS_LOGGED_IN = False
            utils.trace(f"Panel Login from E0 message PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
            
        elif (serial_message[7] == 48 and serial_message[8] == 2 ):
            PANEL_IS_LOGGED_IN = True
            utils.trace(f"Panel Login from E0 message PANEL_IS_LOGGED_IN:{PANEL_IS_LOGGED_IN}")
           
        elif event == 29 or event == 31:
            send = pobj.paradoxArm()
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
        
    statusdata = bytearray(cfg.MESSAGE_LENGTH)
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
        
    statusdata = bytearray(cfg.MESSAGE_LENGTH)


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
    global hassioStatus
    
    statusmsg = pobj.status_1()
    statusmsg.Fire= (inData[17]>>7)&1
    statusmsg.Audible=(inData[17]>>6)&1
    statusmsg.Silent=(inData[17]>>5)&1
    statusmsg.AlarmFlg=(inData[17]>>4)&1
    statusmsg.StayFlg=(inData[17]>>2)&1
    statusmsg.SleepFlg=(inData[17]>>1)&1
    statusmsg.ArmFlg=(inData[17]>>0)&1
    
    if statusmsg.SleepFlg==1:
        hassioStatus[0].HomeKit = "NA"
        hassioStatus[0].stringArmStatus="armed_home"
        hassioStatus[0].intArmStatus=2
    elif statusmsg.StayFlg==1:
        hassioStatus[0].HomeKit = "SA"
        hassioStatus[0].stringArmStatus="armed_home"
        hassioStatus[0].intArmStatus=0
    elif statusmsg.ArmFlg==1:
        hassioStatus[0].HomeKit = "AA"
        hassioStatus[0].stringArmStatus="armed_away"
        hassioStatus[0].intArmStatus=1
    elif statusmsg.AlarmFlg==1:
        hassioStatus[0].HomeKit = "T"
        hassioStatus[0].stringArmStatus="triggered"
        hassioStatus[0].intArmStatus=4
    else:
        hassioStatus[0].HomeKit = "D"
        hassioStatus[0].stringArmStatus="disarmed"
        hassioStatus[0].intArmStatus=3
    hassioStatus[0].Partition = 0
    sendArmStatusMQtt(hassioStatus[0])
         
    
    
        
    
    client.publish(f"{cfg.controller_name}/status_message_1_0",statusmsg.toJson())
    
    statusmsg.Fire= (inData[21]>>7)&1
    statusmsg.Audible=(inData[21]>>6)&1
    statusmsg.Silent=(inData[21]>>5)&1
    statusmsg.AlarmFlg=(inData[21]>>4)&1
    statusmsg.StayFlg=(inData[21]>>2)&1
    statusmsg.SleepFlg=(inData[21]>>1)&1
    statusmsg.ArmFlg=(inData[21]>>0)&1
    
    if statusmsg.SleepFlg==1:
        hassioStatus[1].HomeKit = "NA"
        hassioStatus[1].stringArmStatus="armed_home"
        hassioStatus[1].intArmStatus=2
    elif statusmsg.StayFlg==1:
        hassioStatus[1].HomeKit = "SA"
        hassioStatus[1].stringArmStatus="armed_home"
        hassioStatus[1].intArmStatus=0
    elif statusmsg.ArmFlg==1:
        hassioStatus[1].HomeKit = "AA"
        hassioStatus[1].stringArmStatus="armed_away"
        hassioStatus[1].intArmStatus=1
    elif statusmsg.AlarmFlg==1:
        hassioStatus[1].HomeKit = "T"
        hassioStatus[1].stringArmStatus="triggered"
        hassioStatus[1].intArmStatus=4
    else:
        hassioStatus[1].HomeKit = "D"
        hassioStatus[1].stringArmStatus="disarmed"
        hassioStatus[1].intArmStatus=3
    hassioStatus[1].Partition = 1
    sendArmStatusMQtt(hassioStatus[1])
    
    client.publish(f"{cfg.controller_name}/status_message_1_1",statusmsg.toJson())


def process_status_0_message(inData):
  
    statusmsg = pobj.status_0()
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
            if Zonename in cfg.zonedef:
                if cfg.zonedef[Zonename]["enabled"] == True:
                    zonemq[f"{Zonename}_{cfg.zonedef[Zonename]['name']}"] =  (inData[i]>>j)&1
            else:
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
    


def panel_control(inCommand=pobj.inMessage()):
    
    #panel_login(inCommand.panel_password)
    
    if PANEL_IS_LOGGED_IN ==False:
        panel_login(inCommand.panel_password)
    
    
    
    panel_command = get_panel_command(inCommand.command)
    panel_subcommand = int(inCommand.subcommand) 
    if panel_command == cfg.BYPASS or panel_command == cfg.PGMOFF or panel_command == cfg.PGMON:
        panel_subcommand = int(inCommand.subcommand) -1
    
    if panel_command == cfg.SET_DATE:
        set_panel_date(inCommand.panel_password)
        return
    
    armdata = bytearray(cfg.MESSAGE_LENGTH)
    armdata[0] = 0x40
    armdata[2] = panel_command
    armdata[3] = panel_subcommand
    armdata[33] = 0x05
    armdata[34] = 0x00
    armdata[35] = 0x00
    armdata = checksum_calculate(armdata)
    #for x in range(cfg.MESSAGE_LENGTH):
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
    datemsg = bytearray(cfg.MESSAGE_LENGTH)
    datemsg[0] = 0x30
    datemsg[4] = 0x21
    datemsg[5] = actual_time[0]-2000
    datemsg[6] = actual_time[1]
    datemsg[7] = actual_time[2]
    datemsg[8] = actual_time[3]
    datemsg[9] = actual_time[4]
    datemsg[33] = 0x05
    
    datemsg = checksum_calculate(datemsg)
    #for x in range(cfg.MESSAGE_LENGTH):
    #    utils.trace(f"[armdata{x}]={hex(armdata[x])}")
        
    if serialWrite(datemsg):
        utils.trace(f"datemsg written to serial date:{str(time.localtime(time.time() + UTC_OFFSET))}")
        
    return True


def checksum_calculate(data):
    checksum = 0
    for x in range(cfg.MESSAGE_LENGTH-1):  
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
    
    data = bytearray(cfg.MESSAGE_LENGTH)
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
    
    data1=bytearray(cfg.MESSAGE_LENGTH)
    
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
    if (arm_request == "stay" or arm_request=="0" ):
        retval= paradox_objects.STAY_ARM
    elif (arm_request == "close"  ):
        retval= cfg.CLOSE_CONNECTION
    elif (arm_request == "arm" or arm_request=="1" ):
        retval= cfg.FULL_ARM
    elif (arm_request == "sleep" or arm_request=="2" ):
        retval= cfg.SLEEP_ARM
    elif (arm_request == "disarm" or arm_request == "off" or arm_request == "3"):
        return cfg.DISARM
    elif (arm_request == "bypass" or arm_request == "10"):
        retval= cfg.BYPASS
    elif (arm_request == "pgm_on" or arm_request == "pgmon"):
        retval= cfg.PGMON
    elif (arm_request == "pgm_off" or arm_request == "pgmoff"):
        retval= cfg.PGMOFF
    elif (arm_request == "panelstatus" ):
        retval= cfg.PANEL_STATUS
    elif (arm_request == "setdate"):
        retval= cfg.SET_DATE
    elif (arm_request == "armstate"):
        retval= cfg.ARM_STATE
    return retval
    

def sendArmStatusMQtt(hass):
    print(f"SENDING ARM STATUS {hass}")
    
        
    arm_mesg=pobj.arm_message()
    arm_mesg.topic = cfg.root_topicHassioArm + str(hass.Partition)
    arm_mesg.Armstatus =  hass.intArmStatus
    arm_mesg.ArmStatusD = hass.stringArmStatus
    
    if cfg.homekit_secure == False:
        client.publish(arm_mesg.topic,hass.stringArmStatus, True, 1 )
    
    if hass.intArmStatus != 99:
        #arm_mesg.topic = f"{cfg.root_topicArmHomekit}/Arm{str(hass.Partition)}"
        #client.publish(arm_mesg.topic, hass.HomeKit, True, 1 )
        
        if cfg.homekit==True and isinstance(hk, homekit) :
            hk.set_alarm_state(homekit.SecuritySystemTargetState_characteristic,hass.intArmStatus)
            time.sleep(1)
            hk.set_alarm_state(homekit.SecuritySystemCurrentState_characteristic,hass.intArmStatus)
        
     
    #return arm_mesg.toJson() 
  
def sendArmStatus(hass):
    utils.trace(f"SENDING ARM STATUS {hass}")
    
    LIFO.append(hass)
    print(f"Added to LIFO {hass.HomeKit}")
    #return arm_mesg.toJson() 
  
def timer_tick(timer):
    #print('timer ticked')
    client.ping()
    led.value(True)
    time.sleep_ms(500)
    led.value(False)
    

    

    
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
            
            
            if len(LIFO)>0 and (time.time() - serial_last_read >= 2):
                LIFO = list(set(LIFO))
                #print(f"LIFO is {LIFO}")
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
    main()
    