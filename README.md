# micropython_paradox

Getting Started with Thonny MicroPython (Python) IDE for ESP32 and ESP8266
https://randomnerdtutorials.com/getting-started-thonny-micropython-python-ide-esp32-esp8266/

Change the config.json file to suit your preference. 
After you have the esp32 running Micropython just upload the program and reset. Uploading is done in the thonny IDE


# ParadoxRs232toMqtt

This project uses a ESP32 to read the events of the serial bus on Paradox alarm systems and send them to an MQTT server

## Making a connection

Connect the devices together:
- Alarm system serial to ESP32 through RX2/TX2<br>

## settings

The config.json file contains all settings that can be eddited by the user.
After connecting to wifi, config can be changed using http://ipaddress

        
The 37 byte message is broken down into a json message with "Event Group" and "Sub-group", and one more dummy attribute which is the zone/partition label.

See the wiki for more info on Groups and Sub-groups


### MQTT Topics 

| Topic              | Notes                     |
|--------------------|---------------------------|
| paradoxdCTL/out    | All alarm event messages  |
| paradoxdCTL/status | The program messages      |
| paradoxdCTL/in     | Input topic               |

### HomeAssistant MQTT Topics

| Topic                                   | Notes                                                     |
|-----------------------------------------|-----------------------------------------------------------|
| paradoxdCTL/hassio/zoneX                | Where x is zone number from 1-32                          |
| paradoxdCTL/hassio/Arm[partition]/zoneX | Gives values ON/OFF                                       |
| paradoxdCTL/hassio/Arm[partition]       | Gives values: disarmed, armed_home, armed_away, triggered |

### Sending commands

The command payloads are in JSON. Template:
```json
{
 "password":"1234",
 "command":"arm",
 "cubcommand":"0"
}
```
The password is the user's 4 digit password.

A command can be any of the following:
- arm
- disarm
- sleep
- stay
- bypass
- PGM_ON
- PGM_OFF
	
#### Subcommands depending on the main command
	
| Main Command     | Subcommand                     |
|------------------|--------------------------------|
| arm,sleep,disarm | partition                      |
| bypass           | The zone number from 0 to 31   |
| panelstatus      | panel data                     |
| panelstatus      | panel voltage and battery data |

### Release Logs


Continue reading the wiki for more information.
