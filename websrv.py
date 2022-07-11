
import uasyncio as asyncio
from microdot_asyncio import Microdot, send_file

app = Microdot()

@app.route('/')
async def index(request):
    response = send_file('html/index.html')
    return response

async def main():
    await app.start_server(debug=True)

def runsrv():
    asyncio.run(main())
