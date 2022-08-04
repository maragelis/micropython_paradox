def getsubEvent(event,subevent):
    
    if event == 2:
        if subevent == 2:
            return "Silent alarm"
        
        elif subevent == 3:
            return "Buzzer alarm"
        
        elif subevent == 4: 
            return "Steady alarm"


        elif subevent == 5:
            return "Pulsed alarm"


        elif subevent == 6:
            return "Strobe"


        elif subevent == 7: 
            return "Alarm stopped"
          

        elif subevent == 8:
            return "Squawk ON"
         

        elif subevent == 9: 
            return "Squawk OFF"
         

        elif subevent == 10: 
            return "Ground start"


        elif subevent == 11: 
            return "Disarm partition"


        elif subevent == 12:
            return "Arm partition"


        elif subevent == 13:
            return "Entry delay started"


        elif subevent == 14:
            return "Exit delay started"


        elif subevent == 15:
            return "Pre-alarm delay"
         

        elif subevent == 16: 
            return "Report confirmation"


        elif subevent == 99: 
            return "Any partition status event"
         

        else: 
          return ""
          

    elif event == 03:
        
        if subevent == 0:
            return "Bell OFF"


        elif subevent == 1: 
            return "Bell ON"


        elif subevent == 2: 
            return "Bell squawk arm"


        elif subevent == 3: 
            return "Bell squawk disarm"


        else: 
            return ""

       


    elif event == 06:
        if subevent == 0: 
            return "Telephone line trouble"


        elif subevent == 1: 
            return "CLEAR + ENTER"


        elif subevent == 3: 
            return "Arm in Stay mode"


        elif subevent == 4: 
            return "Arm in Sleep mode"


        elif subevent == 5: 
            return "Arm in Force mode"


        elif subevent == 6: 
            return "Full arm when armed in Stay mode"


        elif subevent == 7: 
            return "PC fail to communicate"


        elif subevent == 8: 
            return "Utility key 1-2 pressed"


        elif subevent == 9: 
            return "Utility key 4-5 pressed"


        elif subevent == 10: 
            return "Utility key 7-8 pressed"


        elif subevent == 11: 
            return "Utility key 2-3 pressed"


        elif subevent == 12: 
            return "Utility key 5-6 pressed"


        elif subevent == 13: 
            return "Utility key 8-9 pressed"


        elif subevent == 14: 
            return "Tamper generated alarm"


        elif subevent == 15: 
            return "Supervision loss generated alarm"


        elif subevent == 20: 
            return "Full arm when armed in Sleep mode"


        elif subevent == 23: 
            return "StayD mode activated"


        elif subevent == 24: 
            return "StayD mode deactivated"


        elif subevent == 25: 
            return "IP registration status change"


        elif subevent == 26: 
            return "GPRS registration status change"


        elif subevent == 27: 
            return "Armed with trouble(s)"


        elif subevent == 28: 
            return "Supervision alert"


        elif subevent == 29: 
            return "Supervision alert restore"


        elif subevent == 30: 
            return "Armed with remote with low battery"



        else: 
            return ""


    elif event == 26:
        if subevent == 0:
            return "Non-valid source ID"
        elif subevent ==1:
            return "WinLoad/BabyWare direct"
        elif subevent ==2:
            return "WinLoad/BabyWare through IP module"
        elif subevent ==3:
            return "WinLoad/BabyWare through GSM module"
        elif subevent ==4:
            return "WinLoad/BabyWare through modem"
        
        elif subevent ==5:
            return "NEware direct"
        elif subevent ==6:
            return "NEware through IP module"
        elif subevent ==7:
            return "NEware through GSM module"
        elif subevent ==8:
            return "NEware through modem"
        elif subevent ==9:
            return "IP100 direct"
        elif subevent ==10:
            return "VDMP3 direct"
        elif subevent ==11:
            return "Voice through GSM module"
        elif subevent ==12:
            return "Remote access"
        elif subevent ==13:
            return "SMS through GSM module"
        elif subevent ==99:
            return "Any software access"
        else:
            return ""

    elif event == 30:
        if subevent == 0: 
            return "Auto-arming"


        elif subevent == 1: 
            return "Late to close"


        elif subevent == 2: 
            return "No movement arming"



        elif subevent == 3: 
            return "Partial arming"


        elif subevent == 4: 
            return "Quick arming"


        elif subevent == 5: 
            return "Arming through WinLoad/BabyWare"


        elif subevent == 6: 
            return "Arming with keyswitch"


        else:
            return ""

       


    elif event == 34:
        if subevent == 0: 
            return "Auto-arm cancelled"


        elif subevent == 1: 
            return "Disarming through WinLoad/BabyWare"


        elif subevent == 2: 
            return "Disarming through WinLoad/BabyWare after alarm"


        elif subevent == 3: 
            return "Alarm cancelled through WinLoad/BabyWare"


        elif subevent == 4: 
            return "Paramedical alarm cancelled"


        elif subevent == 5: 
            return "Disarm with keyswitch"


        elif subevent == 6: 
            return "Disarm with keyswitch after an alarm"


        elif subevent == 7: 
            return "larm cancelled with keyswitch"


        else:
            return ""


        


    elif event == 40:
        if subevent == 0: 
            return "Panic non-medical emergency"


        elif subevent == 1: 
            return "Panic medical"


        elif subevent == 2: 
            return "Panic fire"


        elif subevent == 3: 
            return "Recent closing"


        elif subevent == 4: 
            return "Global shutdown"


        elif subevent == 5: 
            return "Duress alarm"


        elif subevent == 6: 
            return "Keypad lockout"


        else:
            return ""


    elif event == 44:
        if subevent == 1: 
            return "AC failure"


        elif subevent == 2: 
            return "Battery failure"


        elif subevent == 3: 
            return "Auxiliary current overload"


        elif subevent == 4: 
            return "Bell current overload"


        elif subevent == 5: 
            return "Bell disconnected"


        elif subevent == 6: 
            return "Clock loss"


        elif subevent == 7: 
            return "Fire loop trouble"


        elif subevent == 8: 
            return "Fail call station telephone # 1"


        elif subevent == 9: 
            return "Fail call station telephone # 2"


        elif subevent == 11: 
            return "Fail to communicate with voice report"


        elif subevent == 12: 
            return "RF jamming"


        elif subevent == 13: 
            return "GSM RF jamming"


        elif subevent == 14: 
            return "GSM no service"


        elif subevent == 15: 
            return "GSM supervision lost"


        elif subevent == 16: 
            return "Fail to communicate IP receiver 1"


        elif subevent == 17: 
            return "Fail to communicate IP receiver 2"


        elif subevent == 18: 
            return "IP module no service"


        elif subevent == 19: 
            return "IP module supervision loss"


        elif subevent == 20: 
            return "Fail to communicate IP receiver 1"


        elif subevent == 21: 
            return "Fail to communicate IP receiver 2"


        elif subevent == 22: 
            return "GSM/GPRS module tamper trouble"


        else:
            return ""

    elif event == 45:
        if subevent == 1: 
            return "AC failure"


        elif subevent == 2: 
            return "Battery failure"


        elif subevent == 3: 
            return "Auxiliary current overload"


        elif subevent == 4: 
            return "Bell current overload"


        elif subevent == 5: 
            return "Bell disconnected"


        elif subevent == 6: 
            return "Clock loss"


        elif subevent == 7: 
            return "Fire loop trouble"


        elif subevent == 8: 
            return "Fail call station telephone # 1"


        elif subevent == 9: 
            return "Fail call station telephone # 2"


        elif subevent == 11: 
            return "Fail to communicate with voice report"


        elif subevent == 12: 
            return "RF jamming"


        elif subevent == 13: 
            return "GSM RF jamming"


        elif subevent == 14: 
            return "GSM no service"


        elif subevent == 15: 
            return "GSM supervision lost"


        elif subevent == 16: 
            return "Fail to communicate IP receiver 1"


        elif subevent == 17: 
            return "Fail to communicate IP receiver 2"


        elif subevent == 18: 
            return "IP module no service"


        elif subevent == 19: 
            return "IP module supervision loss"


        elif subevent == 20: 
            return "Fail to communicate IP receiver 1"


        elif subevent == 21: 
            return "Fail to communicate IP receiver 2"


        elif subevent == 22: 
            return "GSM/GPRS module tamper trouble"


        else:
            return ""


    
    elif subevent == 48:
        if subevent == 0:
            return "System power up"
        elif subevent ==1:
            return "Reporting test"
        elif subevent ==2:
            return "Software log on"
        elif subevent ==3:
            return "Software log off"
        elif subevent ==4:
            return "Installer in programming mode"
        elif subevent ==5:
            return "Installer exited programming mode"
        elif subevent ==6:
            return "Maintenance in programming mode"
        elif subevent ==7:
            return "Maintenance exited programming mode"
        elif subevent ==8:
            return "Closing delinquency delay elapsed"
        elif subevent ==9:
            return "Any special even"
        
        else:
            return ""

    else:
        return ""
        