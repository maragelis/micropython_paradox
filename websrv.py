
import uasyncio as asyncio
from microdot_asyncio import Microdot, send_file, redirect
import os
import machine
import network
import config
from time import sleep
import _thread


cfg = config.configuration()

_ipaddress=""
_PanelConnected=False

def set_webpage_vars( ipaddress, PanelConnected):
    global _ipaddress,_PanelConnected
    _ipaddress = ipaddress[0]
    _PanelConnected=PanelConnected

def set_panel_isconnected(panelconnected):
    global _PanelConnected
    _PanelConnected=panelconnected

app = Microdot()

@app.route('/')
async def index(request):
    f = open('html/index.html','r')
    htmlstr =f.read()
    
    htmlstr = htmlstr.replace("[controller_name]",cfg.controller_name)
    htmlstr = htmlstr.replace("[ipaddress]",_ipaddress)
    htmlstr = htmlstr.replace("[PanelConnected]",str(_PanelConnected))
    
    #response = htmlstr
    return htmlstr, 200, {'Content-Type': 'text/html'}

def reset_machine():
    sleep(5)
    machine.reset()
    
def softreset_machine():
    sleep(5)
    machine.soft_reset()

@app.route('/reset')
async def reset(request):
    treset = _thread.start_new_thread(reset_machine,())
    return redirect('/')
    

@app.route('/jsonconfig')
async def jsonconfig(request):
    return send_file('config.json',200,'application/json')

@app.route('/config')
async def config(request):
    return send_file('html/config.html')

@app.route('/savejson',methods=['POST'])
async def savejson(request):
    try:
        cfg.wifissid=request.form['wifissid']
        cfg.wifipassword=request.form['wifipassword']
        cfg.mqttserver=request.form['mqttserver']
        cfg.mqttusername=request.form['mqttusername']
        cfg.mqttpassword=request.form['mqttpassword']
        cfg.root_topicOut=request.form['root_topicOut']
        cfg.root_topicStatus=request.form['root_topicStatus']
        cfg.root_topicIn=request.form['root_topicIn']
        cfg.root_topicHassioArm=request.form['root_topicHassioArm']
        cfg.root_topicHassio=request.form['root_topicHassio']
        cfg.root_topicArmHomekit=request.form['root_topicArmHomekit']
        cfg.ESP_UART=int(request.form['ESP_UART'])
        cfg.controller_name=request.form['controller_name']
        cfg.timezone=request.form['timezone']
        
        f = open('config.json','w')
        f.write(cfg.toJson())
        f.close()
        
        return send_file('html/saveOK.html')
    except:
        return "ERROR SAVING <a href='/config'>Return to config</a>",200,"text/html"
        

@app.route('/test')
async def testsave(request):
    return send_file('html/test.html')

    

@app.route('/Soft_reset')
async def Soft_reset(request):
    treset = _thread.start_new_thread(softreset_machine,())
    return redirect('/')

async def main():
    await app.start_server(debug=True,port=80)

def runsrv():
    asyncio.run(main())
    
def stopsrv():
    app.shutdown()

#runsrv()