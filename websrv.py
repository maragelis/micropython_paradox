
import uasyncio as asyncio
from microdot_asyncio import Microdot, send_file
import os
import machine
import network
import config
cfg = config.configuration()

_ipaddress=""
_PanelConnected=False

def set_webpage_vars( ipaddress, PanelConnected):
    global _ipaddress,_PanelConnected
    _ipaddress = ipaddress[0]
    _PanelConnected=PanelConnected

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

@app.route('/reset')
async def index(request):
    machine.reset()
    return "ok"

@app.route('/Soft_reset')
async def index(request):
    machine.soft_reset()
    return "ok"

async def main():
    await app.start_server(debug=True)

def runsrv():
    asyncio.run(main())
